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
