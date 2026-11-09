---
id: O-0003
type: observation
status: local-browser-passed
updated: 2026-11-09
added_by: agent
human_ratified: false
---

# O-0003: CSR browser slice evidence

## Context

Started from PR #7 head `2ed44b43cc86635e93755ed19456f47a847ec6f4`,
stacked on `feat/1-csr-core-foundation`. The independent higher-effort reviewer
found no blocking foundation findings and separately reproduced its core checks.
The PR's run [42691400778](https://github.com/kmosoti/rust-ui-template/actions/runs/42691400778)
passed on that head; its synthetic merge is not a merge to a protected branch.
Branch-protection settings could not be inspected by the reviewer's integration.

## Local results

Environment: Linux x86_64, Rust/Cargo 1.99.1, Node 24.22.1, npm 11.9.0.

- Before changes, `cargo fmt --all -- --check`, `cargo test --workspace --locked --offline`,
  `cargo clippy --workspace --all-targets --locked --offline -- -D warnings`,
  `cargo check -p app-core --target wasm32-unknown-unknown --locked --offline`,
  the metadata boundary checker, nine Python checker tests, and both mutation
  checks passed (13 Rust unit tests and one doc test).
- After adding the UI, `cargo generate-lockfile`, `cargo fetch --locked`, `npm ci`,
  `npm run css`, `node tests/check-css.cjs`, `cargo fmt --all -- --check`,
  `cargo test --workspace --locked --offline`, `cargo clippy --workspace --all-targets
  --locked --offline -- -D warnings`, and `cargo clippy -p client --target
  wasm32-unknown-unknown --locked --offline -- -D warnings` passed.
- The expanded metadata boundary check, all nine Python checker tests, both core
  mutations, and `cargo check -p app-core --target wasm32-unknown-unknown
  --locked --offline` passed.
- The first dependency resolution failed because web-sys 0.3.83 conflicted with
  Leptos's transitive wasm-streams requirement; web-sys 0.3.107 resolved and
  compiled. Trunk's locked installation reported its upstream lockfile contains
  yanked crossbeam-channel 0.5.14; it remains usable but merits a tool update.

- `cargo install trunk --version 0.21.14 --locked` completed successfully.
  For the first local build, the official Trunk 0.21.14 Linux release archive
  was downloaded from GitHub and its SHA-256 matched the upstream checksum
  (`f2b4680cd239693a646a2795e4633c625328d7b2a044fbe749fa3a2fe9e7036b`).
- `env -u NO_COLOR /tmp/trunk-release/trunk build --release --locked` and
  `env -u NO_COLOR trunk build --release --locked --public-url /sub/ --dist dist/sub`
  passed. The environment sets `NO_COLOR=1`, which Trunk 0.21.14 rejects as a
  boolean, so it was unset for these commands. The initial build also exposed
  that Trunk needs the client manifest in the HTML link; this was corrected.
- `CHROMIUM_PATH=/usr/bin/chromium npm run test:browser`: four tests passed in
  Chromium 156.0.8078.79. They exercised stale responses, observed timer clearing
  on cancel and unmount, navigation, keyboard, axe smoke, CSS and subpath assets.
- Review exposed a false positive in the first timer instrumentation: a timer can
  clear itself after firing. The revised test counts only pre-fire clears. A
  deliberately compiled variant replacing both `task.abort()` calls with
  `drop(task)` caused both cancel and unmount browser assertions to fail; the
  restored build passed all four tests again. This is targeted sensitivity
  evidence, not a general mutation-testing claim.
- `git diff --check` passed before commit. The browser workflow is new; no CI
  result for this slice is claimed until its run executes.

## Limits

No native package, desktop or mobile WebView, persistence, network transport,
SSR/hydration, or formal proof was tested. Browser checks cover only the stated
browser and cases, not universal accessibility or a platform support matrix.

## Relations

- **observes**: [D-0003](../decisions/D-0003-csr-browser-adapter.md)
- **continues**: [O-0002](O-0002-core-foundation.md)
