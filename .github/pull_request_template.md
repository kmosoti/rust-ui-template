## Summary
- **Motivation / Why:**
- **Changes / What:**
- **Linked Issue(s):** Refs #

## Stack Position
- [ ] Standalone PR targeting `main`
- [ ] Part of a stacked PR chain:
  - Base branch for this PR: `main` (or `stack/<topic>/...`)
  - Stack order:
    1. #... (`stack/<topic>/01-...`)
    2. **-> This PR** (`stack/<topic>/02-...`)

## Architectural & Boundary Check
- [ ] Single owner per concern preserved (`app-core` pure Rust, `app-ui` Leptos/Tailwind 4, explicit browser/Tauri adapters)
- [ ] Rendering profiles (`csr` / `hydrate` / `ssr`) and platform dependencies remain isolated

## Verification Evidence
- **Commands executed & results:**
  - `...`
- **Not run / untested platforms or environments:**
  - `...`

## Knowledge & Documentation
- **Knowledge records added/updated (`knowledge/`):** `none` (or list IDs with `added_by` and `human_ratified` status)
- **Stable docs updated (`docs/`):** `none` (or list files)

## Merge Readiness (`main` Protection)
- [ ] Branch is rebased onto its target base with a clean linear history (no merge commits)
- [ ] All review conversations are resolved
