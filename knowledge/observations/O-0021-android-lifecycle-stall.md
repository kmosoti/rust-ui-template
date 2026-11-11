---
id: O-0021
type: observation
status: corrected-hosted-validated
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Android shutdown stall during the cache trial

Informed by [O-0020](O-0020-android-cache-partition-trial.md) and #23/#31.

## Observed failure and retained data

Run43069846343/attempt4 (sourcea88b6c6, image20261101.360.1) restored all three
cache entries exactly. Device boot completed in55463ms. Production instrumentation
reported OK at18:10:32 (35.47s test), restricted instrumentation OK at18:10:56
(11.048s test). Both folders contain runtime/instrumentation/logcat/window/UI,
device screenshot, WebView evidence tar and extracted captures. No application
assertion failure appears. The job did not finish afterward.

The wrapper had unbounded AVD creation, postboot shell adb commands, and EXIT
cleanup ending in an unbounded emulator wait after TERM. Existing evidence lacks
shutdown phase markers, so the exact blocked operation is not proven; it lies
after successful test output and complete evidence capture. Do not describe this
as a boot failure or a successful benchmark. At independent review's20min step
triage boundary, `gh run cancel 43069846343` was requested18:28:33. The emulator
step ended18:28:47 after1220s; whole job1476s, canceled. This was operational
triage, not a replay of a failed application assertion.

Downloaded device artifact13882119469 and restored-profile artifact13881443488
using the GitHub artifact connector; inspected actual instrumentation and all
capture files. `gh api .../attempts/4/jobs` and `ci_timings.py` retain timings.
Live job logs returned404 until completion; no hidden current-log information
was available. Runner final cleanup still found bash/QEMU/adb/netsim processes.

## Targeted correction

The shell entry bounds AVD creation to120s with5s kill escalation. A Python
controller owns emulator and test process sessions, preserves the600s boot and
240s instrumentation budgets, bounds postboot adb calls, and supervises each
existing case with an outer900s limit. It writes explicit lifecycle phases to
stdout and an artifact journal. Assertions, offline behavior, both ABIs, SDK
verification, strict Gradle and cache trust rules remain intact. No failed case
is replayed. No workflow/compiler/cache key changed.

Graceful shutdown addresses only the owned serial; bounded TERM/KILL and finite
waits replace the open-ended trap. Shared `owned_process` now supplies the same
termination policy to Android, Wayland, desktop and native driver harnesses.
Cleanup failure fails a successful run, preserving an original error otherwise.
Serial/port preconditions reject an existing listener before emulator actions.

## Executed verification and limits

- `python3 -m unittest discover -s scripts -p 'test_*.py'`:47 passed, including real
  TERM-resistant subprocesses, signal interruption with a live unrelated
  bystander, original-error preservation, cleanup failure after success and
  occupied-port rejection. These fixtures test lifecycle, not real Android UI.
- `bash -n scripts/android_emulator_smoke.sh` and `git diff --check` passed.
- Existing full packaged-app checks remain necessary in fresh hosted CI;
  corrected-runner benchmark observations must be separate from old samples.
- A stopped group leader does not prove every detached/reparented service ended.
  The harness never kills global adb or unrelated groups. External SIGKILL cannot
  execute Python cleanup; ephemeral runner cleanup remains the last backstop.
- No real KVM Android launch was possible in this cloud workspace. No GPU,
  physical ARM64, minimum-API device or manual assistive-technology claim follows.

Revisit when corrected hosted lifecycle journals and complete warm validations
are available, or another shutdown stall occurs. Preserve failures as well as
successes; do not infer a universal speedup or a proven SDK/cache cause.

## First real corrected-runner validation

PR36 head da033df passed its full check set, including actual Android run
43080751204/attempt1 and Linux43080751576. Android artifact13885206265 contains
the new journal: boot49.14s, production complete108.98s, denial complete130.26s,
shutdown request130.263s, process termination130.267s, cleanup complete135.432s.
The owned emulator return code was-9 and cleanup errors were empty. Thus the
finite forced-termination path actually ran after both real app cases, completing
about5.17s after shutdown started. This verifies the bounded path, not the exact
unlogged syscall responsible for the earlier stall or every detached service.
An independent medium reviewer inspected the actual journal.

Both profile phases (artifact13883982991) have all three exact hits, no errors,
synthetic probe false, sourceabfd780204a777923d2f9c41de508f22c3111ade and image
20261101.360.1. Whole job355s; restore65/15/13s, SDK verification9s, ABI64s,
emulator step137s. These corrected-source measurements are separate from the
old-runner successes and cancellation; two more same-source measurements were
requested before any adoption decision.


## Complete corrected hosted series

Attempts2 and3 of the same run/source/image also passed,391s/393s. Actual device
artifacts13884909341/13885572319 end cleanup-complete at145.556s/158.574s,
emulator returncode0, original error null and cleanup errors empty. Production
and restricted cases, hash verification and source-drift passed in all three.
A Python check read all three real journals and both profile phases, asserting
source/image, exact hits, flags and recursively empty measurement errors.
The complete series and its deliberately limited cache decision are in O-0020.
These observations exercise graceful and forced termination; they do not prove
the old unlogged stall's exact cause or guarantee every future emulator exits.
