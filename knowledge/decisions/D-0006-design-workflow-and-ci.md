---
id: D-0006
type: decision
status: proposed
updated: 2026-11-10
added_by: agent
human_ratified: false
---

# D-0006: Explicit design workflow, affordable review and reusable CI

Ship a local distinct-ui skill linked from AGENTS.md. New UI work records its
user task, structural alternatives and spatial spec before component code, then
uses production renders, geometry diagnostics, axe and a bounded critique pass.
Use no Superdesign or account-based design service. An optional restricted
semantic theme removes palette/radius defaults, with an actual CSS-output test;
namespace removal is build-wide and is not a compiler-error guarantee or a
measured originality improvement. Do not impose one visual style on all tasks.

User cost constraint: reviewers use standard/medium reasoning. Never use max or
ultra for review. An alternative family is useful when available; otherwise a
fresh independent standard/medium reviewer suffices. This replaces the previous
higher/highest-effort fallback in the working instructions. Historical review
observations remain as recorded; no human ratification is inferred.

Human review gets maintained overall Mermaid architecture diagrams and a focused
change diagram for architecture/data-flow/IPC/build/CI changes. Prose-only PRs can
explain why no diagram change is needed. Diagrams are checked against code and
must label unimplemented elements clearly.

CI uses a verified official Trunk binary and isolated job/image/Rust/lock/SDK
caches. Only successful develop pushes save trusted cache contents; PRs restore
permitted base caches and still execute applicable checks. Rebuild native
package-owned assets before packaging cached dependencies. Leave OS installation
and pinned Rust component verification in place; measure cold and warm runs
rather than promising an unobserved speedup.

Alternatives rejected: mandatory industrial styling, novelty percentages without
a study, using DOM depth as a quality score, and caching system directories or
sharing PR-built executable caches with trusted signing jobs. Revisit if measured
cache transfer/eviction costs exceed savings, a task requires different visual
constraints, or research/evaluation changes the evidence.

## Relations

- **informed-by**: [R-0002](../research/R-0002-ui-diversity-and-verification.md)
- **extends**: [D-0004](D-0004-node-free-tooling.md)
- **observed-in**: [O-0006](../observations/O-0006-design-ci.md)
