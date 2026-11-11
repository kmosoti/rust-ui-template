# Platform evidence and compatibility

Only the listed build and launch checks establish application behavior. A shared
WASM UI does not by itself establish native platform support.

| Target | Build / package | Launch / behavior |
| --- | --- | --- |
| Browser, Linux Chromium 156 | Production Trunk root and subpath bundles passed | Interaction, navigation, cancellation and axe smoke passed |
| Linux Tauri / WebKitGTK | Ubuntu 24.04 DEB and Fedora 44 RPM, x86_64 built/installed/reinstalled/removed | Xvfb: Ubuntu WebKitGTK 2.52.6 / Fedora 2.54.2; shared UI, IPC validation, CSP and real permission denial passed |
| Windows / WebView2 | Not built | Not launched |
| macOS / WKWebView | Not built | Not launched |
| Android / Android WebView | Test-signed ARM64 and x86_64 APKs built, strict locked Gradle dependencies | API 36 / Android 16 x86_64 emulator, WebView 133.0.6943.137: offline bundled UI, IPC/CSP/real denial, IME, Back, rotation and lifecycle checks passed; ARM64 build-only |
| iOS / WKWebView | Not built; requires macOS/Xcode | Not launched |

Tailwind 4's upstream CSS compatibility floors are Chrome 111, Safari 16.4 and
Firefox 128, as listed in the [upstream compatibility source](https://github.com/tailwindlabs/tailwindcss.com/blob/main/src/docs/compatibility.mdx)
checked on 2026-11-10. These are CSS prerequisites, not test evidence for this
application or its Rust-generated WASM. The native WebView must support the same
CSS and WASM features. No equivalence between Safari versions and WebKitGTK
package versions is assumed; CI reports its actual GTK/WebKit versions.

The Linux job uses Tauri 2.12.5, Tauri CLI 2.12.4 and tauri-driver 2.1.0. Its
production package and restricted-window fixture have distinct roles: the former
tests the installed application, and the latter tests the same registered command
with no matching window permission. Both use the same shared CSR assets and CSP.

Unsigned package build/install/launch checks do not establish reproducible signed
releases, signing, notarization, broad accessibility conformance or formal proof.
Final native [CI run 42908982231](https://github.com/kmosoti/rust-ui-template/actions/runs/42908982231)
passed on the exact source tree landed by PR #10, including the source-drift gate.
See [D-0005](../knowledge/decisions/D-0005-linux-native-host.md) and
[O-0005](../knowledge/observations/O-0005-linux-native-host.md) for exact evidence.

DEB/RPM delivery: [O-0010](../knowledge/observations/O-0010-linux-packages.md) and [package workflow](linux-packages.md). X11 CI does not establish Wayland or hardware GPU behavior.

Android execution: [run 42953564848](https://github.com/kmosoti/rust-ui-template/actions/runs/42953564848), [O-0011](../knowledge/observations/O-0011-android-apks.md). Minimum API 29 and WebView 111+ are prerequisites, not lower-bound runtime evidence. Physical devices and TalkBack remain untested.

Historical Android develop run42960500792 passed functional checks but had blank /
partially presented library/landscape screenshots. PR #25 corrected the capture
path with bounded PixelCopy validation. Its combined dependency/capture run
42979819097 passed all checks; an independent medium reviewer inspected complete
library/landscape and whole-display keyboard/IME captures before develop landing.
See [O-0012](../knowledge/observations/O-0012-presented-captures.md) for failed runs,
fixes, exact-head artifacts and the difference between DOM and pixel evidence.
