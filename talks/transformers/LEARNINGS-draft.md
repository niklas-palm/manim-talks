# Draft learnings and candidate library helpers (transformers deck)

For the parent to fold into the repo `LEARNINGS.md`, `docs/`, and possibly `lib/palette.py`.

## Lessons worth keeping

- Fill the frame (the coordinator's rule 11, learned the hard way here). The first pass drew the mechanism correctly at
  cells of 0.06 to 0.12 with most of the canvas empty; at half size nothing could be read. The second pass used cells of
  0.14 (a persistent reference row) to 0.26 (the object being worked on), labels at 16 to 20, and laid the work out
  across the width. Rule of thumb that worked: the persistent row at the top at 0.14, the thing being explained at
  0.2 to 0.26, and the three-cell q/k/v outputs at 0.24 so a 3-cell column still reads as a vector.
- Show the sum, not the label. "Weighted sum of values" became six value copies flying into the new vector, each scaled
  by its weight while its bar lights, and the new vector's cells filling cumulatively. The audience sees why a big weight
  matters; the earlier version had only a label saying so.
- A stack is the same picture repeated smaller, not text in boxes. A `layer_glyph` miniature (vector, q/k/v, fan,
  feed-forward grid, vector) repeated five times reads as "the same again", which six boxes labelled "attention +
  feed-forward" did not. A deliberate miniature is allowed to go below the cell minimum because the full-size version
  was on screen a moment before.
- The residual is a cell-by-cell landing: the update's cells fly one by one onto the outgoing vector and each cell's shade
  shifts with a flash. "Vector plus update" with a plus sign and an arrow said it; the landing shows it.
- Arcs between points on the same horizontal line bow toward the side given by the sign of `angle`; check the shot,
  the first sign choice put all thirty arcs through the token squares.

- A token vector row placed at the top collides with the title: word labels above vectors at cell 0.09 reach the
  title band. Keep a labelled-vector row at y <= 2.0 so the labels above it clear the title at ~3.3. (Found in shots,
  fixed by lowering the row.)
- When one step both fades an old group out and fades a new group in, split into two plays (fade out, then fade in).
  A single combined play left a faint ghost of the fading group in the step's end frame, which the shot review caught.
- A CurvedArrow with a large positive angle for a "loop back to the start" bows upward through the title. Use a
  negative angle so it bows downward and route it just under the line it connects. (The predict loop.)
- Illustrative numbers are fine for scores/weights if the mechanism is exact. The attention scores here are chosen,
  not computed from the drawn cells, but the dot product, softmax and weighted sum are shown honestly; the note says
  the numbers are illustrative. This keeps the picture legible without lying about the operation.
- The `sweep` helper needs a light-up colour that is not one of the semantic accents, or the "on" flash reads as a
  meaning. I used a plain white constant (`OUTLINE_ON`) for the momentary highlight; consider promoting that to the
  library so every deck's sweep flashes the same neutral colour.

## Candidate library helpers (currently in this talk's objects.py)

These proved general across the reference deck and this one; consider moving to `lib/palette.py`:

```python
def vector(seed, color, cell=0.12, n=8):
    """A vector as a column of cells with per-cell random shades, so two vectors look different. Seeded so a token's
    vector is stable across scenes."""

def shades(v) / restore(v, ops, color):
    """Capture and restore a vector's per-cell opacities around a highlight."""

def dot_product(scene, vec, vcolor, mat, i, out, color):
    """The slow, first demonstration of one output number: vector cell and matrix-row cell light in pairs, products
    collapse into the output cell."""

def sweep(scene, vec, vcolor, jobs, rt):
    """Every row at speed for one or more matrices at once; jobs = [(matrix, out, colour)]. The dim-again builders
    are made AFTER the on-play (the .animate double-target trap). Flashes OUTLINE_ON, a neutral highlight."""

def softmax_bars(scores, x, y, w, colour):
    """Bars whose heights are a softmax over scores, summing to 1; returns (bars, weights). The exact picture of an
    attention pattern; reusable for any distribution."""
```

`vector`, `dot_product`, `sweep` are near-duplicates of the reference deck's `s01_mechanics.py` helpers. The
reference deck keeps them talk-local; this deck copied them. If a third deck needs the multiply picture, promote
`vector`, `shades`, `restore`, `dot_product`, `sweep` (with `OUTLINE_ON`) and `softmax_bars` into the library under a
short "vectors and matrices" section in `docs/library.md`, parameterising cell size and count.

## Note for the docs

Consider adding to `docs/library.md` a short "vectors and matrices" pattern block: a vector is a shaded column, a
matrix is a grid, one output number is a row lighting against the vector (dot_product), the whole output is the row
sweep, and a distribution is softmax_bars. Both decks built their central pictures from exactly these.
