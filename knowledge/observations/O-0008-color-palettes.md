---
id: O-0008
type: observation
status: local-passed-ci-pending
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# O-0008: Color scheme implementation evidence

Started from clean develop d674dab. User requested six named color schemes,
with exact hex anchors for four and descriptions for the remaining two.
Read repository instructions, distinct-ui and cloud-runtime skills. No external
account or Superdesign used. Geometry/alternatives recorded before implementation.

## Observed implementation and checks

App-scoped Appearance signal and native Preferences select apply semantic CSS
overrides to every route. Reload resets Nocturne. First four anchors retained;
last two documented as chosen project shades. Existing core/IPC and owner cleanup
remain intact. No dependencies or generated lockfiles changed.

Initial computed contrast rejected Signal Blue on raised #E4E8F1 at 4.494:1;
lightened only the supporting raised surface to #E9EDF5, preserving anchors.
Host/workspace and WASM Clippy passed; cargo test workspace passed 15 unit tests
plus one doctest; Python unittest discovery passed 14 tests.

Production Tailwind and Trunk root/subpath builds passed. Initial expanded suite
passed seven palettes, 56 route/viewport axe/geometry checks, session navigation
and reload reset. Further hover/focus assertions, select remount checks and
settings captures were then added and the full suite passed again. All seven
schemes also passed settings at 320px with 200% text; returning to Preferences
retains the select value. Actual pointer hover is sent and :hover observed, but
this local browser reports `(hover: hover)` false, so Tailwind correctly keeps the
base state. Assertion now respects that capability and checks hover-token contrast
regardless. Keyboard focus outline is exercised and matched to the brand token.
Independent medium reviewer caught misleading page-only summary text; corrected
to distinguish session appearance from page-local profile state.

## Executed commands and visual inspection

- `cargo fmt --all`; `cargo test --workspace --locked --offline`: passed 15 unit
  tests and one doctest.
- `cargo clippy --workspace --all-targets --locked --offline -- -D warnings` and
  WASM client Clippy passed; Python unittest discovery ran 14 tests successfully.
- `.tools/tailwindcss -i styles/input.css -o styles/generated.css --minify`,
  `NO_COLOR=false .tools/trunk build --release --locked`, then the same build with
  `--public-url /sub/ --dist dist/sub`: passed.
- `CHROMIUM_PATH=/usr/bin/chromium cargo run -p browser-tests --locked --offline`:
  final suite passed original functional/asset tests, seven schemes with 56 new
  route/viewport axe/geometry checks, 14 contrast reports, 28 palette screenshots,
  seven enlarged-text settings checks, select keyboard/focus/remount and reload.
- Viewed Signal Blue desktop library/mobile Preferences, Desert Dusk desktop
  Preferences, and Butter/Iris desktop library. Critique and layout tradeoffs
  are recorded in the brief. Previews copied unchanged from test captures.

Final independent medium review and CI remain pending. No installer/workflow
change or new performance claim; the existing trusted cache strategy is retained.

## Limits

No local native launch without GTK/WebKit SDK. CI must verify actual installed
palette switching, assets and retained CSP/permission checks. Browser smoke and
computed contrast are scoped, not full conformance or every OS popup/disabled
state. No storage, automatic system theme, new brand assets or platform support.
CI/setup mechanisms unchanged; existing verified tools and optional trusted
caches retained, with no new performance claim.

## Relations

- **observes**: [D-0008](../decisions/D-0008-color-palettes.md)
- **continues**: [O-0007](O-0007-workspace-launcher.md)
