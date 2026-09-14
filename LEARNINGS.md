# Learnings

The living log. Add an entry whenever something cost time or changed a rule; date it and name the talk. The
technical Manim entries are consolidated in `docs/manim.md`, the style rules in `docs/principles.md`; this file is
where they arrive first.

## From the reference deck (talks/llm-serving, September 2026)

- Prefill and decode are the same picture with a different number of columns, so draw them that way: the first
  zoom takes the whole block through the layer (one row lit, five columns multiplied), the second takes one column
  through the same stages. The contrast does the teaching; no caption has to say "compute-bound".
- When the second look at a mechanism must say "this is the same computation", show every stage again, not the one
  that carries the point. The decode zoom that swept only the feed-forward read as "decode skips attention".
- Name what a number is spent on. "Bytes per step" hid two reads with different behaviour: weights, fixed per step,
  and cache, growing with every token and every request. Label both where they are read.
- Name the two words before using them. Latency and throughput defined on screen with one request, where they are
  the same number, is what turns batching from a feature into a knob between the two.
- Every number on screen carries its unit and its clock: "tokens/s" alone was read three ways.
- A conveyor with time along x is the honest picture of a scheduler: step width is step time, so load shows as
  wider columns without a word. Slide old columns under a background-coloured mask instead of animating opacity.
- One click per measured point. A curve drawn in one go is a picture; a curve drawn point by point is an argument.
- A caption that changes under an animation is not read. Captions became a quiet footnote, and the scenes rebuilt
  last have none: the words sit next to the thing they name and stay.
- Titles in plain words. "Do not read what you already read" and "the ceiling you can read off a spec sheet" were
  replaced by "reusing the KV cache across turns and engines" and "GPU latency and throughput". Catchy costs
  comprehension.
- Show the speaker the end state of the next step, not its first frame. It answers the question the speaker has.
- Draw the machine, not a box for the machine: a memory bar and two gauges did more teaching than any label.
- When a picture repeats (layer two after layer one), replay it at speed inside the same step, without a click.
- Screenshot the end of every step and review the sheet. Every collision was found there and none in the code.
- Clear a zoomed view before zooming out. The block that lingered over the collapsed box looked like a bug because
  it was one.
- A mobject in two groups animated in one play (a fade-in group and a shifting row) ends where the fade started.
  Keep the groups disjoint. The cell created inside a zoom must be added to the row group that shifts back.
- Never run two renders of the same talk at once; the shared text cache kills the longer one.
- Ask what the audience will read a number as. "330,000 tokens of context" read as tiny until the label said "about
  40 conversations of 8k tokens, or one request at the model's full context".

## Tooling (September 2026)

- Never script the user's PowerPoint to verify an export. An AppleScript that opened a test file and then closed
  "the active presentation" without saving closed the user's own open deck instead. Verify a .pptx by re-reading it
  with python-pptx and inspecting the slide XML; leave opening it to the user, and say so in the report.
- The PowerPoint export is one autoplaying clip per step with the note in the slide notes; 76 steps of 1080p60 came
  to 44 MB. It is a convenience for rooms that demand PowerPoint; the web presenter stays the reference.

## From the example decks (talks/dns, kubernetes, kafka, transformers, agents; 2026-09-14)

Five decks built in parallel by agents from the same instructions. What they found in common, then per deck.

Common to all five:
- The scale trap. Every first pass drew the mechanism correctly at 12 pt labels and cells of 0.06 to 0.12 units and read
  as a paper figure at half size. The second pass scaled up (cells 0.16 to 0.42, labels 15 to 18, blocks 0.35 tall with
  14 pt text) and moved sentences to notes, changing nothing about the mechanism and everything about legibility.
  Design for the half-size review sheet from the start; the rule is now principles.md rule 11 and check.py flags the text.
- On-screen sentences crept in as labels ("min.insync.replicas = 2: the write is refused, not stored on one disk").
  A label is a clause of a few words next to the thing; the sentence is in the note. check.py flags labels over 14 words.
- Primary documentation is often assembled in the browser; fetching the site gives a shell. The sources are the
  repository's markdown (`gh api repos/<org>/<repo>/contents/<path>`), generated reference pages, ar5iv for arXiv papers,
  the RFCs and IANA for DNS. Some learning sites return 403 to a fetcher; the primary source is better anyway.
- State drawn as a list that only grows (a log with offsets, a stack of message blocks) was found independently by
  three decks; it is now `Log`, `Pointer`, `Stack` and `block` in the library.
- End every step on a settled picture; the presenter holds on the last frame.

DNS:
- `Text[a:b]` indexes glyphs without spaces; colouring by string index lands one character left per preceding space.
  Use `thread=True` with `set_thread`, or the library's `"[a:b]"` t2c keys.
- Two texts on one row need one anchor relative to the other's edge, not two fractions of the row.
- Name anything created inline that must later leave the screen; an anonymous `FadeIn(fuse(row))` cannot be faded out.
- A helper that rebuilds the previous scene's final frame in one call is what makes a deck one continuous illustration
  across scene files (the stage pattern, now in the template).
- Live numbers (`dig +trace`: a TTL read at 300 s in one cache and 281 s in another) teach better than textbook ones.
- Six large rows and a counter running to 340,000,000 said "the size of the internet" better than thirty small rows.

Kubernetes:
- A stage object holding the whole fixed picture at fixed coordinates was the single most useful thing in the deck.
- Card text at 12 pt is about 0.072 units per character; a 1.5-unit card holds about 18 characters.
- Space the objects to the labels, not the labels to the objects, when labels sit under thin gates.
- A control loop is three verbs and a gap (wants 3, has 0, gap 3) inside an opened box, under a zoom.
- "Nothing new happens" only teaches after the mechanism has been shown once in full.
- Time the audience cannot feel (40 s, 300 s) is a counter counting through the thresholds with labels at each.
- Rule 11 was met by removing words and adding zooms rather than by enlarging everything.

Kafka:
- One row of cells with offsets served as the vocabulary for a partition, a segment, the offsets topic and the
  metadata log; reusing it for the system's own state made the closing point visible without a word.
- A reader is a triangle under the log; replay, rebalance and offset reset are all pointer movements.
- Budget 0.45 units under the offsets for a pointer and its tag, 1.4 units between stacked logs.
- `group.animate.set_opacity` fills a stroke-only member; dim cells and labels separately (docs/manim.md).
- Ghost copies (`copy().set_opacity(0.25)`) are the cheapest picture of a machine that exists but is idle.
- A gauge in the margin needs a short two-line name ("write\nload"); a long name clips at the frame edge.

Transformers:
- Show the sum, not the label: value copies flying into the new vector scaled by their weights, filling it cumulatively.
- A stack of identical layers is the same picture repeated smaller, not text in boxes.
- A residual is the update's cells landing one by one on the vector.
- Illustrative scores are fine when the operation is exact and the note says the numbers are chosen.
- The sweep highlight must not be a semantic accent; the neutral `HI` is now the library default.
- Arcs bow toward the side the sign of `angle` says; a loop-back arrow with a positive angle crosses the title.

Agents:
- "Every call sends the whole list" as one animation (a copy of the list shrinking into the model) is what makes the
  model's statelessness land.
- A code scene works when the highlight runs against the picture; keep the picture as a colour-only reminder.
- Menlo at 18 pt is about 0.13 units per character; shorten identifiers before shrinking the font.
- A member change and a group move in one play lose the member (docs/manim.md).
- Two-line labels beat wrapping beside a box.
- Switching a deck from its own helpers to the library versions is cheap to verify: compare the end frames of every
  step before and after (mean pixel difference), not the code. Kafka's migration measured under 2/255 everywhere.
- Uneven letter spacing and vanished spaces in small labels, seen in every deck, came from Pango rounding glyph
  positions to pixels at the requested size. Laying out at 48 and scaling down fixed it everywhere at once; the lesson
  is that text must always go through the library, never `Text()` directly, so a fix like this lands in one place.

## From the quality passes and the agents rebuild (2026-09-14, afternoon)

First principles that the passes confirmed, written to outlast the decks they came from:
- The audience re-orients every time the picture changes. One fixed stage per deck, built by one function in
  `objects.py` and added by every scene, is what makes six scene files one illustration; the alternative, a fresh
  layout per scene, cost every deck a second pass.
- Reserve the space the picture will grow into. An empty list inside its box, an empty rack, an empty column: the
  audience reads the emptiness as "something goes here", and later steps have somewhere to go without moving what is
  already placed.
- Open on a still and let the speaker name what is there. Every deck had at least one scene that started moving before
  the audience knew what it was looking at. Splitting the first click costs one note and buys the whole scene.
- Alignment is not decoration. Frames that sat a little off a grid, with labels floating and unequal gaps, read as
  sloppy before anything moved; the same frames on the grid read as professional with no other change. The grid
  overlay (`GUIDES=1`) made the difference visible in one render.
- Text must go through one place. Uneven letter spacing in every deck had one cause (Pango's pixel rounding at small
  sizes) and one fix (lay out at 48 and scale), which landed everywhere at once only because every label came from
  `label()`. Any text built directly would have kept the defect.
- Code on screen is code: highlighted, indented, large, on its own panel, and walked line by line against the picture.
  Plain monospaced text read as a paragraph and was skipped.
- When a thing changes role, morph it; do not replace it. The camera API box becoming the tag on the first tool card is
  the whole point of "from an API to a tool"; a new card appearing beside an old box would have said nothing.
- Standing relations are dashed and horizontal; flows are arrows. A diagonal dashed link across the flow arrows made
  one frame unreadable.
- The group-and-member trap bites experienced hands too: it recurred in the rebuilt deck despite being documented. It is
  now a checker rule, which is where a lesson that keeps recurring belongs.
- Review by looking, at half size, before the 1080p render, and again after. Every pass found something the previous one
  had called done.

## From the pacing pass (2026-09-14, afternoon)

- A still first step is cheap when a scene builds its furniture in one play: insert the click after that play and write
  a note that names what is on screen. Where the opening was an animation of the object itself, a FadeIn of the
  finished object is the still and the reveal becomes the first mechanism.
- The still step needs its own anchor for the eye: a claim line or a label, otherwise the frame reads as unfinished.
- When a first click is split, ask whether the moved animation belongs to the next step's idea; merging it there keeps
  one idea per click without adding a step.
- First occurrences at 0.3 to 0.6 s per beat, repeats at 0.07 to 0.3 s, is the shape that held in every deck.
- A long value in a fixed-column row is shortened, not shrunk: "cdn.example.net." fit where a longer alias did not.
- A row that sat at y -0.35 left the bottom third empty; at y -1.0 the same picture used the band. Where a picture
  does not grow into the lower band, move it down rather than leave the band empty.
- A picture that runs past the frame edge on purpose (a list too long to show) should fade towards the edge; cut off
  rows read as overflow, faded rows read as "it continues".
- Known imperfections left on purpose in the reference deck: the Industry scene is a labelled list of fronts around the
  two-phase picture, and the Fleet scene's first two steps use the upper half. Both would be better as pictures that
  grow; recorded here rather than redesigned in this pass.
