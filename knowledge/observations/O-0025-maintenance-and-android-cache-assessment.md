---
id: O-0025
type: observation
status: preliminary
updated: 2026-11-14
added_by: agent
human_ratified: false
---

# Maintenance exceptions (#28) and Android cache seed assessment (#31)

## Observed — Issue #28 macro maintenance exceptions (`2026-11-14`)

Compact registry and locked reverse-dependency receipts are committed in [issue-28-macro-assessment.json](../evidence/O-0025/issue-28-macro-assessment.json). Upstream metadata was retrieved from `https://crates.io/api/v1/crates/<name>` and `/<version>/dependencies` between `2026-11-14T05:01:24.442344+00:00` and `2026-11-14T05:01:25.401045+00:00`. Local graph queries ran offline against committed lockfiles under `rustc 1.100.0 (0ef1bc386 2026-11-09)` / `cargo 1.100.0 (3acc79c0c 2026-11-05)`:

| Query (`cargo tree --manifest-path ... --locked --offline -i ...`) | Exit | Outcome |
| --- | ---: | --- |
| `Cargo.toml` `-i paste` | `0` | `paste v1.0.15` reachable via `either_of v0.1.9`, `leptos v0.8.23`, `reactive_graph v0.2.16`, `reactive_stores v0.4.4`, `tachys v0.2.19`, `leptos_dom v0.8.8`, `leptos_server v0.8.8` into `app-ui v0.1.0` and `client v0.1.0` |
| `Cargo.toml` `-i proc-macro-error` | `101` | Not present in root workspace graph |
| `apps/native/Cargo.toml` `-i proc-macro-error` | `0` | `proc-macro-error v1.0.4` reachable via `glib-macros v0.18.5` (`glib v0.18.5` and 11 GTK/WebKit/Soup crates) and `gtk3-macros v0.18.2` (`gtk v0.18.2`) into `muda v0.20.0`, `tao v0.37.2`, `tauri-runtime v2.12.2`, `tauri-runtime-wry v2.12.3`, `webkit2gtk v2.0.2`, `wry v0.57.2`, and `tauri v2.12.5` (`rust-ui-native v0.1.0`) |
| `apps/native/Cargo.toml` `-i paste` | `101` | Not present in native workspace graph |

- **`RUSTSEC-2024-0436` (`paste 1.0.15`):** `leptos 0.8.23`, `either_of 0.1.9`, `reactive_graph 0.2.16`, `reactive_stores 0.4.4`, and `tachys 0.2.19` remain the latest stable (`max_stable_version`) releases on crates.io (`0.9.0-rc1`, `0.3.0-rc1`, and `0.5.0-rc1` are prereleases). Each stable release still declares a non-optional `paste ^1.0` normal dependency; `paste 1.0.15` remains latest stable.
- **`RUSTSEC-2024-0370` (`proc-macro-error 1.0.4`):** `tauri 2.12.5` remains `max_stable_version` (`3.0.0-alpha.6` is prerelease) and declares a Linux/BSD normal dependency on `gtk ^0.18`. Although `gtk 0.19.0`, `gtk3-macros 0.19.0`, and `glib-macros 0.22.9` (`rust_version: 1.92`, edition `2024`) omit direct `proc-macro-error` dependencies, `gtk 0.19.0` requires `glib ^0.22` and `gtk3-macros ^0.19.0` and does not satisfy `tauri 2.12.5`'s `gtk ^0.18` constraint. `proc-macro-error2 2.0.1` is a distinct crate name and cannot replace `proc-macro-error` through lockfile regeneration.
- Both exceptions in [security-exceptions.json](../../security-exceptions.json) remain unchanged (`expires: 2027-02-09`, scheduled reassessment `2027-01-09` per [R-0008](../research/R-0008-maintenance-release-readiness.md)); no lockfile, vendor patch ([D-0010](../decisions/D-0010-permissive-rust-dependencies.md), [vendor ownership](../../vendor/README.md)), or workflow changed.

## Observed — Issue #31 Android `develop` cache seed and inventory (`5a2adc1`)

Normalized job, profile, and cache-API evidence is committed in [issue-31-android-cache-5a2adc1.json](../evidence/O-0025/issue-31-android-cache-5a2adc1.json). Data sources and exact queries:

- **Source & run:** `develop` commit `5a2adc1e2a87a287a80e4c5ef5df3a2623629fb5`, workflow run `43503141449` (attempt `1`), job `132153822813` (`android`, runner `GitHub Actions 1000004605`, image `ubuntu24` version `20261111.370.1`), `2026-11-13T20:36:40Z` created / `20:36:42Z` started / `20:45:50Z` completed (`548s` wall time, conclusion `success`).
- **Profile artifact:** `android-cache-profile` artifact ID `14074374557`, verified ZIP SHA-256 `b90719f276701d3e8bb32a013ee29184c8325ae65d8e0e3850f707c8d070ac21`. Both `restored` (`0.000303s` measurement) and `ready-to-save` (`1.650528s` measurement) phases record `cache_key: "android-partitions-v2"`, `cache_hit: "false"`, empty `cache_matched_key`, `synthetic_stale_probe: false`, `forced_cold: false`, and `0` errors across every bucket and child.
- **API queries:** `gh api repos/kmosoti/rust-ui-template/actions/runs/43503141449/jobs` (exit `0`, processed via `python3 scripts/ci_timings.py`) and `gh api repos/kmosoti/rust-ui-template/actions/caches?per_page=100` (exit `0`).

### Job timing breakdown vs. historical [O-0020](O-0020-android-cache-partition-trial.md) / [O-0021](O-0021-android-lifecycle-stall.md) series

| Observation | Run / attempt | Image / Rust | Cache state | Job | Restore (SDK/deps/targets) | SDK setup | ABI build | Emulator | Save (SDK/deps/targets) |
| --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| v1 warm median | PR #32 baseline | `20261101.360.1` / `1.99.1` | 3 warm exact hits | `384s` | `72s` total | `9–12s` | `69–86s` | `151–165s` | skipped |
| v2 `20261101.360.1` seed | `43069846343/1` | `20261101.360.1` / `1.99.1` | all-miss trusted seed | `742s` | misses | `91s` | `274s` | `150s` | `43/17/8s` (`68s`) |
| v2 corrected warm median | `43080751204/1–3` | `20261101.360.1` / `1.99.1` | 3 warm exact hits | `391s` | `82s` median (`93/82/65s`) | `9–14s` | `64–82s` | `137–161s` | skipped (PR) |
| v2 `20261111.370.1` seed | `43503141449/1` | `20261111.370.1` / `1.100.0` | all-miss trusted seed | `548s` | `1/0/0s` (`1s`) misses | `70s` | `182s` | `110s` | `48/12/6s` (`66s`) |

Additional timed steps on `43503141449`: `rustup` `1.100.0` `11s`, CI/frontend/native CLI tools `2s`, SDK licenses/JDK `10s`, `cargo fetch` `5s`, shared frontend assets `57s`, package-owned clean `1s`, AndroidX test compile `12s`, restricted fixture `6s`.

### Non-overlapping filesystem bytes vs. compressed archive bytes

| Partition | Ready-to-save apparent bytes (FS) | Ready-to-save allocated bytes (FS) | `20261111.370.1` compressed archive bytes (API) | `20261101.360.1` compressed archive bytes (API) |
| --- | ---: | ---: | ---: | ---: |
| `sdk` (`.tools/android-sdk`) | `8,713,047,443` | `8,806,326,272` | `3,269,377,488` (`10497106323`) | `3,267,755,610` (`10369184852`) |
| `dependencies` (6 buckets) | `1,851,800,513` | `1,965,297,664` | `684,898,837` (`10497123423`) | `683,180,406` (`10369204165`) |
| `targets` (`frontend` + `native`) | `2,118,874,305` | `2,140,856,320` | `481,497,958` (`10497127709`, `rust1.100.0`) | `543,907,393` (`10369212413`, `rust1.99.1`) |
| **Android v2 total** | **`12,683,722,261`** | **`12,912,480,256`** | **`4,435,774,283`** | **`4,494,843,409`** |

- Apparent filesystem totals (`12,683,722,261` bytes; SDK includes `system-images` `4,585,407,573` and `ndk` `2,494,931,177`) are uncompressed local tree metadata measurements, not compressed cache transfer or storage bytes. `restored.json` reported `0` apparent and `0` allocated bytes across all 9 buckets.
- `cache-inventory.json` lists `11` active caches under `refs/heads/develop` totaling `12,070,841,344` compressed bytes (`4,435,774,283` for `20261111.370.1`, `4,494,843,409` for `20261101.360.1`, plus `3,140,223,652` across `security-v1` and 4 `build-v1` browser/core/native entries).
- **Why `5a2adc1` missed all three partitions:** In [`.github/workflows/android.yml`](../../.github/workflows/android.yml), all three partition `key` and `restore-keys` prefixes include `${{ steps.image.outputs.version }}`. Advancing the hosted runner image from `ubuntu24-20261101.360.1` to `ubuntu24-20261111.370.1` prevented matching the prior image's keys, even though the `sdk` input hash (`9472db2b...`) and `dependencies` hash (`d20706e2...-c858fd60...`) were byte-identical across both images.
- **Same-image reuse before image rollover:** Prior `20261101.360.1` entries `10369184852` (`sdk`, `last_accessed_at: 2026-11-13T18:10:52.018888Z`) and `10369204165` (`dependencies`, `last_accessed_at: 2026-11-13T18:11:47.325439Z`) were accessed during [O-0024](O-0024-rust-1.100-upgrade.md) (PR #39 Rust `1.100.0` run `43480063814`), whereas the `rust1.99.1` target entry (`10369212413`) stayed untouched since `2026-11-11T23:57:47.072438Z`.

## Inferred

- **Issue #28 remains upstream-blocked on stable releases:** Neither `RUSTSEC-2024-0436` (`paste`) nor `RUSTSEC-2024-0370` (`proc-macro-error`) can be removed cleanly by lockfile updates or safe patches without migrating to prereleases or introducing new parent-crate forks. Both issues stay open without extending the `2027-02-09` expiry.
- **Run `43503141449` (`548s`) is an all-miss seed, not a warm regression:** It cannot be compared directly as a warm regression against `O-0020`'s `391s` warm median (`0` restored bytes + `66s` saves vs. warm restore), nor as a controlled cold speedup against `742s` (`43069846343`), because runner image (`20261111.370.1` vs. `20261101.360.1`), compiler (`Rust 1.100.0` vs. `1.99.1`), and source revision all differ.
- **Partition design vs. transfer latency:** `O-0020` established independent `sdk`/`dependencies` reuse across the `Rust 1.99.1 -> 1.100.0` toolchain change within the same runner image (`O-0024`), not faster archive transfer (`82s` median v2 restore vs. `72s` v1). Retaining `${{ steps.image.outputs.version }}` in `sdk` and `dependencies` keys caused `~3.95 GB` of compressed SDK/dependency state (`3,269,377,488 + 684,898,837` bytes) to be re-seeded once when `ubuntu24` rolled from `20261101.360.1` to `20261111.370.1`.

## Hypotheses

- Subsequent runs on `ubuntu24-20261111.370.1` with unchanged SDK/dependency/target prefixes will match the seeded entries (`10497106323`, `10497123423`, `10497127709`), eliminating the `70s` SDK download, most of the `182s` cold ABI compile, and the `66s` save tail while retaining ~`65–93s` restore transfer.
- Because `.tools/android-sdk` (`~3.27 GB` compressed) and `.tools/downloads` / Cargo registry / Gradle caches (`~685 MB` compressed) consist of SHA-256-verified downloads and platform-pinned artifacts rather than runner-image-linked native objects, scoping `sdk` keys by OS/arch and setup/asset hashes (without minor `ImageVersion` bumps) might prevent duplicate `~3.27 GB` SDK archives across runner image updates — untested and not authorized here without a controlled experiment and full `setup_android.py` + emulator verification.

## Unknowns and next smallest controlled step

- Warm exact-hit restore and whole-job timings on `ubuntu24-20261111.370.1` (`Rust 1.100.0`) remain unmeasured until a subsequent run hits `10497106323`/`10497123423`/`10497127709`.
- Whether holding `12.07 GB` across `11` active entries approaches repository cache eviction thresholds, and whether cross-`ImageVersion` `sdk` reuse on `ubuntu24` avoids host-library drift, remain unknown.
- **Next smallest step for #31:** Keep `.github/workflows/android.yml` and cache layout unchanged for now; inspect the next natural `ubuntu24-20261111.370.1` Android run's `android-cache-profile` artifact and step timings to establish a warm `Rust 1.100.0` baseline before designing any controlled PR experiment on `sdk` image-version scoping or transfer latency. Keep #28 and #31 open.

## Relations and revisit when

- *extends*: [R-0008 Macro maintenance readiness](../research/R-0008-maintenance-release-readiness.md)
- *preserves*: [D-0010 Permissive Rust dependencies](../decisions/D-0010-permissive-rust-dependencies.md), [vendor ownership](../../vendor/README.md), [security policy](../../docs/security.md)
- *extends*: [O-0018 Android cache decomposition](O-0018-android-cache-observation.md), [O-0020 Android cache partition trial](O-0020-android-cache-partition-trial.md), [O-0021 Android lifecycle stall](O-0021-android-lifecycle-stall.md), [O-0024 Rust 1.100.0 upgrade](O-0024-rust-1.100-upgrade.md), [CI documentation](../../docs/ci.md)
- *evidence*: [issue-28-macro-assessment.json](../evidence/O-0025/issue-28-macro-assessment.json), [issue-31-android-cache-5a2adc1.json](../evidence/O-0025/issue-31-android-cache-5a2adc1.json)

Revisit when: (1) stable `leptos` (`> 0.8.23`) or `tauri` (`> 2.12.5`) removes `paste`/`proc-macro-error` edges, on `2027-01-09` ahead of the `2027-02-09` expiry, or before a `main` release (#28); (2) warm `ubuntu24-20261111.370.1` Android timings or cache eviction telemetry arrive (#31).
