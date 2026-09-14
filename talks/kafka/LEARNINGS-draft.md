# Learnings from the Kafka quality pass (2026-09-14), for the parent to merge

## Lessons

- One claim slot per deck. A `claim(scene, old, text, colour)` helper that puts the step's one line in the caption band,
  left-aligned to the margin, at most eight words, replaced every scene's ad hoc bottom labels at ad hoc positions. The
  eye learns where to look and the sentence goes to the note. Candidate for the library as the successor of `caption()`.
- Settings are code. `acks=all`, `min.insync.replicas = 2`, `replica.lag.time.max.ms = 30000`, `cleanup.policy = compact`
  as small `code(..., "ini", 13)` blocks in a side column read as configuration; the same strings as plain labels read as
  prose. A two-line block (`key\n= value`) fits a 3-unit side column where one line does not.
- Attach a set to the thing it describes. The in-sync set as numbered markers inside the leader's box (green, red for
  fallen out, dim for gone) that move to the new leader's box at failover carried the whole replication story; the old
  floating "in-sync: 1 2 3" text did not. The marker row's name goes under the marks, because a marker that rides along
  the top of the same box (the high-water mark) needs the height beside them.
- Side columns. With the main object on the centre columns (x -3.3 .. 3.3), the strips -6.4 .. -3.6 and 3.55 .. 6.4 hold
  the producer and consumer, the counters and the settings, each left- or right-aligned to the same x. Nothing floats.
- Two labels above one rail collide. A log's name (left) and an event label (right) above the same rail must together be
  shorter than the rail; when they are not, shorten the event to its noun phrase and keep the rest in the note.
- Log cell size follows the log's role: 0.55 when the log is the whole picture, 0.42 when three share a row, 0.38 when a
  box must hold eight of them beside two neighbours.
- Stacked rows should fill the band exactly: three boxes of 1.55 at y 1.7, 0, -1.7 span 2.5 to -2.5 with equal gaps.
  Taller boxes take cells of 0.5 and leave the top-right corner free for markers only if the rail ends early (capacity
  8 at cell 0.5 in a 6.6 box); check the marker row against the high-water mark's label at the last offset.
- Code blocks at 15 need a column of about 3.3 units for 16 characters; split a long key at a dot
  (`replica.lag.time` / `.max.ms = 30000`) rather than shrinking the font below 15.
- Frames were checked with `GUIDES=1` at ql; the grid made the off-by-a-little placements obvious in a way the plain
  render never did.

## Left imperfect, and why

- The brokers in the partitions scene sit at x -4.0, 0, 4.0 (symmetric about the centre column) rather than on the
  -3.2 / 3.2 lines: three 3.8-unit boxes do not fit on those lines with a gap, and symmetry read better than the grid.
- Steps 1 and 2 of the partitions and retention scenes use the upper two thirds of the band; the lower third fills when
  the consumer group and the compacted log arrive. Growing pictures start emptier than they end.
