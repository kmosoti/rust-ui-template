---
id: O-0022
type: observation
status: preliminary
updated: 2026-11-11
added_by: agent
human_ratified: false
---

# Linux automated keyboard and software output scale

## Reviewed plan and implementation contract

GPT-6 Astra at medium reasoning planned the scope and refined the Weston13
constraint after an actual failure. GPT-6.1 Sol at medium reasoning implements
it; a fresh independent GPT-6.1 Sol medium reviewer owns review and develop
landing. No author self-merge, main promotion, signing or release is authorized.

| Target | Retained production coverage | Added coverage |
| --- | --- | --- |
| Ubuntu24.04 | X11/Xvfb; Weston13 headless scale1 + AT-SPI | Real W3C keys on X11; explicit owned Xvfb → Weston X11 backend → Wayland client at scale2 with keys |
| Fedora44 | X11/Xvfb; Weston15 headless scale1 + AT-SPI | Real W3C keys on X11 and headless scales1/2, using advertised software `--fake-seat` |
| Restricted fixtures | Existing X11 and headless scale1 denial/AT-SPI | No multiplied fixture or scale matrix |

The keyboard sequence uses actual WebDriver W3C key actions. JavaScript only
reads/asserts state: no focus/click/value writes, dispatched DOM events or route
assignment. Semantic Tab traversal has at most40 steps and15 seconds, with the
remaining deadline applied to requests. Failures are not replayed. The skip link
must visibly focus and move focus to main without replacing the route. Real keys
launch the example, edit Number, activate Slow/Fast/Cancel, reverse an adjacent
pair, operate the palette select and preserve selection across navigation.
Pending11 immediately before Fast and observing22 before the original slow
1.5s deadline establish overlap;22 must remain after that deadline. Cancellation
must remain stable beyond its original timer. Representative focus outlines
and viewport-visible rectangles are asserted and captured. Held modifiers are
released even on failure; diagnostic/release failures preserve the original error.

Scale means an actual Weston output setting. Record requested scale, command,
version/help, output and seat protocol, logical viewport, observed DPR and PNG
pixels. DPR mismatch beyond0.05 fails; screenshot dimensions must agree with
viewport×DPR within1 pixel. Xvfb parent geometry is observed with libX11 before
execing Weston. App/WebDriver/wayland-info environments remove DISPLAY and
XAUTHORITY, and only the explicitly owned parent passes an X connection to
Weston. Software nesting is never reported as hardware GPU/real desktop scaling.

## Executed local evidence

Base: develop c3b498b937a62158551d51d87d4eee2fc37ab63b. Isolated worktree
`/workspace/rust-ui-keyboard`, branch `test/linux-keyboard-scaling`. Other
worktrees and the running `rust-ui-fedora-probe` container were preserved.
No host desktop packages were installed; Docker runtime packages were reused
(Fedora) or installed inside a task-owned Ubuntu24.04 container using the existing
`scripts/setup_linux.sh` with the Cloud CA and signed repository metadata.

First actual test used the existing production RPM
`/workspace/scratch/wayland-packages/rust-ui-native-linux.rpm`, SHA256
`52fe391d47348a5b7a1d868b340a87823dc93b869a4fbaf902527f13e814a25f`.
Its exact source is323167e3b536ecaeb3f3ba8574f7fa3e21e0db73, develop run
42982373186, artifact13837539899. A fresh download of its manifest matches both
package hashes; this is an old package probe, not current-source build validation. No application source changes
are included in this patch.

Commands (from the task worktree; driver mounted read-only):

```sh
docker run --rm --name rust-ui-keyboard-oldrpm \
  -v /workspace/rust-ui-keyboard:/work \
  -v /workspace/scratch/wayland-packages:/packages:ro \
  -v /workspace/rust-ui-template/.tools/driver/bin/tauri-driver:/usr/local/bin/tauri-driver:ro \
  rust-ui-wayland-atspi bash scripts/fedora_package_smoke.sh /packages/rust-ui-native-linux.rpm
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 -m py_compile scripts/native_keyboard.py scripts/native_smoke.py scripts/wayland_smoke.py scripts/desktop_evidence.py scripts/x11_parent.py
bash -n scripts/fedora_package_smoke.sh
git diff --check
```

Observed initial failure: Fedora Weston15 headless had no keyboard seat; real
Tab changed activeElement to the skip link but its rect remained(-1,-1,1,1),
`:focus-visible` was false and GTK logged `GDK_IS_SEAT` failures. Original failed
keyboard/runtime/compositor/driver artifacts are retained under
`artifacts/first-failure/`; the failure was not retried into a claimed pass.
Actual Weston15 `--help` advertises `--fake-seat`; explicitly enabling that
software seat resolves the observed focus failure. Upstream Weston13 source and
actual Ubuntu13 help lack that option, motivating the reviewed explicit nested
software topology rather than a silent fallback or CSS workaround.

After that change, old-RPM Fedora X11 and Wayland scales1/2 all pass six keyboard
checkpoints plus existing package/IPC/CSP/freshness checks; scale1 also passes
native AT-SPI. Slow→Fast times were0.052/0.050/0.084s; latest22 observed at
0.214/0.209/0.275s. Logical viewport1600×1100 gives DPR1/PNG1600×1100 and
DPR2/PNG3200×2200 on Weston15. No output-size adjustment was necessary there.
GTK3.24.52, WebKitGTK/WebDriver2.54.2, Weston15.0.1 and tauri-driver2.1.0.
Final Fedora command includes install/reinstall and removal/executable absence.

56 Python unit tests pass, including unreachable/deadline focus traces,
no action replay, modifier release/original failure preservation, diagnostic
write failure, scale/fixture rejection, DPR mismatch, explicit nested forwarding
and display isolation. Existing transport, owned-process and security tests remain.

Exact-base production packages were downloaded separately from Linux run
43085304140 (source c3b498b), artifact13885899263: DEB SHA256
`f2dc312cf599c4578718b613ac624cf82609a613794ea5cc07c27155b3c0f9f1`, RPM
`992040868e2a1cc8590a86aa09e580e3385e33b39f1d894d3cfe97a1916cd19c`.
`gh run download` failed on the redirected blob403; the GitHub artifact connector
succeeded. These packages are for additional known-source probes, not a substitute
for the new PR head's fresh packaged CI build. Ubuntu nested probe and hosted
current-head results/artifact inspection remain pending at this snapshot.

## Cost and external limits

One added production software Wayland scale2 session per distro; existing builds,
installed dependencies, pinned tools and runtime image are reused. No new cache
partition or duplicate restricted builds. Local/hosted incremental timing will be
recorded after execution; no speedup is claimed.

No /dev/dri, active physical desktop, human keyboard review or running Orca was
available. Hardware GPU attribution, real desktop100/200%, usability, Orca
version/settings/speech transcript remain unverified. Issue#23 remains open with
manual checkboxes unchecked, alongside Android physical ARM64/API29/TalkBack,
minimum runtime and broader transport dimensions.

## Relations

- *extends*: [O-0019 Linux Wayland/native accessibility](O-0019-linux-wayland-accessibility.md)
- *implements*: [Linux desktop evidence handoff](../../docs/linux-desktop-validation.md)
- *observed-in*: [overall architecture](../../docs/architecture.md)

Revisit after current-head hosted artifacts and real human desktop/Orca evidence.
