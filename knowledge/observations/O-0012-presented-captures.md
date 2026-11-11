---
id: O-0012
type: observation
status: validation-pending
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Presented Android capture validation

## Observed

Downloaded develop run42960500792 device artifact13829158493. Functional DOM,
IPC, axe, IME and rotation geometry assertions passed. The library screenshot
was blank and landscape showed a partial portrait-width surface. Independent
standard/medium review confirmed this limit. Keyboard and portrait captures
contained content. See [O-0011](O-0011-android-apks.md).

## Change under validation

Instrumentation copies the owned window's WebView rectangle using PixelCopy.
It validates viewport scale, DOM-derived opaque background samples across the
viewport (including its right side), and visible text-region color variation.
Two consecutive valid captures are required within ten seconds. Copy timeouts,
missing frames and failed PNG compression fail explicitly; failed images and
sample diagnostics are retained. Only captures are polled, not functional tests.
No production UI behavior changes. `keyboard.png` is the validated WebView crop;
`keyboard-display.png` separately preserves the entire display and IME for manual
inspection. It is not covered by the crop's pixel checks. PixelCopy bitmaps are
released on unsuccessful attempts too; callback waits use the remaining deadline.

## Execution and limits

`git diff --check` passed. Fresh emulator CI and inspection of new captures are
pending. No physical-device, minimum API or screen-reader claim is made.

## Revisit when

Fresh CI establishes capture behavior or a new compositor/font/inset exposes an
incomplete sample criterion. DOM geometry alone does not prove displayed pixels.
