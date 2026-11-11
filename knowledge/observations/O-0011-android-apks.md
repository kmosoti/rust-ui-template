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


## Emulator startup and setup costs

Run42946216855 passed both ABI APK builds and strict dependency verification,
then failed the10min emulator boot deadline before instrumentation. Downloaded
artifact13822844385 via the GitHub connector; its emulator log says Unknown AVD
name rust-ui-api36 / no matching INI in the emulator lookup path. An environment
location mismatch is inferred; it is not a UI assertion failure or Android pass.
Locally, avdmanager ignores ANDROID_AVD_HOME for its INI location unless the Java
SDK user home is explicit too. Setting ANDROID_USER_HOME, ANDROID_EMULATOR_HOME
and ANDROID_AVD_HOME together created the actual INI, and emulator -list-avds
returned rust-ui-api36. No local VM launch (/dev/kvm absent) is claimed.

`python3 scripts/setup_android.py --emulator --discard-downloads` installed the
full pinned image locally and passed, including package XML recognition and AVD
creation. The actual emulator37.2.13 -help-gpu confirms swiftshader is supported.
CI now checks emulator liveness/log tail while polling boot, uses an explicit
serial and graceful bounded cleanup, and wipes owned fixture data per launch.
No automatic rerun of app assertions was added.

Verified SDK setup measured6.09s locally; after discarding retained archives,
repeated setup measured4.92s with no new downloads. These are local hot-filesystem
measurements, not CI warm-cache speedup claims. CI discards about3.3GB of verified
SDK ZIPs after installation and records available disk before launching the VM.
All20 Python tests, actionlint/bash/diff checks passed. Local tauri-driver install
was blocked by registry503, so no local controlled native transport test occurred.

Linux run42946216732 first failed after navigation with a proxy connection reset;
its failure screenshot showed the application alive on the response page.
DRI3 warnings are also present in passing runs, so no GPU cause is inferred.
One explicit failed-job rerun passed all DEB/RPM production and denial checks;
the failure and known transport limitation are retained, not hidden by automatic
retry. Browser/core source checks passed on the same c74f7786 head.

## First real device UI result and correction

Run42948857272 booted the emulator and passed bundled HTTPS/single CSS/art,
startup axe, real app_info/input rejection, stale/cancel/navigation checks before
failing the unchanged complete-focused-field assertion with IME visible. Actual
runtime: API36, x86_64, Android16, WebView/Chrome133.0.6943.137 (artifact13824108972).
Viewed its screenshot: keyboard top near physicaly1633 clips the lower input
border while the caret is still visible; innerHeight571 / width412 CSSpx.
This is a real geometry failure, not a backend capability failure.

Added an app-owner-scoped gloo resize listener in shared Leptos UI. It scrolls
only a clipped focused form control on viewport shrink; StoredValue ownership
detaches it on cleanup. No native injected-JS UI owner and no request-rule changes.
Native padding also includes observed Pixel7 display-cutout insets. Updated the
brief/architecture and added startup layout/capture and focused-bounds diagnostics.

New browser viewport-shrink regression failed against old production assets,
then passed with the corrected production root/subpath builds. Full browser suite
passed all56 palette/viewport audits plus interactions/assets/axe. CSR WASM
Clippy passed; strict offline AndroidTest compilation passed2s. Cargo locks are
unchanged: only declared web-sys features changed. Device correction pending CI.


## Production test body and instrumentation teardown

Run42951822691 passed current core/browser/Linux checks and booted Android.
Saved production screenshots/phase/axe/layout artifacts show the keyboard fix,
portrait/landscape cutout geometry, palette/Back and background recovery reached
CSP completion. Final axe violations=[] and final geometry had no overflow,
clipped text, escaped controls or overlaps. Viewed the corrected keyboard capture:
complete field and its actions are above the IME. The overall Android job still
failed: ActivityScenario.close in @After destroyed Tauri's final Activity, which
exited its process cleanly before JUnit reported (runner says Process crashed).
No production application-crash conclusion is inferred from that harness result.

Inspected actual AndroidX monitor1.8.0 bytecode: MonitoringInstrumentation.finish
calls its ActivityFinisher before reporting unless waitForActivitiesToComplete
is false. Pass that documented argument, retain @After evidence, and defer owned
package teardown to host ADB after results/collection. Do not alter Tauri's
production exit behavior. Host cleanup preserves an active failure and fails
a previously successful run if cleanup itself fails. Two meaningful regressions
reject a crashed report and cover cleanup error precedence; all22 Python tests
passed. Strict offline AndroidTest compilation passed1s. Device final result,
including the separate real denial APK, remains CI-pending.

## Completed device reports

Head63eb6f23 passed Android run42953564848, including normal JUnit result reporting
and the real restricted-window denial APK; all other source checks passed too.
No app assertion was replayed. Current production UI is verified on API36/x86_64;
ARM64 is build-only. Final source also synchronizes captures with WebView's
visual-state callback and two presentation frames: earlier rotation snapshots
were taken during compositor transition even though DOM geometry was settled.
The capture helper compiled with strict verified dependencies (1s); final
capture-synchronized CI remains pending. This changes test capture timing, not
application behavior or assertion criteria.
