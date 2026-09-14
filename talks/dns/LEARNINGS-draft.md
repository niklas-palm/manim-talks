# Learnings from building talks/dns (2026-09-14), for the parent to merge

## Lessons

- `Text[a:b]` indexes glyphs without spaces, so colouring a phrase by string index lands one character per preceding
  space to the left. Use `label(..., thread=True)` with the word registered in `set_thread`, or `t2c` with the
  `"[a:b]"` index keys the library builds. Two scenes were coloured wrong before this was noticed in the shots.
- A row of text columns (a record: owner, type, value, ttl) needs its columns placed by measured widths, not by
  fractions of the row: a long type name ("CNAME") ran into the value at every fraction tried. Placing the value at
  `max(fraction, type.right + gap)` fixed it in one line. Rule: when two texts share a row, at least one anchor must
  be relative to the other text's edge.
- A `Transform` on a Text that changes its string produces a dissolve rather than garbage when the two strings have
  the same number of glyphs and similar width (an address to another address). It was fine here; keep the fade-out
  and fade-in for strings of different lengths.
- Small elements created inline (`FadeIn(fuse(row))`) cannot be faded out later because there is no reference; the
  teal bar under a record survived the record's removal. Keep a name for anything that must leave the screen.
- A helper that builds "the picture move N left behind" in one call (zone boxes, resolver, client, cached rows) lets
  every scene start from the previous scene's final frame in a few lines, which is what makes a deck one continuous
  illustration across scene files.
- Real numbers from a live trace (`dig +trace`) teach better than textbook ones and are honest about time: the same
  record read at 300 s in one cache and 281 s a moment later in another became the illustration of TTLs counting
  down at every level.
- Cloudflare's learning pages return 403 to a fetcher; the RFCs, IANA and the root zone file itself are reachable and
  better sources anyway.

- Size for the back row first. The first pass drew records at 13 pt in boxes that filled a third of the frame; at half
  size nothing in the resolver's cache could be read. The second pass (rows at 16 pt, 0.42 high, boxes 6 units wide,
  cached rows at 0.78 of that) needed no change to the mechanism and made every frame legible at half size. Start from
  the "fill the frame" rule and the largest text that fits; shrink only what a zoom will later enlarge.
- Fewer, larger rows teach the same thing: six hosts rows and a counter that runs to 340,000,000 said "the list is the
  size of the internet" better than thirty small rows did.

## Candidate library helpers

- `question()` / `answer()` (in this talk's `objects.py`): a dot with a small label that travels from one object's
  near edge to another's and fades; the colour says what kind of message it is. Generic enough for any
  request/response picture; `travel()` in the library lacks the label and the edge-to-edge start.

```python
def message(scene, a, b, color, text="", run_time=0.5, above=True):
    d = Dot(color=color, radius=0.1).move_to(a.get_right() if a.get_x() < b.get_x() else a.get_left())
    lab = label(text, 12, color).next_to(d, UP if above else DOWN, buff=0.06) if text else VGroup()
    g = VGroup(d, lab); scene.add(g)
    target = b.get_left() if a.get_x() < b.get_x() else b.get_right()
    scene.play(g.animate.move_to(target + ((UP if above else DOWN) * 0.12 if text else 0)), run_time=run_time)
    scene.play(FadeOut(g, run_time=0.15))
```

- `fuse(row, fraction)`: a thin bar under an object whose length is the time it may still be kept; `Transform` to a
  shorter one shows time passing. Any TTL, lease, timeout or budget can use it.
- `record(owner, type, value, ttl)`: a row of text columns with measured placement; a generic `row(cells, widths)` with
  per-column colours would serve tables in any talk.
