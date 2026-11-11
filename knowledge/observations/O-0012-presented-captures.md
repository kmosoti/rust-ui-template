---
id: O-0012
type: observation
status: observed
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

`git diff --check` passed. PR run [42976224567](https://github.com/kmosoti/rust-ui-template/actions/runs/42976224567)
passed Android instrumentation. Independent review inspected downloaded device
artifact 13836465371: the production library, landscape and portrait WebView
captures show the expected content across the viewport; `keyboard-display.png`
shows both the focused field and keyboard. Capture diagnostics report zero sampled
background mismatches for each. These are observations of one API 36 emulator run,
not a guarantee for every compositor or device. No physical-device, minimum API or
screen-reader claim is made.

## Revisit when

A new compositor/font/inset may expose an incomplete sample criterion. DOM geometry
alone does not prove displayed pixels.
