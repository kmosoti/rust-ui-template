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

Native AT-SPI inspection selects the exact executable PID from the owned driver
descendants, then inspects only that application's matching window. Other apps
and template instances are neither traversed nor terminated. Direct inspector
use requires `--pid OWNED_APPLICATION_PID`; a matching title alone cannot supply
evidence. Discovery is bounded to 256 top-level applications; the selected tree
retains its 2,000-node and 24-level limits.
From the repository root in that desktop session:

```sh
# Choose the actual session, not both commands on an incompatible desktop.
env -u DISPLAY GDK_BACKEND=wayland python3 scripts/desktop_evidence.py --atspi --expected-dpr 1 --artifact-prefix ubuntu-wayland-hardware
GDK_BACKEND=x11 python3 scripts/desktop_evidence.py --atspi --expected-dpr 1 --artifact-prefix ubuntu-x11-hardware
```

Use `--application` for a deliberately different installed executable. Remove
software renderer overrides first. The tests start/stop their own app/driver;
they do not terminate existing apps. The desktop report deliberately whitelists
metadata. DRM device/driver presence proves capability only: it leaves
`hardware_gpu_verified` false. Attach compositor diagnostics or a graphics trace
attributing hardware rendering to this app, with GPU model/driver/renderer and
capture method. Do not infer that from a WebKit user agent or `glxinfo` alone.

Choose `--expected-dpr 1` or `2` for the intended desktop observation. This asserts
the measured WebView DPR and PNG dimensions; it does not set desktop scaling.
Record the human-requested scale and compositor-observed scale of the output
actually entered by the app separately, especially on mixed-scale desktops.
Keep logical viewport size, DPR and PNG pixel dimensions distinct. If the app
opens on another output, retain the mismatch and correct the test setup before
a separately named run; do not relabel or replay a failed assertion.

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

## Automated keys and software output scale

Production X11 sessions now use WebDriver W3C key actions for the skip link,
forward/reverse Tab navigation, response input/Slow/Fast/Cancel, and the actual
palette select. JavaScript in this sequence only reads state and focus. Each
semantic traversal is bounded to 40 Tabs and 15 seconds, including command timeouts;
input failures and assertions are never replayed. The keyboard JSON records
checkpoint progress, bounded focus traces, viewport/DPR, overlap timing and failure
context. Focused skip-link and number-field PNGs show the observed outline.
These are automated input observations, not a human keyboard usability verdict.

Fedora Weston 15 uses headless pixman and its advertised `--fake-seat` for keyboard
focus at output scales1 and 2. Ubuntu Weston 13 has no headless keyboard seat:
its original headless scale1/AT-SPI run remains unchanged, while the added scale2
keyboard run explicitly uses a Weston X11 backend inside an owned Xvfb parent.
The application and `wayland-info` have neither `DISPLAY` nor `XAUTHORITY`; they
use the owned Wayland socket. This nested software configuration is recorded in
the compositor JSON and is never labeled a hardware desktop.

```sh
# Existing supported software seat (Weston 15):
python3 scripts/wayland_smoke.py --keyboard --scale 2 --artifact-prefix software-scale2
# Explicit software nesting for Weston 13; no automatic fallback:
python3 scripts/wayland_smoke.py --compositor-backend x11 --keyboard --scale 2 --artifact-prefix nested-scale2
# Existing real desktop (does not change renderer or accessibility settings):
python3 scripts/desktop_evidence.py --keyboard --expected-dpr 1 --artifact-prefix desktop-keys
```

Output scaling is a compositor setting, not CSS zoom or browser emulation.
Requested scale, Weston command/version/help, actual output protocol,
logical viewport, observed DPR and PNG pixel dimensions are retained. DPR must
match the requested scale within 0.05, and screenshot pixels must agree with
viewport×DPR within 1 pixel. A mismatch fails. Software output scale2 does not
complete real desktop 100/200% scaling, GPU attribution, human usability or Orca
speech checks. Those manual checkboxes and issue #23 remain open.

Keyboard action release has a 3s timeout. Both owned native wrappers allow 21s
for release, session deletion and driver TERM/KILL cleanup before escalation.
External SIGKILL or forced container destruction cannot run Python finalizers.
