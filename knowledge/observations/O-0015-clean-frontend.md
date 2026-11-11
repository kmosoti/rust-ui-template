---
id: O-0015
type: observation
status: reviewed-reproducibility-passed
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Independent clean frontend build gate

## Implementation and intended evidence

The new script builds the exact HEAD in two independent clean clones with empty
Cargo target directories, fixes SOURCE_DATE_EPOCH, remaps checkout paths and
compares all production file paths/SHA-256 bytes. Source registry downloads can
be reused but compiled caches are not restored. It runs workspace tests and
root/subpath production Chromiumoxide tests in the first clone and retains
commands/logs/manifests plus browser captures. Fresh setup downloads/verifies
pinned tools through the same documented scripts, without Node/npm.

## Executed and limits

`python3 -m py_compile scripts/check_frontend_repro.py` and `git diff --check`
passed. Full clean CI is pending; no byte reproducibility or fresh-browser test
success is claimed from syntax checks. Native signing/package determinism remains
outside this gate and tracked by #24. Runtime, transfer and build costs must be
measured before changing the gate's caching/frequency.

## Revisit when

Actual clean-build reports pass/fail or the build pipeline gains generated time,
absolute paths or additional assets. See [CI contract](../../docs/ci.md).

## Initial clean CI and measured trigger refinement

Run42978968198 passed in6m10s. Inspected artifact13837315617: tested synthetic
merge b0dfac19eb6ab58bb03c08c1b97b153776724460, both manifests identical across
six production files (HTML, JS, WASM, CSS, original SVG and Rust inline snippet).
Every recorded command exited0. Production builds took86.55s/85.33s; fresh
workspace tests96.36s, subpath build1.73s, production browser run75.47s.
Both targets were initially empty; only registry source downloads were reused.

Because this deliberate cold gate costs370s, native-workspace/vendor-only changes
now join prose in its ignore list. Root crate/style/public/test/runner inputs,
manifests, setup/download scripts and the workflow still trigger it. A guard
checks actual tracked frontend inputs against both event filters. Security checks
are not narrowed. This avoids unrelated cold builds without omitting a frontend
input; future cross-workspace/vendor consumption requires revisiting the boundary.
Fresh CI on the changed workflow/integrated base remains required.

## Final integrated verification

Exact-head run42981140733 and post-merge develop run42982373211 passed. The final
PR artifact reports6 identical files and all fresh commands passed. The guarded
native-only filter is included in the reviewed source; current source/frontend
changes still exercised the full gate. [O-0017](O-0017-issue1-completion.md) records
source/artifact identities, timings and the frontend-only reproducibility limit.
