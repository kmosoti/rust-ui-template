# Agent working agreement

Scope: the entire repository across all issues, milestones, and refactors. Keep this document small and revise it through review as workflows mature.

## Before making a change

1. Inspect the actual branch, repository state, existing implementation, and relevant issue or PR stack. Never infer that planned work exists.
2. Read [README.md](README.md), [architecture](docs/architecture.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [knowledge index](knowledge/README.md); follow relevant linked records before repeating research.
3. Identify the smallest coherent change (or stacked PR slice) and how it can be tested. Preserve unrelated edits.

## Architectural invariants

- Leptos alone owns the UI/DOM. Tailwind 4 owns styling. Tauri 2 owns native packaging and permissions. Pure Rust core code (`app-core`) must not depend on UI, browser, or OS frameworks.
- Rendering modes (`csr`, `hydrate`, `ssr`) are explicit compile/deployment profiles, not runtime mixins; validate them in separate target builds rather than `cargo --all-features`.
- Keep platform capabilities behind explicit adapters. Never conflate a shared type with shared process state or authority.
- Do not add a tool, framework, or abstraction without showing which distinct concern it owns.

## Evidence, provenance, and human ratification

- `docs/` contains stable, reader-facing instructions and architectural contracts.
- `knowledge/` contains dated, linked decisions (`D-`), research (`R-`), and observations (`O-`). Distinguish observed facts from interpretations, unknowns, and hypotheses.
- Every `knowledge/` record includes `added_by` (`agent` | `human` | `mixed`) and `human_ratified` (`true` | `false`, plus `ratified_by` and `ratified_on` when `true`).
- **Never block agentic work on ratification:** create and use agent-authored records immediately with `added_by: agent` and `human_ratified: false`. Only set `human_ratified: true` when a human user explicitly ratifies the artifact. Do not silently overturn a `human_ratified: true` decision (`D-`) without explicit human approval.
- Keep links in both directions where practical. Supersede old decisions explicitly; do not silently erase history or describe unexecuted checks as verified.

## Finish responsibly

- Follow the commit template ([`.gitmessage`](.gitmessage)), PR template ([`.github/pull_request_template.md`](.github/pull_request_template.md)), and stacked PR workflow in [CONTRIBUTING.md](CONTRIBUTING.md).
- `main` requires rebased PRs (linear history, no merge commits) with all review conversations resolved.
- Run relevant checks, record exactly what was run and what could not be run, and update affected docs and knowledge records.
- Never claim a platform is supported or code is formally verified without the corresponding reproducible evidence.
