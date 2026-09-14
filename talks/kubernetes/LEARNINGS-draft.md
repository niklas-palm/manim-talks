# Learnings from the Kubernetes grid pass (2026-09-14), for the parent to merge

- A stage is only as aligned as its constants. Putting the four columns on the grid meant one arithmetic pass in
  `objects.py` (widths 1.5, 3.6, 3.0, 3.2 with `GAP_WIDE` between, from -6.4 to 6.4) and every scene followed; the
  scenes themselves only had to attach their labels. Design the stage widths to sum to the 12.8 units between the
  margins before drawing anything.
- Vertical rhythm: one box height per column type and `GAP` between them, counted down from the 2.6 line. Four loops
  of 1.05 fill the band exactly; three nodes of 1.25 leave a label row at 2.55 above them, which every scene then used
  for its one floating word (heartbeats, the open question, kube-proxy).
- One row for counters, left edges on the column lines. Counters that had been scattered at -6.7, -4.8, -2.6, 3.4 and
  5.0 now sit at -6.4, -3.2, 0, 3.2 and read as a dashboard.
- Names inside boxes at the top-left and the secondary word at the top-right (`node 1` / `kubelet`, `etcd` / its
  members) leave the centre free for whatever the box holds; a centred name collides with any marker that rides the
  top edge.
- Equal things need identical geometry: every controller's loop arc in one x column (the legend one had been offset
  and the others centred); pod slots aligned to the box's left padding and the memory bar to its right padding.
- A `code()` block drops into the column that is empty at that moment (the node column before the nodes appear) and
  leaves when the column is needed, so the frame stays full without a dedicated code area.
- A label that used to hang under a box (`NotReady, tainted`) does not fit when boxes are on a 0.25 rhythm; it goes
  inside the box, in the bottom padding, left-aligned.
- Card text at 15 in a 1.6-wide card: about 15 characters. "node 1, Running" is the longest line in this deck.
- Stretch the stage to the whole band: nodes and etcd now end on the -2.3 line, counters sit under it at -2.75, cards are 0.8 tall with 16/15 text and slots 0.5; the taller boxes paid for the larger words.

## Pacing pass (2026-09-14)
- Every scene now opens on a still: the stage as the scene begins plus the one new object (a controller box, a label,
  a frontend pod) fading in, then a click. Splitting cost one line per scene and one note each; the notes for the
  stills are the easiest to write, because they only name what is on screen.
- The first observe pulse in Controllers and the scheduler's first pulse were slowed to 0.6 s; the second and third
  pods, the rolling update and the eviction replay already ran at speed, so the slow-then-fast shape needed no more.
- 22 clicks became 27. The still steps double as the presenter's "where am I" frames between scenes.
