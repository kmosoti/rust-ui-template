---
id: O-0004
type: observation
status: local-browser-passed
updated: 2026-11-10
added_by: agent
human_ratified: false
---

# O-0004: Standalone Tailwind, Rust browser checks, and UI examples

Started from develop's landed browser slice. Rust/Cargo 1.99.1, Trunk 0.21.14,
Tailwind 4.3.4 standalone Linux x64, Chromium 156.0.8078.79 on Linux x86_64.
The executable hashes are pinned from the upstream Tailwind release metadata.
No Node/npm command is used by the new documented build or CI pipeline.

## Observed commands and results

- `python3 scripts/setup_frontend.py`: verified Tailwind SHA-256 and axe archive
  SHA-512; generated the local executable and axe assets in ignored `.tools/`.
- `cargo generate-lockfile` and `cargo fetch --locked`: generated the actual
  expanded Cargo graph and fetched pinned dependencies.
- `.tools/tailwindcss -i styles/input.css -o styles/generated.css --minify` and
  `python3 scripts/check_css.py`: passed; one output includes the shared UI.
- `env -u NO_COLOR trunk build --release --locked` and the same command with
  `--public-url /sub/ --dist dist/sub`: production WASM/CSS bundles passed.
- `CHROMIUM_PATH=/usr/bin/chromium cargo run -p browser-tests --locked --offline`:
  passed stale-result rejection, pre-fire timer cancellation, owner cleanup,
  keyboard activation, direct/subpath navigation, stylesheet and WASM loading,
  error checks, and axe smoke on the response lab, overview, and preferences.
  Captured actual production UI PNGs in ignored `artifacts/`.
- The first axe run flagged a complementary landmark nested in main; changed
  the decorative dashboard panel to a plain container and reran successfully.
- `python3 scripts/check_core_mutations.py`: both named defects rejected after
  updating its disposable checkout to include the browser-test workspace crate.
- Actual Cargo metadata boundary check and nine Python checker tests passed.

- `cargo test --workspace --locked --offline`: passed 13 core unit tests and
  one core doc test (the browser suite is separately executed by the runner).
- `cargo fmt --all -- --check`, host workspace Clippy and CSR WASM Clippy with
  `--locked --offline -- -D warnings` passed; `git diff --check` passed.
- Two separate deliberate UI variants, each successfully compiled with one
  `task.abort()` replaced by `drop(task)`, were rejected at Cancel's and unmount's
  respective pre-fire timer assertions. The source was restored, both asset
  builds regenerated, and the real Rust browser suite passed again.
- Review fixes: copied the tool crate in core mutation fixtures, made polling
  navigation-safe, exercised visible navigation and real CDP mouse clicks,
  selected musl binaries when detected, and cleared applied form state on edits.

## Limits and decisions

Overview metrics are sample content; preferences are local and reset on unmount.
Screenshots show examples, not native-platform or cross-browser support. Native
hosts, other WebViews, SSR/hydration and formal proof remain outside this slice.
Only Linux was exercised; macOS/Windows/musl executable hashes are pinned but
those environments were not tested. CI uses runner-provided Chrome, whose
revision can change; it prints the version. Browser sandboxing stays enabled by
default. Accessibility checks are smoke coverage, not a full audit.

The optional Superdesign canvas required account authorization; the three UI
examples were authored directly in Leptos and captured from the actual build.

## Relations

- **observes**: [D-0004](../decisions/D-0004-node-free-tooling.md)
- **continues**: [O-0003](O-0003-csr-browser.md)
