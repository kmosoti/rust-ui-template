# Contributing

This is a small, evidence-driven Rust UI template. Changes should preserve one owner per concern rather than accumulate overlapping frameworks.

## Development workflow

1. Check the current issues and [architecture contract](docs/architecture.md). v0.1 is CSR; SSR and hydration belong to [Issue #2](https://github.com/kmosoti/rust-ui-template/issues/2).
2. Read [AGENTS.md](AGENTS.md) and search the [knowledge graph](knowledge/README.md) before investigating a previously studied problem.
3. Develop on a focused branch. Keep PRs independently reviewable, with motivation, alternatives considered, tests, and known limitations.
4. Execute the checks relevant to changed code and platforms. Report exact commands/results; mark unavailable hardware or toolchains as untested.
5. Update stable instructions in `docs/` only when the documented contract changes. Record new evidence, nuanced trade-offs, and decisions in `knowledge/`.

## Knowledge contribution contract

Each non-index record belongs in `knowledge/decisions/`, `knowledge/research/`, or `knowledge/observations/` and has:

- Stable ID and Markdown filename (for example `D-0001`, `R-0001`, `O-0001`), plus front matter with `id`, `type`, `status`, and `updated`.
- A clear claim or question; supporting links to code, issue, test output, primary source, or another record.
- An explicit distinction between observation, inference, open question, and rejected alternative.
- Typed links (for example *informed-by*, *challenges*, *observed-in*, *supersedes*) to related records, with reciprocal links where meaningful.
- Revisit conditions: the evidence or experiment that could change the conclusion.

Prefer append-only dated observations; make changing decisions explicit rather than rewriting their rationale. Do not put tokens, personal information, secrets, or unreviewed third-party content in public records.

## Quality standard

Tests should exercise the behavior claimed. A Lean theorem about an abstract model does not verify the actual Rust implementation unless the model-to-code correspondence is established. Likewise, a successful cross-compile is not a platform launch test.

Keep changes compatible with the repository's selected toolchain and licensing. Source code contributed here is distributed under the [MIT License](LICENSE).
