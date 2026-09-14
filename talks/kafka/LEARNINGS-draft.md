# Learnings from the kafka containment-and-routing pass (2026-09-14)

- `arrow(a, b)` aims at `get_boundary_point`, which for a rounded box is the first point of the flat edge, i.e. a corner:
  two objects at the same height got a skewed arrow. For side-by-side objects build the arrow from `a.get_right()` to
  `b.get_left()` at `a`'s y (`harrow` in this talk's `objects.py`); keep the two ends at one y and move both together
  when the target changes (producer and consumer follow the leader).
- A pointer under a log inside a box needs the whole budget: name row 0.33, gap, rail 0.58, offsets 0.25, pointer 0.36
  plus 0.06 gap, padding 0.1 top and bottom; with 0.42 cells that is a 1.75-high box. Compute it before choosing the
  row heights; 1.55 put the pointer on the border.
- A marker whose label rides above the log (the HWM) shares the name row. Put the box name where the marker never goes
  (right-aligned) and the static furniture (in-sync markers) in the corner the pointer never reaches (bottom right).
- A dashed relation whose x equals a rail's edge reads as a line drawn on the border. Centre the rail on the columns
  with 0.4 or more to spare on both sides.
- `bin/shots.py` shows step ends only; a label that lives inside one step (the tombstone's) needs a frame from the
  clip (`ffmpeg -ss`) to check for collisions.
