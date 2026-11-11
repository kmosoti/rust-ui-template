---
id: O-0023
type: observation
status: physical-wayland-observed-manual-pending
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Fedora physical Wayland desktop continuation

Refs [issue #23](https://github.com/kmosoti/rust-ui-template/issues/23).
This extends [O-0022](O-0022-linux-keyboard-scaling.md) with the existing physical
Fedora desktop, rather than another software compositor. Manual observations
below remain separate from WebDriver input and native AT-SPI metadata.

## Source, package and environment

**Observed:** isolated branch `test/linux-physical-desktop`, based on
`origin/develop` `81a1a6b0f98b9a102b11131b8a963b38e27f6d2e`, worktree
`/home/kmosoti/Documents/Codex/2026-11-11-continue-linux-desktop-validation-for-kmosoti/linux-desktop-validation`.
No existing checkout or local edits were found; the new clone and linked worktree
preserve other projects and processes.

The unsigned production RPM was downloaded through the GitHub artifact connector:
[Linux run 43112663525, attempt 2](https://github.com/kmosoti/rust-ui-template/actions/runs/43112663525/attempts/2),
artifact `13896529113` (`unsigned-linux-packages`). The successful run's authored
head was `7e0c2f2fea904ce57f383c2f2a1adbbd3e44bebd`. Actual checkout, independently
read from job `130833644243` logs, was synthetic merge
`61e2121772a904dcf17a3688acf6da1ebeb059b2` into base
`c3b498b937a62158551d51d87d4eee2fc37ab63b`. Authored head, synthetic checkout and
landed develop all resolve to the same Git tree:
`7009a55d3c4bb934cf2c659571ed9bb3dbb87f9c`.
This continuation changes the harness/docs only; the installed application remains
that independently built production package.

RPM SHA256:
`29a50346029962678777f0875700185028e1b92764fed55b0c5d1f4ebfdc3b6b`, matching the
actual downloaded `linux-packages.sha256`. RPM metadata:
`rust-ui-template-0.1.0-1.x86_64`, build time 2026-11-11 22:39:24 UTC, unsigned,
three installed files (executable, desktop entry, icon), no install scriptlets.
`rpm -q rust-ui-template` initially reported absent. The user ran the explained
privileged prerequisite; agent `sudo -n true` had reported a password required:

```sh
sudo dnf --disablerepo='*' install /home/kmosoti/Documents/Codex/2026-11-11-continue-linux-desktop-validation-for-kmosoti/linux-desktop-validation/artifacts/packages/rust-ui-native-linux.rpm
rpm -q rust-ui-template
rpm -V rust-ui-template
```

**Observed:** installation reports `rust-ui-template-0.1.0-1.x86_64`; verification
produces no differences. Existing user data was not removed or modified. No
existing package was replaced. Runtime dependencies were already present.

| Dimension | Observed value |
| --- | --- |
| OS / architecture / kernel | Fedora Linux 44 Workstation / x86_64 / 7.2.13-200.fc44.x86_64 |
| Session / compositor | Existing GNOME Wayland `wayland-0`; GNOME Shell/Mutter 50.6-2.fc44 |
| GTK / WebKitGTK / matching WebKitWebDriver package | GTK 3.24.52-2.fc44; webkit2gtk4.1 and webkitgtk6.0 2.54.2-1.fc44 |
| Python native accessibility | python3-pyatspi 2.58.2-1.fc44; gobject-introspection 1.86.0-3.fc44 |
| Mesa | 26.2.5-1.fc44 |
| Intel adapter | CometLake-H GT2 UHD Graphics, PCI 8086:9bc4, 0000:00:02.0, kernel i915 |
| Other available adapter | NVIDIA GA106M RTX 3060 Mobile/Max-Q, 10de:2520, nvidia kernel module 615.78.08; no separate NVIDIA rendering-path test |
| Initial outputs | eDP-1 BOE 1920×1080@144; DP-1 Sceptre C24 and HDMI-1 Sceptre F24 1920×1080@60; Mutter scale 1 on all three |
| Text scale / experimental features | 1.0 / empty list; unchanged by agent |

The whitelisted [machine snapshots](../evidence/O-0023/machine-initial.json)
retain compositor-observed logical monitors, not merely GNOME's automatic
`scaling-factor=0` preference. System packages verified clean with `rpm -V`.
Pinned `tauri-driver` 2.1.0 was built user-locally with
`cargo install tauri-driver --version 2.1.0 --locked --root .tools/driver --jobs 2`
(20.04s), SHA256
`d63c3a19441b06c410ea5a4a529905e2f6b887f54689557af0f452adb724743d`.
System `/usr/bin/WebKitWebDriver` SHA256:
`7eef4c11bc3f063e97a7a279957f4c6ead3497a23e09006f85350814b0844b2b`.
Neither tool implements `--version`; package/version/install receipts are used.

## First failure and causal correction

**Observed:** the first existing-desktop run used forced Wayland with DISPLAY and
XAUTHORITY removed, no software overrides, and read-only graphics/protocol
logging. All six WebDriver keyboard checkpoints passed. Native AT-SPI then
failed with `Accessibility snapshot exceeded its node/depth bound`. Original
[failure JSON](../evidence/O-0023/fedora-desktop-scale1-failure.json), raw compressed
driver/console logs and GPU samples are retained; the whole run is a failure.
IPC/CSP/About checks after AT-SPI did not execute in that run. That first run's
`wl_surface#38.enter(wl_output#8)` maps to HDMI-1 Sceptre F24; this is
independent of the successful run's output placement below.

**Causal evidence:** the inspector started at the shared desktop and traversed all
applications before filtering by title. This physical session had eight top-level
applications, including large unrelated trees; the 2,000-node budget was global.
The correction selects exactly one installed executable among the owned driver
descendants and passes its PID to the native inspector. Discovery reads only
bounded top-level application identities (at most 256); traversal is limited to
the selected application. Its own 2,000-node/24-level limits remain failures.
A wrong-PID window with the same title cannot supply evidence. The new regression
uses an unrelated object that raises on any content access, independently testing
that no unrelated subtree is traversed. Missing, ambiguous or truncated owned
process discovery fails explicitly; no arbitrary desktop process is selected.

The initial Screen Reader/toolkit preferences were false. After the user's first
“done” (installation), both remained false and no Orca process existed. A later
explicit “its on” corresponded to both settings true and Orca PID 3507407.
The agent did not toggle those settings. Those messages alone do not establish
spoken output or usability.

## Changed-prerequisite 100% pass

After the PID correction and the user's accessibility change, a separately named
run `fedora-desktop-scale1-pid-scoped` completed with exit 0. This is a changed
setup/code observation, not replaying an assertion until it passes.

| Requested / observed quantity | Result |
| --- | --- |
| Desktop setup | Retain current 100%; Mutter output scales independently observed as 1 |
| Actual app output | Wayland `wl_surface#38.enter(wl_output#10)`; `get_xdg_output` maps #10 to `zxdg_output_v1#15`, named eDP-1 BOE |
| Logical WebView viewport | 1200×900 |
| Observed DPR | 1 |
| WebDriver PNG pixels | 1200×900, agrees with viewport × DPR |
| Expected-DPR argument | Not yet exposed by original desktop wrapper; `null` in this historical report |
| Real W3C keys | Six checkpoints pass: skip/main, Library launch, Slow/Fast freshness, reverse Tab, cancel, palette/persistence |
| Native AT-SPI | Exactly owned application PID 3507911, 52 nodes, missing roles/names `[]` |
| Subsequent native checks | Shared CSS/WASM, freshness, typed IPC validation, production CSP and About native result pass |

Independent review caught an initial record error that reused the first run's
HDMI-1 placement for the successful run. The retained protocol logs establish
the distinct outputs above; all outputs were scale 1, so the scale conclusion
survives. A new application launch must have its own output placement verified.

The original first run's Fast result 22 was observed 0.19536s after the
conservative pre-Slow activation anchor, while Slow was still pending immediately
before Fast. The successful changed run retains its own timing in its keyboard
JSON. Cancellation remains stable beyond the original slow timer. Key actions
are never replayed; focus searches retain their existing 40-Tab/15s bounds.

The desktop wrapper now accepts explicit `--expected-dpr 1|2`, delegating to the
existing DPR and PNG consistency assertions. It does not adjust desktop scale or
CSS zoom. No physical output scale is inferred from DPR alone.

Opened the actual [skip-link PNG](../evidence/O-0023/fedora-desktop-scale1-pid-scoped-keyboard-skip-link.png)
and [Number PNG](../evidence/O-0023/fedora-desktop-scale1-pid-scoped-keyboard-number.png):
focus outlines and text are visible, the Number field fits in the viewport, and
the library can scroll. These are agent screenshot observations, not a human
keyboard or screen-reader verdict.

## App-attributed hardware work

The task-local [monitor](../evidence/O-0023/monitor_desktop.py) records only
harness-owned descendants' whitelisted DRM fdinfo fields and graphics-library
paths. Runtime is bounded to 270s, traversal to 64 processes and 256 descriptors
per process, retained rows to 50,000. Diagnostic exit races are counted;
no unrelated process environments, documents or windows are captured. The raw
JSON is retained gzip-compressed with deterministic mtime, without editing rows.

**Observed:** on the successful 100% run, owned `rust-ui-native` PID 3507911,
i915 client 1793, accumulated 44,803,483ns additional render-engine time. Its
owned WebKit Web Process PID 3508000, i915 client 1797, accumulated 65,422,509ns.
Both report PCI device `0000:00:02.0`, independently identified above as Intel UHD.
An additional owned client had zero render delta; it is not counted as rendering
merely because its device was open. Six `FileNotFoundError` capture races occurred
as descriptors/processes exited; zero rows were dropped. One additional final
WebKit row resolved an already-closed fd link to its own `/proc/3508000/fd/23`
pathname rather than `/dev/dri`; its previously read i915 client/device/counter
fields remain intact. A privacy audit initially asserted every symlink resolved
and failed on this row; the original row and [audit note](../evidence/O-0023/privacy-audit-notes.txt) are preserved.
Attribution uses the stable DRM client/device fields, not that unresolved link.
The collector does not claim atomic process/fd snapshots.

The [Linux DRM usage specification](https://www.kernel.org/doc/html/latest/gpu/drm-usage-stats.html)
defines engine time as workload execution belonging to the DRM client.
**Inference supported by these counters:** this actual application's host and
WebKit process performed hardware render-engine work on i915 during the run.
This establishes more than adapter presence or a WebKit user agent. It does not
quantify every rendered pixel, prove all operations avoid software, measure GPU
performance, or test NVIDIA rendering. Exact GL renderer-string diagnostics were
not available; no preload shim or renderer override was introduced to obtain one.
The general desktop JSON intentionally retains `hardware_gpu_verified:false`
because it does not automatically assess supplemental diagnostic evidence.

## Manual Orca and keyboard observations

**Observed configuration:** Orca 50.3-1.fc44 actually running; Speech Dispatcher
0.12.1-6.fc44 and eSpeak NG 1.52.0-3.fc44 installed. Read-only scoped GSettings
capture of the only configured profile (`default`): speech enabled,
`speechdispatcherfactory`, verbose speech, most punctuation, default rate 50,
pitch 5, volume 10, desktop keyboard layout, Insert/KP_Insert modifiers, live
regions enabled. These keys have no user overrides. Voice/synthesizer names are
empty defaults: the actual runtime voice is **unknown**, not inferred from an
installed synthesizer. See [settings JSON](../evidence/O-0023/orca-default-settings.json).

**Pending:** a persistent standalone production app was opened for the user's
skip/main, navigation/reverse-Tab and invalid-number speech/focus observations.
No transcript, human speech result or usability verdict has yet been received.
Slow/Fast/cancel, palette, navigation while pending, narrow-window and real 200%
visual/manual observations are still pending. No recording was started.

## Reproduce and verify

From the isolated worktree after the documented package and human settings setup:

```sh
# Keep operational collectors outside product runtime code.
cp knowledge/evidence/O-0023/{capture_machine,monitor_desktop,manual_session}.py artifacts/
/usr/bin/python3 artifacts/capture_machine.py scale1-accessibility-enabled
env -u DISPLAY -u XAUTHORITY -u LIBGL_ALWAYS_SOFTWARE -u GALLIUM_DRIVER \
  -u WEBKIT_DISABLE_DMABUF_RENDERER GDK_BACKEND=wayland EGL_LOG_LEVEL=debug \
  LIBGL_DEBUG=verbose WAYLAND_DEBUG=1 PATH="$PWD/.tools/driver/bin:$PATH" \
  /usr/bin/python3 artifacts/monitor_desktop.py fedora-desktop-scale1-pid-scoped \
  /usr/bin/python3 scripts/desktop_evidence.py --keyboard --atspi \
  --artifact-prefix fedora-desktop-scale1-pid-scoped
# New runs should also supply --expected-dpr 1 or 2 after the human has selected
# the intended output scale. Use a fresh artifact prefix, preserving old failures.
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 -m py_compile scripts/desktop_evidence.py scripts/inspect_atspi.py scripts/native_smoke.py
git diff --check
```

**Executed local checks:** original 59 tests pass; PID correction 64 tests pass;
final DPR-forwarding suite 65 tests pass. An initial new test failed because its
Popen mock intercepted `platform.platform()`'s subprocess call; the fixture now
mocks that unrelated platform lookup. Failed and corrected test logs are retained
locally. Affected `py_compile` and `git diff --check` pass. No UI/core/host code,
dependency, workflow, cache or platform matrix was changed; existing Linux CI
will exercise PID selection in both production/restricted AT-SPI sessions without
extra builds. Draft [PR #38](https://github.com/kmosoti/rust-ui-template/pull/38) runs fresh-head
CI and independent Terra medium review. Its final evidence and human-pending
status are maintained in the PR; the author does not land the change.

## Limits and relations

No accessibility conformance claim, full compositor/GPU matrix, X11 desktop,
NVIDIA-rendering path, ARM64 package or minimum runtime is established here.
Android physical ARM64/API29/TalkBack remain outside this slice. Issue #23 remains
open. The installed app and user-selected desktop preferences remain in place;
only owned test applications/drivers are stopped.

- *extends*: [O-0019 native Wayland/accessibility](O-0019-linux-wayland-accessibility.md), [O-0022 automated keyboard/software scale](O-0022-linux-keyboard-scaling.md)
- *preserves lifecycle policy*: [O-0021 bounded native cleanup](O-0021-android-lifecycle-stall.md)
- *corrects workflow*: [desktop handoff](../../docs/linux-desktop-validation.md)
- *observed-in*: [overall architecture](../../docs/architecture.md)

Revisit with the remaining human observations, actual 200% desktop run and fresh
PR checks. Keep failed runs and their original assertions alongside new evidence.
