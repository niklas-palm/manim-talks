# Manim: the traps and their fixes

Manim Community Edition 0.21, Python 3.12, macOS, ffmpeg 7, no LaTeX. Each entry cost hours in the reference deck.

## Environment

- **Two Manims.** 3Blue1Brown's own repo is `manimgl`; the maintained fork is Manim Community Edition (`pip install
  manim`, docs at docs.manim.community). This repository uses the community edition.
- **No LaTeX here.** `MathTex`, `Tex` and `DecimalNumber` shell out to LaTeX and fail. Formulas are `Text` plus a
  `Line`; counters are `Counter` (a `ValueTracker` redrawing a `Text`).
- **`--save_sections`** writes one clip per `next_section()` and a JSON index of durations; that is the whole
  presenter mechanism. `manim-slides` was tried and failed with PyAV errors; it is not needed.
- **`--disable_caching`** always. Cached partial movies survived code changes more than once.
- **One render at a time per talk.** Two Manim processes share `media/texts/`, the cache of rasterised text. One
  deletes a glyph file the other is about to read, and the long render dies with `FileNotFoundError` deep in the
  deck. Different talks have different `media/` folders and can render in parallel.

## Animation

- **`.animate` generates the target when the builder is created.** A second `.animate` on the same mobject before
  the first is played overwrites that target, so the first animation quietly animates towards the second's end
  state. The matrix rows told to turn yellow and then, in a list built before the play, told to turn violet again
  never changed colour on screen. Build the next animation's list after the previous `play`.
- **A group and one of its members in the same `play` is the same trap.** `group.animate.move_to` plus
  `member.animate.stretch` left the member behind. Make one target copy of the group, change it, play one
  `Transform(group, target)`.
- **`Transform` pads the animated mobject with empty submobjects** to match the source's structure, so a group's
  `len()` changes silently. When you will index the target later, morph a copy: `ReplacementTransform(src.copy(),
  target)`.
- **`FadeOut` restores the mobject's state on removal, and `FadeIn` brings it back as it was.** Two consequences.
  A caption inside a group that is faded for a zoom comes back with the group later, on top of its replacement:
  keep captions out of fade groups. And a mobject that is in a fade-in group *and* shifted by another animation in
  the same play ends at the pre-shift position: never put a mobject in two groups that are animated in one play.
- **Objects appended to a list after the group was built are not in the group.** The cell stored inside a zoom was
  appended to `filled[0]` but not to `row0`; the zoom-out shifted the row and left the cell one slot to the left.
  Add to the group too (`row0.add(cell)`).
- **`scene.remove(group)` after fading one member does nothing.** `FadeOut(group[k])` restructures the scene: the
  group is replaced at top level by its remaining members, so the group is no longer in the scene and removing it
  is a no-op; the members stay. Fade or remove the remaining members themselves.
- **`become()` on `Text` with a different string produces garbage** mid-animation because the glyph counts differ.
  Fade out and in, or `Transform` between labels.
- **A live `Counter` and fades.** Its digit updater redraws the number every frame; it now keeps the digits' current
  opacity, so `FadeIn` and `FadeOut` work on a counter. For a still frame set `tracker.set_value()`; `counter.stop()`
  freezes the digits entirely.
- **A frozen `Counter` shows the value it was built with.** `tracker.set_value(n)` takes effect on the next frame through the
  updater; `stop()` before any frame has rendered removes that updater, and the digits still read the initial value. For a
  still frame build the counter with its value (`Counter(name, n, ...)`) and then `stop()`.
- **A label riding on a `MoveAlongPath`** must follow by updater, not by being grouped with the traveller: the path moves
  the group's centre, so the dot sits off the path by half the label's height. `route()` does this.
- **Updaters need a stable anchor.** A counter's digits anchored to their own initial position stayed behind when
  the group moved. Anchor to a sibling that moves with the group and recompute in the updater.
- **Build geometry after the move it depends on.** Lines created from a column's position before the animation
  that moved it pointed at the old place. Same for arrows and dot start points. Anchor to the group's centre, not
  its first member.
- **`group.animate.set_opacity(x)` on a group with a stroke-only member fills that member** (a rail turned white). Dim
  the filled cells and the labels separately, or set fill and stroke opacity explicitly.
- **A member change and a group move in one play loses the member.** Setting a block's stroke while moving the stack
  that contains it left the frame in place and moved the text: the group-versus-member trap again. Do the member
  change in its own play first.
- **End every step on a settled picture.** The presenter holds on the step's last frame; a 0.3 s move as the last
  animation leaves the object mid-flight. Add `self.wait(0.3)` or make the last animation the settling one. When a
  step both fades a group out and another in, use two plays; one combined play leaves a ghost in the end frame.
- **Arcs bow toward the side given by the sign of `angle`.** Thirty arcs between points on one line all went through
  the squares they connected until the sign was flipped; a "loop back" `CurvedArrow` with a positive angle bows up
  through the title, a negative one bows down. Check the shot.
- **`get_boundary_point(direction)` returns a corner for a diagonal direction.** Arrows and dashed lines between two
  boxes that are not on one axis came out skewed, ending at corners. The library's `edge_point()` meets the box where
  the centre-to-centre line crosses it; `arrow`, `dashed` and `travel(edges=True)` use it.
- **A negative `z_index` does not put a new mobject behind what is already drawn, during a play.** The Cairo renderer bakes
  every mobject that comes before the first moving one into a static image and draws the moving mobjects over it, sorted
  by `z_index` only among themselves. So `FadeIn(box.set_z_index(-1))` covers the boxes it was meant to sit behind, and
  whether it happens depends on where a live counter or an earlier `retitle` left the first moving mobject in the list.
  Something that must appear behind existing objects is placed, not animated: `scene.add(g); scene.bring_to_back(g)`.
- **`set_opacity` fills hollow shapes.** It sets fill and stroke opacity together, so a stroke-only cell becomes a
  filled one. Hide scrolling things under a background-coloured mask with a higher `z_index` instead.
- **`rate_func=linear` on the play** makes a conveyor move at constant speed; the default smooth easing makes it
  lurch on every step.
- **Zoom in, then draw; clear, then zoom out.** Fade the zoomed contents in a play of their own before the camera
  pulls back. Fading them during the zoom-out looks like the picture breaking.
- **A stretched box opens downward if you shift it.** `stretch_to_fit_height(1.2).shift(DOWN * 0.12)` keeps the
  top edge where the audience expects it while the box grows; remember to undo both on the way out.
- **Smallest cells above 0.07 scene units at a 0.4 zoom.** Below that a 1080p render shows a grid as texture and
  the sweep that is the point of the picture is invisible.
- **Simultaneous `LaggedStart` and `Create` in one play** work; a `LaggedStart` alone with `lag_ratio` around 0.1
  to 0.2 reads as "one after another" without slowing the step.

## Text and layout

- **Font.** Helvetica through Pango renders cleanly; Helvetica Neue had uneven word spacing at small sizes. Set one
  font in one place (`FONT` in the library).
- **Pango rounds glyph positions to whole pixels at small sizes.** Text drawn directly at 14 to 20 pt loses its
  spaces ("offsetback", "newgroup") and crowds or spreads letters unevenly; it showed in every deck's labels. The
  library lays out every `Text` at `BASE_SIZE` (48) with ligatures disabled and scales the geometry to the requested
  size, which is exact. Never construct `Text` directly in a scene; go through `label()`, `small()` or `code()`.
- **Leading spaces vanish in `Text`** because Manim aligns on the glyphs' bounding box; `code()` puts indentation
  back by shifting each line by its indent times a measured character width.
- **Text does not wrap.** `label(width=...)` wraps with `textwrap` at about 175 / font_size characters per scene
  unit and scales to the frame if still too wide. Every caption goes through it.
- **Frame is 14.22 by 8.** Text at size 15 is about 0.09 units per character, at 13 about 0.077, at 22 about 0.13;
  a 60-character label at size 15 is 5.4 units wide. Check the right edge (x 7.1) before placing a long label at a
  left-aligned position past x 1.5.
- **`t2c` keys are substrings and overlapping keys are refused.** `thread_colours()` turns whole-word matches into
  `"[start:end]"` index keys. The glyph list keeps a placeholder for every space and newline, so string indices map
  onto it; do not strip spaces first.
- **Grey text needs its own colour.** The shape grey (#4A4F5C) is unreadable as text on a projector; `label()`
  substitutes `MUTED`.
- **Captions under a moving camera** leave the frame unless pinned: `pin()` keeps them at the frame's bottom and
  scales them with the frame.
- **Multi-line `Text`** with `\n` works and is left-aligned; use it for two-line counter names and legends. The
  `label(width=)` wrap does not apply to strings with an explicit `\n`.
- **A labelled row at the top collides with the title band** (y about 3.3). Keep labelled objects at y <= 2.0 so labels
  above them clear the title.
- **Menlo at size 18 is about 0.13 units per character**; 39 characters is five units. Measure the longest line before
  placing code and hook labels near the right edge.
- **`Counter(decimals=1)`** when a value like 1.8 must not round to 2. Show "1.60" rather than switch decimals
  mid-deck.

## The web player

- **Hold a few frames before a step boundary.** The player's hold loop checks the video time once per animation frame, so
  playback overshoots the boundary by up to a frame before it pauses, showing the next step's first frame for an
  instant; a seek to `end - 0.001` can snap onto that frame too. The player pauses at `end - 0.1` and seeks to
  `end - 0.06`; steps end on a settled picture, so the frame is the same.
- **Swap to a new scene's video only after it has decoded the target frame** (on `seeked`, with a timeout fallback).
  Swapping first shows whatever frame that element last displayed, which is the flash of an old scene.

## Rendering and review

- **Preview at `ql` (480p15)** while building: seconds to a couple of minutes per scene. **`qh` (1080p60)** for the
  talk: a rich scene takes five to ten minutes; a full deck the better part of an hour.
- **Shots are taken 0.08 s before each step's end** (one frame at 15 fps), which is the frame the presenter holds. A label swap or a move as
  the very last animation of a step used to show as a ghost at the earlier 0.15 s; if the sheet still shows one, the
  step itself ends mid-animation and needs a settling wait.
- **Sections are indexed from `_0000`.** `Scene_0000_autocreated.mp4` is the first step; the JSON index lists
  durations in order. `bin/shots.py` uses it to grab each step's end frame.
- **Seek with ffmpeg** to inspect a moment: `ffmpeg -y -ss <t> -i <clip> -frames:v 1 out.png`. Clamp `t` below the
  duration; a seek past the end writes nothing and you review last time's file.
- **Reading the output.** A render prints hundreds of lines. Pipe to a log; `grep -c Traceback` tells you whether it
  worked; `grep -A8 Traceback` shows why.

## `set_opacity` on a group replaces what its members were given

`group.set_opacity(k)` sets every member's fill and stroke opacity to `k`. A row whose strip was drawn at 7 per cent
and whose text is at full strength becomes a row where both are at `k`: the strip turns into a bar. It is invisible on
a dark ground when `k` is small and glaring when it is not, and on a light ground it reads as a black block. To fade
several members together, scale what each already has:

```python
for m in row.family_members_with_points():
    m.set_fill(opacity=m.get_fill_opacity() * k)
    m.set_stroke(opacity=m.get_stroke_opacity() * k)
```

The same applies to a copy that travels as a ghost: a flat opacity on the copy is fine only when every member was
drawn at the same opacity to begin with.
