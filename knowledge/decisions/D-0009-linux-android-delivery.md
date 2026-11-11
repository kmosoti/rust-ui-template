---
id: D-0009
type: decision
status: implementation-in-progress
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# D-0009: Linux DEB/RPM and Android first

Implement the user-approved plan in three focused PRs: shared host entry point,
Ubuntu 24.04 DEB plus Fedora 44 RPM installation/launch, then Android test APKs
and emulator instrumentation. Keep one Leptos tree, one CSS bundle, Nocturne and
seven palettes, pure app-core and the version-1 host boundary. No Windows/macOS/
iOS port, production signing/store, AppImage, SSR or persistence in this slice.

Extract a native library run entry with the documented mobile macro; desktop
stays a thin executable and Linux features stay target-specific. Capability
extension to Android belongs with Android implementation/tests, not this refactor.

Android: installable debug/test-signed ARM64 and x86_64 APKs, SDK/target 37,
minimum API29, API36 x86_64 emulator, JDK21, NDK29.0.14206865. Generate with pinned
Tauri CLI2.12.4, pin generated Gradle/plugin versions and actual dependency locks.
Instrumentation-only AndroidX tests exercise the real WebView; no Node project
or embedded automation server. An ARM64 build is not physical-device evidence.

RPM must install and launch on Fedora44; format generation alone is insufficient.
Keep caches optional and trusted-save-only, setup repeatable, and capture native
failure diagnostics without masking exceptions or adding blanket retries.
Record actual SDK/runtime/distro/ABI and limitations. Independent reviewers use
standard/medium, never max/ultra; reviewer lands into develop, never main. Issue1
stays open with partial completion and other targets explicitly deferred.

Alternatives: Android store release requires signing credentials and is deferred;
RPM-only archive checks would not establish packaged behavior. Revisit when
release signing, another distro/ABI or platform support is requested.

## Relations

- **extends**: [D-0005](D-0005-linux-native-host.md)
- **observed-in**: [O-0009](../observations/O-0009-native-entry.md)
