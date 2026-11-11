---
id: R-0008
type: research
status: upstream-blocked-and-human-release-pending
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Macro maintenance and weekly-monitor readiness

## Observed

Queried crates.io `/api/v1/crates/NAME` and
`/api/v1/crates/NAME/VERSION/dependencies` using Python urllib with bounded
requests on2026-11-11. Inspected actual reverse dependencies with:

```sh
cargo tree --locked -i paste
cargo tree --locked --manifest-path apps/native/Cargo.toml -i proc-macro-error
```

- Leptos0.8.23 is the latest stable release returned by the registry and the
  version already locked. It directly requires paste^1.0; either_of,
  reactive_graph, reactive_stores and tachys also retain paste paths.
  paste1.0.15 is still its latest stable release. A newer unstable Leptos line
  does not establish a compatible maintenance fix for this CSR template.
- Tauri2.12.5 is latest stable and already locked. It requires gtk^0.18.
  The locked gtk0.18.2/glib0.18.5 paths reach gtk3-macros0.18.2 and
  glib-macros0.18.5, both retaining proc-macro-error1.0.4.
- gtk/gtk3-macros0.19.0 and glib-macros0.22.9 are newer stable packages, but
  gtk0.19 uses glib^0.22 and does not satisfy Tauri's gtk^0.18 requirement.
  Their dependency metadata no longer directly lists proc-macro-error; that
  observation is not a whole-graph audit or a compatible Tauri migration.
- `proc-macro-error2` 2.0.1 exists as a separately named replacement package; it
  cannot replace parent crate imports by simply regenerating the lockfile.
- `gh api repos/kmosoti/rust-ui-template --jq '{default_branch}'` returned main.
  GET contents/.github/workflows/security.yml?ref=main returned404. The current
  develop workflow declares Monday06:23UTC, workflow_dispatch, and source PR/
  develop triggers, but GitHub cannot activate its weekly schedule on develop.

## Decision and limits

Keep #28 open. Do not extend exceptions or introduce additional parent-source
forks as a speculative dependency refresh. Both current maintenance-only
exceptions continue to expire2027-02-09; **reassess by2027-01-09**. This is a
reminder date in the documented workflow, not a claim of a running scheduled
reminder. No Cargo locks or dependencies changed in this research slice.

A safe future upgrade must remove each actual graph path, regenerate locks with
Cargo, rerun both cargo-deny/advisory/license gates and full platform checks,
and review vendored patch applicability. Never substitute a version-number
comparison for that evidence or renew an exception automatically.

#24 remains open: no signing keys, release publication, main merge or default
branch change is part of this work. Follow the [activation checklist](../../docs/security.md#weekly-monitor-activation-checklist)
only during a human-approved release. Current PR/develop security checks run
independently of the inactive weekly schedule.

Informed by [O-0017](../observations/O-0017-issue1-completion.md),
[security policy](../../docs/security.md) and the vendor upgrade contract.
Revisit when upstream parent requirements change, on2027-01-09, or before a
human main release, whichever occurs first.
