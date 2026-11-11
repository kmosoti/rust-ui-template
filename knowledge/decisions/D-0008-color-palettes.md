---
id: D-0008
type: decision
status: implemented
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# D-0008: Session-wide semantic color schemes

Add the user's six palettes alongside Nocturne. Preserve the exact first four
hex pairs; choose documented project shades for the two descriptive directions.
Keep Nocturne geometry/default, original artwork and shared Leptos ownership.

Preferences gets a labeled native select; an app-owned signal applies a root
attribute so all routes and the focused skip link inherit one semantic system.
Choice survives navigation and resets on reload. No storage/IPC/new dependencies.
Use separate action-ink and brand-hover, because the canvas is not a safe button
foreground in light themes. Add info/success/warning/danger foregrounds paired
with text and distinguish decorative hairlines from required control boundaries.
Do not duplicate request rules; colors present existing tracker/message states.

Verify computed contrast across surfaces and interactions, axe/geometry for all
palettes/routes, enlarged settings text and native light-mode navigation. Normal
text >=4.5:1; relevant non-text boundaries >=3:1. Neither a palette nor smoke
checks prove full accessibility conformance. Color proportions/numeric shade
counts are heuristics; ship only needed tonal roles, extend when justified.

Alternatives: palette-card gallery crowds settings; header popover adds focus
complexity; persistence or OS matching adds unrequested behavior. Revisit when a
product requires persistent preferences, alternate imagery or additional states.

## Relations

- **extends**: [D-0007](D-0007-default-workspace-design.md)
- **observed-in**: [O-0008](../observations/O-0008-color-palettes.md)
- **specification**: [brief](../../design/color-palettes-brief.md)
