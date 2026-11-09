---
id: D-0001
type: decision
status: accepted-for-v0.1
updated: 2026-11-09
---

# D-0001: CSR first, SSR as an optional later web profile

## Decision

Use one Leptos client-side-rendered UI compiled to WASM for browser and Tauri WebView delivery. Tailwind 4 owns styling; Tauri 2 owns native packaging and permissions. Keep reusable Rust state transitions framework-independent. Investigate web SSR/hydration only after this baseline is implemented and measured.

## Why

This minimizes the number of rendering modes in the first testable release and avoids assuming a bundled native WebView has a local SSR server. Platform-independent UI reuse is the objective, **not** a claim that all target platforms have already passed tests.

## Alternatives and trade-offs

- **SSR/hydration for every target:** not a baseline requirement; local Tauri static assets do not supply server-rendered HTML by themselves.
- **SSR/hydration for web, CSR for native:** explicitly deferred to [Issue #2](https://github.com/kmosoti/rust-ui-template/issues/2); adds build profiles and hydration testing in exchange for initial server HTML.
- **Separate native UI toolkit:** may offer better native integration, but would duplicate the component system and defeat the shared Leptos presentation goal.

## Evidence and limits

This is an architectural decision, not a validated platform-support claim. Browser version compatibility, asset paths, IPC permission behavior, native package startup, and mobile toolchain support still require direct tests.

## Revisit when

Measured web requirements justify SSR; CSR cannot meet required accessibility or performance behavior; or actual WebView/packaging failures undermine UI reuse.

## Relations

- **informed-by**: [R-0001: Cross-platform and verification evidence](../research/R-0001-cross-platform-evidence.md)
- **contextualized-by**: [O-0001: Scaffold snapshot](../observations/O-0001-scaffold-snapshot.md)
- **specified-in**: [docs/architecture.md](../../docs/architecture.md), [Issue #1](https://github.com/kmosoti/rust-ui-template/issues/1)
- **followed-by**: [Issue #2: Optional SSR and hydration](https://github.com/kmosoti/rust-ui-template/issues/2)
