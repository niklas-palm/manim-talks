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

## Library helpers

- `block`, `Stack` and `code_lines` were promoted to `lib/palette.py`; this talk now uses them, with its kinds mapped to
  colours in `objects.py` (`block(text, KIND[kind])`). The small reminder picture in TheCode scales bare blocks with
  `.scale(S)` and passes `h=BH * S, gap=GAP * S` to `Stack`.
- Still local: `call_model(scene, msgs, model, extra)` (the whole list shrinking into the model box), `tool_card`,
  `device`, `app_box`, `model_box`, `reply`.

## Kept below the size guideline, on purpose

- Tool cards carry three lines (name 15 pt, description 13 pt, schema 12 pt) in a 2.2 by 0.8 card. Larger text does
  not fit three lines beside the message list, and the name is the line the audience must read; the description is
  read aloud in the note. `bin/check.py` accepts 12 as the floor.

## Out of scope, noticed

## Out of scope, noticed

- The Strands documentation moved from `/latest/documentation/docs/...` to `/docs/...`; the old URLs 404. Sources in
  `script.md` use the new paths.
