# Linked project knowledge

This directory is a **versioned Markdown knowledge graph**, not a second set of product documentation. It retains why choices were made, what has actually been observed, conflicting evidence, and what would change a conclusion. It must be readable by both humans and agents without a proprietary graph backend.

## Boundary with documentation

- [`docs/`](../docs/architecture.md): relatively stable instructions, public design contracts, and how the project is intended to work.
- `knowledge/`: revisable understanding, dated evidence, failures, alternatives, and contextual decisions. A research note is not an implementation guarantee.

## Provenance and human ratification (non-blocking for agents)

Every knowledge artifact distinguishes **who added it** from **whether a human explicitly ratified it**:

- `added_by`: `agent` | `human` | `mixed` — records whether the artifact was authored by an autonomous/assisted coding agent, a human contributor, or both.
- `human_ratified`: `true` | `false` — `true` **only** when a human user has explicitly ratified the artifact's claim or decision. When `true`, record `ratified_by` (handle/name) and `ratified_on` (`YYYY-MM-DD`).

### Zero-friction velocity rule

Provenance tracking **must never slow down agentic work**:

1. **No ratification gate for execution:** Agents create, link, update, and act on `knowledge/` artifacts immediately with `added_by: agent` and `human_ratified: false`. Agents do not pause or block implementation waiting for human sign-off on knowledge notes.
2. **Asynchronous ratification:** Humans ratify records when convenient (during PR review, issue triage, or a later pass) by flipping `human_ratified: true` and setting `ratified_by` / `ratified_on`, or by explicitly instructing an agent to mark a specific record ratified. Merging a PR does not implicitly ratify every `human_ratified: false` record in the tree unless stated.
3. **Authority semantics:**
   - `human_ratified: false` artifacts are active working knowledge. Agents and humans may refine, challenge, or supersede them freely as new evidence emerges.
   - `human_ratified: true` artifacts carry explicit human confirmation. Agents may always record new observations (`O-`) or research (`R-`) that challenge a ratified record without blocking, but must not silently supersede or violate a `human_ratified: true` decision (`D-`) without explicit human approval.

## Node types

| Directory | Prefix | Purpose |
| --- | --- | --- |
| [`decisions/`](decisions/D-0001-csr-first.md) | `D-` | Choice, constraints, considered alternatives, reopening trigger |
| [`research/`](research/R-0001-cross-platform-evidence.md) | `R-` | Sources, hypotheses, contradictions, unanswered tests |
| [`observations/`](observations/O-0001-scaffold-snapshot.md) | `O-` | Dated reports of actual state, environment, and evidence |

## Connected nodes

| Node | Added by | Human ratified | Summary |
| --- | --- | --- | --- |
| [D-0001 · CSR-first client delivery](decisions/D-0001-csr-first.md) | `agent` | `false` | CSR-first baseline; informed by [R-0001](research/R-0001-cross-platform-evidence.md), contextualized by [O-0001](observations/O-0001-scaffold-snapshot.md) |
| [R-0001 · Cross-platform and verification evidence](research/R-0001-cross-platform-evidence.md) | `agent` | `false` | Alternatives and falsification tests for [D-0001](decisions/D-0001-csr-first.md) |
| [O-0001 · Repository scaffold snapshot](observations/O-0001-scaffold-snapshot.md) | `agent` | `false` | Initial repository state linked to [D-0001](decisions/D-0001-csr-first.md) and [R-0001](research/R-0001-cross-platform-evidence.md) |
| [D-0002 · Latest-request-wins core](decisions/D-0002-latest-request-core.md) | `agent` | `false` | Concrete state contract, adapter ownership, limits, and alternatives for the first implementation slice |
| [O-0002 · Core implementation evidence](observations/O-0002-core-foundation.md) | `agent` | `false` | Local checks, exact CI source/run, passed Rust tests, and untested UI/platform boundaries |

| [D-0003 · CSR browser adapter](decisions/D-0003-csr-browser-adapter.md) | `agent` | `false` | Owner-scoped tasks, shared UI, static assets and fragment navigation |
| [O-0003 · CSR browser evidence](observations/O-0003-csr-browser.md) | `agent` | `false` | Local and CI evidence for the browser slice and its limits |

| [D-0004 · Node-free tooling](decisions/D-0004-node-free-tooling.md) | `agent` | `false` | Official standalone Tailwind and Chromiumoxide browser checks |
| [O-0004 · Node-free examples](observations/O-0004-node-free-examples.md) | `agent` | `false` | Production captures, checks and limits of the Rust-driven examples |

| [D-0005 · Linux native host](decisions/D-0005-linux-native-host.md) | `agent` | `false` | Isolated Tauri host, versioned boundary, explicit permissions and CSP |
| [O-0005 · Linux host evidence](observations/O-0005-linux-native-host.md) | `agent` | `false` | Browser checks and native CI prerequisites/results |

| [R-0002 · UI diversity and verification](research/R-0002-ui-diversity-and-verification.md) | `agent` | `false` | Primary-source assessment of UI sameness claims and practical controls |
| [D-0006 · Design workflow and reusable CI](decisions/D-0006-design-workflow-and-ci.md) | `agent` | `false` | Local skill, standard/medium review, diagrams and trusted caches |
| [O-0006 · Design/CI evidence](observations/O-0006-design-ci.md) | `agent` | `false` | Executed checks, observed geometry defect and CI timing boundaries |

| [D-0007 · Default workspace launcher](decisions/D-0007-default-workspace-design.md) | `agent` | `false` | Nocturne default design and ongoing CI contributor discipline |
| [O-0007 · Workspace launcher evidence](observations/O-0007-workspace-launcher.md) | `agent` | `false` | Rendered design, production assets, accessibility and regression evidence |

| [D-0008 · Semantic color schemes](decisions/D-0008-color-palettes.md) | `agent` | `false` | Six user palettes, session selection and contrast contracts |
| [O-0008 · Color scheme evidence](observations/O-0008-color-palettes.md) | `agent` | `false` | Rendered contrast, interaction, accessibility and native results |

| [D-0009 · Linux/Android delivery](decisions/D-0009-linux-android-delivery.md) | `agent` | `false` | DEB/RPM and Android test APK implementation sequence |
| [O-0009 · Native library entry](observations/O-0009-native-entry.md) | `agent` | `false` | Shared entry preparation and Linux regression evidence |

| [O-0010 · Linux packages](observations/O-0010-linux-packages.md) | `agent` | `false` | DEB/RPM installed tests and native diagnostics |

## Record protocol

1. Use a stable ID, a descriptive filename, and front matter:
   ```yaml
   ---
   id: D-0001
   type: decision # decision | research | observation
   status: proposed # e.g., proposed | accepted | preliminary | historical-snapshot | superseded
   updated: YYYY-MM-DD
   added_by: agent # agent | human | mixed
   human_ratified: false # true | false
   # Include when human_ratified is true:
   # ratified_by: <github-handle>
   # ratified_on: YYYY-MM-DD
   ---
   ```
   IDs must not be reused.
2. Label statements as **Observed**, **Inferred**, **Hypothesis**, or **Unknown** when confusing them would change a decision. Link sources and state the date/environment of observations.
3. In a **Relations** section, use ordinary relative Markdown links with a typed edge such as *informed-by*, *challenges*, *supports*, *observed-in*, or *supersedes*. Maintain backlinks when they communicate real meaning.
4. Keep alternatives and a **Revisit when** trigger. If evidence overturns a choice, add a new decision and link it with *supersedes* rather than silently rewriting past reasoning.
5. Before doing research, walk the index and relevant outgoing links. Independent checks should record their own methods and observations, then link to the claim they corroborate or challenge.

The index is curated, not automatically generated. Start with Markdown and version control; introduce graph tooling only after an actual retrieval or integrity failure justifies it.
