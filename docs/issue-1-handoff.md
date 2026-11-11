# Current Issue #1 completion handoff

The agreed milestone is browser/Linux CSR plus delivered Android test evidence.
Windows/macOS/iOS, broader runtime coverage and production signing have explicit
follow-ups (#22–#24); proof continuation is #27, maintenance replacements #28.
No main promotion, tag or publication is included.

The implementation is reviewed and landed on develop at323167e3; all six
post-merge source workflows passed. Exact runs/artifacts, commands, cache
measurements and limits are in [O-0017](../knowledge/observations/O-0017-issue1-completion.md).
The final documentation PR30 and issue checklist complete the handoff; no
cross-platform release or formal proof is implied.

- [Pinned toolchains and fresh checkout commands](toolchains.md)
- [Platform evidence and untested configurations](platforms.md)
- [Dependency checks and bounded exceptions](security.md)
- [Actual core extraction assessment; no proof claim](proof-feasibility.md)
- [Milestone release notes](release-notes.md)
- [CI measurements, cache trust and clean build contract](ci.md)

The remainder below preserves historical foundation notes. They are not a list
of still-missing browser/native crates or instructions to repeat landed work.

---

## Historical foundation and native snapshots

> Historical handoff (status at that time, superseded by the completion record above): browser/Nocturne/seven palettes, the shared native entry and Ubuntu 24.04 DEB/Fedora 44 RPM checks are implemented. Android APK/device work is tracked in [O-0011](../knowledge/observations/O-0011-android-apks.md) and the [platform matrix](platforms.md). Desktop work remains Linux-focused; Windows/macOS and iOS are deferred. At that snapshot, security/release checks and source-linked proof feasibility remained open and Issue #1 stayed open.
>
> The foundation notes below are historical, not instructions to repeat already-landed browser/native work.

> Historical foundation handoff: the browser slice is now implemented; see [O-0003](../knowledge/observations/O-0003-csr-browser.md) for current evidence and the README for build commands. The subsequent native and verification slices remain open.

# Issue #1: implementation handoff

This is the first implementation slice, not the completed CSR release. Work is
based on `develop` at `e959615423c7deaa0608fc3a51769b71239bc2b1`.

## Implemented in this slice

- An Edition 2024/resolver 3 workspace, pinned to Rust 1.99.1.
- `app-core`: dependency-free, `no_std`, unsafe forbidden; a latest-request-wins
  tracker with an explicit black-box interface.
- Thirteen Rust unit tests, including all six completion orders for three
  requests, boundary/overflow cases, and 55,987 bounded sequence prefixes.
- A documentation example and two targeted mutation-sensitivity checks.
- A check of the actual Cargo metadata graph, with nine Python checker tests.
- Read-only PR CI for formatting, unit/doc tests, Clippy, WASM compilation,
  dependency boundaries, mutation sensitivity, and tracked-file drift.

Implementation is not execution evidence. Consult the exact PR commit's CI and
[O-0002](../knowledge/observations/O-0002-core-foundation.md) for what actually ran.

## Public interface and ownership

```rust
let mut state = app_core::LatestRequest::<Result<u32, &'static str>>::new();
let id = state.begin()?;                      // adapter schedules the work
let outcome = state.complete(id, Ok(42));      // Applied or Ignored
state.cancel();                               // revokes authority, not actual I/O
```

The UI adapter owns timers/network requests, cancellation, and reactive-owner
lifetime. The core owns freshness and ID allocation. A stale/duplicate/cancelled
completion leaves the complete tracker state unchanged. The last committed value
remains visible while a new request is pending. Overflow is rejected atomically.

IDs are local to one tracker lifetime. Never route an old owner's completion into
a newly constructed tracker. Clones are snapshots, not globally unique namespaces.
Do not serialize these IDs as durable request identities or credentials.

## First coding-agent task: complete the browser vertical slice

Work on a focused branch based on the reviewed foundation in `develop`, or stack
against this PR's head until it lands. Do not close Issue #1 with this slice.

1. Run the core checks below and inspect any failing CI before expanding scope.
2. Add `crates/app-ui` and `crates/client` as actual workspace members. Keep all
   Leptos/browser dependencies out of `app-core`; update the root Cargo lockfile.
3. Use Leptos CSR, not SSR/hydration. A minimal `Latest response` page should have
   an accessible labelled numeric input, `Slow request`, `Fast request`, and
   `Cancel` actions, a pending indicator, and a live result status.
4. Wire the real tracker into the UI. A request captures its ID and submitted
   value; completion calls `complete`. Do not duplicate the freshness check in
   JS or component-local counters. Use owner-bound task cleanup and avoid
   writing disposed signals; cancellation must not be confused with merely
   ignoring an eventual result.
5. Compile one Tailwind 4 stylesheet before Trunk bundles it. Explicitly scan the
   shared Rust UI sources. Do not add Vite, npm runtime dependencies, or a second
   state-management system just to run the Tailwind CLI. Choose and pin either
   the standalone CLI or the npm CLI, not both.
6. Test the production `dist/`, not only the development server. Verify fast B
   remains visible after slow A finishes, duplicate and cancelled results cannot
   commit, and navigating/unmounting during a pending task does not panic.
7. Add direct-link/navigation and keyboard/accessibility smoke tests. Keep root
   vs subpath asset handling explicit rather than assuming Tauri will load every
   web URL unchanged.
8. Generate and commit lockfiles using the actual tools; require `--locked`/`npm ci`
   as applicable. Update CI to include the production WASM/CSS build and browser
   smoke tests. Record commands, target, commit, versions, and limitations in a
   new observation node.

Candidate upstream versions independently checked on 2026-11-09: Leptos 0.8.23,
Trunk 0.21.14, Tailwind 4.3.4. These are **source-verified candidates, not a tested
combination**. Confirm the selected compatibility set before committing pins.

- [Leptos CSR guide](https://book.leptos.dev/getting_started/index.html)
- [Leptos crate](https://docs.rs/crate/leptos/0.8.23)
- [Trunk configuration](https://trunk-rs.github.io/trunk/guide/configuration/index.html)
- [Trunk assets](https://trunk-rs.github.io/trunk/guide/assets/index.html)
- [Tailwind 4.3.4 release](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.4)

Use the Trunk project's current GitHub Pages documentation, not an old third-party
or abandoned domain. Do not consume build binaries from unverified mirrors.

## Local core commands

From the repository root, with rustup installed:

```sh
rustup show
cargo fmt --all -- --check
cargo test --workspace --locked --offline
cargo clippy --workspace --all-targets --locked --offline -- -D warnings
cargo check -p app-core --target wasm32-unknown-unknown --locked --offline
cargo metadata --format-version 1 --locked --offline > /tmp/rust-ui-metadata.json
python3 scripts/check_core_boundary.py /tmp/rust-ui-metadata.json
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/check_core_mutations.py
```

These offline commands apply to this dependency-free slice. When external
frontend crates are added, run `cargo fetch --locked` first on an online machine;
then use locked builds. Toolchain installation itself also requires network access.
The mutation runner uses disposable copies and requires Cargo; a compiler error
must not count as a successful rejection of a defect.

## Subsequent slices, not implemented here

- Tauri host, least-privilege IPC, browser fallback, production CSP, and a tested
  Linux desktop package; then Android and the remaining platform matrix.
- Signing/notarization and full dependency/security/release checks.
- Implementation-linked Lean extraction. First candidate: for a non-active ID,
  `complete` returns `Ignored` and preserves state; also atomic non-wrapping ID
  exhaustion. Do not replace actual extraction with a handwritten-model proof.
- SSR/hydration remains Issue #2. Do not introduce its dependencies here.

No test here establishes DOM correctness, a working browser UI, native platform
support, secure Tauri permissions, or an end-to-end formal proof. Independent
review is required before merge. Agents must not merge into `main`.
