---
id: O-0010
type: observation
status: implementation-ci-pending
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# O-0010: DEB/RPM and native diagnostics

Follows the shared entry PR18 at a7618b9. Its CI passed core27s, browser1m25s,
and installed Linux production/denial3m39s (run42939987815), establishing the
refactor's Linux behavior. No Android launch is inferred.

Added production DEB/RPM bundling from one executable, Fedora44 digest-pinned
installed runtime tests, package metadata/reinstall/removal checks, separate
production versus restricted artifacts, and failure-stage/driver-log capture.
No blanket retry or exception swallowing was added to test execution.

Local Fedora44 image digest:
15da97ed9aa94dd3d92c3925eb89520f6c80e07ea7ee24cba848d1f8b6912b3e.
Docker probe installed matching WebKit2GTK4.1/WebKitGTK6 2.54.2 packages and found
WebKitWebDriver at /usr/sbin. Source-native GTK headers are absent on the outer
host. GitHub artifact redirect returned403, so the earlier CI-built binary could
not be downloaded for this local probe; no local installed-app pass is claimed.

`python3 -m unittest discover -s scripts -p 'test_*.py' -q`:16 passed, including
new diagnostic-capture failure cases. `bash -n scripts/fedora_package_smoke.sh`
and diff checks passed. CI installed-package evidence remains required.

## Limits and revisit

Xvfb is X11, not Wayland/GPU hardware coverage. Fedora44 validation does not imply
other RPM distro support. Signing, release reproducibility, and ARM Linux remain
future work. Revisit on distro/runtime updates or another native disconnect.

## Relations

- **observes**: [D-0009](../decisions/D-0009-linux-android-delivery.md)
- **continues**: [O-0009](O-0009-native-entry.md)
