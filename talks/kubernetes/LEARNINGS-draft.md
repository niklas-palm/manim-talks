# Learnings while building talks/kubernetes (2026-09-14)

Candidate additions for `LEARNINGS.md`, `docs/library.md` and `lib/palette.py`, written here because this talk was
built in parallel with others. The parent session merges.

## Lessons

- A "stage" object that builds the whole fixed picture at fixed coordinates (client, API server, store, loops, nodes,
  counters) and lets each scene `self.add()` the parts it starts from was the single most useful thing in this deck.
  Every scene begins where the previous one ended without a shared Manim state, and the audience keeps one mental
  picture across six scene files. Suggest the template's `objects.py` show this pattern (a `Stage` class), not just a
  single shared drawing.
- Small record cards need short text. Card text at 12 pt is about 0.072 units per character; a 1.5-unit card holds
  about 18 characters. "replicas: 3, image v1" overflowed on the first render; "3 replicas, v1" fits. Put the fuller
  wording in the note.
- Labels under thin gates or bars collide when the gate spacing is smaller than the label width. Space the objects to
  the labels, not the labels to the objects.
- A control loop is best drawn as its three verbs (observe, compare, act) and a gap: "wants 3, has 0, gap 3" as three
  counters inside the opened box says more than an arrow diagram. Opening the box under a zoom to show the counters, then
  closing it, kept the wide picture untouched.
- "Nothing new happens" is a teachable claim only if the audience has already seen the mechanism once in full. The
  node-failure move reuses the loops from moves two and three at speed and says so on screen; it would not work as the
  first appearance of any of them.
- Time on screen for a timeline the audience cannot feel (40 s grace, 300 s toleration) works as a counter that counts
  through the thresholds with labels appearing at each, rather than a real-time wait.

## Candidate library helpers

- `pulse(scene, a, b, color)`: a small dot travelling from a record to a loop or from a loop to the API server, the
  unit of "observe" and "act". Same as `travel()` but without the flash and with a smaller radius; `travel(..., flash="")`
  covers it, so no new helper is needed; document the idiom instead.
- `watch(a, b)`: a dashed line labelled "watch" between a component and a hub, used for "everything talks only to the
  API server". General enough for any hub-and-spoke system (message brokers, a control plane); candidate for the library:

```python
def watch(a: Mobject, b: Mobject, color: str = MUTED, text: str = "watch") -> VGroup:
    ln = DashedLine(a.get_boundary_point(b.get_center() - a.get_center()), b.get_boundary_point(a.get_center() - b.get_center()),
                    color=color, stroke_width=1.6, dash_length=0.1, stroke_opacity=0.7)
    return VGroup(ln, label(text, 11, MUTED).move_to(ln.get_center() + UP * 0.14))
```

- `card(kind, detail)` and `set_detail(scene, card, text, color)`: a record with a replaceable detail line. Records
  appear in many systems talks (rows, messages, tickets); candidate for the library as `record()`.

## Second pass for legibility (after the coordinator's review)

- What changed: boxes and text scaled up (API server 3.8 wide, cards 1.75 by 0.62, nodes 3.2 by 1.25; 15 pt minimum
  inside boxes, 13 only for "memory"); legend words appear once (the three verbs on the first loop, "watch" on the first
  line, "kube-proxy" once above node 1); pods are plain blocks, v2 pods outlined; every sentence-length label moved to
  the note; three camera zooms added where the action is local (the API server's gates, the node column for filtering
  and scoring, node 1 for the kubelet). Click count unchanged at 22.
- The stage pattern made the pass cheap: one change to `objects.py` re-laid every scene, and the scenes only lost
  labels. Without a shared stage this would have been six layouts to redo.
- Labels inside a zoom must be scaled by the zoom factor (`label(..., 15).scale(ZOOM)`), otherwise they appear
  enormous; `small()` is tuned for 0.4 and reads faint at 0.5 with MUTED, so use `label(..., 20, colour).scale(0.5)`.
- A wide picture with many parts is legible when the labels on it are names the audience already learnt and the
  numbers live in counters; it is not legible when it carries explanation. The cut that helped most was removing
  "no new mechanism: the loops from moves two and three, closing a gap of one" from the screen; the note says it.
- One controller box per loop (four in a column) is a named simplification; they all run inside
  kube-controller-manager. Drawing the process would hide the point, that the loops are independent.

## On the "fill the frame" rule (docs/principles.md 11)

- With the second pass, the deck meets it: labels 15 and up inside boxes, one unit label at 13, and the acting part
  zoomed to half the frame for the steps in between. What made it possible was not enlarging everything but removing
  words and adding zooms; the wide view stays for the first and last step of each move.
