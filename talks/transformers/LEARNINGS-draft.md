# Learnings from the no-cuts pass on talks/transformers (2026-09-14)

- Every boundary object needs one builder used by both scenes. The producing scene creates the object through the
  builder (or swaps its animated stand-in for the builder's object at the end: `self.remove(qbig); self.add(qbig_t)`),
  the consuming scene rebuilds it with the same call, and the two frames agree to the pixel. Six such builders in
  `objects.py` made every seam identical or title-only on the first measured run.
- The hand-over is the teaching moment, not a technicality: the connections coming off the tokens, the vectors rising
  into the row, the softmax bars folding into the grid's last row, the attention output becoming the feed-forward's
  input, the tiny token growing back, "mat" stepping out of the row before it is predicted and rejoining it in the
  model's colour. Each one says "this is the same thing" without a word.
- A Counter left on a still frame must have its updaters cleared (`num.clear_updaters()`), or a FadeOut leaves its
  digits behind while the frame is redrawn.
- Keeping the token row across the top for four scenes cost vertical room: pipelines moved to y -0.85 and the tall
  objects (16-cell vector, 12-row vocabulary matrix) shrank a cell size so labels above them clear the row at 1.2.
  Rule of thumb: a persistent row at the top takes the band from 1.2 up; everything else lives below it with its
  labels included.
- Labels that stack vertically at one x (the loop's label and the training/inference pair) collide when both sit in
  the middle band; put the second on the row line below.
- `FadeIn(VGroup(*cells))` of members of a grid, then `self.remove(temp); self.add(grid)`, is how to fade part of a
  group in and still have one group to fade out later.
