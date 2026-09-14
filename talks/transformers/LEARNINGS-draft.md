# Learnings from the alignment pass on talks/transformers (2026-09-14)

- Putting the work on `COLS`/`ROWS` removed every "a little off" feeling at once: source vector on column 1, matrices on
  column 2, outputs at a fixed x, names left-aligned to one edge; token columns symmetric about x = 0.
- A lone object in a first step reads best centred; it then slides to its working position when the rest of the
  picture appears (Layer and Predict first steps). An object parked at the far left with the frame empty looked wrong.
- Labels that used to sit in the caption band (`to_edge(DOWN)`) all had a natural anchor: under the bars, right of
  the grid, above the vector. Attaching them made the bottom band free and the picture read as one object.
- Bars sharing a baseline on a row line (`ROWS[4]`) and equal widths are what makes a distribution read as one thing.
- Keep the distribution on screen through the loop step at the end; fading everything left a near-empty final frame.
- Library wish: a `place(mob, col, row, edge)` helper that snaps to the grid would save the `[COLS[i], ROWS[j], 0]`
  boilerplate; and `token_row`-style helpers per deck benefit from taking `y` from `ROWS`.

## Pacing pass (2026-09-14)
- Every scene already opened on a still except MaskAndHeads, whose first click flashed a row; the flash moved into the
  mask step, so the still is the grid alone and the click count stayed at 32. The first dot product now runs at 0.3 s
  per pair (library `beat=`), the first three residual landings at 0.35 s, later ones at 0.15 s.
- When a first click is split, check whether the moved animation belongs to the next step's idea; merging it there
  keeps one idea per click without adding a step.
