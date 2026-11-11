---
id: O-0019
type: observation
status: hosted-software-validated-hardware-pending
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Installed Linux Wayland and native accessibility checks

Informed by [O-0017](O-0017-issue1-completion.md), D-0009 and #23. This slice
adds software Wayland and native AT-SPI coverage, plus a real-desktop handoff;
it does not establish hardware rendering or manual Orca behavior.

## Executed observations

- `python3 -m unittest discover -s scripts -p 'test_*.py'`:30 tests passed.
  `python3 -m py_compile scripts/inspect_atspi.py scripts/wayland_smoke.py
  scripts/desktop_evidence.py`, `bash -n scripts/fedora_package_smoke.sh` and
  `git diff --check` passed. Cleanup escalation, busy ports and original HTTP
  failure evidence have focused regressions.
- Installed source-locked tauri-driver2.1.0 with `cargo install --locked`, using
  two build jobs. No --version flag exists; inspected its actual CLI help.
- Downloaded the previously validated develop323167e3 production RPM from Linux
  run42982373186, artifact13837539899. Ran the source's complete Fedora package
  script against it in a task-local Fedora44 container: install/reinstall,
  package ownership/desktop/icon checks, forced X11, actual software Wayland,
  native AT-SPI roles/names and remove all passed. This exercises a previously
  built real package; current-source packages and Ubuntu remain CI-pending.
- Fedora44 digest15da97ed9aa94dd3d92c3925eb89520f6c80e07ea7ee24cba848d1f8b6912b3e,
  Weston15.0.1, GTK3.24.52, WebKitGTK/WebKitWebDriver2.54.2. Owned Weston uses
  headless/pixman/kiosk-shell; client uses explicit Mesa software overrides.
  DISPLAY absent and actual wl_surface/xdg_toplevel messages observed. WebKit
  nevertheless reports X11 in userAgent: never infer display backend from it.
- `docker run --rm ... rust-ui-wayland-atspi bash
  scripts/fedora_package_smoke.sh /packages/rust-ui-native-linux.rpm` passed.
  Mounts were this worktree, read-only driver and production package directory;
  no privileged container or blanket WebKit sandbox bypass. Fedora image builds
  used the environment CA as a BuildKit secret, not a TLS verification bypass.
- Initial Docker run failed creating its VFS rootfs due to disk pressure; no test
  ran. `cargo clean --manifest-path /workspace/rust-ui-template/Cargo.toml
  --profile dev` reclaimed only generated artifacts (4.5GiB). Initial AT-SPI run
  failed importing missing DBus typelib. `dnf provides '*/DBus-1.0.typelib'`
  identified gobject-introspection; added explicitly and reran successfully.
  The minimal-image decorative glyphs prompted an explicit symbol-font package.
- Package-local DNF operations formerly refreshed unrelated repositories (over
  one minute, mirror503s). Disable repositories for install/reinstall/remove;
  dependencies must already exist in the runtime image and missing ones fail.
- PR32 Linux run43052897797 stalled in apt before any tests, was canceled once
  and rerun; the rerun also stalled. This slice replaces only the exact hosted
  Azure Ubuntu mirror URL and hosted mirror+file lists with the kernel.org third-party Ubuntu HTTPS mirror, retains signed
  suites/components, and bounds transport and overall setup time. Independent review found the
  hosted mirror+file indirection in canceled logs; the initial literal-URL-only
  replacement was insufficient and corrected before landing. No test
  assertion is retried or skipped. The initial official archive.ubuntu.com replacement also timed out. Bounded
  curl probes fetched kernel.org noble and noble-security InRelease successfully,
  with Origin/Label Ubuntu and current signed metadata (2026-11-11). This is a
  third-party mirror, not Ubuntu-operated. Ubuntu keyring/signatures/suites and
  metadata expiry validation remain unchanged. Current-source CI must validate
  the complete installation and application checks.

## Ownership and limitations

The software wrapper owns a private bus before enabling accessibility, a0700
runtime, compositor/test process groups and socket. Readiness/commands/cleanup
are bounded. The real-desktop harness preserves the existing session/settings,
whitelists metadata and labels DRM presence as capability only. Native AT-SPI
checks exposed main heading/navigation roles/names; they do not test spoken
announcements, keyboard flow or WCAG conformance. Hardware GPU attribution,
100/200% desktop scaling and actual Orca remain pending. No /dev/dri device is
available on this cloud host. See [desktop validation](../../docs/linux-desktop-validation.md).

Revisit when current-source Ubuntu/Fedora CI artifacts and real hardware/Orca
observations are available. Update this record with failures as well as passes;
keep #23 open for missing dimensions.


## Subsequent transport investigation

PR35 Linux43064819211 failed in Fedora production X11 while switching the actual
WebDriver window: RemoteDisconnected/connection reset after session creation.
Artifact13874274853 retains the failure and complete driver log. It contains an
unsupported DRI3 warning but no conclusive crash cause. No assertion was replayed.
Xvfb now uses the same explicit Mesa software/DMABUF-off client configuration as
Wayland. A bounded owned-process snapshot and driver return code improve future
failure evidence; tests enforce descendant-only capture, field whitelisting,
limits and process-exit tolerance. This does not prove the warning caused the
reset or that intermittent resets are eliminated.

An actual one-day `linux-restricted-test-fixture` RPM artifact is separate from
production packages, uploaded only after a successful restricted build with
missing-output failure. It supports genuine local denial reproduction without
fake IPC responses, recompiling packages or distributing the fixture as production.
Local current-source production/denial and new-head hosted results remain pending
until executed. Ubuntu metadata now lives in an owned /tmp directory so _apt can
traverse the parent; RUNNER_TEMP had caused a root-download fallback warning.
The prior fresh/repeated Ubuntu probe already used /tmp with no such warning.


## HTTP boundary investigation

The next run43066561532 still reset at Fedora X11 window-handles despite software
flags and no DRI3 warning. Artifact13876661535 shows tauri-driver, WebKitWebDriver,
the app and both WebKit workers alive at capture, with no core dump. Thus the
warning was not established as the cause and software flags did not solve the
transport failure. No assertion was replayed.

Inspected actual pinned tauri-driver2.1.0 server.rs: it forwards incoming headers
unchanged through a pooled Hyper client, with canceled-request retries disabled.
A real local HTTP/1.1 wire probe showed Python urllib forces Connection: close.
The harness now uses stdlib http.client, omits that hop-by-hop close header,
consumes responses and closes its frontend socket. The backend's default HTTP/1.1
persistence is preserved. No failed command is replayed, no driver fork or app
change is introduced. HTTP failure status, bounded body and original exceptions
remain available; timeout/socket cleanup and wire-level success/non-2xx are
covered. The same wire probe now observes no Connection header. This is evidence
for the interoperability hypothesis, not proof of every upstream root cause.
Local production and fresh hosted verification are required before landing.
## Hosted current-source validation

PR33 exact head93f5df8e211f3f090b673985b8fee2a057b9d17e passed all six checks;
independent medium reviewer owned rebase landing into developdabb1479. Linux
run43058376459 passed289s. Downloaded artifact13873615841 with the GitHub
artifact connector, extracted it and inspected all runtime/compositor/AT-SPI
JSON plus Ubuntu production library and Fedora restricted-denial screenshots.
The independent reviewer separately inspected all four native accessibility trees.

- Ubuntu24.04: GTK3.24.41, WebKitGTK/WebDriver2.52.6, Weston13.0.0.
- Fedora44: GTK3.24.52, WebKitGTK/WebDriver2.54.2, Weston15.0.1.
- Production and restricted packages each passed forced X11 and real software
  Wayland. Four AT-SPI snapshots have52 nodes each and zero missing required
  roles/names; restricted title correctly differs from production. No failure
  JSON exists. Wayland reports DISPLAY null, own display/socket and explicit
  software client overrides, with actual surface/toplevel protocol evidence.
- The source-drift gate and preserved production package SHA checks passed.
  Native screenshots show application text, original artwork and symbol glyphs;
  a viewport screenshot does not by itself prove every scroll/scaling state.

Command families: `gh run view`, `gh api .../actions/runs/RUN/{jobs,artifacts}`,
artifact connector download, `unzip`, Python JSON inspection and local image
viewing. No current-source Ubuntu/Fedora software result remains pending.
Actual GPU/compositor/scaling/manual Orca evidence remains pending in #23.
The real-desktop harness has not been run; close other template instances before
its title-based AT-SPI inspection so another matching window cannot confuse it.

A further controlled experiment used the actual pinned tauri-driver2.1 proxy and
a minimal standard-library HTTP/1.1 backend:300 unique GETs with urllib and300
with http.client both passed, with0 assertion/request retries. Executed
`python3 /workspace/scratch/probe_proxy_keepalive.py`; results retained locally.
This negative result does not reproduce the Fedora/WebKit failure and must not
be represented as causal proof. The wire-header observation and production
packaged-app verification are distinct evidence.

The HTTP-client sourcee8bd7f6 passed current Linux run43068162381 (404s), including
Ubuntu/Fedora production/restricted packages on both software display backends.
Downloaded its actual restricted RPM artifact13877825330, then executed
`docker run --rm ... rust-ui-wayland-atspi bash -lc
'bash scripts/fedora_package_smoke.sh /packages/*.rpm restricted'` using the real
fixture and current harness. Install/reinstall, real X11 denial, real Wayland
denial/native AT-SPI and removal passed locally with exit0. An independent medium
reviewer inspected the actual log. No IPC response was faked. This successful
configuration is evidence for compatibility, not proof that every intermittent
upstream transport failure has been eliminated.


The final evidence slice also makes Ubuntu restricted-package removal explicit
after its denial checks and preserves the executable-absence assertion. Fedora
already removes both variants. This improves repeatable cleanup rather than
relying on runner disposal; actual final-head hosted execution remains required.

## Automated keyboard and software-scale continuation

[O-0022](O-0022-linux-keyboard-scaling.md) extends these observations with actual
WebDriver key actions and measured software output scale. It retains the original
headless/AT-SPI matrix and documents the Weston13 headless seat limitation and
explicit nested software alternative. Hardware desktop scaling and human Orca
remain separate pending dimensions; historical failures above remain evidence.

[O-0023](O-0023-linux-physical-desktop.md) records the first actual Fedora GNOME
Wayland desktop continuation, its retained failed AT-SPI run and PID-scoped
correction, measured app-attributed hardware work, and manual observation limits.
