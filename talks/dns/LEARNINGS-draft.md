# Learnings from the alignment pass on talks/dns (2026-09-14)

- Put the whole deck's geometry in `objects.py` as named columns and rows derived from the library grid (client column,
  resolver column, tree column; zones stacked from `CONTENT_TOP` with `GAP`; the resolver spanning the same height;
  `CACHE_Y[i]` for cached rows). Every scene then places by name, and the picture is the same one across six files.
- A row of text columns needs both neighbours anchored: the type is pushed right of a long owner, the value right of a
  long type, each with one `next_to(..., buff=0.15)`; fractions alone collided in three different rows.
- Records at 15 pt with the type at 38% and the value at 45% of a 5.3-unit row fit the longest real values
  (`hera.ns.cloudflare.com.` with `2 days` at the right); 16 pt did not. Cached rows are scaled copies (0.8) so their
  columns stay aligned with each other; their text is below the 15 pt floor on purpose, the zone rows carry the reading.
- Fill the frame without moving the mechanism: widen boxes to the column, attach every label to its box
  (`next_to(box, DOWN, buff=GAP_TIGHT).align_to(box, LEFT)`), keep footnotes at y -3.3 centred or aligned to a column
  edge. `GUIDES=1` renders made the off-grid objects obvious in one look.
- Not done: no `code()` blocks; Pygments has no DNS lexer and the record rows already read as a table. A `dig` output
  block in the packet scene would be the one place worth trying with language "text".
- Library wish: `record`-style rows (owner, type, value, ttl) are general enough (any table of records) to consider a
  `row(cells, widths, colors)` helper that anchors neighbours to each other's edges.

## Pacing pass (2026-09-14)
- Every scene now opens on a still picture with its own click and note; the first question or change happens on the
  next click at 0.6 s per beat, the final replay in Standing stays at 0.25 s. Five clicks added (26 total).
- The still step is cheap to add when a scene already builds its furniture in one play: insert `next_slide` after that
  play. Where the opening was an animation of the object itself (the name being written), a FadeIn of the finished
  object is the still; the reveal (the boxes around its parts) becomes the first mechanism.
- The Price resolvers row sat at y -0.35 and left the bottom third empty; at y -1.0 the same picture uses the band and
  the labels attached below it still clear the caption band.
- A CNAME value plus its TTL overran the record row; the fix was a shorter value ("cdn.example.net."), which also matches
  the zone box it points to. Long values in a fixed-column row need shortening, not smaller text.
