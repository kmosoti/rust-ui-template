# Contributing to `rust-ui-template`

This repository is an iterative, evidence-driven Rust UI template (`Leptos` + `WASM` + `Tailwind CSS 4` + `Tauri 2` + pure Rust `app-core`). Every change—across any milestone, feature, refactor, or bugfix—follows the same repeatable development loop.

---

## 1. The Iterative Development Loop

Use this loop for every unit of work, regardless of which issue or release phase is active:

1. **Orient from actual repository state**
   - Read [`README.md`](README.md), [`docs/architecture.md`](docs/architecture.md), [`AGENTS.md`](AGENTS.md), and [`knowledge/README.md`](knowledge/README.md).
   - Inspect the current working tree, open GitHub Issues, and existing PRs. Never assume a planned crate, deployment profile, or platform target already exists until verified in the tree.
2. **Slice into a focused branch or stacked PR chain**
   - Keep each PR small, coherent, and independently testable.
   - When a task spans multiple layers (for example, `app-core` state transitions -> `app-ui` components -> client/Tauri adapter -> integration tests), use **stacked PRs** (see [Section 2](#2-stacked-pr-workflow)).
3. **Implement within architectural boundaries**
   - **Pure core (`app-core`):** domain state and transitions only; zero UI, browser (`web-sys`), or host (`tauri`) dependencies.
   - **Shared UI (`app-ui`):** Leptos components and Tailwind 4 utility classes; single owner of DOM updates.
   - **Profile & platform adapters (`client`, `apps/native`, optional web server profile):** explicit compilation profiles (`csr`, `hydrate`, `ssr`) and capability-scoped IPC adapters with browser fallbacks.
   - Pin toolchains and lockfiles; do not introduce overlapping frameworks.
4. **Verify by touched layer**
   - Run formatting, Clippy, unit/property tests, and target builds for every touched crate/profile.
   - Validate mutually exclusive rendering profiles (`csr`, `hydrate`, `ssr`) in **separate** Cargo invocations—never rely on `cargo --all-features` when features are mutually exclusive.
   - Record exact commands and outcomes. State explicitly which target platforms or WebViews were not exercised.
5. **Update `knowledge/` and `docs/`**
   - Record new decisions (`D-`), research (`R-`), and dated empirical observations (`O-`) in [`knowledge/`](knowledge/README.md) with provenance (`added_by: agent | human | mixed`) and ratification state (`human_ratified: true | false`).
   - **Do not block agentic work on human ratification:** agents record `added_by: agent` and `human_ratified: false` and continue immediately (see [Section 5](#5-knowledge-base-and-ratification-contract)).
   - Update [`docs/`](docs/architecture.md) only when stable architectural contracts, boundaries, or developer workflows change.
6. **Rebase, resolve conversations, and land**
   - `main` is protected: every change lands through a **rebased PR** (linear history, no merge commits) with **all review conversations resolved**.

---

## 2. Stacked PR Workflow

Use stacked PRs whenever a feature or milestone is too large for a single small diff or naturally decomposes into sequential layers.

### Branch topology and naming

Name branches with an explicit stack prefix and ordinal so review order is obvious:

```text
main
 └── stack/<topic>/01-core
      └── stack/<topic>/02-ui
           └── stack/<topic>/03-adapter
```

Single-PR changes use `<type>/<topic>` (for example `feat/core-reducer`, `fix/tailwind-source-scan`, `docs/workflow-guides`).

### Creating a stack

1. Start the base layer from an up-to-date `main`:
   ```bash
   git switch main && git pull --ff-only
   git switch -c stack/<topic>/01-core
   # commit and verify layer 1
   git push -u origin stack/<topic>/01-core
   ```
2. Branch the next layer directly off the previous layer:
   ```bash
   git switch -c stack/<topic>/02-ui
   # commit and verify layer 2
   git push -u origin stack/<topic>/02-ui
   ```
3. Open each PR against its **immediate parent branch** so GitHub shows only that layer's diff:
   - PR 1: `base: main` <- `compare: stack/<topic>/01-core`
   - PR 2: `base: stack/<topic>/01-core` <- `compare: stack/<topic>/02-ui`
   - PR 3: `base: stack/<topic>/02-ui` <- `compare: stack/<topic>/03-adapter`
4. Fill in the **Stack position** section in every PR description so reviewers can navigate the chain.

### Updating a stack after review feedback or `main` updates

Use `git rebase --update-refs` (Git 2.38+) from the top branch of the stack so all intermediate branch pointers update in a single rebase:

```bash
git fetch origin
git switch stack/<topic>/03-adapter
git rebase --update-refs origin/main
```

If you amend or add a commit inside `stack/<topic>/01-core`, switch to the top branch (`stack/<topic>/03-adapter`) and run:

```bash
git rebase --update-refs stack/<topic>/01-core
```

After verifying each layer still builds and passes tests, push updated branches safely:

```bash
git push --force-with-lease origin \
  stack/<topic>/01-core \
  stack/<topic>/02-ui \
  stack/<topic>/03-adapter
```

### Landing a stack into `main`

Always land from the **bottom of the stack upward**:

1. Ensure PR 1 (`base: main`) is rebased onto `origin/main`, passes checks, and has **all review conversations resolved**.
2. Merge PR 1 into `main` using **Rebase and merge** (`gh pr merge <pr-1> --rebase --delete-branch`).
3. Retarget PR 2 to `main`, rebase the remaining stack onto `origin/main`, and push:
   ```bash
   gh pr edit <pr-2> --base main
   git fetch origin
   git switch stack/<topic>/03-adapter
   git rebase --update-refs origin/main
   git push --force-with-lease origin stack/<topic>/02-ui stack/<topic>/03-adapter
   ```
4. Repeat until every layer in the stack is merged.

---

## 3. Commit Message Convention and Template

Enable the repository commit template locally once per clone:

```bash
git config commit.template .gitmessage
```

### Format ([`.gitmessage`](.gitmessage))

```text
<type>(<scope>): <imperative summary under 72 chars>

Why:
- <problem, constraint, or goal driving this change>

What:
- <focused summary of code, config, or documentation changes>

Verification:
- Ran: <exact commands and results>
- Untested: <platforms, WebViews, or checks not run in this environment>

Refs: #<issue-or-pr>
Knowledge: <D-xxxx / R-xxxx / O-xxxx or none>
```

- **Allowed `<type>` values:** `feat`, `fix`, `refactor`, `test`, `docs`, `build`, `ci`, `proof`, `chore`.
- **Typical `<scope>` values:** `core`, `ui`, `client`, `native`, `ssr`, `styles`, `proofs`, `knowledge`, `repo`.
- Keep commits atomic: a rebased PR merges commits onto `main` without squashing by default, so every commit in a PR should build cleanly and carry an accurate message.

---

## 4. Pull Request Template and `main` Branch Protection

GitHub automatically loads [`.github/pull_request_template.md`](.github/pull_request_template.md) on new PRs:

```markdown
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
```

### Protected `main` rules

`main` enforces:
- Changes must merge via a Pull Request (no direct pushes or force-pushes to `main`).
- **Linear history required:** merge commits are disabled; PRs must be rebased and merged via **Rebase and merge**.
- **Conversation resolution required:** every review thread must be resolved before a PR can merge.

---

## 5. Knowledge Base and Ratification Contract

Each non-index record in [`knowledge/decisions/`](knowledge/decisions/D-0001-csr-first.md), [`knowledge/research/`](knowledge/research/R-0001-cross-platform-evidence.md), or [`knowledge/observations/`](knowledge/observations/O-0001-scaffold-snapshot.md) includes:

- Stable ID and filename (`D-0001`, `R-0001`, `O-0001`) plus YAML front matter:
  - `id`, `type`, `status`, `updated` (`YYYY-MM-DD`)
  - `added_by`: `agent` | `human` | `mixed`
  - `human_ratified`: `true` | `false` (plus `ratified_by` and `ratified_on` when `true`)
- Explicit separation of **Observed** facts, **Inferred** conclusions, **Hypotheses**, and **Unknowns**.
- Typed relative Markdown links (*informed-by*, *challenges*, *observed-in*, *supersedes*) and a **Revisit when** condition.

### Keeping agentic work fast

- Agents **never wait** for human ratification to write or use `knowledge/` records; they set `added_by: agent` and `human_ratified: false` and proceed.
- Humans ratify records asynchronously when reviewing or directing work by setting `human_ratified: true` (with `ratified_by` and `ratified_on`).
- Agents may freely update or supersede `human_ratified: false` records as new evidence arrives, and may record challenging observations (`O-`) or research (`R-`) against any record, but must not silently overturn a `human_ratified: true` decision (`D-`) without explicit human approval.

---

## 6. Quality and Licensing Standard

Tests must exercise the behavior claimed. A Lean theorem about an abstract model does not verify the Rust implementation unless source extraction and assumptions are audited; a cross-compile is not a platform launch test.

All contributions are distributed under the [MIT License](LICENSE).
