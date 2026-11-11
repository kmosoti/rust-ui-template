---
id: D-0011
type: decision
status: accepted-for-implementation
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Finish the browser/Linux CSR milestone with explicit Android evidence

## Decision and authority

The user selected scoped closure of Issue #1 instead of waiting for all five
native platforms. Completion includes browser/Linux and the delivered Android
test evidence, remaining security/fresh-build/frontend reproducibility checks,
source-linked extraction assessment and release/handoff documentation.
Windows/macOS/iOS development remains deferred, not silently marked tested.
No main merge, tag, publication or production signing is authorized here.

## Completion evidence and follow-ups

- #22: Windows/macOS/iOS packaging and actual launch validation.
- #23: broader Linux/Android, minimum browser/WebView and manual accessibility coverage.
- #24: signing/distribution/provenance, native package determinism and default-branch weekly security schedule activation.
- #27: compatible Aeneas/Lean translation, real theorem, axiom audit and proof mutation sensitivity after successful Charon extraction.
- #28: replace the two dated compile-time macro maintenance exceptions before2027-02-09.
- #2: optional web SSR/hydration; native stays CSR.

A passing independent clean-frontend comparison establishes configured unsigned
frontend bytes only. Charon JSON extraction establishes source feasibility only.
Platform support and screenshot quality require their actual checks/artifacts.
The agent-authored records remain unratified until the user ratifies the artifacts
explicitly; chat approval of the work does not silently set every record true.

## Review and landing

Focused PRs land into develop by an independent alternative-family reviewer when
available, otherwise a fresh independent available-model reviewer at medium.
Never max/ultra. Reviewers own rebase landing; main remains human-gated. Close #1
only after applicable final-source checks, artifact review and documentation land.

## Revisit when

Scope expands, platform evidence changes or release promotion is requested.
Supports [D-0001](D-0001-csr-first.md); preserves [D-0010](D-0010-permissive-rust-dependencies.md).
