# CSR foundation milestone on develop

This is an engineering milestone for Issue #1, not a published release, signed
artifact distribution or promotion into main. Final completion evidence is linked
from [the handoff](issue-1-handoff.md) and knowledge records.

## Delivered behavior

- One Leptos CSR component tree with a dependency-free Rust core, browser client
  and Tauri2 native host. SSR/hydration remains separate in #2.
- Accessible latest-response example with slow/fast/cancel actions, stale-result
  rejection, real task cancellation and explicit reactive-owner cleanup.
- Nocturne workspace/launcher design plus six alternate palettes, production
  local assets and one standalone Tailwind4 stylesheet bundled by Trunk.
- Chromiumoxide production root/subpath, navigation, cancellation, layout/keyboard
  and axe accessibility smoke coverage without Node/npm or Superdesign.
- Linux x86_64 Ubuntu24.04 DEB and Fedora44 RPM installation/reinstallation,
  packaged launch, removal, typed app_info validation, CSP and real ACL denial.
- Android test-signed ARM64/x86_64 APK builds and API36/Android16 x86_64 emulator
  tests for bundled startup, IPC/denial, keyboard, navigation/Back, rotation and
  lifecycle. ARM64 runtime has not been exercised.
- Permissive Rust dependency gates with reviewed Tauri/Wry/directory patches,
  dated maintenance exceptions and Cargo/Gradle advisory checks.
- An independent clean frontend build/test gate compares production asset bytes.
  Only a passing report establishes that property for its recorded source/runner.

## Boundaries and open risk

Windows/macOS/iOS are deferred to #22. Wayland, hardware GPU, Linux ARM64,
physical/minimum-API Android devices, minimum browser/WebView runtime checks and
manual assistive-technology coverage are #23. Automated accessibility smoke is
not full conformance testing. A previously observed Linux WebDriver connection
reset remains documented; no sandbox disabling or blanket assertion retry hides it.

Linux packages are unsigned; Android APKs use test/debug signing. Frontend asset
reproducibility does not establish signed/native package byte determinism.
Production signing, provenance/distribution and human main promotion are #24.
The new weekly security schedule activates only after its workflow reaches the
default branch through that release process; PR/develop checks run independently.

Rust dependencies use an explicit permissive allowlist. Two compile-time macro
maintenance exceptions expire 2027-02-09 and are tracked in #28; they waive no
MPL license or identified vulnerability. Android's separate license inventory
reports unknown entries explicitly. Vendored source patch security/upgrade
ownership is described in the vendor guide.

The actual Rust core extracts with the pinned Charon/Aeneas preset, but Aeneas
translation, Lean/Lake checking and theorem/axiom/mutation audits remain #27.
**No formal verification claim is made.** Persistence, sync, a production game
launcher and server rendering are not implemented by the example UI.
