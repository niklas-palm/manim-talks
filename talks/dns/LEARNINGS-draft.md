
## Containment and routing pass (2026-09-14, evening)

- The two delegation pointers ran diagonally from a record's value to the next zone's name, crossing the zone box
  they left and landing inside the next one. They are now vertical, from the record straight down through the box's
  bottom edge to the next box's top edge, at the value's x: the only line each crosses is its own box's border.
- The laptop-to-resolver arrow came out skewed: the library's `arrow()` takes each end's extreme boundary point in
  the centre-to-centre direction, which for a box as tall as the resolver is its top-left corner, so the line ran from
  the laptop up to that corner. The deck draws it as a horizontal Arrow between facing edges at the laptop's height
  (`client_link` in objects.py). Library wish: `arrow()` and `dashed()` should intersect the centre-to-centre ray with
  the bounding box (t = min(hw/|ux|, hh/|uy|)) instead of using `get_boundary_point`, so links between boxes of
  different heights stay straight and aimed at the facing edge.
- Everything else already sat inside its container with padding: cache rows at 4.25 in a 4.6 box, fuses under their
  rows inside the box, records inside the zone boxes, the NXDOMAIN row inside the resolver in move four. No code
  blocks in this deck, so the monokai change has no effect here.
