---
id: O-0006
type: observation
status: local-checked-ci-pending
updated: 2026-11-10
added_by: agent
human_ratified: false
---

# O-0006: Design workflow and CI acceleration evidence

Started from develop 8f2c2f8. User requested extensive critical research of the
provided AI UI sameness explanation, a reusable design skill, reduced repeated
CI setup, no max/ultra review, and architecture diagrams for human review.
No Superdesign is used. A fresh independent reviewer was explicitly spawned at
medium reasoning; the previous max-effort reviewer was not reused for this work.

## Research boundary

[R-0002](../research/R-0002-ui-diversity-and-verification.md) distinguishes primary
research, plausible mechanisms and unsupported claims. The connected research
service required authentication and was not connected; public primary sources
were inspected instead. No controlled study of this project's design diversity
was run. No numerical anti-sameness improvement is claimed.

## Measured baseline

GitHub jobs API timings for native run 42908982231, job 130154305222:
14m20s total; Trunk source install 342s, production native build 191s, frontend
build 85s, native Clippy 81s, OS prerequisites 27s, tauri-driver 22s, Rust 11s.
These are observed prior-CI timings, not predictions for the new workflow.

## Local commands and results

Environment: Linux x86_64, Rust/Cargo 1.99.1, Chromium 156.0.8078.79, official
standalone Tailwind 4.3.4 and pinned official Trunk 0.21.14 binary.

- `python3 scripts/setup_ci_tools.py` verified the official archive's SHA-256
  (`f2b4680cd239693a646a2795e4633c625328d7b2a044fbe749fa3a2fe9e7036b`)
  and extracted Trunk; `.tools/trunk --version` reported 0.21.14.
- `python3 -m unittest discover -s scripts -p 'test_*.py' -v`: 14 tests passed,
  including verified archive reuse, cached binary replacement, corrupt archive
  recovery and refusal to install a bad download.
- `python3 scripts/check_design_profile.py`: the pinned Tailwind CLI emitted
  semantic utilities and omitted stock palette/large-radius utilities after the
  namespace reset. This is CSS generation evidence, not visual quality or
  accessibility evidence for the unused optional profile.
- Rebuilt production CSS and root/subpath Trunk bundles with locked dependencies.
  `CHROMIUM_PATH=/usr/bin/chromium cargo run -p browser-tests --locked --offline`
  passed original interactions/cancellation/navigation/axe coverage and added
  desktop/390px/320px metrics, captures and axe checks. All four routes (response, overview, preferences, About) passed at 1440,
  390 and 320 CSS px: 12 screenshots and 12 JSON reports. Subsequent CI
  observations are recorded below when executed.
- Deliberate DOM fixture checks detect page overflow, clipped text and annotated
  sibling-region overlap. A separate control-protrusion fixture has no page
  overflow but is rejected by the parent-containment check.
- Initial metrics falsely treated visible glyph overhang (44px scroll height in
  a 40px h1 line box) as clipping; corrected vertical clipping detection to
  require a clipping/scrolling overflow style. A screenshot then exposed the
  number input protruding from its form at 320px despite fitting the viewport;
  added containment checks and `max-w-full`, then reran successfully.
- Manual image inspection included the 320px overview and response page. The
  former is still a card-based demo, not a claimed originality success. Final spot inspection also covered corrected response at 320px, overview at
  1440px and preferences at 390px. The input now fits its form. The overview
  still uses equal metric cards and a competing dark promotional panel; these
  remain candid baseline critique, not evidence of a new distinctive design.
- actionlint 1.7.12, downloaded from its official release and checksum-verified,
  passes all workflows. It exposed a pre-existing untrusted head_ref interpolation
  in the main human-gate log; values now pass via environment variables. The
  manual environment gate and no-agent-main-merge rule are unchanged.

- `cargo test --workspace --locked --offline`: 15 unit tests and one doctest
  passed. Host/workspace and WASM client Clippy with `-D warnings` passed.
- `cargo metadata --format-version 1 --locked --offline` followed by
  `python3 scripts/check_core_boundary.py /tmp/design-ci-metadata.json`: pure
  dependency-free core graph passed. `python3 scripts/check_core_mutations.py`
  rejected both seeded defects. `cargo check -p app-core --target
  wasm32-unknown-unknown --locked --offline`, `git diff --check`, and actionlint
  passed.
- Fresh independent `gpt-6.1-terra` reviewer, explicitly medium effort, reported
  no blocking source findings. Final browser/native CI is still required.

## Limits

Geometry checks cover visible leaf text, immediate horizontal control containment
and explicitly annotated sibling regions. DOM depth/nested borders are advisory;
they are not a universal collision, occlusion, optical-weight or aesthetic checker.
Axe smoke is not full accessibility conformance. Optional profile colors require
rendered contrast checks when adopted. Existing sample layouts are not globally
restyled; the skill guides subsequent task-specific design.

Native build/launch cannot run locally due to missing GTK/WebKit development
packages; CI must verify native behavior under caching/profile changes. Cold
pipeline improvement and warm cache reuse remain unmeasured until those runs
execute. OS libraries still install on fresh runners. No native/mobile support
matrix expansion, persistence, signing or formal proof is implied.

## Relations

- **observes**: [D-0006](../decisions/D-0006-design-workflow-and-ci.md)
- **uses**: [R-0002](../research/R-0002-ui-diversity-and-verification.md)
- **continues**: [O-0005](O-0005-linux-native-host.md)
