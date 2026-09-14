# The illustration library: `lib/palette.py`

Everything a scene needs beyond Manim itself, in one file, imported with `from lib.palette import *`. It is small
on purpose: helpers exist where the same drawing was needed three times or where Manim has a trap worth hiding.
Compose Manim directly for everything else; the patterns section shows how the reference deck does it.

## Colours

| name | hex | use |
|---|---|---|
| `BLUE` `YELLOW` `VIOLET` `TEAL` `RED` `GREEN` `ORANGE` | accents | a talk assigns each ONE meaning in `objects.py` |
| `DIM` | #4A4F5C | shapes out of focus: outlines, empty slots, faded members. Never text. |
| `MUTED` | #8B93A5 | small text: names, units, axis labels. `label()` substitutes it when asked for DIM. |
| `TEXT` | #E8E8E8 | body text and titles |
| `CAPTION` | #B9BFCC | the footnote at the bottom of a step |
| `BG` | #0f1116 | background, for masks that hide things |

In `objects.py` give the accents names that carry the talk's meaning and register the nouns:

```python
from lib.palette import *
PROMPT, OUTPUT, WEIGHTS, CACHE, HOT = BLUE, YELLOW, VIOLET, TEAL, RED
set_thread({"prefill": PROMPT, "decode": OUTPUT, "weights": WEIGHTS, "cache": CACHE})
```

`set_thread` makes `title()` and `caption()` colour those words (whole words, any case) wherever they appear.

## Layout constants

`FRAME_W, FRAME_H = 14.22, 8.0`; the origin is the centre. Titles sit at the top edge (`title()`), content between
`CONTENT_TOP = 2.6` and `CONTENT_BOTTOM = -2.3`, captions around `CAPTION_Y = -3.3`. Put fixed furniture at fixed
coordinates with `move_to([x, y, 0], aligned_edge=LEFT)`; use `next_to` only for a label attached to an object.

## `TalkSlide`

```python
class MyScene(TalkSlide):
    def construct(self):
        t = title(self, "How a resolver finds an address", "2  the lookup")
        ...animations...
        self.next_slide("""Note the speaker reads for the step that just played. One paragraph.""")
        ...
        self.finish("""Note for the last step.""")
```

`next_slide` ends a step (a click) and records its note; `finish` ends the scene with a short hold. Each scene
class becomes one continuous video with pause points; scenes play in file order (`s00_`, `s01_`, ...), classes in
file order within a file. The scene name (CamelCase) is shown in the presenter as the section name.

## Text

| helper | what it does |
|---|---|
| `label(s, size=30, color=TEXT, width=0, thread=False)` | text in the talk font. `width` wraps to that many scene units. `thread=True` colours the talk's nouns. Never below size 12. |
| `small(s, color)` | text for a zoomed view (render at 20, scale 0.3). Use inside a 0.4 camera zoom. |
| `title(scene, s, move)` | the scene title at the top with the move name in small type above it. Returns `VGroup(title, kicker)`. |
| `caption(scene, s)` / `swap_caption(scene, old, s)` | one quiet line pinned to the frame bottom. Set before the step's animation; swap only at a step boundary. Prefer labels next to objects. |
| `pin(scene, m, buff)` | keep any mobject at the frame bottom through camera zooms. |

Text does not wrap by itself; use `width`. `Text.become()` with a different string produces garbage mid-animation:
fade the old label out and a new one in, or `Transform` to a new label of the same length class.

## Objects

| helper | what it draws | notes |
|---|---|---|
| `tokens(n, color, side, gap)` | a row of squares | tokens, messages, requests, records |
| `box(w, h, name, color)` | rounded box with a name inside its top edge | a machine, an engine, a service; `box[0]` is the rectangle |
| `node(name, color, w, h, sub)` | a named component with an optional subtitle | system diagrams; `node[0]` rectangle, `node[1]` name |
| `arrow(a, b, text, color)` | an arrow between two objects' edges with a small label | build it after both ends are in place |
| `travel(scene, a, b, color, flash=...)` | a dot travels from a to b and vanishes, optionally flashing b | the unit of motion in every system picture |
| `column(n, color, cell, op)` | a vector: a thin column of cells | shades vary per cell to look like numbers (see the reference deck's `vector()`) |
| `grid(rows, cols, color, cell, op)` | a matrix or a memory | indexed `grid[row * cols + col]` |
| `dot_grid(n, cols, color, radius)` | n dots in rows | a population whose members change one by one |
| `Gauge(name, color, height)` | a vertical gauge; `.set(level)` returns the animation | red above 0.9 |
| `Counter(name, value, unit, color, size, decimals)` | a number with unit and name; `.to(value)` counts | the name must carry unit and clock |
| `Bars(heights, width, gap, color)` | a small bar chart | `Transform(bars, Bars(new))` to redraw |
| `timeline(y, x0, [(kind, length)], colors)` | a horizontal bar of labelled segments | time along x |

Anything a talk needs three times that is not here goes in the talk's `objects.py` (the reference deck's `GPU`
drawing lives there). If a second talk needs it, move it here and document it in this file.

## Patterns from the reference deck

**Grow, never replace.** Keep every object in a variable; later steps add to the same picture. To make room, move
or shrink what is there with an animation the audience can follow, never by removing and redrawing.

**Zoom to open.** Camera zoom with `self.camera.frame.animate.scale(0.4).move_to(...)`; in the same play, fade what
falls outside the zoom, stretch the box that is being opened, and move the object of interest into it. Draw the
contents; group everything drawn (`layer = VGroup(...)`). On the way out: first `FadeOut(layer)` alone (0.4 s), then
zoom out while the box shrinks back and the wide view fades in. Captions are pinned with `pin()` so they survive.
See `s01_mechanics.py`.

**The sweep.** One row of a matrix lights with the vector, one output cell fills; repeat for every row at speed.
"Producing one output vector reads the whole matrix" is learned by watching, not by being told. Dim-again
animations must be built after the light-up play (see `docs/manim.md`).

**The fan.** A read over many stored items: `Line`s from the reader to every item, the items brighten with
`LaggedStart`, then squares from the items `ReplacementTransform` into the result vector.

**Counters and curves together.** Feed a `ValueTracker` from a list of measured points and `Create` the curve
segment by segment inside the same `play` as the counters and gauges, so picture and numbers move as one thing.
One click per measured point turns a picture into an argument.

**The conveyor.** Time along x: each step is a column whose width is its duration; new columns enter at the right
and everything shifts left with `rate_func=linear`; old columns slide under a background-coloured mask
(`Rectangle(fill_color=BG).set_z_index(1)`, labels at z_index 2) and are removed once behind it. Each request keeps
its colour from queue to completion; empty slots are hollow cells. See `s03_batching.py`.

**Define by contrast.** Show two things side by side that make a term concrete before writing the term down once:
latency and throughput with a single request, where they are the same number.

**Replay at speed.** After the slow first demonstration, the second instance (next layer, next request) plays the
same picture at `rt=0.07` inside the same step. A helper that takes the position and returns the drawn group makes
this a two-line replay (`replay_layer` in the reference deck).

**Population dots.** `dot_grid(100)` with members recoloured by `LaggedStart` for "4 of 100 changed, 2 each way".
Legends in plain words ("answer changed from wrong to right"), never in jargon.

**Masks over opacity.** To hide things that scroll away, slide them under a `BG`-coloured rectangle with a higher
`z_index` rather than animating opacity: `set_opacity` also fills hollow shapes.

**Named simplification labels.** When a drawing shows fewer parts than the real thing, the label says both numbers:
"drawn as 8 experts with 2 chosen (the model has 128, with 8)".
