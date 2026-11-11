---
id: O-0011
type: observation
status: implementation-ci-pending
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# O-0011: Android APK implementation evidence

## Observed locally

Generated the Android project with pinned Tauri CLI2.12.4, using the Android-safe
identifier dev.kmosoti.rustuitemplate. Native x86_64 Rust compiled successfully
with the existing unsafe_code forbid and mobile_entry_point; no lint exception.
Actual `tauri android build --debug --target x86_64 --apk --ci -- --locked`
produced an installable debug APK. A first Gradle attempt failed because the
system JDK21 path was actually JRE-only; downloaded Temurin21.0.13+9 from its
upstream GitHub release and verified SHA256 against its release checksum.
The cloud proxy CA required the system Java trust store, not TLS bypass.

Actual Gradle `:app:assembleUniversalDebug :app:assembleUniversalDebugAndroidTest
-PabiList=x86_64 -PtargetList=x86_64 -ParchList=x86_64 -x
:app:rustBuildX86_64Debug --write-locks --write-verification-metadata sha256
--no-configuration-cache` passed, compiling AndroidX tests and generating locks/
artifact verification metadata. `:app:dependencies :tauri-android:dependencies
--write-locks --write-verification-metadata sha256 --no-configuration-cache`
resolved remaining configurations; project locks are redirected into this repo,
not Cargo's external Tauri source. Cargo locks remained unchanged.

SDK archives were downloaded from Google, checked against official repository
SHA1 metadata, then SHA256 pinned in android-assets.json. Includes SDK37/36,
build-tools37/36, NDK29, platform-tools37.0.1, cmdline-tools19, emulator37.2.13,
and API36 Google APIs x86_64 rev7. No floating latest installer is used.
First/repeated `python3 scripts/setup_android.py` passed; `sdkmanager
--list_installed` recognized exact intended versions without XML warnings after
fixing local package license namespaces. Setup tests exercise warm no-download,
corrupt installed bytes/archive recovery and wrong-hash preservation.

`python3 -m unittest discover -s scripts -p 'test_*.py' -q`:18 passed on the
pre-rebase branch (16 existing +2 installer tests). Bash syntax and actionlint
passed. Production CSS checker passed with coarse-pointer48px controls.

## Pending and limitations

No /dev/kvm is available locally. Android launch, screenshots/visual critique,
IME/Back/rotation/lifecycle, offline assets, IPC/CSP and restricted ACL checks
remain pending the real emulator CI run. ARM64 build evidence pending. No store
signing, physical-device/TalkBack/minimum-API29 runtime validation is claimed.
The reviewed browser layout is reused; mobile equivalence is not assumed.

Android cold/warm timing/cache-transfer effects remain unmeasured. Caches are
optional/trusted-develop-save-only; no debug keys/AVD state/SDK ZIPs. Source and
artifact hash gates retain the security/functional checks.

## Relations

- **observes**: [D-0009](../decisions/D-0009-linux-android-delivery.md)
- **continues**: [O-0010](O-0010-linux-packages.md)
- **implements**: [Android guide](../../docs/android.md)
- **geometry**: [host brief](../../design/android-host-brief.md)

Revisit on CI runtime failure, upstream Tauri Gradle-template migration, changed
SDK/WebView versions, release signing or physical-device support requests.
