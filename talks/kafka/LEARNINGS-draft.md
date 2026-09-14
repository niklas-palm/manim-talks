# Learnings from building talks/kafka (2026-09-14)

For the parent session to merge into `LEARNINGS.md`, `docs/library.md` and `lib/palette.py` as it sees fit.

## Lessons

- A row of cells with offsets underneath is a complete vocabulary for a log system: the same `Log` drew a partition,
  a segment, the consumer-offsets topic and the controller's metadata log. Reusing one drawing for the data and for
  the system's own state made the closing point ("Kafka keeps its own state as a log") visible without a word.
- A reader's position drawn as a triangle under the log, moved by `Transform`, is the picture of "the consumer owns
  one integer": replay is the triangle moving left, a rebalance is the triangle's tag changing, an offset reset is the
  triangle jumping to the first remaining cell. Every consumer concept became a pointer movement.
- Pointer tags under a log collide with whatever sits below (a box border, the next row's name). Budget 0.45 scene
  units below the offsets for a pointer and its tag, and space stacked rows by at least 1.4 units when each carries
  a pointer.
- `box()` names at the top centre collide with any marker whose label rides along the top of the same box (the
  high-water mark). Left-aligned names inside the top-left corner leave the top-right free. Candidate library
  option: `box(..., name_align="left")`.
- `group.animate.set_opacity(x)` on a group that contains a stroke-only rectangle fills it: the returned broker's rail
  turned white. Dim a log by `cells.animate.set_fill(opacity=...)` and `offs.animate.set_opacity(...)` separately.
- Ghost copies for "not yet used" objects (`b.copy().set_opacity(0.25)`) are the cheapest way to show a machine that
  exists but is idle, and `scene.remove()` of the copies at the reveal keeps the real objects' state untouched.
- The `label(width=...)` wrap estimate is loose at 14 pt: a width of 12.6 from x -5.9 still clipped at the right edge
  in two scenes. Use 12.0 for 14 pt labels that start at the left margin.
- For a shot-based review the last play of a step should not be a label swap alone: `bin/shots.py` grabs the frame
  0.15 s before the end, which lands mid-fade and shows a ghost of the old label. The presenter's hold frame is fine;
  the review sheet is slightly misleading. Either swap the label before the step's final animation or accept ghosts
  on the sheet.
- Primary documentation is often assembled client-side: `kafka.apache.org/documentation` is a navigation shell, and
  WebFetch saw nothing. The sources live as markdown in `apache/kafka` under `docs/` on GitHub and the generated
  config tables at `kafka.apache.org/<version>/generated/*.html`; `gh api repos/<org>/<repo>/contents/<path>` finds
  the file names.

## Candidate library helpers (talk-specific versions live in talks/kafka/scenes/objects.py)

- `Log(x0, y, capacity, base, name)` with `append(scene, colour, source)`, `put(colour)`, `slot(i)`, `below(i)`:
  an append-only row of record cells with offset labels on a rail. Generic enough for any log, queue, buffer or
  timeline of discrete items (Kafka partitions, WAL, event store, a ring buffer with a base offset).
- `Pointer(name, colour)` with `place(log, i, dy)` and `to(log, i, dy)` (returns a Transform): a reader's position
  under a row of cells. Also fits a program counter, a cursor, a replica's fetch position.
- `read_flash(scene, cell, pointer, target)`: a cell's copy travels to a reader and vanishes. Close to `travel()` but
  carries the record's colour; could be an option on `travel(..., carry=cell)`.
- `producer()`, `consumer()`, `broker()` are thin wrappers over `node()`/`box()`; not worth promoting.

## Second pass (fill the frame)

- The first version put everything in the top third at 0.34-unit cells with 12 pt offsets and full sentences as
  labels; it read as a paper figure. Cells at 0.42, brokers 4 to 10 units wide, consumers 2.1 wide, offsets 14 pt,
  labels 17 pt and cut to one clause changed nothing about the mechanism and everything about legibility. Check the
  shots at half size before the first render at 1080p, not after.
- A label that is a clause ("min.insync.replicas = 2: the write is refused, not stored on one disk") does the work of
  a sentence; the sentence is in the note. Every bottom label in the deck is now under 70 characters at 17 pt.
- Gauge names wider than the gauge clip at the frame edge when the gauge sits in the margin; two short lines
  ("write\nload") fit, a broker name does not.

## Library migration (for the parent)

- Scenes now use `lib.palette`'s `Log`, `Pointer` and `travel(carry=)`; `objects.py` keeps only the colours, the
  SIDE/GAP/PITCH constants (passed as `gap=GAP` so the HWM marker and tombstone geometry stay aligned) and the
  producer/consumer/broker wrappers. End frames of all 22 steps compared against the previous render: mean grey
  difference under 2/255 everywhere, layout identical.
- `bin/shots.py` at `ql` (15 fps) produced no frames: the seek to 0.05 s before a step's end lands after the last
  frame of a 15 fps file, ffmpeg writes nothing, and the tiling step then fails on the empty glob. At `qh` it works.
  Clamp the seek to `dur - 1/fps` or fall back to `-0.15` when nothing is written.
