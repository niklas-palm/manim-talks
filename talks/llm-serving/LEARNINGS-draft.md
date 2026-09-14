# Learnings from the containment-and-routing pass (draft, 2026-09-14)

General things learned while fixing borders, crossings and margins in this deck. Move what holds for every talk into
`LEARNINGS.md`.

- **A zoom's frame is part of the layout.** Compute the camera rectangle from the objects it must show (box left minus a
  margin, last used slot plus clear space) and derive the scale from it (`(right - left) / FRAME_W`), rather than picking
  a round scale and a centre and hoping. Named constants for the open box's width and shift make the undo at the zoom-out
  a mirror image of the zoom-in instead of a second set of magic numbers.
- **A row that runs past a zoom's edge looks clipped whatever you do.** Cutting at a slot gap makes the last slot touch
  the frame; cutting mid-slot reads as damage. Hide the slots the zoom never reaches (stroke opacity 0 on stroke-only
  cells, so `FadeIn` of the row later leaves them hidden) and show them again on the way out.
- **Shift a row member by member when one member also changes.** `row.animate.shift()` plus `row[6].animate.set_stroke()`
  in one play is the group-versus-member trap; a list of per-member `animate.shift()` with the change chained on the
  members that need it does both.
- **Counters in a row: budget the name widths first.** `Counter` names are always size 15 (about 0.09 units per
  character); three names of 28, 23 and 15 characters need 6.7 units plus gaps, more than looks available. Measure the
  rendered widths on a shot (pixels times 14.22 / frame width), then place from the right margin (6.4) leftwards.
- **A hub above a row of boxes: route, do not fan.** Straight lines from one hub point to eight boxes are skewed and
  cross each other; a trunk, a rail and a vertical drop per box (a bus diagram) is all axis-aligned and extends by one
  drop when a box is added. For a travelling dot, `MoveAlongPath` over a two-corner path (across the free band under
  the hub, then straight down into the slot) keeps source and destination exact and crosses no neighbour.
- **Leave the lane a traveller uses empty.** A token that leaves a stack downward needs the label under the stack to
  sit below where it stops (stack bottom + token side + a gap); a request that leaves a balancer needs the band under the
  balancer free, so status lines go above it.
- **A loop arrow belongs inside its box.** A `CurvedArrow` hung from a box's bottom edge starts and ends on the border;
  drawn from centre + 0.6 to centre - 0.6 with the same negative angle it bows down inside, under the name, if the box
  is 1.3 high or more.
- **Exchanges between neighbours go over the links drawn.** Twelve travellers "everyone to everyone" across a row of
  four boxes cross the boxes in between; six travellers edge to edge between neighbours, above and below the sync
  arrow, say the same thing over the arrows already on screen.
- **Measure margins on the shot, not in the head.** At 960 px wide a shot is 0.0148 units per pixel; a label ending at
  938 px is at x = 6.8, inside 0.3 of the edge, however comfortable it looked in the code.
