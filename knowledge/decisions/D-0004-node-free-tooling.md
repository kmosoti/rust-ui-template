---
id: D-0004
type: decision
status: proposed
updated: 2026-11-10
added_by: agent
human_ratified: false
---

# D-0004: Node-free browser tooling

Use the official Tailwind 4.3.4 standalone CLI at build time and Chromiumoxide
0.9.1 to drive production-browser checks from Rust. Keep Leptos CSR, Trunk,
and the pure core unchanged in responsibility. The standalone binary embeds
its own runtime; users and CI do not install Node/npm for this pipeline.

`scripts/tool-assets.json` pins official executable SHA-256 digests and the npm
registry axe-core 4.10.3 archive's SHA-512 integrity. Python downloads, verifies,
and extracts the assets; axe JavaScript runs inside the browser, not Node.
The Rust runner serves static dist files on an ephemeral loopback port, owns
browser shutdown, performs interaction and accessibility checks, and captures
three example pages. Chrome/Chromium must be provided by the environment and
its version recorded. This replaces D-0003's npm CLI/test-tool choice only.

Alternatives: Tailwind-RS would require a separate Tailwind 4 compatibility
assessment. Taffy duplicates the browser's CSS layout responsibility. Neither
is added. Revisit browser provisioning if reproducible browser revisions or
additional browser engines become required; CDP checks cover Chromium only.

## Relations

- **partially-supersedes**: [D-0003](D-0003-csr-browser-adapter.md)
- **observed-in**: [O-0004](../observations/O-0004-node-free-examples.md)
