// Copyright 2019-2024 Tauri Programme within The Commons Conservancy
// SPDX-License-Identifier: Apache-2.0
// SPDX-License-Identifier: MIT
//! Repository patch: HTML5 parsing without a CSS selector engine.
//! Internal Tauri APIs; the DOM representation is not a stable public API.

use crate::{
  assets::{SCRIPT_NONCE_TOKEN, STYLE_NONCE_TOKEN},
  config::DisabledCspModificationKind,
};
use html5ever::{Attribute, LocalName, QualName, ns, tendril::TendrilSink};
use markup5ever_rcdom::{Handle, Node, NodeData, RcDom, SerializableHandle};
use std::{cell::RefCell, rc::Rc};

/// Parsed HTML5 document, shared only within one build/runtime operation.
pub struct Document {
  root: Handle,
}

/// Parse with the upstream HTML5 tree builder, including malformed-input recovery.
pub fn parse_doc(html: String) -> Document {
  Document {
    root: html5ever::parse_document(RcDom::default(), Default::default())
      .one(html)
      .document,
  }
}

/// Serialize using the upstream HTML5 serializer (including raw-text elements).
pub fn serialize_doc(document: &Document) -> Vec<u8> {
  let mut bytes = Vec::new();
  html5ever::serialize(
    &mut bytes,
    &SerializableHandle::from(document.root.clone()),
    Default::default(),
  )
  .expect("serialize HTML document to memory");
  bytes
}

fn elements(document: &Document, tag: &str) -> Vec<Handle> {
  let mut result = Vec::new();
  let mut pending = vec![document.root.clone()];
  while let Some(node) = pending.pop() {
    if matches!(&node.data, NodeData::Element { name, .. } if &*name.local == tag) {
      result.push(node.clone());
    }
    // Do not traverse template contents: like DOM selectors these are a separate document fragment.
    pending.extend(node.children.borrow().iter().rev().cloned());
  }
  result
}

fn attr(node: &Handle, key: &str) -> Option<String> {
  if let NodeData::Element { attrs, .. } = &node.data {
    attrs
      .borrow()
      .iter()
      .find(|a| a.name.ns == ns!() && &*a.name.local == key)
      .map(|a| a.value.to_string())
  } else {
    None
  }
}

fn set_attr(node: &Handle, key: &str, value: &str) {
  if let NodeData::Element { attrs, .. } = &node.data {
    let mut attrs = attrs.borrow_mut();
    if let Some(a) = attrs
      .iter_mut()
      .find(|a| a.name.ns == ns!() && &*a.name.local == key)
    {
      a.value = value.into();
    } else {
      attrs.push(Attribute {
        name: QualName::new(None, ns!(), LocalName::from(key)),
        value: value.into(),
      });
    }
  }
}

fn element(tag: &str) -> Handle {
  Node::new(NodeData::Element {
    name: QualName::new(None, ns!(html), LocalName::from(tag)),
    attrs: RefCell::new(vec![]),
    template_contents: RefCell::new(None),
    mathml_annotation_xml_integration_point: false,
  })
}

fn attach(parent: &Handle, child: Handle, prepend: bool) {
  child.parent.set(Some(Rc::downgrade(parent)));
  if prepend {
    parent.children.borrow_mut().insert(0, child);
  } else {
    parent.children.borrow_mut().push(child);
  }
}

fn head(document: &Document) -> Handle {
  if let Some(head) = elements(document, "head").into_iter().next() {
    return head;
  }
  let html = elements(document, "html")
    .into_iter()
    .next()
    .expect("HTML5 document root");
  let head = element("head");
  attach(&html, head.clone(), true);
  head
}

/// Preserve existing nonce attributes and per-directive modification controls.
pub fn inject_nonce_token(document: &Document, disabled: &DisabledCspModificationKind) {
  for (tag, directive, token) in [
    ("script", "script-src", SCRIPT_NONCE_TOKEN),
    ("style", "style-src", STYLE_NONCE_TOKEN),
  ] {
    if !disabled.can_modify(directive) {
      continue;
    }
    for node in elements(document, tag) {
      if tag == "script" && !attr(&node, "src").is_some_and(|src| src.starts_with("http")) {
        continue;
      }
      if attr(&node, "nonce").is_none() {
        set_attr(&node, "nonce", token);
      }
    }
  }
}

/// Insert the production policy as HTML attributes, never interpolated markup.
pub fn inject_csp(document: &Document, csp: &str) {
  let meta = element("meta");
  set_attr(&meta, "http-equiv", "Content-Security-Policy");
  set_attr(&meta, "content", csp);
  attach(&head(document), meta, false);
}

fn text_content(node: &Handle) -> String {
  let mut text = String::new();
  let mut pending = vec![node.clone()];
  while let Some(node) = pending.pop() {
    if let NodeData::Text { contents } = &node.data {
      text.push_str(&contents.borrow());
    }
    pending.extend(node.children.borrow().iter().rev().cloned());
  }
  text
}

/// Contents of nonempty HTML script elements in document order, matching the
/// previous script:not(:empty) query without implementing general CSS selectors.
pub fn inline_script_contents(document: &Document) -> Vec<String> {
  elements(document, "script")
    .into_iter()
    .filter(|node| {
      node
        .children
        .borrow()
        .iter()
        .any(|child| matches!(child.data, NodeData::Element { .. } | NodeData::Text { .. }))
    })
    .map(|node| text_content(&node))
    .collect()
}

/// Prepend trusted Tauri bootstrap script text to the head.
pub fn append_script_to_head(document: &Document, script: &str) {
  let node = element("script");
  attach(
    &node,
    Node::new(NodeData::Text {
      contents: RefCell::new(script.into()),
    }),
    false,
  );
  attach(&head(document), node, true);
}

/// Preserve Tauri's optional isolation script injection.
#[cfg(feature = "isolation")]
pub fn inject_codegen_isolation_script(document: &Document) {
  use serialize_to_javascript::DefaultTemplate;
  let script = crate::pattern::isolation::IsolationJavascriptCodegen {}
    .render_default(&Default::default())
    .expect("render isolation script")
    .into_string();
  append_script_to_head(document, &script);
  set_attr(
    &elements(document, "script")[0],
    "nonce",
    SCRIPT_NONCE_TOKEN,
  );
}

/// Preserve the upstream isolation file inclusion behavior.
#[cfg(feature = "isolation")]
pub fn inline_isolation(document: &Document, dir: &std::path::Path) {
  for node in elements(document, "script") {
    let Some(src) = attr(&node, "src") else {
      continue;
    };
    let path = std::path::PathBuf::from(src);
    let path = if path.has_root() {
      path
        .strip_prefix("/")
        .expect("isolation paths must be relative or start with /")
    } else {
      path.as_path()
    };
    let contents = std::fs::read_to_string(dir.join(path)).expect("read isolation script");
    node.children.borrow_mut().clear();
    attach(
      &node,
      Node::new(NodeData::Text {
        contents: RefCell::new(contents.into()),
      }),
      false,
    );
    if let NodeData::Element { attrs, .. } = &node.data {
      attrs
        .borrow_mut()
        .retain(|a| !(a.name.ns == ns!() && &*a.name.local == "src"));
    }
  }
}

/// Normalize script line endings before CSP hashing.
pub fn normalize_script_for_csp(input: &[u8]) -> Vec<u8> {
  let mut output = Vec::with_capacity(input.len());

  let mut i = 0;
  while i < input.len() {
    match input[i] {
      b'\r' => {
        if i + 1 < input.len() && input[i + 1] == b'\n' {
          // CRLF → LF
          output.push(b'\n');
          i += 2;
        } else {
          // Lone CR → LF
          output.push(b'\n');
          i += 1;
        }
      }
      _ => {
        output.push(input[i]);
        i += 1;
      }
    }
  }

  output
}

#[cfg(test)]
mod tests {
  use super::*;
  use crate::{
    assets::{SCRIPT_NONCE_TOKEN, STYLE_NONCE_TOKEN},
    config,
  };

  #[test]
  fn malformed_html_csp_attribute_escaping_and_raw_scripts() {
    let doc = parse_doc("<!doctype html><title>x</title><p>unfinished<script>if (a < b && c > d) { x = '&'; }</script>".into());
    inject_csp(&doc, "default-src 'self'; report-uri /?x=\"&y=<probe>");
    let html = String::from_utf8(serialize_doc(&doc)).unwrap();
    assert!(html.contains("&quot;"));
    assert_eq!(
      attr(&elements(&parse_doc(html.clone()), "meta")[0], "content"),
      Some("default-src 'self'; report-uri /?x=\"&y=<probe>".into())
    );
    assert_eq!(
      inline_script_contents(&doc),
      vec!["if (a < b && c > d) { x = '&'; }"]
    );
    assert_eq!(
      inline_script_contents(&parse_doc(html)),
      inline_script_contents(&doc)
    );
  }

  #[test]
  fn script_order_empty_template_and_foreign_namespace() {
    let doc = parse_doc("<script></script><script>first\r\nsecond</script><template><script>inert</script></template><svg><script>foreign</script></svg><script>last</script>".into());
    assert_eq!(
      inline_script_contents(&doc),
      vec!["first\nsecond", "foreign", "last"]
    );
    inject_nonce_token(&doc, &config::DisabledCspModificationKind::Flag(false));
    assert!(
      !String::from_utf8(serialize_doc(&doc))
        .unwrap()
        .contains("foreign</script nonce")
    );
  }

  #[test]
  fn csp() {
    let htmls = vec![
      "<html><head></head></html>".to_string(),
      "<html></html>".to_string(),
    ];

    for html in htmls {
      let document = parse_doc(html);
      let csp = "csp-string";
      inject_csp(&document, csp);

      assert_eq!(
        String::from_utf8(serialize_doc(&document)).unwrap(),
        format!(
          r#"<html><head><meta http-equiv="Content-Security-Policy" content="{csp}"></head><body></body></html>"#
        )
      );
    }
  }

  #[test]
  fn normalize_script_for_csp_test() {
    let js = "// Copyright 2019-2024 Tauri Programme within The Commons Conservancy\r// SPDX-License-Identifier: Apache-2.0\n// SPDX-License-Identifier: MIT\r\n\r\nwindow.__TAURI_ISOLATION_HOOK__ = (payload, options) => {\r\n  return payload\r\n}\r\n";
    let expected = "// Copyright 2019-2024 Tauri Programme within The Commons Conservancy\n// SPDX-License-Identifier: Apache-2.0\n// SPDX-License-Identifier: MIT\n\nwindow.__TAURI_ISOLATION_HOOK__ = (payload, options) => {\n  return payload\n}\n";

    assert_eq!(normalize_script_for_csp(js.as_bytes()), expected.as_bytes())
  }

  #[test]
  fn parse_and_serialize_roundtrips() {
    let htmls = [
      "<html><head><title>Test</title></head><body><h1>Hello</h1></body></html>",
      "<!DOCTYPE html><html><head></head><body></body></html>",
    ];

    for html in htmls {
      let parsed = parse_doc(html.to_string());
      let serialized = serialize_doc(&parsed);
      let result = String::from_utf8(serialized).unwrap();

      assert_eq!(result, html);
    }
  }

  #[test]
  fn inject_nonce_to_scripts() {
    let html = r#"<html><head><script src="http://example.com/script.js"></script></head><body></body></html>"#;

    let document = parse_doc(html.to_string());
    inject_nonce_token(&document, &config::DisabledCspModificationKind::Flag(false));

    assert_eq!(
      String::from_utf8(serialize_doc(&document)).unwrap(),
      format!(
        r#"<html><head><script src="http://example.com/script.js" nonce="{SCRIPT_NONCE_TOKEN}"></script></head><body></body></html>"#
      )
    );
  }

  #[test]
  fn inject_nonce_to_styles() {
    let html = r#"<html><head><style>body { color: red; }</style></head><body></body></html>"#;

    let document = parse_doc(html.to_string());
    inject_nonce_token(&document, &config::DisabledCspModificationKind::Flag(false));

    assert_eq!(
      String::from_utf8(serialize_doc(&document)).unwrap(),
      format!(
        r#"<html><head><style nonce="{STYLE_NONCE_TOKEN}">body {{ color: red; }}</style></head><body></body></html>"#
      )
    );
  }

  #[test]
  fn append_script_to_head_test() {
    let html = r#"<html><head></head><body></body></html>"#;

    let document = parse_doc(html.to_string());
    append_script_to_head(&document, r#"console.log('Test')"#);

    assert_eq!(
      String::from_utf8(serialize_doc(&document)).unwrap(),
      "<html><head><script>console.log('Test')</script></head><body></body></html>".to_string()
    );
  }

  #[test]
  fn inject_nonce_skips_existing() {
    let html = r#"<html><head><script src="http://example.com/script.js" nonce="existing"></script></head><body></body></html>"#;

    let document = parse_doc(html.to_string());
    inject_nonce_token(&document, &config::DisabledCspModificationKind::Flag(false));

    assert_eq!(String::from_utf8(serialize_doc(&document)).unwrap(), html);
  }

  #[test]
  fn inject_nonce_respects_disabled_modification() {
    let html = r#"<html><head><script src="http://example.com/script.js"></script></head><body></body></html>"#;

    let document = parse_doc(html.to_string());
    inject_nonce_token(&document, &config::DisabledCspModificationKind::Flag(true));

    assert_eq!(
      String::from_utf8(serialize_doc(&document)).unwrap(),
      r#"<html><head><script src="http://example.com/script.js"></script></head><body></body></html>"#
    );
  }

  #[test]
  #[cfg(feature = "isolation")]
  fn inline_isolation_replaces_src_with_content() {
    use std::io::Write;

    let temp_dir = tempfile::tempdir().unwrap();
    let mut file = tempfile::NamedTempFile::with_suffix_in(".js", &temp_dir).unwrap();
    file.write_all(b"console.log('test');").unwrap();
    let file_name = file.path().file_name().unwrap().to_str().unwrap();

    let html =
      format!(r#"<html><head><script src="/{file_name}"></script></head><body></body></html>"#);
    let document = parse_doc(html);
    inline_isolation(&document, temp_dir.path());

    assert_eq!(
      String::from_utf8(serialize_doc(&document)).unwrap(),
      r#"<html><head><script>console.log('test');</script></head><body></body></html>"#
    );
  }
}
