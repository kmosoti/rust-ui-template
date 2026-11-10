# Default design: Nocturne workspace launcher

## Task and constraints

The user requested a default merging Obsidian's workspace structure with Riot/
Steam-style game launchers. The template user should identify available examples,
open one quickly and keep navigation/context while working. Original visual
identity; no copied logos, game artwork, fonts, accounts or external assets.
Preserve latest-request/cancellation rules, native IPC and owner cleanup.
Library data/artwork are clearly sample content; launch means opening an example,
not running or installing a game. Settings remain component-local.

## Structural alternatives considered before implementation

1. **Workspace/library hybrid (chosen):** 224px navigation, flexible content;
   compact workspace header, editorial featured landscape and library rows;
   optional narrow contextual column on wide displays. Persistent context suits
   both launcher discovery and working in a tool.
2. **Cinematic storefront:** full-width artwork with overlay navigation and
   carousel. Strong visual impact but weak information density and navigation.
3. **Dense split-pane vault:** file tree, tab strip, editor and inspector with
   equal structural borders. Strong editing affordance but weak launch hierarchy.

Choice: workspace chrome from option 3 plus the library/featured hierarchy of 1.
Use a two-column main region within the shell only when space permits; avoid a
permanent extra inspector that would squeeze the actual demo at 1200px native size.

## Geometry specification (before view code)

Desktop >= 1024px:

```text
224px workspace rail | flexible workspace (minmax(0, 1fr))
brand + workspace   | 64px context bar / current location
main navigation    | page title + sample label
example index      | featured scene: 1.5fr art / 1fr task (>= 1280px)
local/demo note     | library rows (2fr) | activity notes (1fr)
                   | slim build/status footer
```

Content max width 1240px, 32px gutters (24px intermediate), >= 0 shrinking
children. At <1024px rail becomes a top workspace header and wrapping main nav;
secondary index omitted because it duplicates main nav. At <=640px 16px gutters,
scene above details, library/activity stack, buttons wrap, no fixed page height.
At 320px all text and controls fit and navigation keeps labels. Document scrolling
and visible focus remain available. Main has a skip target; current navigation
link uses aria-current=page. Initial URL opens the library; #/ remains response
lab for existing direct links. Other fragment routes unchanged.

## Visual system

Near-black plum canvas, charcoal sidebar/panels, lavender primary action,
soft silver text, muted readable labels, pale mint readiness accents. Semantic
Tailwind tokens replace stock color/radius namespaces across all routes.
System sans for reading, monospace only for small metadata/numbers. 36-44px page
headings; compact 13-15px navigation; 16px body. Squared 6px controls, 10px feature
art clipping; thin separators, flat surfaces, no nested decorative cards.
Large feature scene is original local SVG: an observatory in a violet night
landscape. Content and launch action live beside the artwork so contrast does
not depend on pixels behind text. Reduced motion respected; no auto animation.

## States and verification

Library launch opens response lab through normal navigation. All original
pending/empty/result/cancel/error and navigation cleanup states retained.
Settings save/reset and host Unsupported/native/denied states retain semantics.
Production assets must include local SVG at root and /sub paths. Verify actual
image loading, active navigation, skip link, keyboard, axe and metrics across
all four routes at 1440/390/320; inspect screenshots. Add 200% text/reflow evidence.
Native CI verifies installed package and security behavior after styling change.
No new Rust dependencies or lockfile edits are expected.

## Rendered critique

Inspected actual production library captures at 1440px/320px and the response lab
at 390px. Desktop rail x=0..224, content x=256, artwork x=256..928 and feature
details from x=928 provide clear alignment. The library heading, original scene
and lavender action carry the hierarchy; rows use separators and notes stay
secondary. Other routes share the same canvas/type/control system.

At 320px labeled navigation wraps and the feature stacks. The image-first feature
puts the action below the initial viewport; document scrolling and keyboard
navigation keep it reachable. This is a deliberate visual-first landing tradeoff,
not an optimum-mobile-task-speed claim. The lab remains a compact functional form.

Visual inspection found missing-font boxes for diagonal arrows, outside the
geometry/axe checks. Replaced them with supported horizontal arrows. Enlarged-text
verification then exposed a fixed 24px arrow column: its 32px glyph protruded at
200%. Made the column scale in rem. Also added an explicit heading/render wait
before each zoom audit, so it cannot inspect the previous route during navigation.
The hidden skip link has a single reasoned clipping exception and a focused-size/
position test before actual keyboard activation. Final results and remaining
limitations are in [O-0007](../knowledge/observations/O-0007-workspace-launcher.md).
