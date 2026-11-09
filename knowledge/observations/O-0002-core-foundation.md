---
id: O-0002
type: observation
status: local-checks-only
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
