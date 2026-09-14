# Learnings from the no-cuts pass on talks/kafka (2026-09-14)

- Build each move's last frame from a function in objects.py (`log_end`, `partitions_end`, ...) and let the next scene
  add it statically; the scene that owns the picture uses the same builder for its own start, so the two frames cannot
  drift. Seams went from 5.7 to 15.4 down to 0.5 to 0.8 (identical, only the title fades).
- Transform only the rectangles of boxes across a seam and fade the names; a `Transform` between two `Text`s of
  different lengths morphs through garbage.
- The end state must be reproduced exactly, including randomness: the four records written before the split came from
  `random.Random(2)`, so the builder draws them from the same seed; pointer positions follow the scene's read rounds.
- A `ReplacementTransform` between two `Log`s with the same cell count is a clean morph (the leader's log into the first
  segment file); with different counts Manim pads and it is still acceptable for a one-second transition.
- The old s00_title render folder stays under media/videos; build, shots and seams read scene classes from the source
  files, so it is ignored, but `rm -rf talks/kafka/media/videos/s00_title` keeps the folder honest.
- Travel audit (rule 3a): every append starts at the producer node and lands in its slot, every read starts at the cell
  under the pointer and lands on the consumer, every replica copy goes from the leader's cell to the follower's matching
  slot, the metadata event from the active controller into the next cell and from there to controllers and brokers. Two
  exceptions found and fixed: the offset-commit dots started at a consumer's bottom edge, the acknowledgement dot ended
  at the producer's right edge; both now use the object's centre. The tombstone still appears above the compacted log
  because no producer is drawn in that scene (noted, not changed).
