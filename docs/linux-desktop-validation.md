# Linux desktop evidence handoff

CI uses software rendering. A successful headless test does not establish GPU
composition, desktop scaling, or an Orca user experience. Issue #23 remains open
until these separate native desktop observations are attached and reviewed.

Install the exact production DEB/RPM under test on Ubuntu 24.04 or Fedora 44.
Record its SHA256, source commit, OS, compositor/session and scaling. Install the
matching WebKitWebDriver, tauri-driver 2.1.0, system Python and pyatspi (Fedora
also needs gobject-introspection). Enable accessibility using the desktop's normal
settings before an AT-SPI run. The harness never changes those settings, starts a
replacement compositor or adjusts the existing session bus.

Close other instances of this template before title-based AT-SPI inspection.
From the repository root in that desktop session:

```sh
# Choose the actual session, not both commands on an incompatible desktop.
env -u DISPLAY GDK_BACKEND=wayland python3 scripts/desktop_evidence.py --atspi --artifact-prefix ubuntu-wayland-hardware
GDK_BACKEND=x11 python3 scripts/desktop_evidence.py --atspi --artifact-prefix ubuntu-x11-hardware
```

Use `--application` for a deliberately different installed executable. Remove
software renderer overrides first. The tests start/stop their own app/driver;
they do not terminate existing apps. The desktop report deliberately whitelists
metadata. DRM device/driver presence proves capability only: it leaves
`hardware_gpu_verified` false. Attach compositor diagnostics or a graphics trace
attributing hardware rendering to this app, with GPU model/driver/renderer and
capture method. Do not infer that from a WebKit user agent or `glxinfo` alone.

For each actual GPU/session under review, attach the report, native AT-SPI tree,
functional results, library/latest-response screenshots, and manual observations:

- At 100% and 200% desktop scaling, inspect text, icons, clipping, scrolling and
  focus indicators. Resize the window; navigate away during a slow request and
  return. Confirm no stale result appears or task survives its owner.
- With keyboard only, use the skip link, visit navigation, launch slow then fast,
  cancel, change palette, and return to Library. Check a logical focus order,
  visible focus, no trap and usable controls at narrow sizes.
- With Orca actually running, record version, speech settings and results for
  navigation names, main heading, input labels, pending/latest/cancelled states,
  errors and result announcements. Check announcements are understandable and
  not duplicated. Attach a short transcript or recording with consent.
- Run the restricted-window fixture separately if available and verify its
  predictable permission error. Never distribute this fixture as production.

AT-SPI roles/names are an automated smoke test, not a substitute for Orca or a
claim of accessibility conformance. Record every untested GPU/compositor/scaling
combination and every failed/manual-pending item; never mark this list complete
from CI screenshots. Put dated evidence in `knowledge/` with provenance and link
it to #23. No hardware GPU or manual Orca result was obtained in the cloud host.
