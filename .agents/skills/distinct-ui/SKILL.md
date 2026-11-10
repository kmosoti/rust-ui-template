---
name: distinct-ui
description: Design or change this template's Leptos UI with explicit task hierarchy, spatial alternatives and rendered desktop/mobile verification. Use for UI creation, redesign and layout changes; no external design account required.
---

# Distinct UI from a concrete brief

Follow AGENTS.md. Do not use Superdesign. Use Leptos, the standalone Tailwind CLI,
Trunk and the existing Chromiumoxide runner. Keep app-core and host authority
boundaries intact. A visually unusual UI still needs to be usable and accessible.

## 1. Establish the brief before writing view! macros

Read the target route/components, styles/input.css, docs/architecture.md and the
relevant knowledge. Record `design/<feature>-brief.md` using
[the brief template](references/brief.md). Identify the user, primary task,
important information, real/sample content, states, viewport constraints and
existing brand. Discover facts from the code; ask only for consequential missing
preferences. Use reasonable recorded assumptions where authorization is clear.

Propose **three structurally different directions**, not three accent colors.
Compare reading order, information density, column ratios, type scale and primary
action. Examples: editorial reading surface, dense operations console, focused
single-task workflow. Choose by the task; novelty alone is not the criterion.
Do not copy a referenced product's branding or claim a measured originality score.

## 2. Lock geometry in a separate artifact/pass

Before component code, write an ASCII wireframe or grid specification with:
- Desktop region widths/ratios, alignment edges, content measure and action rank.
- Mobile stacking/reading order and which regions scroll. Use minmax(0, 1fr) and
  shrinking children where appropriate; never blindly freeze desktop widths.
- Empty/loading/error/success and long-content states, focus order and landmarks.
- Palette/type/radius tokens and the reason each surface or divider exists.

The spec and implementation are distinct passes, even if completed in one work
session. Do not add an approval pause unless the user asks for one or a genuinely
blocking preference remains. Make the chosen assumptions reviewable.

## 3. Implement the chosen system

Prefer semantic tokens and complete, statically discoverable Tailwind classes.
`design/restricted-theme.css` is an **optional starting profile**, not a universal
look and not imported into the existing demos. Adapt its tokens to the brief.
It resets color/radius namespaces; missing utilities produce no CSS, not compiler
errors. Run `python3 scripts/check_design_profile.py` when changing that profile.
Namespace reset is build-wide, not isolated to one route. If adopting it for a
project/build profile, migrate all affected shared components/routes and verify output;
never silently apply it to components still using stock palette classes.

Avoid these defaults unless the brief documents a functional reason:
- Nested decorative cards; large rounded/shadowed p-6 panels as the only hierarchy.
- Tinted-circle decoration, gratuitous gradients, and repeated decorative icons.
- Centered application heroes and symmetric three-card feature rows by reflex.
- One weight/size for all headings; monospace everywhere; fixed-height text clipping.

Use grouping, whitespace, proportional areas, typographic scale and tabular
alignment when they clarify the task. Borders around actual controls, tables,
dialogs and selected regions are legitimate. Large radii or symmetry may also be
appropriate; record the rationale rather than inventing a dogmatic ban.
Do not add tailwind_fuse or another styling dependency by default—it is not
currently installed. A variant abstraction must own a distinct repeated concern.

## 4. Close the rendered loop

Build the **production** CSS/WASM assets. Run the Chromiumoxide suite; it writes
screenshots and `artifacts/layout-*.json` at desktop, 390px and 320px widths.
For a new route, add it to the runner’s audit cases or run equivalent instrumented
captures for that route; passing only old demo routes does not verify new UI.
Inspect actual screenshots using the available image viewer. If no image-viewing
capability is available, record that visual critique is unperformed, not passed.
For interactive/state work include relevant error, pending and long-content states.

Annotate peer regions with `data-layout-region`; sibling-region overlap checks
cover those annotations, not every visible pair of elements. Check region counts.
Use the metrics as diagnostics: page overflow, clipped text and controls escaping their parent are failures;
optical weight, overlap, nesting and action prominence still need judgment. Mark
intentional two-dimensional regions/overlays with a narrowly scoped
`data-ui-overflow="allow"` / `data-ui-overlap="allow"` and a
`data-ui-reason` when needed. Do not hide a real defect with a broad exception.
Axe contrast/semantics checks complement screenshots; neither proves full WCAG
conformance. Check keyboard focus, 200% text/400% zoom reflow as applicable,
reduced-motion behavior and mobile reachability. Do not set `h-screen overflow-hidden` globally; explicit scrolling regions and exceptions need tests.

Write a critique with coordinates/affected elements and concrete changes:
“at 320px, number input exceeds the form content box by 8px; allow it to shrink”
is actionable. “Make it less generic” is not. Check hierarchy against the primary
task and compare the output with the selected spatial spec. Make at most two
focused correction passes, rerun affected checks, then disclose unresolved issues.
Do not spend unlimited model calls or claim that novelty/accessibility is proven.

## 5. Hand off evidence

Record choices, screenshots, metrics, executed commands and limitations in the
brief and knowledge/ with agent provenance. Update the overall architecture when
boundaries change and include the focused change diagram in the PR. Preserve the
independent standard/medium review policy; never use max/ultra reviewers.
The existing demo pages are examples, not a mandatory visual system for new work.
