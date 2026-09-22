# The illustration library: `lib/palette.py`

Everything a scene needs beyond Manim itself, in one file, imported with `from lib.palette import *`. It is small
on purpose: helpers exist where the same drawing was needed three times or where Manim has a trap worth hiding.
Compose Manim directly for everything else; the patterns section shows how the reference deck does it.

## The theme

Nothing in the library carries a colour, a font, a corner radius or a stroke width of its own. They come from the
active theme, loaded once at import (`lib/theme.py`; `THEME=<name>`, a talk's `.theme`, the repository's `.theme`, else
`themes/dark.json`). A talk's `.theme` reaches the library because `bin/render.sh` exports `THEME` before Manim starts;
running `manim` by hand sees only the environment and the repository's `.theme`. AGENTS.md, "Choosing the look", names the two styles and how to import a company's own.
What a scene may use:

| token | what it is |
|---|---|
| `A1` `A2` `A3` `A4` `A5` `A6` | the accent slots, each with a character every theme keeps: cool, warm, deep, fresh, growth, spice |
| `ALERT` | wrong, hot, refused, over a limit. Never a second meaning |
| `ACCENT` | `[A1..A6]`, for a talk that needs to walk them |
| `TEXT` `MUTED` `CAPTION` `DIM` | ink, small text, the footnote, shapes out of focus. `DIM` is never text |
| `BG` | the ground; a mask that hides something is drawn in it |
| `HI` | the momentary highlight of a cell being read or a line being run. Neutral, never a meaning |
| `PANEL` `CODE_STYLE` `CODE_FONT` `FONT` | what a code block sits on, its Pygments style, and the two families |
| `rad(k)` `sw(k)` | a corner radius and a stroke width derived from the theme's, so every drawing squares off or thickens together. `RADIUS`, `STROKE` and `THEME` are the raw values behind them; a scene uses the functions |
| `FILL` `SOLID` | a container's fill opacity and a filled mark's; both are fainter in the bright style |
| `MODE` | `"dark"` or `"light"`; a scene should not need to ask |
| `identity(n)` | n colours that are told apart, for a thing whose colour means only "this one": twelve requests sharing a step. Chosen by perceptual distance from each other and from the accents. Identity, not vocabulary; never a substitute for a slot |
| `ink_on(color)` | the legible ink for a label written on a solid mark of that colour: the ground or the body colour, whichever the eye can read there, pushed past both if neither clears the 4.5:1 small text needs |

Two rules follow, and `bin/check.py` enforces the first:

- **A scene never names a hue.** `objects.py` maps the talk's nouns onto slots (`USER, MODEL = A1, A3`) and the scenes
  use those names. `bin/check.py` refuses both a hue name and a literal `"#RRGGBB"`: either one is a colour that will
  not follow the theme. The library deletes Manim's own colour constants from its namespace as well, so a scene that
  reaches for `RED` fails to render rather than drawing a hue that ignores the theme.
- **A scene never invents a corner, a stroke or a fill.** Use `rad()`, `sw()`, `FILL`, `SOLID`, scaled if it must be
  smaller: `rad(0.4)`, `sw(0.56)`, `FILL * 1.6`. A literal `0.06` is what stops a style from reaching a drawing.

Runtime opacity changes (`set_fill(colour, 0.25)` to ghost something, `set_opacity` on a copy that travels) are still
written as plain numbers: they are a fraction of whatever the theme gave, not a value from it. Scale a member's own
opacity rather than replacing it when several members must fade together (see `docs/manim.md`).

## Colours

The seven accent slots and the seven roles above, as the active theme sets them. The default style (`dark`):

| name | hex | use |
|---|---|---|
| `A1` `A2` `A3` `A4` `A5` `A6` `ALERT` | accents | a talk assigns each ONE meaning in `objects.py` |
| `DIM` | #4A4F5C | shapes out of focus: outlines, empty slots, faded members. Never text. |
| `MUTED` | #8B93A5 | small text: names, units, axis labels. `label()` substitutes it when asked for DIM. |
| `TEXT` | #E8E8E8 | body text and titles |
| `CAPTION` | #B9BFCC | the footnote at the bottom of a step |
| `BG` | #0f1116 | background, for masks that hide things |
| `HI` | #F4F6FA | the momentary highlight of a cell being read or a line being run; neutral so it never reads as a meaning |

In `objects.py` give the slots names that carry the talk's meaning and register the nouns:

```python
from lib.palette import *
PROMPT, OUTPUT, WEIGHTS, CACHE, HOT = A1, A2, A3, A4, ALERT
set_thread({"prefill": PROMPT, "decode": OUTPUT, "weights": WEIGHTS, "cache": CACHE})
```

`set_thread` makes `title()` and `caption()` colour those words (whole words, any case) wherever they appear.

## Layout grid

`FRAME_W, FRAME_H = 14.22, 8.0`; the origin is the centre. Titles sit at the top edge (`title()`), content between
`CONTENT_TOP = 2.6` and `CONTENT_BOTTOM = -2.3`, captions around `CAPTION_Y = -3.3`. The alignment grid is `COLS`
(x = -6.4, -3.2, 0, 3.2, 6.4) and `ROWS` (y = 2.6, 1.3, 0, -1.3, -2.3); the gaps are `GAP_TIGHT` 0.12, `GAP` 0.25,
`GAP_WIDE` 0.5. `GUIDES=1 bin/render.sh <talk> ql <Scene>` draws the grid into the render so shots show what is
off. Put fixed furniture on the grid with `move_to([x, y, 0], aligned_edge=LEFT)`; attach labels to objects with
`next_to(obj, DOWN, buff=GAP_TIGHT).align_to(obj, LEFT)`.

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
| `title(scene, s, move)` | the scene title at the top with the move name in small type above it, written in. Only for the very first frame of a deck. Returns `VGroup(title, kicker)`. |
| `title_still(scene, s, move)` | the same title added without animation, for a scene whose first frame repeats the previous scene's last frame |
| `retitle(scene, old, s, move, extra=[...])` | the title changes in place while the first change to the picture plays; the way every scene after the first announces its move |
| `caption(scene, s)` / `swap_caption(scene, old, s)` | one quiet line pinned to the frame bottom. Set before the step's animation; swap only at a step boundary. Prefer labels next to objects. |
| `pin(scene, m, buff)` | keep any mobject at the frame bottom through camera zooms. |

Text does not wrap by itself; use `width`. `Text.become()` with a different string produces garbage mid-animation:
fade the old label out and a new one in, or `Transform` to a new label of the same length class.

## Objects

| helper | what it draws | notes |
|---|---|---|
| `tokens(n, color, side, gap)` | a row of squares | tokens, messages, requests, records |
| `box(w, h, name, color, name_align)` | rounded box with a name inside its top edge | a machine, an engine, a service; `box[0]` is the rectangle; `name_align="left"` frees the top-right corner for markers |
| `node(name, color, w, h, sub)` | a named component with an optional subtitle | system diagrams; `node[0]` rectangle, `node[1]` name |
| `arrow(a, b, text, color)` | an arrow between two objects' edges with a small label | build it after both ends are in place; ends meet the box where the centre-to-centre line crosses it (`edge_point`), so put the two objects on one axis for a horizontal or vertical arrow |
| `travel(scene, a, b, color, flash=..., carry=..., text=..., edges=...)` | a dot travels from a to b and vanishes, optionally flashing b; `carry=cell` sends a shrunken copy of an object, `text` rides above the dot, `edges=True` goes edge to edge | the unit of motion in every system picture: a request, a query and its answer, an observe and an act |
| `route(scene, [p0, p1, ...], color, carry=..., text=..., keep=...)` | a dot (or a copy of `carry`) travels a path with corners at constant speed | a journey that must follow the layout's lanes (down a corridor, along a row, into a box) instead of cutting across; `keep=True` leaves the traveller where the path ends and returns it |
| `dashed(a, b, text, color)` | a dashed line between two objects with a small label | a watch, a subscription, a heartbeat; hub-and-spoke systems are one hub and several of these |
| `column(n, color, cell, op)` | a vector: a thin column of cells | shades vary per cell to look like numbers (see the reference deck's `vector()`) |
| `grid(rows, cols, color, cell, op)` | a matrix or a memory | indexed `grid[row * cols + col]` |
| `dot_grid(n, cols, color, radius)` | n dots in rows | a population whose members change one by one |
| `Gauge(name, color, height)` | a vertical gauge; `.set(level)` returns the animation | `ALERT` above 0.9 |
| `Counter(name, value, unit, color, size, decimals)` | a number with unit and name; `.to(value)` counts; `.stop()` freezes it before a FadeOut | the name must carry unit and clock; set `tracker.set_value()` for a still frame |
| `Bars(heights, width, gap, color)` | a small bar chart | `Transform(bars, Bars(new))` to redraw |
| `timeline(y, x0, [(kind, length)], colors)` | a horizontal bar of labelled segments | time along x |

Anything a talk needs three times that is not here goes in the talk's `objects.py` (the reference deck's `GPU`
drawing lives there). If a second talk needs it, move it here and document it in this file.

## Vectors and matrices

| helper | what it does |
|---|---|
| `vector(seed, color, n, cell)` | a vector of shaded cells; same seed, same look. Use cell 0.16 to 0.2 unzoomed, 0.07 to 0.08 inside a 0.4 zoom |
| `shades(v)` / `restore(v, ops, color)` | remember a vector's shades before a highlight, animations to put them back |
| `dot_product(scene, vec, vcolor, mat, i, out, color)` | one output number, slowly: pairs light up, products fly, the cell fills |
| `sweep(scene, vec, vcolor, [(mat, out, color)], rt)` | every row at speed; several matrices swept together |

Pass `cols` when the matrix is not eight wide and `mat_color` when the matrix is not the deep accent. The light-up colour is
`HI` in every deck: the neutral extreme of the ground, near-white on the dark style and near-black on the bright one.
A highlight in an accent colour would read as that accent's meaning.

## Lists that grow

Three decks independently drew state as a list that only grows; these are the shared shapes.

| helper | what it does |
|---|---|
| `Log(x0, y, capacity, base, name, cell, gap)` | an append-only row of cells with offsets beneath on a rail: a partition, a queue, a buffer, a write-ahead log. `append(scene, colour, source)` flies an item in; `put(colour)` places one silently; `cells[i]`, `offs[i]`, `slot(i)`, `below(i)` |
| `Pointer(name, color)` | a reader's position under a Log; `place(log, i)`, `to(log, i)` returns the Transform. Replay is the pointer moving back |
| `block(text, color, w, h, size, bare)` | one item of a Stack: a coloured block with a bar and one line of text; `"role · text"` colours the role |
| `Stack(x, top, h, gap)` | a list of blocks growing downward; `append(scene, block, frm)` flies a block in from what produced it; `slot(i, h)` is where the next one goes, under the real height of those above it, so a block may grow a line; the whole list is one VGroup so a copy can travel as one thing |
| `code(source, language, size, width)` | syntax-highlighted code (the theme's Pygments style, any language Pygments knows) on the theme's panel, laid out large and scaled so spacing is exact; `block.lines[i]` per line, `block.panel` |
| `highlight_line(block, i)` | a translucent bar behind line i; add it after the code and move it down the lines while the picture does each step |

Budget 0.45 units under a Log's offsets for a pointer and its tag, and 1.4 units between stacked logs that each carry
one. Code at size 18 is about 0.13 units per character: shorten identifiers before shrinking the font. Never build
`Text` directly in a scene: every helper lays text out at `BASE_SIZE` and scales it, which is what keeps letter spacing
even; a bare `Text(font_size=14)` comes out with vanished spaces and crowded glyphs.

## Patterns from the reference deck

**The stage.** Give each talk one function in `objects.py` that builds the whole fixed picture at fixed coordinates
(the machines, the store, the loops, the counters) and returns its parts by name. Every scene calls it, adds the parts
it starts from, and grows from there: six scene files, one continuous picture, no shared Manim state. See
`talks/_template/scenes/objects.py` and `talks/kubernetes/scenes/objects.py`.

**A timer as a shrinking bar.** A lease, a TTL, a timeout: a bar under the object that shrinks to zero
(`bar.animate.stretch_to_fit_width(w).align_to(left_edge, LEFT)`), refilled when renewed. The audience sees "how much
time is left" without a number; a counter beside it carries the unit when the number matters.

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

**The list that grows.** Conversations, logs, queues and event streams are all a list that only grows: draw every item
as a block or cell that flies from where it was produced into its slot, coloured by kind, and the mechanism (a loop, a
replay, a rebalance) becomes visible as movement of items and pointers. "Every call sends the whole list" is one
animation: a copy of the list shrinks into the box that consumes it. See `talks/agents` and `talks/kafka`.

**Show the sum, not the label.** A weighted sum is copies of the summands flying into the result, each scaled by its
weight, the result filling cumulatively. A residual is the update's cells landing one by one on the vector. A stack of
identical layers is the same picture repeated smaller, not text in boxes. See `talks/transformers`.

**Code against the picture.** When a mechanism is also ten lines of code, give the code half the frame at size 18 and
run a highlight bar down it while the picture on the other half does each step; hook points are dots at the lines.

**Named simplification labels.** When a drawing shows fewer parts than the real thing, the label says both numbers:
"drawn as 8 experts with 2 chosen (the model has 128, with 8)".
