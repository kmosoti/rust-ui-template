// Copyright 2019-2024 Tauri Programme within The Commons Conservancy
// SPDX-License-Identifier: Apache-2.0
// SPDX-License-Identifier: MIT
//! Legacy entry names backed by the same permissive HTML5 implementation.
//! The former kuchiki NodeRef representation is intentionally not retained.
use crate::config::PatternKind;
pub use crate::html2::{
  Document as NodeRef, inject_csp, inject_nonce_token, normalize_script_for_csp,
  parse_doc as parse, serialize_doc as serialize_node,
};
#[cfg(feature = "isolation")]
pub use crate::html2::{inject_codegen_isolation_script, inline_isolation};
use serde::Serialize;
/// The shape of the JavaScript Pattern config
#[derive(Debug, Serialize)]
#[serde(rename_all = "lowercase", tag = "pattern")]
pub enum PatternObject {
  /// Brownfield pattern.
  Brownfield,
  /// Isolation pattern. Recommended for security purposes.
  Isolation {
    /// Which `IsolationSide` this `PatternObject` is getting injected into
    side: IsolationSide,
  },
}

impl From<&PatternKind> for PatternObject {
  fn from(pattern_kind: &PatternKind) -> Self {
    match pattern_kind {
      PatternKind::Brownfield => Self::Brownfield,
      PatternKind::Isolation { .. } => Self::Isolation {
        side: IsolationSide::default(),
      },
    }
  }
}

/// Where the JavaScript is injected to
#[derive(Debug, Serialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum IsolationSide {
  /// Original frame, the Brownfield application
  #[default]
  Original,
  /// Secure frame, the isolation security application
  Secure,
}
