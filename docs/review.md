# Review checklist

Run it per scene while building (preview quality) and once for the whole deck at 1080p60. Every item is a yes or the
deck is not done. Look at `media/shots/<Scene>.png` and `media/review/<Scene>.png`; do not answer from the code.

## The picture

- [ ] With the sound off, a viewer could say what each step showed.
- [ ] Each step adds exactly one idea; after every click the audience can say what changed.
- [ ] Nothing already on screen was replaced; the picture grew, moved, opened or faded because its job was done.
- [ ] The final frame of each move contains everything the move drew, in the places the storyboard planned.
- [ ] Nothing on screen is outright wrong. Every simplification is named in a label or note.
- [ ] Zooms open an object and close cleanly: contents fade first, then the camera pulls back to an untouched view.
- [ ] Repeated pictures replay at speed inside the step; nothing is explained twice by clicks.

## Words and numbers

- [ ] No bullet lists, no paragraphs, no sentence that explains. Labels name visible things and stay.
- [ ] Every number carries its unit and its clock ("tokens/s, each request, while decoding").
- [ ] Every number traces to a source in `script.md`.
- [ ] Captions, if any: one per step, set before the animation, never changed while something moves.
- [ ] Terms are defined on screen by contrast before they are used.
- [ ] Titles say what the scene teaches in plain words (no puns, nothing catchy).

## Colour and layout

- [ ] Each accent colour has one meaning in the whole deck; `set_thread` covers the nouns.
- [ ] Grey text is `MUTED`, never `DIM`; no text under size 12 except `small()` in a zoom.
- [ ] No text clipped at the frame edge, no label over another label or over a shape it does not name.
- [ ] Fixed furniture (title, kicker, gauges, counters) sits in the same place across the scene's steps.
- [ ] Rendered once with `GUIDES=1`: furniture on the grid lines, labels attached to their objects, three gaps only,
      numbers in a column right-aligned, rows sharing a y, no empty third of the frame.
- [ ] Code is a `code()` block with highlighting, never plain text; the highlight bar walks the lines.
- [ ] Smallest cells at least 0.07 units at a 0.4 zoom; grids read as cells at 1080p.
- [ ] The main object fills at least half the content band; unzoomed cells 0.14 to 0.25 units; no scene is a small
      drawing in an empty frame. Viewed at half size, everything is still legible.

## Motion

- [ ] The first demonstration is slow enough to follow (0.2 to 0.5 s per beat); repeats are fast (0.07).
- [ ] No object flashes into existence and out again within a step (check the review sheet, not only the shots).
- [ ] Conveyors and timelines move at constant speed (`rate_func=linear`); time along x, width is duration.
- [ ] Nothing dragged back by a fade-in, nothing left behind by a group move (see `docs/manim.md`).

## Notes and script

- [ ] Every step has a note: one paragraph, readable aloud, saying what is on screen, what changed, why it matters.
- [ ] Notes carry the caveats, measured figures and sources; the picture carries the claim.
- [ ] `script.md` has the spine, the moves, the sources; its first `# ` line is the deck title.
- [ ] `README.md` of the talk says what it is, the moves with minutes, and how to run it.

## Build and presenter

- [ ] `bin/render.sh <talk> qh` completed with no `Traceback`; `bin/build.py` reports 0 steps without a note.
- [ ] In a browser via `bin/serve.sh`: the presenter steps through every click, the audience window follows, each
      step holds on its end frame, the next-step preview shows where the next click lands, back works.
- [ ] `LEARNINGS.md` updated with whatever cost time or changed a rule.
