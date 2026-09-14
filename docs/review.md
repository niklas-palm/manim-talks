# Review checklist: what "done" means

Run `bin/check.py <talk> qh` first; it catches the mechanical part. Then go through this list with the shot sheets
(`media/shots/<Scene>.png`, viewed at half size), the contact sheets (`bin/review.sh`), one render with `GUIDES=1`,
and finally the presenter in a browser. Every line is a yes or the deck is not done. The list is in the order a viewer
experiences a deck: what they see first, then how it moves, then the words, then the details.

## 1. One picture that unfolds

- [ ] Each move is one continuous illustration. Nothing already on screen is replaced by a different picture; it
      grows, moves, opens under a zoom, or fades because its job is done. A new scene file starts from the previous
      scene's final picture (the stage), so the audience never has to re-orient.
- [ ] `bin/seams.py <talk> qh` reports every seam as "identical" or "title only": no scene opens on a fresh picture,
      no title slide, no black frame with a header. The first change of a scene is a `retitle()` with the first animation.
- [ ] The final frame of each move contains everything the move drew, where the storyboard planned it.
- [ ] Every scene opens on a still: title, kicker, furniture, the objects the scene begins with; nothing moves until the
      next click. The note for that click names what is on screen.
- [ ] Zooms open an object where the audience was looking and close cleanly: contents fade first, then the camera
      pulls back to an untouched wide view.
- [ ] Repeated pictures replay at speed inside one click; nothing is explained twice by clicks.

## 2. The frame is used, and organised

- [ ] The main object spans at least half the content band (about 14 by 5 units); no step is a small drawing in an
      empty frame, and no third of the frame stays empty except in a scene's very first still.
- [ ] Space that will be filled later is visibly reserved (an empty list inside its box, an empty rack) so growth has
      somewhere to go without rearranging.
- [ ] With `GUIDES=1`: fixed furniture sits on the column and row lines; nothing a little off.
- [ ] Only three gaps: `GAP_TIGHT` label to object, `GAP` object to object, `GAP_WIDE` group to group; equal things
      have equal gaps and sizes (a column of boxes: one x, one width, one height).
- [ ] Every label is attached to its object (left edges aligned or centred on it); numbers in a column share a right
      edge; counters that belong together sit in one row at one y. Nothing floats.
- [ ] Nothing within 0.3 units of the frame edge; nothing clipped; nothing overlapping unless the overlap is the point.
- [ ] Everything inside a container is inside it with padding: loops inside their boxes, bars inside their nodes,
      cards inside their stores, arrivals landing inside the box, never on its border.
- [ ] No connection crosses another object; dashed relations are straight and axis-aligned, not skewed; at most one
      unavoidable crossing per frame, and the layout was tried first.
- [ ] Code is highlighted in the library's scheme for its language (Pygments knows it); plain names read white, not red.
- [ ] Flow runs left to right (source on the left, result on the right); standing relations (a watch, a call path) are
      dashed and horizontal so they never cross the flow arrows.

## 3. Motion

- [ ] The first occurrence of a mechanism runs slowly enough to follow (0.3 to 0.6 s per beat, one thing at a time);
      repetitions run fast (0.07 to 0.15 s) inside one click.
- [ ] Every step ends on a settled picture; nothing is mid-flight in the end frame (the shot sheet shows it).
- [ ] No object flashes into existence and out again within a step (check the contact sheet, not only the shots).
- [ ] Conveyors and timelines move at constant speed (`rate_func=linear`); time along x, width is duration.
- [ ] Nothing dragged back by a fade-in, nothing left behind by a group move: a member's change and its group's move
      are never in one play (the checker flags it).
- [ ] The camera moves only when the movement is the point (a zoom to open something); the picture never jumps.
- [ ] Every travelling object starts at the thing that produced it and ends at the exact thing that receives it (the
      slot, the cell, the device), never at a container's edge or a group's centre; one motion per exchange. Check the
      contact sheet for each `travel`, `append` and `Transform` with a moving source.

## 4. Text

- [ ] Every text goes through `label()`, `small()` or `code()`; no bare `Text` (letter spacing depends on it).
- [ ] Sizes: 15 or larger for labels, 13 only for units and tags, 12 the floor anywhere; `small()` only inside a zoom.
      Viewed at half size everything is still legible.
- [ ] Words on screen name visible things and stay: no bullet lists, no paragraphs, no label over eight words; the
      explanation is in the note. A caption, if any, is one quiet line set before the animation and never changed while
      something moves.
- [ ] Titles say what the scene teaches in plain words; no puns, nothing catchy; the kicker above names the move.
- [ ] Terms are defined on screen by contrast before they are used.
- [ ] Every number carries its unit and its clock, and traces to a source in `script.md`.
- [ ] Code is a `code()` block with highlighting; a highlight bar walks the lines while the picture does each step;
      identifiers shortened before fonts are shrunk; indentation intact.

## 5. Colour and truth

- [ ] Each accent has one meaning in the whole deck, declared with `set_thread`; the highlight is the neutral
      `HI`; grey text is `MUTED`, never `DIM`.
- [ ] The deck was reviewed in the style it will be presented in; `bin/check.py` names that style and reports the
      theme fit to present (text 7:1 against the ground, accents 3:1 and 22 apart, both fonts installed).
- [ ] No scene names a hue (`BLUE`, `RED`, ...) or invents a corner, a stroke or a fill: meanings come from
      `objects.py`, geometry from `rad()`, `sw()`, `FILL`, `SOLID`. `bin/check.py` flags the first.
- [ ] In the bright style, nothing assumed a dark ground: no near-white fill used as a highlight, no faint strip turned
      into a dark bar by a flat `set_opacity`, no pale grey where something must still be seen, and the code panel still
      reads as a panel. `bin/gallery.sh` renders every sample in both styles; look at the sheets, not at one frame.
- [ ] Nothing on screen is outright wrong. Every simplification is named in a label or note ("drawn as 8, the real
      thing has 128").
- [ ] Measurements and examples support the mechanism; no scene is a report of an experiment.

## 6. Notes and script

- [ ] Every step has a note: one paragraph, readable aloud, saying what is on screen, what changed, why it matters.
- [ ] Notes carry the caveats, figures and sources; the picture carries the claim.
- [ ] `script.md`: spine, moves with click counts, sources with URLs and dates, simplifications; first `# ` line is the title.
- [ ] `README.md`: what the talk is, the moves with minutes, how to run it, decisions taken on purpose.

## 7. Build and presenter

- [ ] `bin/render.sh <talk> qh` completed with no `Traceback`; `bin/check.py <talk> qh` reports ok; `bin/build.py`
      reports 0 steps without a note.
- [ ] In a browser via `bin/serve.sh`: the presenter steps through every click, the audience window follows, each step
      holds on its end frame, the next-step preview shows where the next click lands, back and Home work.
- [ ] `LEARNINGS.md` updated with whatever cost time or changed a rule; if a helper was added to the library,
      `docs/library.md` says so in the same commit.
