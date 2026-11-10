---
id: O-0007
type: observation
status: ci-verified
updated: 2026-11-10
added_by: agent
human_ratified: false
---

# O-0007: Workspace launcher and CI contributor instructions

Started from develop 5b29101, with no open PRs and a clean tree. User requested
CI efficiency/idempotency as ongoing contributor instructions and a default
merging Obsidian workspace organization with game launcher hierarchy.
The local distinct-ui and cloud-runtime skills were read; no Superdesign used.

## Changes and choices

Recorded three structural alternatives and concrete desktop/mobile geometry
before component work in the linked brief. Implemented the chosen Nocturne
workspace/library composition and migrated every shared route to semantic dark
tokens. Original SVG artwork is local, bundled and covered at root/subpath.
Default landing is library; explicit #/ retains the functional response lab.
No new dependencies were introduced; existing generated lockfiles remain intact.

Contributor rules now require relevant CI efficiency review, safe repeated setup,
measured cold/warm tradeoffs, optional compatible trusted caches and retained
functional/security coverage. No new workflow mechanism was needed for this
instructional change; existing verified binaries/cache reuse remain in use.

## Executed local verification

- `cargo fmt --all`, host/workspace Clippy with locked offline dependencies:
  passed after initial component implementation.
- Official standalone Tailwind compiled the semantic namespace/reset and shared
  recipes; `python3 scripts/check_css.py` passed.
- Trunk production root and /sub builds passed, copying original SVG artwork.
- First browser run proved default library, real artwork loading, current nav,
  keyboard skip/launch, stale result rejection and cancellation, then stopped:
  old click helper compared raw text including the new aria-hidden navigation
  glyph. Added accessible navigation labels and compare labels in the helper.
  This test adjustment retains actual CDP clicks and button-label assertions.
- A later browser run reached geometry audits and rejected the intentionally
  hidden skip link. Added one scoped reasoned overflow exception plus an explicit
  focused-width/position assertion before real keyboard activation; confirmed
  focus goes to main and the fragment route does not change.
- `cargo test --workspace --locked --offline`: 15 unit tests and one doctest passed.
  Host/workspace and WASM client Clippy (`--locked --offline -- -D warnings`) passed.
  `python3 -m unittest discover -s scripts -p 'test_*.py' -v`: 14 tests passed,
  including existing corrupt-cache and re-extraction installer tests.
- Final production builds: `.tools/tailwindcss -i styles/input.css -o
  styles/generated.css --minify`, `python3 scripts/check_css.py`, and
  `NO_COLOR=false .tools/trunk build --release --locked` passed. Repeated with
  `--public-url /sub/ --dist dist/sub` for subpath assets.
- `CHROMIUM_PATH=/usr/bin/chromium cargo run -p browser-tests --locked --offline`
  passed all original stale/cancel/unmount/navigation/keyboard/asset behavior.
  New landing, actual SVG, current-nav and focused skip-link checks passed.
  All four routes passed geometry/axe at 1440/390/320; all four passed geometry
  at 320 with 200% text. `python3 scripts/check_design_profile.py` and
  `git diff --check` passed.
- Inspected production library 1440/320 and response390 images. Diagonal arrow
  glyphs rendered as missing-font boxes despite geometry/axe passing; replaced
  with supported horizontal arrows. Enlarged text then exposed a 32px glyph in
  the fixed 24px library-row arrow column; changed columns to rem units.
  Added a heading/render wait to the zoom loop after observing navigation could
  still be settling, then rebuilt and passed the full suite. Final desktop and
  320px library images were viewed again; arrows render correctly.
- Spatial/optical critique and the mobile image-first/scroll tradeoff are in the
  design brief. No new CI/install logic changed, so no new cache-speedup claim is
  made; O-0006 retains existing cold/warm evidence. Independent medium reviewer
  reported no initial source blocker; final source review and all CI subsequently passed (below).

## CI, review and landing

[PR #14](https://github.com/kmosoti/rust-ui-template/pull/14), source `d5a6bda`,
passed all checks and fresh independent gpt-6.1-terra review explicitly at medium
effort. Automated code review reported no issues and no review threads remained.
The independent reviewer rebase-merged into develop as
`fb82b91233173cfed41c91327a7f5ffc57c3c952`. Main was unchanged and Issue #1 open.

| Job | Executed run | Total | Result |
| --- | --- | ---: | --- |
| Core | [42923175434](https://github.com/kmosoti/rust-ui-template/actions/runs/42923175434) | 23s | Passed all Rust, lint, boundary, mutation and Python checks |
| Browser | [42923175766](https://github.com/kmosoti/rust-ui-template/actions/runs/42923175766) | 40s | Passed production assets, original interactions, 12 route/viewport audits, 200% text, axe/keyboard and artwork loading |
| Linux native | [42923175517](https://github.com/kmosoti/rust-ui-template/actions/runs/42923175517) | 3m17s | Passed actual installed package/artwork, typed IPC, CSP and restricted-window denial |

Executed `gh api repos/kmosoti/rust-ui-template/actions/runs/RUN/jobs` for all three
runs and `python3 scripts/ci_timings.py` on native output. Retrieved native log
with `gh run view 42923175517 --log`. It confirms exact cache restore, already
installed tauri-driver, production smoke and real app_info permission denial.
Native steps: restore 13s, OS dependencies 37s, Rust ensure 14s, frontend 4s,
production package 29s, installed smoke 35s, fixture 27s and denial smoke 31s.
Cache keys/trust/verification logic were unchanged; these are observations rather
than a new performance guarantee. Native checks here executed in CI, not locally.

Copied the final actual production captures from artifacts/layout-overview-1440.png
and artifacts/layout-overview-320.png into docs/images/nocturne-desktop.png and
nocturne-mobile.png without editing. They are Chromiumoxide-generated screenshots
of the implemented UI, not design mockups. Both were visually inspected after
arrow corrections. Local capture environment: Chromium 156.0.8078.79, Tailwind
4.3.4, Trunk 0.21.14 and Rust 1.99.1. The brief records composition and tradeoffs.
Preview/evidence-only follow-up is separate so updating this record does not
rerun native packaging for an otherwise unchanged PR implementation diff.

## Limits

Browser geometry/axe smoke complements visual and keyboard review; it is not a
complete WCAG or optical-quality proof. Sample library content is not persistence,
installation, account connectivity or game execution. Native GTK/WebKit SDK is
unavailable locally; the installed-package/security regression runs in CI.
Other platform builds remain outside the established evidence matrix.

## Relations

- **observes**: [D-0007](../decisions/D-0007-default-workspace-design.md)
- **continues**: [O-0006](O-0006-design-ci.md)
- **specification**: [design brief](../../design/workspace-launcher-brief.md)
