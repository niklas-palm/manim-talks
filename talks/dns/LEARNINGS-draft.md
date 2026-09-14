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
