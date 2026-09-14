
## Seams pass (2026-09-14, evening)
- Every scene now opens on the previous scene's last frame, rebuilt with `self.add` and `title_still`, and its first
  play is `retitle` with the first change. `bin/seams.py kubernetes` reads 0.6 to 1.5 (title only) on all four seams.
  The stage object made it cheap: its constructor takes the state (node memory used, which controllers exist) and
  `base()` returns the furniture to add; what the previous scene left (cards, pods, kubelet colours, dead node) is a
  few lines of state before `self.add`.
- The end state has to be read from the previous scene's code, not remembered: three things the memory got wrong were
  the API server's gates left lit blue after the zoom (now dimmed again on the way out), node three's kubelet never
  having spoken (no line, grey name) at the end of move three, and node two's stroke opacity left at 0.35 when it died.
  Write each scene's true end state as a comment before writing the next scene's opening.
- When the next move needs room in a shared container (the store's six slots), make the clearing visible and say why
  in the note ("we stop drawing the Pod records to make room; they still exist") rather than starting the scene
  without them. The first click of a move can carry several settling changes at once if they are all consequences of
  the previous move (node two returns, the node controller goes quiet, the ReplicaSet gets its version), because the
  audience already understands every object that changes.
- No title slide: the deck opens on the first move's still picture, and the opening note (audience, spine, colours)
  is read over it. Nothing was lost.
