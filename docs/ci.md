# CI runtime, cache boundaries and measurement

Contributors must continually inspect affected workflows for efficiency and
idempotency within their change scope. The [contributor rules](../CONTRIBUTING.md#ci-efficiency-and-idempotency-are-contributor-responsibilities)
make measurement, safe repeated setup, optional caches and retained verification
part of review, rather than a one-time optimization task.

The native baseline [run 42908982231](https://github.com/kmosoti/rust-ui-template/actions/runs/42908982231)
(job 130154305222) took 14m20s on Ubuntu 24.04:

| Step | Seconds |
| --- | ---: |
| Compile/install Trunk | 342 |
| Native production build | 191 |
| Frontend build | 85 |
| Native Clippy | 81 |
| OS prerequisites | 27 |
| Install tauri-driver | 22 |
| Ensure Rust/toolchain components | 11 |

The workflow now uses the official Trunk 0.21.14 binary verified by a committed
SHA-256, replacing source compilation. `scripts/setup_ci_tools.py` checks cached
archive bytes and re-extracts the binary on every use. A modified executable is
not accepted just because its filename/version metadata looks right.

## Cached state and invalidation

The local composite actions restore/cache Cargo registry/git data, compiled root
and isolated native targets, Trunk's tool cache and `.tools/`. Keys distinguish
OS, architecture, runner image, job profile, Rust version, both lockfiles, installer
scripts, tool manifest and native GTK/WebKit SDK versions. Missing image-version
metadata falls back to a run-specific key instead of sharing unknown images.
Compatible dependency caches can be restored across lock changes; Cargo still
resolves/builds with the committed locks and checks source/features normally.
Root/native project source is never supplied by the cache. Native packaging
cleans its own release package before rebuilding embedded production assets,
so a cached restricted fixture cannot substitute for the production package.

Only successful `push` jobs on `develop` save caches. PRs restore the permitted
base cache but do not publish trusted executable caches. GitHub's service-level
branch scoping complements the workflow guards. Do not switch these jobs to
pull_request_target or restore these build outputs into a privileged signing
workflow. No credentials or signing material belong in a cache.

Cache keys are immutable; a hit does not overwrite an existing entry. Source
changes rebuild through Cargo fingerprints, and misses use the same verification
pipeline. CI disables incremental compilation and dev/test debuginfo to reduce
cache size; local development profiles remain unchanged. Change the cache epoch
when cache layout/tool semantics require a clean reset. Monitor restore time,
cache size and eviction before adding more cached paths.

Fresh hosted runners still install OS libraries and ensure the pinned Rust
components. Restoring /usr or a package database is not supported. The measured
OS step was 27s; Trunk compilation was the dominant repeated installation.
The tauri-driver Cargo installation uses a cached dedicated install root and
skips recompilation when the pinned version is already installed.

## Measure cold and warm runs separately

Use the GitHub jobs API response after completion:

```sh
gh api repos/kmosoti/rust-ui-template/actions/runs/RUN_ID/jobs | python3 scripts/ci_timings.py
```

Record run/source, runner image/SDK, result, matched cache key and hit/miss, tool
setup time, build time, restore/save cost and job wall time. A first PR can miss
all trusted caches; the first successful develop push seeds them. A rerun of the
same develop source can then demonstrate warm reuse. Do not label a fast local
build or a cold prebuilt-tool run as a measured warm CI speedup. Results and
limitations are tracked in [O-0006](../knowledge/observations/O-0006-design-ci.md).

## Observed results (2026-11-10)

| Job | Prior baseline | New cold PR | Warm exact-hit rerun |
| --- | ---: | ---: | ---: |
| Browser | 8m51s | 2m15s | 44s |
| Core | Not compared | 3m28s | 26s |
| Linux native | 14m20s | 9m06s | 3m00s |

Warm runs used the same develop source after a successful push seeded each cache.
Times include cache transfer and all applicable checks. Native warm restore cost
20s for ~880 MiB; installed production/CSP and restricted-window denial tests
passed. These are single observed runs with runner variability, not guarantees.
Run/attempt links, image/SDK/key, seed costs and commands are in
[O-0006](../knowledge/observations/O-0006-design-ci.md).

## Human review

[Overall architecture](architecture.md) and the [change diagrams](design-ci-change.md)
show ownership and cache trust. All existing lock, format, lint, boundary,
mutation, browser, native permission/CSP and source-drift checks remain. Browser
CI also uploads `browser-ui-evidence` with screenshots and geometry JSON; native
CI retains its separate unsigned package/screenshot artifact. The template's
reviewers use standard/medium effort; max and ultra are prohibited for review.


## Linux and Android delivery profiles

Linux packaging now builds DEB/RPM once, preserves production copies/hashes, and
validates install/reinstall/metadata/launch/removal on Ubuntu 24.04 and Fedora 44.
Separate restricted fixtures must pass real denial without overwriting production
artifacts. Fedora runtime dependencies are installed in a digest-pinned container;
no system package-database snapshot is restored.

Android has an isolated cache profile for Cargo/Gradle dependencies, wrapper
archives, verified installed SDK/NDK/emulator trees and target builds. Keys include
runner/Rust/JDK, SDK manifest, Gradle scripts, generated locks and checksum metadata.
Normal builds verify dependencies strictly; the update-only metadata helper never
runs in CI. Mutable AVD/user homes, debug keys and SDK ZIP staging are excluded.
SDK ZIPs are discarded after verified installation, saving about 3.3 GB of staging
space before the VM starts. Each ABI's own native package is cleaned before
embedding current production frontend assets; dependency compilation stays cached.

The API 36 VM uses explicit SDK-user/emulator/AVD homes, an owned serial, fresh
fixture data, KVM and SwiftShader. Early process exit prints bounded diagnostics
and fails promptly. Assertions are never automatically replayed. Browser/native
checks, artifact hashes and source-drift checks remain required; unsigned/test-
signed build evidence is separate from production release signing.

Local repeated SDK-tree verification measured 6.09 s and 4.92 s without downloads;
these hot-filesystem samples are not CI warm-cache speedup measurements. Exact
runs, failures and pending measurements live in [O-0010](../knowledge/observations/O-0010-linux-packages.md)
and [O-0011](../knowledge/observations/O-0011-android-apks.md).
