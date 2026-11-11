---
id: O-0009
type: observation
status: local-checked-ci-pending
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# O-0009: Native library entry preparation

Started from clean develop c3ca50f and no open PR. Read working instructions,
architecture/contributor guidance and relevant D5/O8 records, plus cloud-runtime
package/network/Docker references. Existing develop browser/core CI was green.

Moved unchanged command/startup into lib.rs with mobile_entry_point gated on
mobile, exposed run, added lib/cdylib/staticlib crate types and retained the thin
Linux binary name. Scoped x11/dbus features to Linux. No host wire, permission,
UI or app-core change. Android is not yet built by this slice.

Local native GTK/WebKit headers remain unavailable; Java21 and Docker daemon are
available, /dev/kvm and Android SDK are absent. Linux installed regression is
required in GitHub CI. Formatting and locked metadata checks are recorded with
the PR; subsequent execution evidence is linked from the next packaging record.

## Relations

- **observes**: [D-0009](../decisions/D-0009-linux-android-delivery.md)
- **continues**: [O-0008](O-0008-color-palettes.md)
