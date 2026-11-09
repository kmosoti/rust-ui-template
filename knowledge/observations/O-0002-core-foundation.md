---
id: O-0002
type: observation
status: core-ci-passed
updated: 2026-11-09
added_by: agent
human_ratified: false
---

# O-0002: First core implementation and evidence boundary

## Context

Started Issue #1 from `develop` commit
`e959615423c7deaa0608fc3a51769b71239bc2b1`. Read the existing repository rules,
architecture, issue, and knowledge records. No open PR competed with this slice
at the time checked. All work remains on a feature branch targeting `develop`.

## Observed in the chat execution environment

- Python 3.13.5 and Git 2.47.3 were available. Rust/Cargo/rustup were not installed.
- Network DNS resolution prevented installing a compiler in this environment.
- `python3 -m unittest discover -s scripts -p 'test_*.py' -v`: 9 tests passed.
- `python3 -m compileall -q scripts`: passed.
- Python `tomllib` accepted the workspace, package, toolchain, and lockfile syntax.
- Arithmetic independently confirms the bounded traversal has 55,987 prefixes
  at depth 6 over six event choices. This is not evidence that Rust executed it.

## Not yet established by those local checks

Rust compilation/tests, formatting, Clippy, mutation rejection, and WASM
compilation require the attached CI or a coding agent with the pinned toolchain.
The lockfile is the minimal dependency-free manifest; Cargo must validate it.
No Leptos page, Tailwind asset, browser launch, Tauri host, mobile build, or Lean
proof is delivered or validated by this initial core slice.

## Revisit when

Append exact CI run/commit and results after actual execution. On a source change,
attach new evidence rather than assuming old checks cover the new program.
Do not interpret a green Python checker test as a successful Rust core build.

## Relations

- **tests**: [D-0002](../decisions/D-0002-latest-request-core.md)
- **continues**: [O-0001](O-0001-scaffold-snapshot.md)
- **next-validation**: [handoff](../../docs/issue-1-handoff.md)

## Subsequent CI observation: 2026-11-09 20:12 UTC

[Run 42690694066](https://github.com/kmosoti/rust-ui-template/actions/runs/42690694066)
completed successfully. Inspected both the job step results and decoded logs.
Source head: `30965001ff880dcb2d38708d8b26eaddb9dffa45`; base: `e959615423c7deaa0608fc3a51769b71239bc2b1`.
GitHub tested synthetic merge `37a9f728e616fda8788adcb452ab1f0a1abafcb8`; this was
not a merge into `develop` or `main`.

Environment: Ubuntu 24.04 hosted x86_64 runner, Rust 1.99.1 and Cargo 1.99.1.

- `cargo fmt --all -- --check`: passed.
- `cargo test --workspace --locked --offline`: 13 unit tests and 1 doc test passed.
  The bounded sequence test executed its 55,987-prefix assertion.
- `cargo clippy --workspace --all-targets --locked --offline -- -D warnings`: passed.
- `cargo check -p app-core --target wasm32-unknown-unknown --locked --offline`: passed.
  This is a core target-compilation check, not a WASM browser bundle or runtime test.
- Actual Cargo metadata boundary check and 9 Python checker tests: passed.
- Both deliberate mutants executed and failed the intended named Rust tests.
- Tracked and untracked source/lockfile drift checks: passed.

The runner warned that checkout v4 targets deprecated Node 20. The follow-up
pins the upstream v7.0.1 commit `3d3c42e5aac5ba805825da76410c181273ba90b1` after
checking its official release/tag and `action.yml` Node 24 metadata. Re-run CI
on that commit rather than assuming the workflow change is covered by run 1.

This extends the earlier local-only evidence; it does not establish browser,
Tauri/mobile, Lean, or general safety properties beyond the executed checks.
