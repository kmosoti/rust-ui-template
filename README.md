# rust-ui-template

**Status: CSR browser slice; not a complete UI template.** A Leptos browser example uses the dependency-free core. Native packaging and platform validation remain future work.

A minimal Rust-first UI foundation for browser, desktop, and mobile clients. The template will be implemented incrementally through the repository's GitHub issues.

## Implemented foundation

`crates/app-core` provides a latest-request-wins state tracker without UI or platform dependencies. Its tests cover stale, duplicate and cancelled responses, non-wrapping request IDs, and bounded event sequences. The adapter, not the core, owns actual I/O and task cleanup.

```sh
cargo fetch --locked
cargo test --workspace --locked --offline
```

See the [coding-agent handoff and full check commands](docs/issue-1-handoff.md), [decision D-0002](knowledge/decisions/D-0002-latest-request-core.md), and [execution evidence O-0002](knowledge/observations/O-0002-core-foundation.md). A successful core test is not a browser, desktop, or mobile launch test. Issue #1 remains open.

## Browser development

Install Rust 1.99.1 with the `wasm32-unknown-unknown` target, Python 3,
Chrome or Chromium, and Trunk 0.21.14 (`cargo install trunk --version 0.21.14 --locked`).
Node and npm are not required. From the repository root:

```sh
python3 scripts/setup_frontend.py
cargo fetch --locked
.tools/tailwindcss -i styles/input.css -o styles/generated.css --minify
python3 scripts/check_css.py
trunk build --release --locked
trunk build --release --locked --public-url /sub/ --dist dist/sub
cargo run -p browser-tests --locked --offline
```

The setup script verifies the official Tailwind 4.3.4 executable and axe-core
4.10.3 test asset against committed hashes. On Windows, use `.tools/tailwindcss.exe`.
Linux musl is detected automatically; `TAILWIND_TARGET` can explicitly select a
pinned asset name from `scripts/tool-assets.json`. Set `CHROMIUM_PATH` if
Chrome/Chromium is not discoverable. Sandboxing is enabled
by default; `CHROMIUM_NO_SANDBOX=1` is available only for restricted containers
that cannot launch Chromium's sandbox. If your environment sets `NO_COLOR=1`,
unset it for Trunk 0.21.14, which expects a boolean string.

The second build exercises a `/sub/` asset base; use the matching `--public-url`
for a different deployment path. Navigation uses URL fragments and requires no
route rewrite. The Rust browser runner serves the production files on an ephemeral
loopback port, checks interactions and accessibility, and writes actual screenshots
to `artifacts/response-lab.png`, `artifacts/workspace-overview.png`, and
`artifacts/preferences.png`.

Example routes are `#/` (response lab), `#/overview` (sample dashboard), and
`#/settings` (preferences form). Dashboard figures are sample data. Preferences
are local component state and reset on navigation; no persistence or network API
is implemented. Browser binaries come from the environment; their versions must
be recorded with test results. Other system browsers/WebViews remain unverified.

## Selected architecture

- **Leptos** owns UI components, client-side routing, and reactive presentation state.
- **WebAssembly** executes the browser client build; browser-facing glue remains explicit.
- **Tailwind CSS 4** provides one shared styling pipeline.
- **Tauri 2** packages the same client for desktop (Windows, macOS, Linux) and mobile (Android, iOS), with native functionality behind narrow capability-scoped adapters.
- **Pure Rust core** owns reusable application rules and state transitions, independent of UI, browser, or operating-system APIs.

The core workspace pins Rust 1.99.1 with Edition 2024/resolver 3. The remaining implementation roadmap calls for current Leptos APIs, Tailwind 4 CSS-first configuration, explicit Tauri custom-command ACLs/CSP, locked builds, and least-privilege CI. The browser slice pins its dependencies and build tools; native toolchain compatibility remains to be established.

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
