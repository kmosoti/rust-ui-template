# Source-linked core extraction assessment

The assessed invariant is: for `LatestRequest<u32>`, completing a request whose ID
is not active returns `Ignored` and leaves `last_issued`, `active` and `value`
unchanged. This covers stale, duplicate and cancelled responses. Arbitrary payload
destructor effects, UI task cancellation, DOM behavior and native IPC are outside
that theorem candidate. Existing Rust bounded-sequence/mutation tests exercise
its behavior; they are not a Lean proof.

## Executed pilot

The actual generic `app-core` source extracted successfully with Charon's Aeneas
preset. The JSON reports `has_errors: false` and contains a structured body for
`app_core::{LatestRequest<T>}::complete` (declaration 41). No handwritten reducer
was substituted and the shipping Rust toolchain/manifests were not downgraded.

| Component | Pinned assessment input |
| --- | --- |
| Shipping compiler (at pilot; current shipping pin 1.100.0) | Rust 1.99.1 |
| Aeneas source inspected | `0d21a9ec7bbbb110110cacc14464a47fd71c8705` |
| Charon required by that Aeneas `charon-pin` | `454586e9b770231e66d2062993e632dfc06463e2` |
| Charon compiler | `nightly-2026-09-17`, rustc 1.100.0-nightly |
| Lean required by that Aeneas source | `leanprover/lean4:v4.36.0-rc2` |

The normal distributed sysroot was selected explicitly. Its external library
bodies and Charon's conditional drop/unwind semantics need auditing before any
implementation-linked theorem. Successful JSON extraction alone does not prove
that Aeneas accepts every operation or that a theorem follows.

## Reproduce the assessment

Use a separate tool checkout; keep the application's `rust-toolchain.toml` intact.
The example uses an absolute `CHARON_ROOT` of your choice:

```sh
git clone https://github.com/AeneasVerif/charon.git "$CHARON_ROOT"
git -C "$CHARON_ROOT" checkout 454586e9b770231e66d2062993e632dfc06463e2
git -C "$CHARON_ROOT" submodule update --init --depth 1 crates/minirust
rustup toolchain install nightly-2026-09-17 --profile minimal
rustup component add --toolchain nightly-2026-09-17 rustc-dev rust-src llvm-tools
CARGO_BUILD_JOBS=2 CARGO_PROFILE_DEV_DEBUG=0 cargo +nightly-2026-09-17 build \
  --manifest-path "$CHARON_ROOT/charon/Cargo.toml" --locked --bin charon --bin charon-driver
mkdir -p artifacts/extraction
"$CHARON_ROOT/charon/target/debug/charon" cargo --preset aeneas --sysroot default \
  --dest-file "$PWD/artifacts/extraction/app-core.llbc" \
  -- --manifest-path "$PWD/Cargo.toml" -p app-core --lib --locked --offline
"$CHARON_ROOT/charon/target/debug/charon" pretty-print artifacts/extraction/app-core.llbc
```

Inspect `has_errors`, the actual `complete` body, source spans and source hashes,
not merely process exit status. Full commands/results and hashes are retained in
[O-0016](../knowledge/observations/O-0016-core-extraction.md).

## Remaining proof work

A future proof must audit the analysis compiler/standard-library assumptions for
the shipping compiler rather than treating source extraction as a binary proof.
OCaml/Dune, Aeneas translation, Lean/Lake and theorem/axiom auditing were not run
in this pilot. They are tracked in [#27](https://github.com/kmosoti/rust-ui-template/issues/27),
with the exact compatible tool pins. Do not call the Rust implementation formally
verified until extracted definitions are regenerated, the theorem is checked by
Lake, assumptions/no-sorry are audited and the freshness mutant breaks the linked
proof. This optional proof continuation does not block the scoped CSR milestone.
