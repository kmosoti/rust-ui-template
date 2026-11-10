---
id: D-0003
type: decision
status: proposed
updated: 2026-11-09
added_by: agent
human_ratified: false
---

# D-0003: CSR browser adapter and owner-scoped work

Use Leptos CSR in a shared UI crate with a small browser entrypoint. The UI owns
an `app-core` tracker for each mounted example. It starts abortable simulated
timer tasks, passes their IDs back to the tracker on completion, aborts all
outstanding timers on cancellation or owner cleanup, and uses fallible signal
updates to avoid writing disposed state. Superseded tasks can finish so the real
core's stale-response rule is exercised. IDs never cross owner lifetimes.

Use one Tailwind 4 npm CLI output scanned from the shared Rust component source
and bundled by Trunk. Hash navigation works on static hosts without route
rewrites; the Trunk public URL must match the deployment asset prefix. No
persistence, network service, SSR, hydration, or native host is implied.

A direct component-local generation counter was rejected because it would
replicate [D-0002](D-0002-latest-request-core.md). Revisit when real I/O needs
transport-specific cancellation, a server needs path-based routes, or native
packaging establishes different asset requirements.

The npm tooling choice is superseded by [D-0004](D-0004-node-free-tooling.md);
the owner-lifetime and freshness contract is retained.

## Relations

- **extends**: [D-0002](D-0002-latest-request-core.md)
- **observed-in**: [O-0003](../observations/O-0003-csr-browser.md)
