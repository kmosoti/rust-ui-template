---
id: O-0005
type: observation
status: native-ci-passed
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

## CI observation: first native run

[Native run 42903521256](https://github.com/kmosoti/rust-ui-template/actions/runs/42903521256)
on source head 452db7a built the production Debian package, passed native Clippy,
installed the package, launched its packaged executable via WebKitWebDriver,
and successfully returned the expected app_info result. The next deliberate
unsupported-version call returned the correct application rejection, but the
Python helper mistook its `error` field for a WebDriver protocol failure and
stopped the test. CSP and restricted-window denial were not reached.

The helper now leaves successful HTTP/WebDriver values unchanged, including
application errors; urllib still rejects actual HTTP/WebDriver failures. Two
focused Python regression tests pass along with the nine boundary tests.
At that point the native job needed a rerun before CSP, permission denial or
a complete native smoke success could be claimed; the final successful run is
recorded below. README now rebuilds root assets before packaging,
matching CI and removing the browser subpath fixture from the embedded assets.

Browser [run 42903521168](https://github.com/kmosoti/rust-ui-template/actions/runs/42903521168)
and core [run 42903521132](https://github.com/kmosoti/rust-ui-template/actions/runs/42903521132)
passed on that same head. This does not establish the final corrected native run.

## CI observation: native runtime smoke passed

[Run 42906605542](https://github.com/kmosoti/rust-ui-template/actions/runs/42906605542)
on source 7b6dd69 passed the native build, Clippy, Debian package installation,
and all runtime smoke assertions on Ubuntu 24.04, GTK 3.24.41 and WebKitGTK /
WebKitWebDriver 2.52.6-0ubuntu0.24.04.1. The installed production package passed
shared CSS/WASM, stale-response behavior, typed IPC validation, effective CSP
blocking of an injected inline script, and host information rendered in About.
The restricted-window package passed actual app_info denial and its predictable
UI error without page errors. This is packaged-client evidence under Xvfb,
not a manual GPU/desktop accessibility audit or evidence for other platforms.

The overall job failed only its final source-drift check: cargo-tauri normalized
`tauri-build = "=2.7.4"` to the equivalent table with `features = []`. The
canonical form is now committed; the native lockfile is unchanged. A fresh
full CI run must pass the drift check before landing. Current check results
are linked from [PR #10](https://github.com/kmosoti/rust-ui-template/pull/10).
The package and screenshot were uploaded by CI; downloading artifacts into this
session returned HTTP 403 from artifact storage, so local inspection is not claimed.

## Final CI observation and develop landing

[Native run 42908982231](https://github.com/kmosoti/rust-ui-template/actions/runs/42908982231)
completed successfully on source eebd4ae907e892bff206c138b60566fb838306c2.
[Browser run 42908982340](https://github.com/kmosoti/rust-ui-template/actions/runs/42908982340)
and [core run 42908982222](https://github.com/kmosoti/rust-ui-template/actions/runs/42908982222)
also passed on that head. The independent higher-reasoning reviewer verified
source, logs and review threads and landed [PR #10](https://github.com/kmosoti/rust-ui-template/pull/10)
into develop at e8b7fa3108bfbf224407106fe76ff995c2486826. Its merged tree is
identical to the reviewed source tree; the automated review found no issues.

Executed native CI commands included:

- `../../.tools/cargo-tauri tauri build --bundles deb -- --locked` from apps/native.
- `cargo clippy --manifest-path apps/native/Cargo.toml --all-targets --locked
  --offline -- -D warnings`.
- `sudo dpkg -i apps/native/target/release/bundle/deb/*.deb` and
  `xvfb-run -a python3 scripts/native_smoke.py` for the production package.
- The same package build with `--config tauri.e2e.conf.json`, package installation,
  and `xvfb-run -a python3 scripts/native_smoke.py --denial-fixture`.
- The final tracked/untracked source-drift gate passed. Native Cargo.lock remained
  unchanged after both configuration builds. The job uploaded the unsigned
  production package and native screenshot as `linux-native-evidence`.

Local manifest-only verification additionally ran the pinned CLI with
`--runner /bin/false --no-bundle -- --locked` for both production and e2e configs.
Both intentionally stopped at the stub runner after manifest processing;
`git diff --exit-code -- apps/native/Cargo.toml apps/native/Cargo.lock` confirmed
idempotence. This is manifest processing evidence, not local native compilation.

The documented browser/native build commands require no Node installation.
Native workflow path filters skip a separate documentation-only change; every
code, asset, script, lockfile and workflow change still triggers native checks.

## Limits and follow-up

No Windows, macOS, Android or iOS build/launch; no signing/notarization or
formal proof. Desktop and mobile support must follow actual packaged-client
results. No network service, persistence or sync was introduced. Chromium tests
do not establish WebKit behavior; CI results must be recorded distinctly.
Issue #1 remains open. No merge into main is authorized.

## Relations

- **observes**: [D-0005](../decisions/D-0005-linux-native-host.md)
- **continues**: [O-0004](O-0004-node-free-examples.md)
