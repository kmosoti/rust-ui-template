# Contributing to `rust-ui-template`

This repository is an iterative, evidence-driven Rust UI template (`Leptos` + `WASM` + `Tailwind CSS 4` + `Tauri 2` + pure Rust `app-core`). Every change—across any milestone, feature, refactor, or bugfix—follows the same repeatable development loop.

---

## 1. The Iterative Development Loop

Use this loop for every unit of work, regardless of which issue or release phase is active:

1. **Orient from actual repository state**
   - Read [`README.md`](README.md), [`docs/architecture.md`](docs/architecture.md), [`AGENTS.md`](AGENTS.md), and [`knowledge/README.md`](knowledge/README.md).
   - Inspect the current working tree, open GitHub Issues, and existing PRs. Never assume a planned crate, deployment profile, or platform target already exists until verified in the tree.
2. **Slice into a focused change or stacked PR chain (`jj` preferred)**
   - Keep each PR small, coherent, and independently testable.
   - **Jujutsu (`jj`) in colocated mode (`jj git init --colocate`) is the preferred development method.** `jj` treats changes as first-class objects and automatically rebases descendant commits whenever an earlier layer in a stack is edited. Standard `git` (`git rebase --update-refs`) remains fully supported as a fallback.
   - When a task spans multiple layers (for example, `app-core` state transitions -> `app-ui` components -> client/Tauri adapter -> integration tests), use **stacked PRs** (see [Section 2](#2-preferred-vcs-jujutsu-jj-and-stacked-pr-workflow)).
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
6. **Independent cross-model review, rebase, and land into `develop` (plus human-gated promotion to `main`)**
   - **Autonomous agent landing on `develop`:** Hand off the PR or stacked PR chain to an **independent reviewing agent** from an **alternative model family** (or a fresh independent agent at standard/medium reasoning if no cross-family model is available). The reviewing agent audits the stack, resolves review conversations, and owns merging the stack bottom-up into `develop` via **Rebase and merge** (linear history, no merge commits).
   - **Human-gated releases into `main`:** Merges from `develop -> main` require **human review and manual approval** of the `main-release` GitHub Environment gate ([`.github/workflows/main-human-gate.yml`](.github/workflows/main-human-gate.yml)). Agents may open a `develop -> main` release PR, but must never approve the `main-release` deployment gate or merge into `main`.

---

## CI efficiency and idempotency are contributor responsibilities

For every change, inspect affected CI and setup steps for practical efficiency
and idempotency improvements. Fix relevant waste within the change's scope;
record larger opportunities for follow-up rather than mixing in a broad rewrite.
Use [docs/ci.md](docs/ci.md) for existing cache boundaries and measured baselines.

- **Measure first:** identify repeated installs/builds and the critical path from
  job/step timings. Compare cold, seed and warm runs with source, runner, cache
  state and transfer costs; label estimates and single-run limitations.
- **Make reruns safe:** setup/build steps must converge on the same intended
  versions/output when repeated. Verify cached assets and pinned hashes, replace
  partial/corrupt downloads, and rebuild generated/embedded assets from current
  inputs. Idempotency does not mean identical timestamps or skip-all-on-hit.
- **Treat caches as optional:** cold misses, stale dependency restores and warm
  hits must all remain correct. Key compatibility by platform/toolchain/locks/SDK
  as appropriate; use the existing trusted-save policy and least permissions.
  No secrets, system-directory snapshots or PR-to-release executable trust.
- **Reuse verified work:** prefer pinned verified binaries over recompiling tools,
  compatible dependency caches, shared setup actions, appropriate concurrency and
  cancellation of superseded PR runs. Avoid redundant network/download/build
  steps; test artifact handoffs if introducing them.
- **Preserve verification:** never buy speed by weakening tests, dropping security
  checks, using floating versions, hiding failures, or skipping required checks
  through unsafe path filters. Validate both fresh setup and repeated setup when
  changing installers/workflows; exercise cache-miss and warm paths as relevant.
- **Report the tradeoff:** PRs touching CI/setup/build tooling state executed
  fresh/repeated-run evidence, retained coverage, cache trust/invalidation and
  measured runtime/resource effects (or explicitly unmeasured effects). Prefer a
  small justified improvement over speculative cache complexity.

The reviewer checks these points at standard/medium effort, never max/ultra.

---

## 2. Preferred VCS (`jj`), Branch Topology (`develop` vs `main`), and Stacked PRs

### Why Jujutsu (`jj`) is the preferred development method

Colocated **Jujutsu (`jj`)** (`jj git init --colocate`) is the recommended local workflow for both humans and coding agents:

1. **Zero-friction stacked PRs:** Editing an earlier commit (`jj edit <change-id>` or `jj squash --into <change-id>`) **automatically rebases every descendant commit** in the stack. No manual `git rebase --update-refs` choreography is needed after review fixes.
2. **Working-copy-as-a-commit:** There is no separate staging area or dirty-tree stash juggling when switching between stack layers.
3. **First-class conflicts and operation log:** Conflicts can be committed and resolved layer by layer, and any mistake can be undone instantaneously with `jj undo` / `jj op restore`.
4. **Full Git & GitHub interoperability:** Colocated mode shares the `.git` repository in place—`gh`, Cargo, IDE integrations, and GitHub's rebase-only linear-history branch protection work unchanged, with `jj` bookmarks mapping 1:1 to Git branches and `jj git push` enforcing `--force-with-lease`-equivalent safety checks automatically.

Initialize `jj` once in an existing Git clone:

```bash
jj git init --colocate
jj bookmark track develop@origin main@origin
```

*(Note: `.jj/` is local to your clone and ignored by Git automatically.)*

### Two-branch topology (`develop` for agents, `main` for human-gated releases)

Day-to-day feature work and stacked PRs branch from and land into **`develop`**. **`main`** is the human-gated release branch promoted from `develop`:

```text
main (human-gated release branch; requires main-release environment approval)
 └── develop (autonomous agent integration branch; linear history + cross-model review)
      └── stack/<topic>/01-core
           └── stack/<topic>/02-ui
                └── stack/<topic>/03-adapter
```

Single-PR changes targeting `develop` use `<type>/<topic>` (for example `feat/core-reducer`, `fix/tailwind-source-scan`, `docs/workflow-guides`).

### Creating a stack on `develop` (`jj` preferred)

1. Fetch and start the first layer on top of `develop@origin`:
   ```bash
   jj git fetch
   jj new develop@origin -m "feat(core): ..."
   # implement and verify layer 1
   jj bookmark create stack/<topic>/01-core -r @
   ```
2. Stack subsequent layers directly on top:
   ```bash
   jj new -m "feat(ui): ..."
   # implement and verify layer 2
   jj bookmark create stack/<topic>/02-ui -r @

   jj new -m "feat(client): ..."
   # implement and verify layer 3
   jj bookmark create stack/<topic>/03-adapter -r @
   ```
3. Push all stack bookmarks to `origin`:
   ```bash
   jj git push \
     --bookmark stack/<topic>/01-core \
     --bookmark stack/<topic>/02-ui \
     --bookmark stack/<topic>/03-adapter
   ```
4. Open each PR against its **immediate parent branch** so GitHub shows only that layer's diff:
   - PR 1: `base: develop` <- `compare: stack/<topic>/01-core`
   - PR 2: `base: stack/<topic>/01-core` <- `compare: stack/<topic>/02-ui`
   - PR 3: `base: stack/<topic>/02-ui` <- `compare: stack/<topic>/03-adapter`
5. Fill in the **Stack Position & Target Branch** section in every PR description so reviewers can navigate the chain.

### Updating a stack in `jj` after review feedback or `develop` updates

- **To edit an earlier layer in the stack:**
  ```bash
  jj edit stack/<topic>/01-core
  # modify files; @ is now 01-core and 02-ui / 03-adapter are automatically rebased on top
  ```
- **To rebase the entire stack onto the latest `develop`:**
  ```bash
  jj git fetch
  jj rebase -s stack/<topic>/01-core -d develop@origin
  ```
- **Verify each layer and push:**
  ```bash
  jj git push \
    --bookmark stack/<topic>/01-core \
    --bookmark stack/<topic>/02-ui \
    --bookmark stack/<topic>/03-adapter
  ```

### Alternative: Creating and updating a stack with standard `git`

When working in an environment where `jj` is not installed, use `git` with `--update-refs` (Git 2.38+):

1. Create sequential branches off `develop`:
   ```bash
   git switch develop && git pull --ff-only
   git switch -c stack/<topic>/01-core
   # commit and verify layer 1
   git push -u origin stack/<topic>/01-core

   git switch -c stack/<topic>/02-ui
   # commit and verify layer 2
   git push -u origin stack/<topic>/02-ui
   ```
2. Rebase the entire stack and update intermediate branch refs in one pass from the top branch:
   ```bash
   git fetch origin
   git switch stack/<topic>/03-adapter
   git rebase --update-refs origin/develop
   git push --force-with-lease origin \
     stack/<topic>/01-core \
     stack/<topic>/02-ui \
     stack/<topic>/03-adapter
   ```

### Agentic Cross-Model Review & Stack Merge Ownership (`develop`)

To catch model-specific blind spots while keeping agentic development autonomous and fast, **every feature PR or stacked PR chain targeting `develop` must be reviewed and merged by an independent reviewer agent**:

1. **Authoring vs. reviewing separation**
   - The authoring agent creates the PR (or stack), verifies all touched layers, and populates verification evidence, but **does not self-merge** feature stacks into `develop`.
   - Instead, the authoring agent delegates review and merge execution to a dedicated **Reviewer & Merger Agent**.
2. **Reviewer model selection hierarchy**
   - **Preferred — Alternative model family:** Delegate to a subagent running a **different model family/provider** from the authoring agent (for example, Claude <-> Gemini <-> GPT/DeepSeek). Cross-family review reduces correlated errors in Rust ownership, Leptos reactivity, Tauri security capabilities, and test coverage claims.
   - **Fallback — Independent standard review:** If an alternative model family is unavailable, use a fresh independent agent from an available model at standard/medium reasoning. Independence, evidence and focused checklists are the review controls. Never select `max` or `ultra` for review; do not automatically raise effort when another family is unavailable.
3. **What the Reviewer & Merger Agent checks**
   - Architectural boundaries (`app-core` purity, single Leptos UI owner, explicit `csr`/`hydrate`/`ssr` profile isolation, capability-scoped Tauri ACLs).
   - Verification honesty (reported commands were actually executed; untested platforms/WebViews are explicitly disclosed).
   - Knowledge provenance (`added_by` and `human_ratified` fields accurate; no silent overturning of `human_ratified: true` decisions).
   - Commit hygiene (atomic commits conforming to [`.github/.gitmessage`](.github/.gitmessage), clean linear history).
4. **Bottom-up stack merge ownership into `develop` (executed by the Reviewer & Merger Agent)**
   - Once review findings are addressed and all review conversations are resolved, **the reviewing agent is responsible for landing the stack into `develop` from the bottom upward**:
     1. Confirm PR 1 (`base: develop`) is rebased onto `origin/develop`, passes checks, and has **all review conversations resolved**.
     2. Merge PR 1 into `develop` using **Rebase and merge**:
        ```bash
        gh pr merge <pr-1> --rebase --delete-branch
        ```
     3. Retarget PR 2 to `develop`, rebase the remaining stack onto `origin/develop`, and push:
        ```bash
        gh pr edit <pr-2> --base develop
        # Using jj (preferred):
        jj git fetch
        jj rebase -s stack/<topic>/02-ui -d develop@origin
        jj git push --bookmark stack/<topic>/02-ui --bookmark stack/<topic>/03-adapter
        # Or using git:
        # git fetch origin && git switch stack/<topic>/03-adapter
        # git rebase --update-refs origin/develop
        # git push --force-with-lease origin stack/<topic>/02-ui stack/<topic>/03-adapter
        ```
     4. Re-verify if the rebase touched code, then repeat until every layer in the stack is merged into `develop`.

### Promoting `develop` to `main` (Human-Gated Release)

1. When `develop` reaches a release or milestone checkpoint, a contributor or agent opens a release promotion PR (`base: main` <- `compare: develop`).
2. Opening or updating a PR targeting `main` triggers the [`Main Branch Human Gate`](.github/workflows/main-human-gate.yml) workflow (`main-human-approval`), which pauses in a `Waiting` state on the `main-release` GitHub Environment.
3. A **human reviewer** audits the diff, ratifies any applicable [`knowledge/`](knowledge/README.md) decisions (`human_ratified: true`), approves the `main-release` deployment gate in GitHub, and merges the PR into `main` via **Rebase and merge**.
4. Agents must **never** approve the `main-release` environment gate or run `gh pr merge` on a PR targeting `main`.

---

## UI workflow and architecture diagrams

For UI work read [.agents/skills/distinct-ui/SKILL.md](.agents/skills/distinct-ui/SKILL.md).
Separate the design brief, spatial specification, implementation and rendered
critique. Do not make token restrictions a substitute for task usability or
accessibility. No Superdesign account or other design service is required.

Every PR links the overall [architecture](docs/architecture.md). Changes to crate
boundaries, data/control flow, build/CI topology, IPC or deployment include a
small Mermaid diagram explaining the changed path and its trust/ownership
boundaries. Show before/after when the topology changes; prose-only changes can
state “no architectural change” with a reason. Diagrams describe the shipped
state, identify future components as such, and must agree with the code. A human
reviewer should be able to locate inputs, decisions, effects and validation.

## 3. Commit Message Convention and Template

The commit message template lives in [`.github/.gitmessage`](.github/.gitmessage) alongside the repository's GitHub workflow templates.

Enable it locally once per clone:

```bash
git config commit.template .github/.gitmessage
```

*(When writing commit descriptions with `jj describe` or `jj commit`, follow the same structure in [`.github/.gitmessage`](.github/.gitmessage).)*

### Format ([`.github/.gitmessage`](.github/.gitmessage))

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
- Keep commits atomic: a rebased PR merges commits onto `develop` and `main` without squashing by default, so every commit in a PR should build cleanly and carry an accurate message.

---

## 4. Pull Request Template and Branch Protection (`develop` vs `main`)

GitHub automatically loads [`.github/pull_request_template.md`](.github/pull_request_template.md) on new PRs:

```markdown
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
- **CI/setup impact (when touched):** fresh/repeated-run behavior, cold/warm evidence, cache trust/invalidation, retained checks and efficiency opportunities.
- **Not run / untested platforms or environments:**
  - `...`

## Knowledge & Documentation
- **Knowledge records added/updated (`knowledge/`):** `none` (or list IDs with `added_by` and `human_ratified` status)
- **Stable docs updated (`docs/`):** `none` (or list files)

## Merge Readiness & Review Gate (`develop` vs `main`)
- **Authoring agent / model:** `...`
- **Reviewer & merger agent / model (for `develop`):** `...` (prefer alternative model family; fallback: fresh independent agent at standard/medium reasoning)
- [ ] For PRs targeting `develop`: reviewed by an alternative model family (or independent standard/medium fallback) and ready for the reviewing agent to rebase-merge bottom-up into `develop`
- [ ] For PRs targeting `main`: **`main-human-approval` (`main-release` environment gate) approved and merged by a human user** (agents must never merge into `main` or approve the `main-release` gate)
- [ ] Reviewer used standard/medium reasoning; max/ultra were not used
- [ ] Branch is rebased onto its target base with a clean linear history (no merge commits)
- [ ] All review conversations are resolved
```

### Protected `develop` and `main` rules

Both **`develop`** and **`main`** enforce:
- Changes must merge via a Pull Request (no direct pushes, force-pushes, or branch deletions).
- **Linear history required:** merge commits and squash merges are disabled; PRs must be rebased and merged via **Rebase and merge**.
- **Conversation resolution required:** every review thread must be resolved before a PR can merge.

Additionally:
- **`develop` (Autonomous Agent Integration Branch):** `required_approving_review_count: 0` on GitHub so an independent **Reviewer & Merger Agent** (alternative model family, or independent standard/medium fallback) can review and land stacked PRs bottom-up into `develop` without blocking on human availability.
- **`main` (Human-Gated Release Branch):** requires the **`main-human-approval`** status check ([`.github/workflows/main-human-gate.yml`](.github/workflows/main-human-gate.yml)), which is gated by the **`main-release` GitHub Environment** with required human reviewer approval (`kmosoti`). Even when an agent shares local CLI credentials, GitHub blocks `gh pr merge` into `main` until the human reviewer approves the `main-release` deployment in GitHub, and [AGENTS.md](AGENTS.md) strictly forbids agents from approving that environment gate or merging into `main`.

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

## Dependency updates

Run [both Rust policy checks and all Gradle lock scans](docs/security.md) when
updating dependencies. Regenerate real locks and verification metadata with the
owning tools; preserve licenses and reviewed source patch provenance. Maintenance
exceptions must name an advisory, explain scope and carry an enforced expiry.
A cache hit never substitutes for dependency/advisory/license verification.
