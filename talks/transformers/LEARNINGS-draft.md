# Learnings from the containment-and-routing pass (draft)

- A label that sits directly under a target of a fan (a score under each key) is crossed by the line arriving
  at that target from below, whatever the fan's origin. Put such labels beside the target, on the side the lines
  never reach, or make the lines end elsewhere. Scores now sit to the right of each token's triple.
- Fan lines should leave from the edge of the source that faces the targets (the query's left edge), not a corner:
  a corner origin puts the near lines through whatever label sits above the source. Labels on a fan's source go on
  the side away from the fan (right of the query).
- Two-line labels above an object need about 0.6 units plus GAP; under a token row whose bottom is at y 1.13, an
  object's top must be at or below about 0.25 for the label to clear the row. Compute the object's true height
  from the helper (vector: n * cell * 1.15; column and grid: n * cell + (n - 1) * 0.012) before fixing its centre.
- A picture built from the same helpers on both sides of a seam (attention_result, head_tiles, projection_parts,
  layer_stack) can be moved freely in objects.py: both scenes follow and bin/seams.py stays identical.
- A label whose position is animated with `.animate.move_to` next to an object that moves in the same play drifts
  from it; compute the destination copy first and `animate.next_to(dest, ...)`.
