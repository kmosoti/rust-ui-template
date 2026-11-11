---
id: O-0018
type: observation
status: measurement-in-progress
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Android cache decomposition before optimization

## Observed baseline

Read AGENTS/CONTRIBUTING, O-0017 and issues #23/#24/#28/#31. Latest source f7a49bd
has green applicable develop checks; Issue #1 remains complete. The cache API
reports nine active entries totalling14,295,156,427 bytes; the latest Android entry
alone is4,970,485,718 compressed bytes. These API values do not establish a quota
or an eviction cause. Prior source323167e3 Android work measured61s restore and
445s whole job; these are observations, not a promised optimization target.

## Measurement implementation

The profiler records non-overlapping SDK, Cargo sources/git, Trunk/tool archives,
Gradle cache/wrapper and root/native compiled-target buckets, with immediate child
breakdowns. It reads metadata, not contents; avoids symlink traversal and counts
hardlinked file data once per bucket. Apparent and allocated sizes distinguish
sparse VM images. Parent totals must not be added to their child breakdowns.
Source/image/key/hit/phase and measurement overhead are retained as JSON.

A PR-only `ci-cache-cold` label skips restores without changing application source
or privileged permissions. Relevant label changes can rerun Android; unrelated
labels do not run its job. Cold PR jobs never save trusted caches. Normal develop
pushes still restore/save the original layout only after successful validation.
This first slice changes neither cache layout nor functional assertions.

## Executed and limits

`python3 -m unittest discover -s scripts -p 'test_*.py' -v`:28 passed, including
sparse-file size and hardlink/symlink measurement regressions. `git diff --check`
passed. CI decomposition, forced-cold and repeated warm results are pending.
Local filesystem sizes are not substituted for hosted-runner cache measurements.

## Revisit and relations

Implements the observation stage of #31, informed by [O-0017](O-0017-issue1-completion.md).
Keep or reject later cache candidates using total runtime, transfer and storage
measurements while preserving every applicable verification/trust boundary.

## Independent review corrections

An unrelated label's skipped job could still cancel active validation through the
workflow concurrency group. Unrelated label events now use a separate group;
only the deliberate cold control shares the validation group. Review also caught
a root symlink followed by the child-breakdown code; a no-follow bucket helper and
root-symlink regression now cover that path. Child breakdowns are informational,
not additive: cross-child hardlinks can appear in more than one child while the
parent counts file data once. All29 Python tests pass after these corrections.


Independent automated review identified an evidence gap: v1 reported primary key
and exact-hit only, so compatible fallback could look like a cold miss. Both
profile phases now retain cache-matched-key too; a saved-profile regression
distinguishes an old compatible key from the requested primary. No cache path,
key or save policy changed.


PR32 Linux run43060770879 attempts1/2 reproducibly fetched signed noble indices,
then reported normal packages missing before any test. PR35's identical Linux
setup progressed successfully. No application assertion ran in either failure;
only one manual setup rerun was attempted. The cause is unknown. To investigate
and improve setup convergence, log whitelisted apt state/list/architecture,
index filenames/sizes and critical package policy, compare default/fresh policy,
and make install recompute metadata from signed lists instead of generated
binary package caches. This is an unconfirmed cache-state hypothesis until
new diagnostics provide evidence; retain signatures, timeouts and every check.


Further diagnostics on43061916965 disproved the generated-binary-cache theory:
full main/universe signed lists were present, architecture amd64, and both default
and cache-disabled policies had no package candidates. Do not describe the
binary-cache change as a successful root-cause fix.

A controlled setup experiment now copies Ubuntu's source declaration into an
owned temporary directory, selects the reachable mirror there, and uses identical
explicit source/list/compression options for update, policy and install. It logs
active index filenames/suites/components and critical package candidates. Global
sources/lists are neither edited nor deleted. Cleanup preserves the original
status; SIGINT/TERM exit through cleanup, SIGKILL relies on runner temp cleanup.

Executed a real fresh/repeated Ubuntu24.04 container test using digest
fe81560990fae86dc4743202b2cb4d3df98d0bcf949173cecef15ce1127ef852:
`docker run --rm --name rust-ui-ubuntu-apt-probe ... ubuntu:24.04 bash -lc
'bash /work/setup_linux.sh && bash /work/setup_linux.sh'`. Mounted this source
script read-only and the environment CA read-only; forwarded proxy variables,
set RUST_UI_APT_CA to that CA file and DEBIAN_FRONTEND=noninteractive. TLS,
Ubuntu keyring/signatures and metadata validity checks remained enabled.
Fresh install resolved all critical candidates and installed543 new packages;
repeat reported0 upgraded/0 newly installed. Both commands and cleanup exited0.
Minimal-container timings/size are not hosted CI speed measurements. Hosted
current-source validation remains required; no underlying root-cause claim.
