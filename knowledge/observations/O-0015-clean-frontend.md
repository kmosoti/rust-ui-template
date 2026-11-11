---
id: O-0015
type: observation
status: ci-validation-pending
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
