---
id: D-0010
type: decision
status: accepted-for-implementation
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Permissive Rust dependency policy

## Decision

The user selected permissive Rust dependencies only and reviewed parent-crate
patches while retaining Tauri 2. Enforce this across resolved application/build
Rust dependencies, not only direct/runtime dependencies. Preserve all upstream
licenses/notices; do not copy or relabel MPL code. System GTK/WebKit and SDK/tool
licenses are a separate inventory, not a claim that all installed software is
permissive. New metadata/advisory checks must include both Cargo workspaces.

## Observed and implementation

The original native graph includes MPL-only cssparser, selectors, cssparser-macros,
dtoa-short and option-ext. Active paths include Tauri build/codegen, dirs-sys and
Wry's Android initialization fallback. The root browser graph has no MPL-only
packages. Five permissively licensed parent sources are retained with archive
checksums, original file hashes and reviewable patches. HTML5 parsing/serialization
uses html5ever/markup5ever_rcdom, direct traversal replaces CSS selectors, and
Option comparison replaces option-ext. No application IPC API/schema change.

## Risks and alternatives

Local patches require security review and ongoing upgrade ownership. rcdom is a
basic unsupported DOM crate: its integration is our responsibility. Legacy Tauri
internal DOM representation compatibility is explicitly limited. Allowing MPL
with notices or waiting indefinitely for upstream were alternatives; the user
selected patches. Disabling CSP or using regex HTML rewriting was rejected.

## Revisit when

Upstream removes these dependency edges or changes HTML/CSP/Android behavior.
Prefer removing the patches after equivalent permissive upstream integration is
validated. See [vendor ownership](../../vendor/README.md) and
[O-0013](../observations/O-0013-permissive-native.md).

## Serializer integration correction

The initial four-parent implementation exposed an upstream rcdom serialization
omission: template fragment children were dropped. A fifth small permissively
licensed source patch makes the existing serializer traverse those children.
Actual Wry/Tauri regressions demonstrate both preservation and inert-template CSP
behavior. This extends the patch set without copying/relabeling MPL code.
