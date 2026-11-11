# Color schemes

Open **Preferences → Appearance → Color scheme**. Selection affects the entire
workspace and survives navigation for this app session. Reloading restores
Nocturne; no storage, server, native command or OS-preference detection is used.
The native select supports keyboard selection and sets the correct light/dark
control color-scheme. Nocturne remains the default geometry and identity.

| Scheme | Exact anchor colors / project choices | Mode |
| --- | --- | --- |
| Nocturne | Lavender #B69CFF / charcoal #111216 | Dark |
| Signal Blue & Porcelain | #0057FF / #F8F7F4 | Light |
| Butter Yellow & Royal Iris | #FFF275 / #3A0CA3 | Dark |
| Lime Spark & Graphite | #B6FF2E / #23262F | Dark |
| Sulu & Deep Fir | #9FE870 / #163300 | Dark |
| Blooming Romance | Burgundy #7A2849, soft pink #F8E7ED, muted purple #655064 | Light |
| Desert Dusk | Cognac #A46542, muted orange #E6A16F, purple #261B29 | Dark |

The first four pairs preserve the user's hex values. The last two are project
interpretations of descriptive palettes, not claimed canonical upstream hexes.
Original artwork remains unchanged. Supporting surfaces/foregrounds are chosen
for readability rather than recoloring every element to a brand hue.

## Production previews

Actual browser captures: [Signal Blue light workspace](images/palette-signal-blue.png) ·
[Butter/Iris dark workspace](images/palette-butter-iris.png). The original artwork
is unchanged; selected colors affect the shared UI.

## Semantic contract

[styles/input.css](../styles/input.css) defines Nocturne and component recipes;
[styles/palettes.css](../styles/palettes.css) overrides their semantic variables.
Both compile into the single production Tailwind stylesheet. Avoid per-route
hardcoded colors and dynamic utility strings. The app-level Appearance signal
is presentation state, separate from app-core request rules and native authority.

- canvas/sidebar/panel/raised define four surface tones; ink/muted are text roles.
- brand, brand-hover and action-ink explicitly cover actions, hover, selection
  and skip-link text. Light backgrounds require independent button foregrounds.
- info/success/warning/danger are readable foregrounds with text labels; request
  validation errors use danger, cancellation warning, pending info and result
  success. Color is never the sole way to convey a state.
- control is a required boundary; hairline is decorative and is not a substitute
  for a control outline. Brand focus outlines have visible offset and contrast.

The suggested 60–30–10 proportions and 5–9 shade scales are design heuristics,
not accessibility requirements. This slice supplies the tonal roles actually
used; extend scales when a real component needs them. Feedback conventions do
not imply that every green brand accent announces success.

## Verification scope

The browser runner resolves real computed colors and checks normal text at
4.5:1 on all four surfaces, button text on brand/hover at 4.5:1, and required
boundaries/focus colors at 3:1. It sends real pointer hover, checks the rendered state against hover capability
(and always checks the hover token contrast), then exercises native-select keyboard
input, visible focus and session navigation/reset. Every palette is checked on
four routes at 1440/320px with axe and geometry, plus settings at 200% text.
Captures and contrast JSON reports are uploaded as browser evidence. Native CI
also checks light-mode switching and navigation in the installed WebKit app.

These are scoped smoke/contrast checks, not complete WCAG conformance or a
universal guarantee for arbitrary opacity/background combinations, disabled
states, future components, OS-rendered option popups or color-vision differences.
The [WCAG 2.2 contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
and [non-text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)
remain authoritative. User-provided [Figma inspiration](https://www.figma.com/resource-library/color-combinations/)
is inspiration, not the source of the project-specific last-two hex choices.

See [brief](../design/color-palettes-brief.md),
[D-0008](../knowledge/decisions/D-0008-color-palettes.md) and
[O-0008](../knowledge/observations/O-0008-color-palettes.md) for decisions,
executed evidence and limitations.
