---
id: O-0020
type: observation
status: measured-retained-with-transfer-followup
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
  overlaps them. Dependency/target fallback retains the same compatibility
  tuple; only lock/verification identities vary after its prefix. SDK key excludes Rust/
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


## Compatible restore and synthetic probe

Author review identified that exact-only target keys would throw away useful
compilation after lock-only updates. Dependency/target prefixes now fix the
runner/image, Rust/JDK, relevant SDK/tool/setup/build/vendor identities and vary
only lock/verification identity. SDK remains exact. Independent medium review
approved these boundaries; Cargo locked/strict Gradle/SDK-byte checks and own
native-package clean remain unconditional.

The optional PR-only `ci-cache-stale` label appends a synthetic primary-key
suffix for dependency/target groups, leaving compatibility prefixes and SDK key
unchanged. The cold label takes precedence. Profiles retain synthetic-probe
status plus actual matched/primary keys and exact-hit. This deliberately tests
backend fallback, not a real changed dependency graph. Neither benchmark label
can change develop keys or grant PR cache writes. Hosted cold/exact/stale probe
results must be recorded; prefix-invariance local checks supplement them.


Local compatibility property checks against the actual workflow hashFiles path
selections passed: lock/verification-only fixture changes preserve dependency/
target prefixes and SDK identity while changing primary identities; SDK/setup,
vendor, manifest and workflow build-input changes invalidate the relevant
prefixes. These fixtures do not edit generated repository locks and do not claim
to implement GitHub's full expression engine. The reusable regression will ship
with the final evidence PR used for the hosted synthetic fallback probe.


## Provisional landing and cold observations

Independent medium review owned PR35's provisional rebase merge into develop
`a88b6c66a2fc9f9d72f6f165601af30814cd9508` after all six final-head checks passed.
This authorizes trusted seeding, not performance adoption or #31 closure.

- Early all-miss Android43061948302:742s, source d1395070d6836520c7b0068ea13100ec4e5d5b10,
  artifact13873939388. SDK setup135s, ABI build282s, emulator155s.
- Final exact-head PR35 Android43068162561:564s, source86ba0fe27247692d6712ba9fe7d9cc282b031163,
  artifact13876764253. Three restore lookups1/1/0s, SDK115s, ABI213s,
  emulator110s. Every cache component had an empty hit/matched key and populated
  primary; both profile phases were error-free, observer0.0004/1.398s.
- Both images ubuntu24/20261101.360.1. These cold results vary substantially and
  do not establish a speedup: compiler/emulator/network time varies too. Preserve
  source IDs and compare repeated warm jobs, not a favorable single cold sample.
- Trusted develop seed is run43069846343. No candidate cache was saved by a PR.
  Three warm exact hits and a synthetic fallback probe remain pending.
- After inheriting the final transport fix,42 local Python tests pass, including
  five stdlib compatibility properties against actual workflow key patterns.
  Fixture locks are temporary synthetic data, not edits to generated repo locks.

Runtime investigation required actual package evidence before this landing:
[O-0019](O-0019-linux-wayland-accessibility.md) retains failed runs, the negative
proxy experiment, actual restricted RPM checks and the HTTP-client decision.

Comparison control: evaluated both Android workflows with local YAML inspection;
all21 non-profiler shell commands and the build environment match between
baseline3160e4a and developa88b6c6. `git diff --exit-code` also found no changes
in Cargo locks/manifests, Rust pin, crates, native Rust/capabilities/Android source,
Android/tool asset pins, Android/frontend/native setup Python, emulator/device
scripts, styles, Trunk configuration and index input. Cache/profiler changes and
separate Linux harness work account for the source-ID differences; a faster
single cold result is not evidence of reduced build/test coverage.


## Trusted seed

Develop run43069846343/attempt1 passed742s on sourcea88b6c6 and image
ubuntu24/20261101.360.1; artifact13876849920 has error-free all-miss profiles.
All three save steps succeeded and the cache API confirms their exact keys under
refs/heads/develop, not a PR ref:

| Component | Cache ID | Compressed bytes | Save step |
| --- | --- | ---: | ---: |
| SDK |10369184852 |3267755610 |43s |
| Dependencies/tools/Gradle |10369204165 |683180406 |17s |
| Compiled targets |10369212413 |543907393 |8s |
| Total | |4494843409 |68s |

The measured archive sum is9.57% below the existing4,970,485,718-byte v1 archive,
but **freshness is a confound**: the warm v1 archive retains old unused state.
Both the actual v1 forced-cold and v2 seed produce the same apparent bucket sizes
(SDK8309.4MiB, Gradle924.2MiB, native target1492.4MiB), while the old warm v1 cache
contains Gradle1409.4MiB and native target2336.3MiB. Do not attribute the full
byte reduction to partitioning or claim a controlled compression improvement.
SDK archive identity is independently stable across lock-only fixture/probe
identities; avoiding future duplicate SDK saves is a separate structural benefit,
not a measured quota/eviction improvement.

Seed SDK setup91s, ABI274s, emulator150s. Warm1 has been requested with
`gh run rerun 43069846343`; no failed assertion is being retried. Preserve the
seed profile before rerunning because Actions artifact retention/attempt behavior
can remove earlier downloads. Adoption still awaits three successful exact-hit
warm runs and the actual read-only synthetic fallback probe.


## Old-runner warm observations and canceled sample

Same sourcea88b6c6 and image20261101.360.1:

| Attempt | Outcome | Job | Restores SDK/deps/targets | ABI | Emulator step |
| --- | --- | ---: | --- | ---: | ---: |
|2 |passed |347s |67/15/14s |62s |127s |
|3 |passed |311s |60/15/13s |50s |113s |
|4 |canceled after stall |1476s |79/13/10s |82s |1220s |

The first two successful attempts have error-free all-exact-hit profiles
(artifacts13877614409,13881780197). Attempt4 restored all three exact entries,
passed both actual instrumentation cases and captured complete evidence, then
stalled after its last application output. It is NOT a successful warm sample.
The independent reviewer recommended canceling only that run at20min emulator
step time; cancellation requested18:28:33, step ended18:28:47. Preserve device
artifact13882119469 and restored profile13881443488. No post-validation profile
or source-drift result exists, so do not impute a successful total or speedup.

The actual synthetic fallback probe43072463454 passed320s, with SDK exact match
and dependency/target primary equal to matched+'-probe'; both phases error-free,
no PR cache saves. Source d2df099cb93bc1b066f8c169ae188c2f451fba25, same image,
artifact13879665097. This tests backend fallback, not a real dependency upgrade.

[O-0021](O-0021-android-lifecycle-stall.md) records the targeted lifecycle correction.
Corrected-runner measurements must be labeled separately; old canceled data
cannot be discarded or combined as a successful third observation. No adoption
or #31 closure is established from only the two successes. Transfer itself was
not faster in these samples, regardless of shorter successful job totals.


## Corrected-runner results and bounded retention decision

Run43080751204/attempts1–3 used PR36 headda033df, actual tested synthetic
sourceabfd780204a777923d2f9c41de508f22c3111ade and ubuntu24 image20261101.360.1.
These are a separate corrected-harness series, not a replacement for the canceled
old-runner sample. `gh run rerun 43080751204` requested repeated measurements
of successful validation; no failed application assertion was replayed.

| Attempt | Job | Restores SDK/deps/targets | SDK verify | ABI | Emulator | Profile artifact | Device artifact |
| --- | ---: | --- | ---: | ---: | ---: | --- | --- |
|1 |355s |65/15/13s |9s |64s |137s |13883982991 |13885206265 |
|2 |391s |60/12/10s |14s |80s |147s |13885396302 |13884909341 |
|3 |393s |45/11/9s |11s |82s |161s |13884938306 |13885572319 |

Downloaded each profile/device ZIP before the next rerun using the GitHub
artifact connector. `gh api .../attempts/N/jobs` plus `ci_timings.py` supplied
job/step durations. A Python inspection of both profile phases for all three
attempts asserted the same source/image, all three exact primary/matched keys,
normal probe/cold flags and no recursive measurement errors. Each lifecycle
journal ends cleanup-complete with no original/cleanup error; emulator return
codes were -9/0/0. All original validation and source-drift checks passed; PR
save steps were skipped. [O-0021](O-0021-android-lifecycle-stall.md) interprets
actual termination evidence and its limits.

**Decision:** retain the disjoint v2 layout for independently reusable SDK state
and compatible dependency/target fallback. The actual trusted seed stores one
3,267,755,610-byte SDK entry; the hosted synthetic lock-identity probe reused
that same exact SDK while restoring compatible dependencies/targets. Local
lock-only key properties agree. This establishes independent reuse, not a
measured future quota/eviction saving or a real dependency-upgrade result.

The corrected series median whole job391s versus v1's384s is **1.82% slower**,
below the preregistered10% regression boundary (422.4s). Summed restore times
93/82/65s have median82s versus72s: **13.89% slower**, so this is explicitly not
a cache-transfer speed improvement. Harness/source differences, three samples,
runner variance and archive freshness limit causal comparison. No statistical
significance, universal speedup or partition-only compression benefit is claimed.
The previous two successes and canceled1476s stall remain visible above.

#31 stays open for transfer latency and longer-term cache reuse/storage evidence.
Revisit on SDK/tool/image changes, real lock upgrades, quota/eviction pressure,
or sustained runtime regression. Keep full verification on every cache state;
reconsider the simpler layout if independent reuse no longer justifies it.
