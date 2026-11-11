---
id: O-0013
type: observation
status: local-tests-passed-ci-pending
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Permissive native dependency patch evidence

## Executed

- `cargo tree --manifest-path apps/native/Cargo.toml --locked --offline --target all -i cssparser@0.38.0` identified Wry's Android edge after Tauri's build edge was removed.
- Cargo generated the updated native lockfile through targeted `cargo update` invocations; no handwritten lockfile entries.
- `cargo test --manifest-path apps/native/Cargo.toml -p tauri-utils --features html-manipulation,html-manipulation-2,isolation --locked --lib html`: 11 passed. One initial new assertion overconstrained attribute serialization; corrected to verify parsed attribute equality/escaping rather than a particular encoding of angle brackets.
- `cargo test --manifest-path apps/native/Cargo.toml -p native-html-tests -p dirs-sys --locked`: 7 actual Wry-source tests and 9 directory tests passed.
- An exploratory strict Clippy run on the vendored parent packages surfaced pre-existing upstream lints (for example unwrap_or(Vec::new)); it did not pass. Application Clippy and the focused source checks remain required in CI.

## Limits

Local GTK/WebKit headers are unavailable. Linux package/runtime, Android ABI/runtime,
full production browser regression and license/advisory gates are pending. This
record does not claim final platform validation or issue completion.

## Relations and revisit

Implements [D-0010](../decisions/D-0010-permissive-rust-dependencies.md).
Update with exact reviewed source/run results; retain failed-command history.
