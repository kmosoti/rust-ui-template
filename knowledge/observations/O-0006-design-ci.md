---
id: O-0006
type: observation
status: cold-and-warm-ci-passed
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
  no blocking source findings. All final PR CI passed (see below).

## Limits

Geometry checks cover visible leaf text, immediate horizontal control containment
and explicitly annotated sibling regions. DOM depth/nested borders are advisory;
they are not a universal collision, occlusion, optical-weight or aesthetic checker.
Axe smoke is not full accessibility conformance. Optional profile colors require
rendered contrast checks when adopted. Existing sample layouts are not globally
restyled; the skill guides subsequent task-specific design.

Native build/launch cannot run locally due to missing GTK/WebKit development
packages; actual GitHub native CI passed. All three profiles passed exact-hit warm reruns, including native production
and restricted-window checks (measurements below). OS libraries still install on fresh runners. No native/mobile support
matrix expansion, persistence, signing or formal proof is implied.

## Cold CI and independent landing

PR [#12](https://github.com/kmosoti/rust-ui-template/pull/12), source
`fd7590f0bf4787395721e12c2e025fdf000071bc`, passed all three jobs. Each restored
no build cache and skipped trusted cache save, as intended for pull requests.
The fresh medium-effort reviewer independently checked the PR, CI and empty
review-thread list, then rebase-merged into develop as
`96b2baad832d3eb9de3eb0cd7bc0cb0ad959c4ba`. Main was not merged and Issue #1
remained open.

| Profile | Baseline run / total | Cold PR run / total | Selected cold steps |
| --- | --- | --- | --- |
| Browser | [42913938158](https://github.com/kmosoti/rust-ui-template/actions/runs/42913938158), 8m51s | [42918057649](https://github.com/kmosoti/rust-ui-template/actions/runs/42918057649), 2m15s | Trunk setup 1s; production frontend 56s; browser runner compile/test 58s; cache restore 1s |
| Core | Not compared | [42918057543](https://github.com/kmosoti/rust-ui-template/actions/runs/42918057543), 3m28s | Full Rust/Python/boundary/mutation checks passed |
| Native | [42908982231](https://github.com/kmosoti/rust-ui-template/actions/runs/42908982231), 14m20s | [42918057774](https://github.com/kmosoti/rust-ui-template/actions/runs/42918057774), 9m06s | Trunk setup <1s; frontend 89s; production build 196s; Clippy 86s; production smoke 35s; fixture build 27s; denial smoke 31s |

The latest pre-change develop browser run (8m51s) is a better baseline than the
older 9m11s PR example mentioned during progress reporting. Browser Trunk source
installation was 349s in that latest baseline. These are single observed runs,
not repeated-trial causal estimates or performance guarantees. The changes also
alter CI debuginfo/incremental settings, and hosted-runner variability matters.

Environment: Ubuntu 24.04 image `20261101.360.1`, Linux X64; Rust 1.99.1.
Native SDK key is GTK `3.24.41` / WebKit `2.52.6`. Lock/tool digest:
`259ea3c5188f4affd9278a5730a0e3eb6a22f3ef8acf32d0beee2b8bfca4f8b1`.
Cache primary-key prefix is `build-v1-Linux-X64-ubuntu24-20261101.360.1-`, followed
by `browser-portable`, `core-portable` or `native-3.24.41-2.52.6-`, Rust and digest.
For avoidance of ambiguity, the exact native key (including the double hyphen) is:
`build-v1-Linux-X64-ubuntu24-20261101.360.1-native-3.24.41-2.52.6--rust1.99.1-259ea3c5188f4affd9278a5730a0e3eb6a22f3ef8acf32d0beee2b8bfca4f8b1`.

Executed `gh api repos/kmosoti/rust-ui-template/actions/runs/RUN/jobs` for every
listed run and piped responses to `python3 scripts/ci_timings.py`. Retrieved PR
browser/native logs with `gh run view RUN --log` to confirm misses and tool
verification; all PR saves were skipped. Browser evidence artifact contains
12 screenshots/JSON metrics with axe scans and prior functional checks. Native
installed production UI, real command, CSP rejection and unauthorized-window
error paths passed; source/lockfile drift checks also passed.

## Trusted seed and warm measurements

Executed `gh run rerun RUN` after each successful develop push saved its cache.
Collected explicit attempt-one/two jobs endpoints
`gh api repos/kmosoti/rust-ui-template/actions/runs/RUN/attempts/ATTEMPT/jobs`
and `gh run view RUN --attempt ATTEMPT --log`. All reruns use exact develop source
`96b2baad832d3eb9de3eb0cd7bc0cb0ad959c4ba`, not a different optimization commit.

| Profile / run | Seed attempt 1 | Warm attempt 2 | Warm cache restore | Cache archive | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| [Core 42919435911](https://github.com/kmosoti/rust-ui-template/actions/runs/42919435911/attempts/2) | 2m25s | 26s | 6s | ~348 MiB | All checks passed; exact hit; no cache overwrite |
| [Browser 42919436010](https://github.com/kmosoti/rust-ui-template/actions/runs/42919436010/attempts/2) | 3m13s | 44s | 8s | ~391 MiB | All checks passed; exact hit; no cache overwrite |
| [Native 42919436364](https://github.com/kmosoti/rust-ui-template/actions/runs/42919436364/attempts/2) | 8m08s | 3m00s | 20s | ~880 MiB | Production/CSP/denial and all checks passed; exact hit; no cache overwrite |

Seed cache saves took 4s/core and 6s/browser. Warm browser rebuilt production CSS
and root/subpath assets (4s/2s Trunk), ran the browser interactions/audits (11s),
and passed source/lock drift. Warm core tests, host Clippy and WASM Clippy each
took 1s; pure-core boundary and mutation checks still executed. These numbers
include restore costs; the pinned Rust ensure step still took 12s in both jobs.
Native seed cache save took 10s. Warm tauri-driver installation was correctly
skipped as already installed (0s); frontend build was 4s, production native build
21s, Clippy 1s, installed production smoke 39s, restricted fixture build 21s and
denial smoke 31s. The package-owned clean explicitly removed 31 files/57.2 MiB
before building production from a cache left after the restricted fixture.
Both real production `app_info`/CSP tests and the restricted-window denial passed.
The native SDK/image/key were unchanged between seed and rerun. OS prerequisites
still took 25s and pinned Rust setup 10s; these costs are not claimed eliminated.

Local raw API/log captures were kept in `/tmp/design-ci-evidence` during this
session; durable run/attempt links and commands above are the reproducible source.
No secret material or full runner logs are committed. A failed exploratory
`gh run view --json attempt` query revealed that field is unsupported by this gh
version; explicit attempts API endpoints and `--attempt` logs were used instead.
The reviewed cold and warm comparison does not replace repeated-trial benchmarking
and says nothing about the unmeasured originality of future generated UIs.

## Relations

- **observes**: [D-0006](../decisions/D-0006-design-workflow-and-ci.md)
- **uses**: [R-0002](../research/R-0002-ui-diversity-and-verification.md)
- **continues**: [O-0005](O-0005-linux-native-host.md)
