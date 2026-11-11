---
id: O-0014
type: observation
status: local-checks-passed-ci-pending
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Dependency checks and setup reuse

## Executed

Inspected cargo-deny 0.20.2 and OSV-Scanner 2.7.1 official release assets and
SHA-256 files; downloaded binaries matched both upstream checksums. Both Cargo
workspaces pass advisories/bans/licenses/sources using the committed policy and
two explicit unmaintained-macro exceptions expiring 2027-02-09. An actual
MPL-only temporary crate is rejected by cargo-deny. Registry wildcard checks
initially rejected internal path dependencies; allowing path wildcards preserves
registry enforcement and the existing local-workspace architecture.

Initial OSV scans found vulnerabilities in AGP/lint/build dependency locks.
Settings-time rules now select patched Jackson, Guava, Netty, Bouncy Castle,
Commons Lang, HttpClient, jose4j, JDOM and stable Kotlin Gradle plugin versions.
Gradle `:app:dependencies :tauri-android:dependencies buildEnvironment
:buildSrc:dependencies --write-locks --write-verification-metadata sha256`
completed successfully. Local Java initially bypassed the inherited proxy and
failed with Network is unreachable; retry with JVM proxy properties and system
Java trust store succeeded (37s first update, 33s Kotlin follow-up).

The final OSV scan of four actual locks reported no vulnerabilities, inventoried
388 distinct dependency versions and marked four licenses UNKNOWN. Inventory is
not approval of unknown licenses. OSV's custom extractor prefix attempts failed;
byte-identical temporary files named gradle.lockfile are recognized and mapped
back to originals in reports. Tool-generated locks/verification data are committed.

25 Python tests pass, including warm/corrupt download recovery, rejected download
preservation and expiry rejection. Fresh/repeated actual security-tool setup
passes. The shared downloader removes repeat Tauri CLI and axe archive downloads
and is reused by Trunk/security setup. No CI speedup magnitude is yet claimed.

## Limits and next evidence

Android strict metadata/ABI/emulator integration with updated dependencies and
fresh security CI remain pending. Weekly GitHub scheduling is not yet active:
default branch is main; schedule/manual default-branch activation is tracked by
#24 and must not bypass the human main gate. Branch-protection detail API returned
403, so no new required-check/path-filter assumption was made.

## Relations and revisit

Implements [D-0010](../decisions/D-0010-permissive-rust-dependencies.md); see
[security contract](../../docs/security.md). Append exact source/run/timings and
strict Gradle outcomes before milestone closure. Exceptions require new review
before expiry, never automatic extension.

## Strict local Gradle validation

`recordResolvedPomChecksums --init-script scripts/record_gradle_metadata.init.gradle.kts
--write-verification-metadata sha256 --dependency-verification=off --no-configuration-cache`
recorded actual cached POM bytes through Gradle. Normal
`:app:assembleUniversalDebugAndroidTest -PabiList=x86_64 -PtargetList=x86_64
-ParchList=x86_64 -x :app:rustBuildX86_64Debug --dependency-verification=strict
--no-configuration-cache` then passed (40s; 77 tasks). This compiled instrumentation
and Android resources/code with Kotlin 2.4.21 and strict metadata; it deliberately
excluded the Rust build task and is not APK runtime/ABI evidence.

## HTML template preservation regression

Final backend inspection found rcdom's serializer ignored template_contents.
`cargo test --manifest-path apps/native/Cargo.toml -p native-html-tests --locked
--offline template_contents_survive_injection` first failed with the actual output
`<template></template>` instead of its paragraph/script fragment. A small fifth
upstream-source patch makes SerializableHandle traverse template fragment children
using the existing HTML5 serializer (no regex or application DOM mutation).
Cargo generated the native lockfile source change. All8 actual Wry-source tests,
12 Tauri HTML/CSP tests (including nested/inert templates) and the full native
cargo-deny gate now pass locally. Native integration CI must rerun. Archive/file
provenance and complete patch diffs are retained for the additional source.

The first diff check on the regenerated unified patch flagged its required blank
context line as trailing whitespace. `.gitattributes` now disables whitespace
warnings only for vendor/patches/*.patch; source checks remain unchanged and
patch bytes are preserved. `git diff --check` passes with that format-specific
attribute. The combined branch is rebased on reviewed native/capture develop
8b45f560, retaining both sides of the knowledge-index append conflict.
