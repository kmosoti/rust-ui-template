# rust-ui-template

**Status: first core implementation; not a complete UI template.** The dependency-free Rust core has CI evidence. Leptos/Tailwind browser integration and native packaging are still to be implemented and validated.

A minimal Rust-first UI foundation for browser, desktop, and mobile clients. The template will be implemented incrementally through the repository's GitHub issues.

## Implemented foundation

`crates/app-core` provides a latest-request-wins state tracker without UI or platform dependencies. Its tests cover stale, duplicate and cancelled responses, non-wrapping request IDs, and bounded event sequences. The adapter, not the core, owns actual I/O and task cleanup.

```sh
cargo test --workspace --locked --offline
```

See the [coding-agent handoff and full check commands](docs/issue-1-handoff.md), [decision D-0002](knowledge/decisions/D-0002-latest-request-core.md), and [execution evidence O-0002](knowledge/observations/O-0002-core-foundation.md). A successful core test is not a browser, desktop, or mobile launch test. Issue #1 remains open.

## Selected architecture

- **Leptos** owns UI components, client-side routing, and reactive presentation state.
- **WebAssembly** executes the browser client build; browser-facing glue remains explicit.
- **Tailwind CSS 4** provides one shared styling pipeline.
- **Tauri 2** packages the same client for desktop (Windows, macOS, Linux) and mobile (Android, iOS), with native functionality behind narrow capability-scoped adapters.
- **Pure Rust core** owns reusable application rules and state transitions, independent of UI, browser, or operating-system APIs.

The core workspace pins Rust 1.99.1 with Edition 2024/resolver 3. The remaining implementation roadmap calls for current Leptos APIs, Tailwind 4 CSS-first configuration, explicit Tauri custom-command ACLs/CSP, locked builds, and least-privilege CI. Frontend/native toolchain pins still require implementation and compatibility testing.

## Release sequence

1. **v0.1, client-side rendering:** establish a single Leptos CSR frontend usable in the browser and through Tauri 2, with build/test/packaging evidence. No server-rendering dependency in the client bundle.
2. **Follow-up, optional web SSR + hydration:** add a separate web deployment profile using the same components where technically justified. Keep Tauri clients on CSR; do not introduce a parallel UI framework.

See [Architecture and verification scope](docs/architecture.md) and the repository's GitHub Issues for implementation plans and acceptance criteria.

## Collaboration and linked knowledge

- [AGENTS.md](AGENTS.md): minimal, repo-wide working agreement for coding agents (`develop` for autonomous agent stacks, `main` gated by human review).
- [CONTRIBUTING.md](CONTRIBUTING.md): the authoritative, issue-agnostic contributor guide covering the iterative development loop, the `develop` vs. `main` branch model ([`.github/workflows/main-human-gate.yml`](.github/workflows/main-human-gate.yml)), colocated Jujutsu (`jj`) and stacked PR workflows, cross-model agentic review & stack merge ownership, commit conventions ([`.github/.gitmessage`](.github/.gitmessage)), and the PR template ([`.github/pull_request_template.md`](.github/pull_request_template.md)).
- [Knowledge graph](knowledge/README.md): linked, dated decisions (`D-`), research (`R-`), and observations (`O-`) that track provenance (`added_by: agent | human | mixed`) and explicit human sign-off (`human_ratified: true | false`) without gating agent velocity.
- [docs/](docs/architecture.md) remains relatively stable documentation; `knowledge/` records evolving understanding and must not be treated as proof of implementation.


## Deliberately excluded from the baseline

Topcoat, htmx, Electron, parallel reactive frameworks, custom mount coordinators, and an embedded HTTP server in the native shell.

## Verification standard

The template should state only what its tests and proofs establish. A Lean proof over a handwritten model does not verify Leptos or the shipped WebView. Formal verification, if introduced, must be tied to supported Rust source extraction and explicitly scoped invariants; platform interactions require independent integration tests.

## Licenses and platform support

Licensed under the [MIT License](LICENSE) (Copyright 2026 Kennedy Mosoti). The validated platform-support matrix remains a release decision; public repository visibility alone does not establish platform support.
