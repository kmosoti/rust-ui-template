# Agent working agreement

Scope: the entire repository. Keep this document small and revise it through review as workflows mature.

## Before making a change

1. Inspect the actual branch, repository state, existing implementation, and relevant issue. Never infer that planned work exists.
2. Read [README.md](README.md), [architecture](docs/architecture.md), and [knowledge index](knowledge/README.md); follow relevant linked records before repeating research.
3. Identify the smallest coherent change and how it can be tested. Preserve unrelated edits.

## Architectural invariants

- v0.1 uses Leptos CSR/WASM, Tailwind 4, and Tauri 2; SSR/hydration is a separate follow-up profile (Issue #2).
- Leptos alone owns the UI/DOM. Tauri owns native packaging and permissions. Pure Rust core code must not depend on UI, browser, or OS frameworks.
- Keep platform capabilities behind explicit adapters. Never conflate a shared type with shared process state or authority.
- Do not add a tool, framework, or abstraction without showing which distinct concern it owns.

## Evidence and knowledge

- `docs/` contains stable, reader-facing instructions and architectural contracts.
- `knowledge/` contains dated, linked decisions, research, and observations. Distinguish observed facts from interpretations, unknowns, and hypotheses.
- Record significant discoveries with environment/date, reproduction or source, confidence, and links to related records. Capture competing explanations and what would disprove the leading one.
- Keep links in both directions where practical. Supersede old decisions explicitly; do not silently erase history or describe unexecuted checks as verified.

## Finish responsibly

- Prefer focused commits and reviewable PRs; do not rewrite shared history without explicit approval.
- Run relevant checks, record exactly what was run and what could not be run, and update affected docs and knowledge records.
- Never claim a platform is supported or code is formally verified without the corresponding reproducible evidence.

Contributor workflow: [CONTRIBUTING.md](CONTRIBUTING.md).
