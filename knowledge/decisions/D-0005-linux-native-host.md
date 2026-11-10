---
id: D-0005
type: decision
status: proposed
updated: 2026-11-10
added_by: agent
human_ratified: false
---

# D-0005: First Linux Tauri host and versioned host boundary

Embed the existing Leptos CSR production assets in Tauri 2.12.5. Keep the
native packaging workspace and generated lockfile separate from the root
browser workspace so GTK/WebKit dependencies do not become browser prerequisites.
A small shared `app-contract` crate owns serializable request/response types;
`app-core` remains dependency-free. The client provides a host-reader function
to the UI. Browser mode returns Unsupported; the Tauri adapter invokes app_info.

The request and response carry schema_version 1. Rust rejects unsupported
versions and malformed/unknown input fields. The informational command returns
only application name, version and OS family; it accepts no path or OS action.
Register it in `tauri_build::AppManifest::commands` and grant its generated
allow permission only to the local Linux main window. No default broad core,
filesystem, shell, remote-origin or dynamic ACL grants are added.

Production CSP restricts scripts and styles to bundled assets, permits WASM
compilation and the Tauri IPC transport, and blocks arbitrary inline scripts.
A separate merged test configuration adds a restricted window without changing
the production command or its capability. The denial test must exercise the
real registered command from that unprivileged window, not a nonexistent command.

Alternatives: adding GTK dependencies to every browser check was rejected;
copying or forking the UI for native was rejected. Mobile and other desktop
hosts remain subsequent slices. Revisit the contract when introducing a second
capability, persisted data or another transport; no persistence/sync is implied.

## Relations

- **extends**: [D-0004](D-0004-node-free-tooling.md)
- **observed-in**: [O-0005](../observations/O-0005-linux-native-host.md)
