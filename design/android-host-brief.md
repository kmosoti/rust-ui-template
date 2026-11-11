# Android host geometry

Audience/task: a developer installing the template's debug APK, using the same
library, lab, preferences and About screens offline. Content remains sample;
Nocturne/seven session palettes and shared Rust ownership are unchanged.

Alternatives: (1) reuse the wrapping workspace rail and document scroll;
(2) introduce a fixed bottom navigation and nested scrolling; (3) collapse into
a modal drawer. Choose (1): preserves reading/focus order without a parallel
mobile shell or overlay authority. Native host owns only system/IME insets.

```
portrait/landscape, Android content bounds
+ system top inset --------------------------------+
| wrapping workspace brand + navigation (scrolls)  |
| context bar                                     |
| main: library / lab / settings / about           |
| footer                                          |
+ max(system bottom inset, visible IME) -----------+
```

Use root-view padding for system bars and IME, no extra CSS safe-area padding.
Layout remains natural document scroll; minmax/shrinking children already apply.
Coarse pointer controls: minimum48CSSpx high, nav links48px; shared semantic
tokens, no new palette/type/radius. Existing text/error/loading/empty states and
native focus order stay intact. Host Back follows WebView fragment history.

Acceptance: production Android screenshots portrait/landscape, keyboard show/
hide, navigation and background/foreground preserve palette, no horizontal
page overflow/clipped text/escaped controls. Existing browser screenshot/axe/
text-zoom suite must pass after shared CSS. Local emulator unavailable (/dev/kvm
absent); actual device critique remains pending CI evidence, never assumed.
