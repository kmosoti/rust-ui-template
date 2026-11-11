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
