# Selectable color schemes

User asks to add six supplied color directions to the existing Nocturne default.
Keep workspace geometry, native authority and app-core rules intact. First four
pairs retain exact hex anchors; Blooming Romance/Desert Dusk have descriptive
colors, so chosen hex values are project interpretations, not upstream standards.

## Alternatives and selected geometry (before implementation)

1. **Preferences select + sample feedback (chosen):** one labeled native select,
   palette pair description and small text-labeled feedback previews before the
   existing profile form. No new top-level route or permanent shell controls.
2. **Seven palette tiles:** visually useful but a large repetitive grid overwhelms
   a narrow settings view and introduces many buttons into a simple form.
3. **Header switcher/popover:** discoverable everywhere but crowds mobile shell
   and needs more keyboard/focus handling than a native select.

Within existing max-w-3xl settings route: Appearance h2, label/select (max-w-lg,
100% shrinking on mobile), session scope note, base-pair note, four feedback labels
wrapping naturally. Then existing profile form. No nested decorative cards.
Palette affects root workspace/skip link and every route. It survives route
unmounts but resets on full reload; no storage/API/IPC. Nocturne remains default.
Select uses native keyboard behavior, visible focus and accurate color-scheme.

## Color system

Semantic canvas/sidebar/panel/raised/ink/muted/control/hairline tokens, separate
brand/action-ink/brand-hover, and info/success/warning/danger foregrounds. Dark and
light schemes receive independent readable foregrounds; a light canvas cannot
also be assumed to be readable button text. Selection and focused skip-link use
explicit action-ink. Status meanings are paired with text, never color alone.
Nocturne geometry/artwork remains identical across palettes; the artwork is not
recolored. Color proportions and 5–9-step scales are design aids, not WCAG rules
or prerequisites; ship only tonal roles actually used and check their real pairs.

## Verification

Change schemes through the actual select/event; assert application session state
survives navigation and reload resets. All seven at desktop and 320px, four routes,
axe + actual rendered token contrast (including hover/focus and control boundaries),
layout geometry and PNGs. Keep original stale/cancel/cleanup/subpath/native checks.
Test semantic error/cancel/result state labels. Include all schemes at 200% text
on preferences. Bounds: browser smoke is not full accessibility conformance;
no persistent theme, automatic OS preference or platform-support expansion.

## Executed critique

All seven variants retain the same rail/content alignment and artwork hierarchy.
Viewed Signal Blue library at 1440px and Preferences at 320px, Desert Dusk
Preferences at 1440px, and Butter/Iris library at 1440px. The light scheme's blue
CTA stays stronger than secondary labels; on mobile Appearance fits the existing
288px content width and feedback labels wrap into two rows. Desert Dusk uses
cognac separators and orange actions against purple without changing layout.
Butter/Iris is intentionally more saturated, as requested; the neutral artwork
remains a distinct visual region rather than becoming yellow/purple text backing.

Computed tests caught Signal Blue/raised contrast 4.494:1. Lightened only the
raised surface, preserving exact anchor hexes. Reviewer corrected misleading
scope copy to distinguish session-wide appearance from page-local profile fields.
Native select labels remain readable and a remount assertion confirms the chosen
value is retained when returning to Preferences. The current browser reports
hover capability false: actual pointer :hover is exercised but hover style is
correctly gated, and token hover contrast is still checked. This is documented,
not counted as physical mouse/OS-popup conformance. Final full suite passed.

No artwork recoloring, new layout regions, full accessibility audit, persistence
or platform expansion is claimed. Exact commands/CI results follow in O-0008.
