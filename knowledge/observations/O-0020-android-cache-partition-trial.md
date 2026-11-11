---
id: O-0020
type: observation
status: candidate-awaiting-hosted-measurements
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Android cache partition trial

Informed by [O-0018](O-0018-android-cache-observation.md) and #31. Measure before
adopting; a split archive is not inherently a faster archive.

## Executed v1 observations

PR32 head3160e4a, actual tested synthetic mergef07d7506a1c60a246993e7cfbb0f2a15f57b673f,
Ubuntu24 image20261101.360.1. Applied then removed the `ci-cache-cold` label
without source changes; downloaded and inspected every profile artifact using
the GitHub artifact connector (gh downloads returned403). Obtained jobs JSON via
`gh api .../actions/runs/RUN[/attempts/N]/jobs` and fed it to
`python3 scripts/ci_timings.py` on stdin. Its CLI has no --help mode.

| Observation | Run / attempt | Whole job | Restore | SDK verify/setup | ABI build | Emulator |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| warm1 |43052897725/1 |402s |72s |12s |86s |165s |
| forced cold |43054680023/1 |711s |skipped |113s |278s |159s |
| warm2 |43056742413/1 |379s |95s |9s |69s |151s |
| warm3 |43056742413/2 |384s |65s |11s |82s |158s |

All passed the unchanged full Android validation. All three warm samples are complete: median job384s, restore72s. Profiles
had no errors; observer elapsed2.425/2.355s on warm1 and2.206/1.991s on warm2.
Cold restored measurement had no existing cache; post-validation took2.096s.
SDK raw apparent8,713,047,443bytes; its system image is4,585,407,573bytes,
NDK2,494,931,177bytes. These are filesystem totals, not transfer sizes.
Current v1 compressed archive4,970,485,718bytes. Cache API also shows an older
v1 archive4,749,872,833bytes:9,720,358,551bytes across the two keys. This does
not establish the repository quota, actual eviction or each compressed bucket's
contribution. Warm runtime variance includes build/emulator costs, not just I/O.

## Candidate and adoption gate

- Disjoint SDK / sources-tools-Gradle / compiled-target partitions. No v1 restore
  overlaps them and no partial compatibility fallback. SDK key excludes Rust/
  Gradle locks, retaining image/asset/setup identity. Dependency key includes
  actual locks, pinned tools and Gradle configuration/verification metadata.
  Targets include Rust/JDK/NDK, locks, manifests, setup/tool fingerprints, vendor
  source and workflow flags. Independent review caught the need to fingerprint
  external NDK/linker setup as well as its asset manifest; corrected. Hashing the
  complete workflow conservatively invalidates targets on instrumentation edits.
- Every component remains optional and fully verified on restore. The cold label
  skips every restore. PRs cannot save; only successful develop pushes seed
  missing exact keys after all original validation/source-drift checks pass.
  No AVD, signing material or system-directory cache is introduced.
- `python3 -m unittest discover -s scripts -p 'test_*.py'`:29 passed locally;
  `git diff --check` passed. YAML parse also passed. No candidate hosted result is claimed yet.
- Collect a candidate cold/miss run, trusted seed and three warm observations.
  Compare median whole-job and summed restore/transfer sizes against the v1
  three-warm baseline. Record source/image differences. A practical benefit must
  be observed in transfer/runtime or immutable SDK reuse/storage, with no more
  than10% median whole-job regression; otherwise restore the simpler v1 layout.
  This threshold is an experiment decision, not a statistical significance claim.
  Retain all unsuccessful experiment evidence and the observer on rollback.

No speedup, cache quota increase or eviction reduction is established yet. #31
remains open until the candidate is measured and retained/rejected explicitly.
Revisit after trusted seed and three complete warm validations.
