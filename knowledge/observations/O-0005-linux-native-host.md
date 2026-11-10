---
id: O-0005
type: observation
status: browser-passed-native-ci-pending
updated: 2026-11-10
added_by: agent
human_ratified: false
---

# O-0005: Linux host implementation and execution boundaries

Started from develop ef3188c (Node-free UI slice, PR #9). Both post-merge
browser/core runs completed successfully. User confirmed continuing to Tauri;
Superdesign is not used.

## Local commands and observed results

Environment: Debian 13 x86_64, Rust/Cargo 1.99.1, Trunk 0.21.14,
Tailwind standalone 4.3.4 and Chromium 156.0.8078.79.

- `cargo generate-lockfile` and `cargo generate-lockfile --manifest-path
  apps/native/Cargo.toml`, followed by their respective `cargo fetch --locked`:
  tool-generated root and native dependency graphs committed.
- `cargo test --workspace --locked --offline`: 15 unit tests (13 core, 2 contract)
  and 1 core doc test passed. Contract tests reject wrong versions and malformed,
  missing and unknown request fields.
- `cargo clippy --workspace --all-targets --locked --offline -- -D warnings`,
  root/native format checks, actual metadata boundary check, nine Python checker
  tests and both core mutation checks passed.
- `cargo check -p client --target wasm32-unknown-unknown --locked`: passed.
- Rebuilt the single CSS output and Trunk production assets at root and /sub/.
  `CHROMIUM_PATH=/usr/bin/chromium cargo run -p browser-tests --locked --offline`
  passed, including the explicit browser-mode unavailable status on About.
- `python3 scripts/setup_native_cli.py`: verified official Tauri CLI 2.12.4
  Linux x64 archive against committed SHA-256. `cargo-tauri tauri icon` generated
  the required PNG from the checked-in SVG; only the Linux icon is committed.
- `cargo check --manifest-path apps/native/Cargo.toml --locked` could not compile:
  pkg-config could not find glib-2.0 >= 2.70. GTK/WebKit development packages,
  Xvfb and WebKitWebDriver are missing, and sudo/package elevation is unavailable
  in this execution container. This is a local prerequisite failure, not a
  successful native check or a claim of platform support.
- Python native smoke/setup scripts passed syntax compilation. Native build,
  Debian package installation, WebKit launch, effective CSP and actual ACL
  denial remain pending the dedicated Ubuntu 24.04 CI job.

## Planned CI evidence, not yet observed

The job installs Linux prerequisites, builds the production Debian package,
installs it and launches its packaged executable via tauri-driver 2.1.0 under
Xvfb. It tests the shared styles/WASM and latest-response behavior, real typed
IPC input validation and effective inline-script CSP blocking. A separate
restricted-window package configuration tests actual app_info denial without
granting that window any permission. Screenshots are test artifacts.

## Limits and follow-up

No Windows, macOS, Android or iOS build/launch; no signing/notarization or
formal proof. Desktop and mobile support must follow actual packaged-client
results. No network service, persistence or sync was introduced. Chromium tests
do not establish WebKit behavior; CI results must be recorded distinctly.
Issue #1 remains open. No merge into main is authorized.

## Relations

- **observes**: [D-0005](../decisions/D-0005-linux-native-host.md)
- **continues**: [O-0004](O-0004-node-free-examples.md)
