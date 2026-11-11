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

## Follow-up local checks

After rebasing onto reviewed PR19, all20 Python tests passed. Normal Gradle builds
with `--dependency-verification=strict` passed (95tasks,53s), without lock writes.
Browser production root/subpath tests passed all seven palettes/56 route-viewport
axe-layout cases plus stale/cancel/navigation/asset checks. Viewed actual desktop
and320px screenshots: existing rail/feature/rows remain legible and unclipped;
this is browser visual evidence, not Android evidence.

Review identified Kotlin cache directories not covered by generated ignores;
added a precise `.kotlin/` output ignore. A standalone test-build attempt invoked
Tauri's Rust bridge with no running CLI and failed; the corrected Gradle test
step excludes only the already-built x86_64 Rust task. Device tests now stage the
checksum-verified axe asset into the test APK only, assert HTTPS/single loaded
CSS, run WCAG-tag smoke and wait for real IME visibility using native insets.

First Android CI run42943799945 failed4m0s in Gradle buildSrc verification: a
transient Kotlin coroutines BOM1.8.0 POM was absent from warm-generated metadata.
Both native Rust ABIs compiled before Gradle failed. Browser1m3s/core30s/Linux
3m15s passed. Regenerating verification with a fresh GRADLE_USER_HOME exercises
cold resolution rather than trusting only the warm cache. No verification bypass.

Cold Gradle resolution generated the missing BOM checksum via Gradle, but local
Google Maven returned HTTP503 for EE4J lookup and then Android tools common.
No full cold-local pass is claimed. Scoped Google repository content to Android/
AndroidX/material/test-platform groups, avoiding unrelated Central POM lookups;
normal CI remains strict. Corrected test/insets/axe code compiled locally with
strict verification (74tasks/1s), and all20 Python tests still pass. Actual
Android screenshots remain inaccessible locally (artifact redirect403 persists,
including a cache-busting request); no device visual pass is claimed.


Run42944940860 reached ARM64 runtime-classpath verification but failed for two
Jackson2.15.3 parent POMs, still before device tests. The update-only Gradle init
helper now records transient POM artifacts from the original project cache,
validates their SHA1 content-address directories (Gradle omits leading zeros),
and resolves the exact bytes through a temporary local Maven repository. Actual
`recordResolvedPomChecksums --offline --write-verification-metadata sha256
--no-configuration-cache` passed2s, adding158 POM artifacts via Gradle, including
both reported Jackson parents. No checksum values were hand-written and normal
CI verification stays strict. Cold network resolution remained blocked by503.

Added package-only per-ABI clean before Android production builds, preserving
cached dependencies while ensuring cached denial/embedded assets cannot replace
current application output. Improved ADB failure output and independent native
screenshots, plus a visible-input check with the actual keyboard open. Corrupt
JSON marker shapes now converge safely too. The GitHub connector successfully
retrieved Linux evidence despite workspace artifact403; viewed Fedora About
capture shows intact layout/text but missing decorative-symbol fallback in the
minimal container fonts. No physical Fedora font-uniformity claim is made.
Issue1 checklist updated for completed browser/Linux foundations; stays open
with Android launch pending and Windows/macOS/iOS explicitly deferred.

After this expansion, strict offline application/AndroidTest build passed2s (95tasks); all20 Python tests and actionlint/diff checks passed.
