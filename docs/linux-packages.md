# Linux packages: Ubuntu DEB and Fedora RPM

Build one production frontend and one native executable, then bundle both formats:

```sh
.tools/tailwindcss -i styles/input.css -o styles/generated.css --minify
trunk build --release --locked
(cd apps/native && ../../.tools/cargo-tauri tauri build --bundles deb,rpm -- --locked)
```

The isolated native Cargo lock remains authoritative. Linux needs the documented
GTK/WebKit development packages. Outputs are under native target/release/bundle.
Unsigned package generation is not signing or byte-for-byte reproducibility.

Ubuntu24.04 x86_64 DEB and Fedora44 x86_64 RPM are the explicit validation targets;
DEB does not imply every Debian version, nor RPM every RPM distribution. CI tests
forced X11 under Xvfb and genuine Wayland under an owned headless Weston
compositor, both with software rendering. This is not a hardware GPU matrix. Both install and reinstall the
actual package, check package-owned desktop entry/icon/executable, exercise real
UI/assets/app_info/CSP, and remove the production installation. A separate
restricted-window package exercises real permission denial.

The Fedora runtime image is pinned by digest. Fedora's matching-version
webkitgtk6.0 package supplies WebKitWebDriver; the application uses webkit2gtk4.1.
Compatibility is established by the installed app test, not by assuming the
package names or GTK ABI are interchangeable. GUI tests run as an ordinary user;
package manager commands run as container root. No privileged Docker mode or
blanket WebKit sandbox override is introduced.

Successful CI publishes `unsigned-linux-packages` (production DEB/RPM and SHA256
manifest). `linux-native-evidence` contains logs, images and failure JSON. The
restricted fixture is test-only and excluded from distributable artifacts.

The shared native smoke accepts `--artifact-prefix` so Ubuntu/Fedora and
production/denied results remain separate. Driver output is always recorded;
exceptions retain their traceback and stage in failure JSON, with a best-effort
screenshot. Capture/cleanup failures cannot turn a test failure into a pass or
replace the original exception. No automatic retry hides transport failures.

## Wayland and native accessibility

`scripts/wayland_smoke.py --atspi` owns a private session bus, runtime directory,
Weston process group and display socket. DISPLAY is absent; GDK_BACKEND is
wayland, Xwayland is never enabled. Pixman paints the compositor; client Mesa
software overrides are explicit. The test retains Wayland protocol evidence for
actual wl_surface/xdg_toplevel creation, compositor diagnostics and GTK/WebKit
versions. WebKit may still report X11 in its user agent: that string is not
backend evidence. Bounded cleanup kills only owned processes and retains original
failures. Unique ephemeral driver ports prevent collisions with other sessions.

Both production and restricted packages run through the existing functional/CSP/
IPC assertions; no frontend or package build is duplicated for Wayland. Native
AT-SPI checks inspect actual heading/navigation roles and names, independently
of the DOM. This is smoke coverage, not an Orca or conformance claim. Fedora's
minimal image explicitly installs gobject-introspection for the DBus typelib,
as well as pyatspi and symbol fonts. Local RPM operations disable repositories:
all runtime dependencies belong in the image, missing dependencies fail clearly,
and install/reinstall/remove no longer refresh unrelated mirrors.

For real compositor/GPU/scaling and manual Orca evidence, follow
[the desktop handoff](linux-desktop-validation.md). These observations remain
pending in #23. See D-0009 and O-0019 for executed results and limits.
