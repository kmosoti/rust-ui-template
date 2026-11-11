# Reviewed permissive dependency patches

The application keeps Tauri 2. Published support crates currently pull MPL-only
Rust libraries through HTML selection and directory lookup. These sources retain
their upstream MIT/Apache licenses and notices. No MPL implementation is vendored
or relabeled. `upstream.json` records original crate archive checksums and file
hashes; `patches/` contains the complete text changes against those sources.

- tauri-utils 2.10.2: replace dom_query/kuchikiki with html5ever +
  markup5ever_rcdom; traverse actual parsed nodes for nonce/CSP operations.
- tauri-codegen 2.7.4: consume explicit script contents from that backend.
- dirs-sys 0.5.0: compare the optional directory key with standard Rust.
- wry 0.57.2: use HTML5 parsing/serialization for Android initialization injection.

The legacy internal tauri-utils html entry names remain, but its old kuchiki
NodeRef representation is replaced by Document. Only the configured CSR host and
explicit HTML/isolation regression tests are validated; these are application
patches, not drop-in compatibility guarantees for arbitrary third-party users.
The rcdom crate describes itself as an unsupported basic DOM; we own integration,
regression tests and upgrades. It does not own the application's live DOM.

## Upgrade and removal

The repository maintainers own these patches. For each Tauri/Wry update, review
upstream HTML/CSP changes, regenerate archive/file provenance and diffs, regenerate
Cargo.lock using Cargo, and run HTML tests plus browser/Linux/Android production
and denial suites. Prefer an upstream release with a permissive dependency graph
when it provides equivalent behavior. Do not silently update vendored code or
carry patches without reviewing their security effect.

Run the actual patched tests without Linux GTK headers:

```sh
cargo test --manifest-path apps/native/Cargo.toml -p tauri-utils --features html-manipulation,html-manipulation-2,isolation --locked --lib html
cargo test --manifest-path apps/native/Cargo.toml -p native-html-tests -p dirs-sys --locked
```

The Wry test crate compiles the actual patched Android injection source; it is not
a separately rewritten algorithm. Runtime native integration still requires CI.
