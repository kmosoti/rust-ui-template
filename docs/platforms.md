# Platform evidence and compatibility

Only the listed build and launch checks establish application behavior. A shared
WASM UI does not by itself establish native platform support.

| Target | Build / package | Launch / behavior |
| --- | --- | --- |
| Browser, Linux Chromium 156 | Production Trunk root and subpath bundles passed | Interaction, navigation, cancellation and axe smoke passed |
| Linux Tauri / WebKitGTK | Ubuntu 24.04 Debian package built and installed | Launch/valid IPC observed; full smoke retry pending |
| Windows / WebView2 | Not built | Not launched |
| macOS / WKWebView | Not built | Not launched |
| Android / Android WebView | Not built | Not launched |
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
See [D-0005](../knowledge/decisions/D-0005-linux-native-host.md) and
[O-0005](../knowledge/observations/O-0005-linux-native-host.md) for exact evidence.
