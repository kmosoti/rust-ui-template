# Validated toolchain set

Pins describe the configured CSR build; actual platform launches are listed in
[the evidence matrix](platforms.md). They are not support claims for other hosts.

| Concern | Pin / source |
| --- | --- |
| Rust / edition / resolver | 1.99.1 / 2024 / 3; rust-toolchain.toml, package rust-version 1.99 |
| Leptos | 0.8.23; root Cargo.lock |
| wasm-bindgen | 0.2.130; both Cargo locks, Trunk selects matching CLI |
| Trunk | 0.21.14; verified official binary via setup_ci_tools.py |
| Tailwind standalone | 4.3.4; platform asset SHA-256 manifest |
| Accessibility test asset | axe-core 4.10.3; SHA-512 integrity and archive SHA-256 |
| Tauri host / build / codegen / utilities | 2.12.5 / 2.7.4 / 2.7.4 / 2.10.2; native lock and reviewed parent patches |
| Wry | 0.57.2; reviewed permissive Android HTML patch |
| Tauri CLI / Linux driver | 2.12.4 / 2.1.0 |
| Android JDK | Temurin 21.0.13+9 |
| Gradle / Android Gradle plugin | 9.6.1 / 9.3.1 |
| Kotlin Gradle plugin | 2.4.21; security update with generated locks/checksums |
| Android SDK / build tools | 37 / 37.0.0; Tauri library SDK 36 |
| Android NDK | 29.0.14206865 |
| Android API contract | min 29, target 37; API 36 emulator exercised |
| Emulator | 37.2.13; API 36 Google APIs x86_64 revision 7 |
| Dependency checks | cargo-deny 0.20.2, OSV-Scanner 2.7.1; verified official assets |

Browsers/WebViews and Linux system libraries are supplied by the recorded runtime,
not Cargo locks. Tailwind's CSS floors are Chrome111/Safari16.4/Firefox128; those
are prerequisites, not tested application minimums. Chromium156, Linux WebKitGTK
and Android WebView133 evidence is scoped in the matrix. Python3 orchestrates
setup/tests; Node/npm is not required by the application build/test commands.
GitHub Actions' own pinned runtimes are separate from application tooling.

## Fresh Linux x86_64 browser checkout

Install Python3, Git, rustup and Chrome/Chromium, then clone the desired reviewed
revision and run from its root:

```sh
rustup toolchain install 1.99.1 --profile minimal --component rustfmt --component clippy --target wasm32-unknown-unknown
python3 scripts/setup_ci_tools.py
python3 scripts/setup_frontend.py
export PATH="$PWD/.tools:$PATH" NO_COLOR=false
cargo fetch --locked
cargo test --workspace --locked --offline
.tools/tailwindcss -i styles/input.css -o styles/generated.css --minify
python3 scripts/check_css.py
trunk build --release --locked
trunk build --release --locked --public-url /sub/ --dist dist/sub
cargo run -p browser-tests --locked --offline
```

Set CHROMIUM_PATH when the installed browser is not discoverable. Browser
sandboxing remains enabled. The [clean build gate](ci.md#clean-frontend-reproducibility-gate)
executes these build/test concerns from independent fresh clones, retaining
exact commands/timings/manifests. Native setup/build prerequisites remain in
[Linux packaging](linux-packages.md) and [Android](android.md); use their actual
installed-package/emulator checks before claiming native runtime support.

The optional [extraction toolchain](proof-feasibility.md) is isolated and does not
replace the shipping Rust pin. Update this set through reviewed compatible locks,
verified tools and actual CI evidence rather than floating versions.
