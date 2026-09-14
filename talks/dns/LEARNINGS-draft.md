# Learnings from the no-cuts pass on talks/dns (2026-09-14)

- Every seam was a cut before this pass (scores 5.7 to 15.4); after it, 0.4 to 2.1. The method that worked: one
  `<scene>_end_state()` function per scene in objects.py, returning the last frame's objects by name, so the next
  scene rebuilds it with one `self.add(*state.values())` and can transform any part of it in its first play.
- A Counter survives FadeOut: its digits are redrawn by an updater every frame at full opacity. Call
  `counter.num.clear_updaters()` before fading it, or remove it after the play. Candidate for the library: make
  Counter's updater respect the group's opacity, or give Counter a `stop()` method.
- Transforming a zone box between two positions works when the box and the name morph and the subtitle (different
  text) swaps: `ReplacementTransform(old[0], new[0])`, `ReplacementTransform(old[1], new[1])`, `FadeOut(old[2])`,
  `FadeIn(new[2])`. Morphing texts of different lengths produces garbage mid-animation.
- The transition click doubles as the new scene's still: the previous picture is on screen, the click changes the
  title and moves the picture into the new starting state, and the hold that follows is where the speaker names
  what is there. No extra click was needed for the still.
- The one true cross-fade left (Price to Standing, the alias picture to the root's machines) still scores
  "identical" at the seam, because the fade happens inside the new scene's first play, not at the boundary.
- Deleting the opening scene lost nothing: its note's content moved into the first scene's first note.
