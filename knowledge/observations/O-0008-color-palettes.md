---
id: O-0008
type: observation
status: ci-verified
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

Final independent medium review and all CI passed (below). No installer/workflow
change or new performance claim; the existing trusted cache strategy is retained.

## Final CI and independent landing

[PR #16](https://github.com/kmosoti/rust-ui-template/pull/16), source `81eba6a`,
passed final fresh independent gpt-6.1-terra review explicitly at medium effort,
all checks and an empty unresolved-thread list. The reviewer rebase-landed into
develop as `d3fcd91`; main was not merged and Issue #1 remains open.

| Job | Run | Total | Result |
| --- | --- | ---: | --- |
| Core | [42930328064](https://github.com/kmosoti/rust-ui-template/actions/runs/42930328064) | 25s | All locked Rust/Clippy/boundary/mutation/Python checks passed |
| Browser | [42930328000](https://github.com/kmosoti/rust-ui-template/actions/runs/42930328000) | 55s | Original behavior plus seven palettes, contrast, 56 route/viewport axe/geometry, focus/hover/select/remount/reset and text zoom passed |
| Linux native | [42930328046](https://github.com/kmosoti/rust-ui-template/actions/runs/42930328046) | 3m10s | Installed assets, Signal Blue light selection/navigation, typed IPC, CSP and restricted-window denial passed |

Executed jobs API reads for the native job and
`python3 scripts/ci_timings.py` on its JSON; retrieved native logs using
`gh run view 42930328046 --log`. Native steps: cache restore 23s, OS prerequisites
34s, Rust ensure 9s, frontend 4s, production build 22s, installed smoke 38s,
restricted fixture build 18s, denial smoke 32s. All drift checks passed. Existing
cache trust/invalidation and required security checks were retained; single-run
observations are not a performance guarantee.

The production native script now selects Signal Blue in Preferences, asserts
native control color-scheme light, navigates to About and verifies canvas
rgb(248,247,244), in addition to the existing real command/CSP/denial coverage.
This passed on installed WebKit; no inference from Chromium alone is used.

Minimum ratios from the final desktop computed-color reports (rounded only for
this table; test comparisons use full precision):

| Scheme | Tested text pairs (>=4.5) | Tested non-text pairs (>=3) |
| --- | ---: | ---: |
| nocturne | 6.647 | 3.513 |
| signal-blue | 4.701 | 3.774 |
| butter-iris | 5.950 | 3.670 |
| lime-graphite | 6.382 | 3.626 |
| sulu-fir | 5.719 | 3.763 |
| blooming-romance | 4.597 | 3.101 |
| desert-dusk | 5.554 | 3.800 |

JSON reports and all captures are browser CI evidence artifacts. The two committed
palette previews are unedited test captures; source layout and scope are in the
brief. Hover capability false is explicitly reported by the local JSON, and the
rendered base/hover expectation respects it; this does not claim that every OS
popup or hardware hover state was exercised. Evidence update is docs-only to
avoid rerunning native packaging for a PR whose implementation is unchanged.

## Integration-native disconnect and unchanged rerun

The subsequent develop push run
[42930850475 attempt 1](https://github.com/kmosoti/rust-ui-template/actions/runs/42930850475/attempts/1)
failed in installed-production smoke: WebDriver disconnected with
`http.client.RemoteDisconnected` at native_smoke.py line 75 while registering the
error observer, before palette assertions. The log shows connection reset by
peer. EGL/DRI3 warnings appear in both successful and failed logs, so they do not
establish the cause. PR16's native run had already passed.

Executed `gh run rerun 42930850475 --failed` without changing source, workflow,
assertions or timeouts. [Attempt 2](https://github.com/kmosoti/rust-ui-template/actions/runs/42930850475/attempts/2)
passed in 3m19s, including installed palette/navigation/CSP and restricted-window
permission checks. Retrieved explicit attempts/1/jobs and attempts/2/jobs API
responses and `gh run view 42930850475 --attempt 2 --log`; preserved the failed
attempt log before rerun. Attempt 2 production smoke was 37s, fixture build 27s,
and denial smoke 32s. Source remained develop d3fcd91 throughout.

Observed: one integration transport disconnect, followed by an unchanged pass.
Unknown: root cause and recurrence rate. This is not proof of deterministic
native stability or a repaired browser crash. No blanket retry or weakened check
was added. Investigate driver/WebKit process diagnostics if it recurs; do not
attribute it to palette contrast or the EGL warning without evidence.

## Limits

No local native launch without GTK/WebKit SDK. Actual installed palette switching, assets and retained CSP/permission checks
passed in GitHub CI; this is not a local native launch claim. Browser smoke and
computed contrast are scoped, not full conformance or every OS popup/disabled
state. No storage, automatic system theme, new brand assets or platform support.
CI/setup mechanisms unchanged; existing verified tools and optional trusted
caches retained, with no new performance claim.

## Relations

- **observes**: [D-0008](../decisions/D-0008-color-palettes.md)
- **continues**: [O-0007](O-0007-workspace-launcher.md)
