---
id: D-0002
type: decision
status: proposed
updated: 2026-11-09
added_by: agent
human_ratified: false
---

# D-0002: Start Issue #1 with a latest-request-wins core

## Decision and rationale

Implement a small dependency-free `no_std` tracker before coupling it to Leptos
or Tauri. The core allocates non-wrapping request IDs and decides whether a
completion may commit. The adapter owns I/O, task cancellation, and component
lifetime. This is a testable initial slice of the CSR-first decision, not a new
framework or a reason to postpone the client indefinitely.

## Contract

A completion with an ID other than the active ID does not change state. A valid
completion commits at most once. Cancellation revokes the pending ID without
clearing the last result. Starting retains the last result and supersedes older
work. Exhaustion returns an error before mutation; IDs never wrap.

## Limits and alternatives

IDs are scoped to one tracker lifetime. No cross-instance, durable-session, or
security authority is claimed. Cloning is for snapshots, not identity isolation.
Generic values allow success/failure to share freshness semantics, but generic
extraction support must be tested before any Lean claim. The core's state
contract does not constrain arbitrary side effects of a payload's destructor.

Alternative: implement generation checks directly in the component. Rejected for
this example because it couples an independently testable rule to UI machinery.
A stateless extracted reducer or a narrower concrete type may be preferable if
the Lean extraction pilot cannot handle this supported Rust subset.

## Revisit when

Actual UI integration needs different cancellation/result-retention semantics,
requests cross component/session boundaries, or extraction evidence justifies a
smaller proof surface. Do not build a global task coordinator speculatively.

## Relations

- **implements-part-of**: [D-0001](D-0001-csr-first.md)
- **tested-as-recorded-in**: [O-0002](../observations/O-0002-core-foundation.md)
- **implementation**: [app-core](../../crates/app-core/src/lib.rs)
- **handoff**: [Issue #1 handoff](../../docs/issue-1-handoff.md)
