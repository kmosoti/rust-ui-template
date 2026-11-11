# Dependency policy and checks

Both Cargo workspaces use the permissive SPDX allowlist in `deny.toml`; unknown
licenses, unapproved licenses, unknown registries/git sources and registry
wildcard dependencies fail. Internal path dependencies are allowed. Multiple
transitive versions are allowed because ecosystem version convergence is not a
security guarantee. Build dependencies receive the same checks as runtime ones.
The reviewed parent-source patches in [vendor ownership](../vendor/README.md)
remove MPL-only Rust edges while retaining Tauri/CSP behavior and licenses.

```sh
python3 scripts/setup_security.py
python3 scripts/check_security_policy.py
.tools/cargo-deny --locked check
.tools/cargo-deny --manifest-path apps/native/Cargo.toml --config deny.toml --locked check
python3 scripts/scan_android_dependencies.py
```

Setup supports Linux x86_64, downloads official cargo-deny 0.20.2 and OSV-Scanner
2.7.1 and verifies committed upstream SHA-256 pins. Valid archive caches avoid
repeat downloads; extracted executables are recreated from verified bytes.
Partial/corrupt caches are replaced only after downloaded bytes pass checks.
No Node/npm, external design service or signing credential is needed.

## Advisory exceptions

Two specific Rust maintenance advisories (paste and proc-macro-error) have
rationales and expiry dates in `security-exceptions.json`. They are archived
compile-time macro dependencies required by Leptos/GTK, not identified security
vulnerabilities. The policy checker fails at expiry, requires the exact same IDs
as cargo-deny and rejects an actual MPL-only fixture. Their advisory output is
retained; no MPL or vulnerability exception is granted. Review upstream options
before 2027-02-09 rather than silently renewing the records.

## Android dependencies

Every tracked Gradle lockfile is copied byte-for-byte to a temporary directory
under OSV's supported `gradle.lockfile` name. The scanner resolves no manifests;
its report paths are mapped back to source locks and a SHA-256 lock manifest is
retained. Application, Tauri, buildscript and buildSrc dependencies are included.

The settings-time security resolution rules update vulnerable AGP/lint transitive
libraries within compatible major APIs; Kotlin's Gradle plugin is pinned to
stable 2.4.21. Gradle generated the locks and SHA-256 verification metadata.
Normal Android CI uses strict dependency verification, never update mode.
OSV produces both vulnerability results and a dependency-license inventory.
`UNKNOWN` licenses are reported honestly and require investigation; the strict
permissive-only policy here applies to Rust, not an assertion that every SDK,
system library or Android tooling dependency is permissively licensed.

## CI and release boundaries

Security checks run on source/policy PRs and develop pushes with read-only tokens.
The dedicated cache includes registry sources and verified tool archives, not
compiled application targets, Gradle homes, SDK snapshots or signing material.
Only successful develop pushes save trusted caches. PRs restore but cannot save.
Cold and repeated setup durations are attached as evidence; checks run on hits.

A weekly schedule is declared, but GitHub schedules run only from the default
branch. The current default is main, and this work does not change or merge main.
Weekly/manual default-branch activation is a release-promotion prerequisite in
[#24](https://github.com/kmosoti/rust-ui-template/issues/24); PR/develop checks are
active independently. Do not claim an operational weekly monitor before that.
