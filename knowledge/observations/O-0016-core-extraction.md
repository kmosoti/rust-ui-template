---
id: O-0016
type: observation
status: extraction-assessed-no-proof
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Actual core extraction feasibility

## Observed inputs

`app-core/src/lib.rs` SHA-256:
`032ed5f1d04133b99c8ba152d0d178f64e11f3fb4bcb5694d4ec364c563f90bd`.
Root Cargo.lock SHA-256:
`f15f64c26bd5da994f186b3d0dc63c08f587c0d43b2067163f85633fdb0d0686`.
The core was not edited. Shipping Rust stays 1.99.1.

Inspected Charon main at bfb01963317890c3fbf4e5b5280110a827f3fc80 and Aeneas
0d21a9ec7bbbb110110cacc14464a47fd71c8705. Aeneas's actual charon-pin requires
454586e9b770231e66d2062993e632dfc06463e2, so the final pilot rebuilt and used that
compatible Charon source, rather than assuming latest versions interoperate.
Its compiler pin is nightly-2026-09-17; actual rustc is 1.100.0-nightly
(923c95cdf 2026-09-16). Its Lean backend pins leanprover/lean4:v4.36.0-rc2.

## Executed commands and results

- `cargo +1.99.1 check --manifest-path /workspace/scratch/charon/charon/Cargo.toml --locked --bin charon-driver`: failed E0554 in libspecr (nightly feature on stable). This is an analysis-tool requirement, not an application failure.
- Installed the separate nightly minimal toolchain and rustc-dev/rust-src/llvm-tools components. No application toolchain file changed.
- Initial nightly build found an uninitialized miniutil/minirust submodule. `git submodule update --init --depth 1 crates/minirust` resolved the pinned source, followed by successful debug Charon/driver builds (58.45s initial, 22.86s after selecting the Aeneas-compatible commit).
- `charon cargo --sysroot default --dest-file /workspace/scratch/app-core.llbc -- --manifest-path /workspace/rust-ui-finish/Cargo.toml -p app-core --lib --locked --offline`: passed.
- Final compatible `charon cargo --preset aeneas --sysroot default --dest-file /workspace/scratch/app-core-paired.llbc -- --manifest-path /workspace/rust-ui-finish/Cargo.toml -p app-core --lib --locked --offline`: passed (0.75s). Parsed JSON has_errors=false and declaration41 is the real local complete function with a nonempty Structured body/source span.
- `charon pretty-print /workspace/scratch/app-core-paired.llbc`: passed. Inspected active-ID comparison, unchanged stale branch and active/value writes on the accepted branch.
- Final artifact SHA-256: `ec42cea72a299cfd081765077d66fadc45c048f732537c060296e59dae13ef5d`. This identifies the local snapshot including environment paths, not a portable artifact-byte reproducibility claim. The artifact is not a checked Lean theorem.
- `command -v opam dune ocaml lake lean`: none installed. Inspected pinned Aeneas README/charon-pin/Lean toolchain requirements; Aeneas/Lean were not built or executed.

## Invariant and interpretation

For LatestRequest<u32>, a completion with a nonactive ID returns Ignored and
preserves last_issued, active and value. General payload destructor side effects
are excluded. Source extraction is feasible for the generic transition with this
Charon preset; end-to-end Aeneas acceptance, library/drop/unwind assumptions and
Lean proof remain unknown. The distributed sysroot leaves some external library
bodies opaque. No axiom audit or proof-sensitivity test was run or claimed.

## Relations and revisit

Supports assessment of [D-0002](../decisions/D-0002-latest-request-core.md).
[Reproduction guide](../../docs/proof-feasibility.md); implementation-linked proof
continuation is #27. Reassess on source/toolchain changes. Do not replace a real
extraction with an unrelated handwritten theorem or claim general verification.

After retaining source/artifact hashes and the reproduction guide, the local
external Charon build cache was cleaned to recover2.2GiB on the32GiB executor.
This changes no repository source, lock or evidence artifact; optional tool source
and recorded pins remain available for reproduction. No missing-tool limitation
was used to claim that Rust extraction itself is unsupported.
