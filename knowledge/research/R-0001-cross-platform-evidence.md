---
id: R-0001
type: research
status: preliminary
updated: 2026-11-09
---

# R-0001: Cross-platform and verification evidence to establish

## Question

Can one Leptos CSR/WASM frontend be delivered through a web host and Tauri 2 on desktop/mobile without crossing rendering, styling, platform, and domain concerns?

## Source pointers (not runtime validation)

- [Leptos CSR deployment guide](https://book.leptos.dev/deployment/csr.html) describes the CSR path.
- [Tauri 2 documentation](https://v2.tauri.app/) describes desktop and mobile targets and packaging.
- [Tauri capability model](https://v2.tauri.app/security/capabilities/) defines permissions to examine in native IPC tests.
- [Tailwind CSS compatibility](https://tailwindcss.com/docs/compatibility) and [source detection](https://tailwindcss.com/docs/detecting-classes-in-source-files) inform WebView and build tests.
- [Aeneas](https://github.com/AeneasVerif/aeneas) and [Hax Lean manual](https://hax.cryspen.com/manual/lean/) establish potential extraction paths for supported pure Rust, not verified coverage of this project.

## Competing implementations

1. **CSR on every platform:** least rendering machinery for the initial shared UI; selected by [D-0001](../decisions/D-0001-csr-first.md).
2. **SSR web + CSR native:** retain native delivery while optimizing initial web HTML; defer until measured under Issue #2.
3. **Remote SSR URL inside Tauri:** can reuse server HTML but introduces network availability and remote-origin security questions; not chosen for offline-first local shell startup.

## Claims to cross-check independently

- Does production Tailwind CSS render correctly in the **actual** Windows, Linux, Apple, and Android WebViews being supported?
- Do browser and Tauri client builds reference the same intended assets and respect identical UI state transition semantics?
- Do configured Tauri commands deny unauthorized calls, and does browser mode degrade explicitly?
- Does an extracted Rust reducer preserve the intended invariant in Lean without `sorry`, unapproved axioms, or assumptions that make the result vacuous?

## Evidence status

**Unknown:** platform launch results, packaging footprint, cold-start latency, WebView behavior, signed release reproducibility, and real implementation-linked proof coverage. No measurements are recorded in this note.

## Revisit when

New upstream breaking changes, representative device tests, profiling data, or failed extraction provide stronger evidence. Preserve independent counterexamples as dated observations rather than overwriting this research question.

## Relations

- **informs-and-challenges**: [D-0001: CSR-first decision](../decisions/D-0001-csr-first.md)
- **baseline-observed-in**: [O-0001: Scaffold snapshot](../observations/O-0001-scaffold-snapshot.md)
- **to-be-tested-by**: [Issue #1](https://github.com/kmosoti/rust-ui-template/issues/1), [Issue #2](https://github.com/kmosoti/rust-ui-template/issues/2)
