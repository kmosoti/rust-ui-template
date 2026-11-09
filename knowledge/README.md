# Linked project knowledge

This directory is a **versioned Markdown knowledge graph**, not a second set of product documentation. It retains why choices were made, what has actually been observed, conflicting evidence, and what would change a conclusion. It must be readable by both humans and agents without a proprietary graph backend.

## Boundary with documentation

- [`docs/`](../docs/architecture.md): relatively stable instructions, public design contracts, and how the project is intended to work.
- `knowledge/`: revisable understanding, dated evidence, failures, alternatives, and contextual decisions. A research note is not an implementation guarantee.

## Node types

| Directory | Prefix | Purpose |
| --- | --- | --- |
| [`decisions/`](decisions/D-0001-csr-first.md) | `D-` | Choice, constraints, considered alternatives, reopening trigger |
| [`research/`](research/R-0001-cross-platform-evidence.md) | `R-` | Sources, hypotheses, contradictions, unanswered tests |
| [`observations/`](observations/O-0001-scaffold-snapshot.md) | `O-` | Dated reports of actual state, environment, and evidence |

## Initial connected nodes

- [D-0001 · CSR-first client delivery](decisions/D-0001-csr-first.md), informed by [R-0001](research/R-0001-cross-platform-evidence.md), contextualized by [O-0001](observations/O-0001-scaffold-snapshot.md).
- [R-0001 · Cross-platform and verification evidence](research/R-0001-cross-platform-evidence.md), with alternatives and falsification tests for [D-0001](decisions/D-0001-csr-first.md).
- [O-0001 · Repository scaffold snapshot](observations/O-0001-scaffold-snapshot.md), linked to both [D-0001](decisions/D-0001-csr-first.md) and [R-0001](research/R-0001-cross-platform-evidence.md).

## Record protocol

1. Use a stable ID, a descriptive filename, and front matter: `id`, `type`, `status`, `updated` (YYYY-MM-DD). IDs must not be reused.
2. Label statements as **Observed**, **Inferred**, **Hypothesis**, or **Unknown** when confusing them would change a decision. Link sources and state the date/environment of observations.
3. In a **Relations** section, use ordinary relative Markdown links with a typed edge such as *informed-by*, *challenges*, *supports*, *observed-in*, or *supersedes*. Maintain backlinks when they communicate real meaning.
4. Keep alternatives and a **Revisit when** trigger. If evidence overturns a choice, add a new decision and link it with *supersedes* rather than silently rewriting past reasoning.
5. Before doing research, walk the index and relevant outgoing links. Independent checks should record their own methods and observations, then link to the claim they corroborate or challenge.

The index is curated, not automatically generated. Start with Markdown and version control; introduce graph tooling only after an actual retrieval or integrity failure justifies it.
