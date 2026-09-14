# Learnings draft from talks/agents (2026-09-14)

For the parent to merge into `LEARNINGS.md`, `docs/library.md` and `docs/manim.md`.

## Lessons

- A list that grows is the natural state picture for anything with a conversation, a log or a queue: draw every
  message as a block that flies from where it was produced (the user, the model box, a tool card) into its slot.
  Colour by kind (user, model text, tool call, tool result) and the loop becomes visible without an arrow diagram.
- "Every call sends the whole list" is one animation: a copy of the list shrinks into the model box and fades. Doing it
  on every call, at speed, is what makes "the model has no memory" land; saying it does not.
- A code scene works when the code runs against the picture: a highlight bar moves line by line while the picture does
  the step. Keep the picture as a small reminder with colour-only blocks; text at half scale is unreadable and the
  colours carry it.
- The scale trap, twice: a picture designed at 12 pt labels looked right in the render and unreadable on the half-size
  shot sheet; enlarging to 14 pt was still judged small by the coordinator. What worked: message blocks 3.4 by 0.35
  units with 14 pt text and the role coloured, the model box 2.4 by 1.7, tool cards 2.2 by 0.8 with a 15 pt name, code
  at 18 pt filling the right half. Design for the half-size sheet from the start.
- Code at 18 pt in Menlo is about 0.13 scene units per character: 39 characters is five units. Shorten identifiers
  (`msgs`, `run`) before shrinking the font, and keep hook labels inside the frame by measuring the longest line.
- Setting a member's stroke and moving its group in the same play loses the member (the frame moved, text and bar did
  not): the group-versus-member trap from docs/manim.md again, in a new costume. Do the member change in a play of its
  own first.
- A step's end frame is what the presenter holds on: end every step on a settled picture. A 0.3 s append as the last
  animation left the block mid-flight in the shot; `self.wait(0.3)` fixed it.
- The `label()` wrap does not apply to `Text` with an explicit `\n`; two-line labels are the cheapest way to fit a
  sentence beside a box without running off the frame edge.

## Candidate library helpers (used here, in `scenes/objects.py`)

- `block(kind, text, s, bare)`: a one-line message block with a colour bar; `bare=True` for colour-only reminder
  pictures.
- `Messages(x, top, s)` with `slot(i)` and `append(scene, block, frm)`: a growing list whose items fly in from a source.
- `call_model(scene, msgs, model, extra)`: the whole-list-into-the-box animation.
- `code_lines(lines, size)`: monospaced code as a VGroup of lines for line-by-line highlighting (Menlo renders cleanly).
- A generic "list that grows" (`Messages`) and `code_lines` would serve other talks (Kafka's log, a queue, any code
  walk-through) and could move to `lib/palette.py`.

## Out of scope, noticed

- The Strands documentation moved from `/latest/documentation/docs/...` to `/docs/...`; the old URLs 404. Sources in
  `script.md` use the new paths.
