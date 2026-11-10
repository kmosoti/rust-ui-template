## Summary
- **Motivation / Why:**
- **Changes / What:**
- **Linked Issue(s):** Refs #

## Stack Position & Target Branch
- [ ] Standalone PR targeting `develop` (agentic / day-to-day integration)
- [ ] Part of a stacked PR chain targeting `develop`:
  - Base branch for this PR: `develop` (or `stack/<topic>/...`)
  - Stack order:
    1. #... (`stack/<topic>/01-...`)
    2. **-> This PR** (`stack/<topic>/02-...`)
- [ ] Release promotion PR (`develop` -> `main`, **human review & merge required**)

## Architectural & Boundary Check
- [ ] Single owner per concern preserved (`app-core` pure Rust, `app-ui` Leptos/Tailwind 4, explicit browser/Tauri adapters)
- [ ] Rendering profiles (`csr` / `hydrate` / `ssr`) and platform dependencies remain isolated

## Architecture for Human Review
- **Overall architecture:** [docs/architecture.md](docs/architecture.md)
- **Change diagram:** include a focused Mermaid diagram for changed architecture, data flow, IPC, build or CI; for prose-only changes explain why no update is needed.
- **Ownership/trust boundaries and impact:**

## Verification Evidence
- **Commands executed & results:**
  - `...`
- **Not run / untested platforms or environments:**
  - `...`

## Knowledge & Documentation
- **Knowledge records added/updated (`knowledge/`):** `none` (or list IDs with `added_by` and `human_ratified` status)
- **Stable docs updated (`docs/`):** `none` (or list files)

## Merge Readiness & Review Gate (`develop` vs `main`)
- **Authoring agent / model:** `...`
- **Reviewer & merger agent / model (for `develop`):** `...` (prefer alternative model family; fallback: fresh independent standard/medium reviewer)
- [ ] For PRs targeting `develop`: reviewed by an alternative model family (or fresh independent standard/medium reviewer) and ready for the reviewing agent to rebase-merge bottom-up into `develop`
- [ ] For PRs targeting `main`: **`main-human-approval` (`main-release` environment gate) approved and merged by a human user** (agents must never merge into `main` or approve the `main-release` gate)
- [ ] Reviewer used standard/medium reasoning; max/ultra were not used
- [ ] Branch is rebased onto its target base with a clean linear history (no merge commits)
- [ ] All review conversations are resolved
