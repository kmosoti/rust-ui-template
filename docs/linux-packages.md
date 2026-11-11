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
X11 under Xvfb, not a full Wayland/hardware matrix. Both install and reinstall the
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

See D-0009 and the dated packaging observation for executed results and limits.
