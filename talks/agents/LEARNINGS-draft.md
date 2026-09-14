# Learnings draft from talks/agents, second build (2026-09-14)

For the parent to merge into `LEARNINGS.md`, `docs/library.md` and `docs/manim.md`.

## Lessons

- Start the story before the agent. Opening with the application's own API call (a function that fetches a frame and
  asks a model about it) gives the audience something they already own; the wall (the code decided what to fetch) then
  motivates tools, and the tool scene can turn that same function into a tool without introducing anything new. The
  same function node sits in the same column throughout and becomes the first tool card in place.
- Put each tool card on the row of the device it reaches. A tool call is then a horizontal line, and the model box
  sits above those rows so no call path crosses it. The first layout put the model on the device rows and every travel
  line crossed the model box, which said the opposite of the point.
- The grid overlay (`GUIDES=1`) found every misplacement in one pass: a label two lines wide crossing the model box, a
  label running past its column, a user node on the same row as a box's name. Render with guides before the first
  review, not after.
- Code blocks set the widths. At 15 pt Menlo is about 0.107 units per character; a 46-character line plus the panel's
  padding is 5.8 units, which is the whole right half. Write the code to a character budget before drawing anything
  else on that half, and drop return type hints and long expressions that do not carry meaning (`-> str`,
  `cameras.get(f"/cameras/{camera}/frame")` became `camera_api.frame(camera)`).
- Two hook labels beside one code line need a line pitch of at least 0.4 units at 12 pt; the library's `code()` uses
  Pango's 0.6 line spacing (about 0.3 units at 15 pt). Shifting each line down by 0.13 times its index and stretching
  the panel worked; a `line_spacing` parameter on `code()` would be cleaner (library wish).
- An overflow that is the point may cross the box that contains it (the tenth message crossing the application's
  bottom edge), but nothing else may sit below that edge: the window label moved from under the box to the free space
  under the cards column.
- Right-align a label that sits under an object at the right margin (`align_to(obj, RIGHT)`), or it runs off the frame.
- A label that names a relation between two objects belongs in the free space between them, not centred on the middle
  object (the loop labels under the stop reason, clear of the device column).

## Library wishes

- `code(..., line_spacing=0.9)` to open the pitch when labels sit beside lines.
- `highlight_line(block, i, color)` already covers the inserted-lines case (several bars at once); a `highlight_lines`
  taking a list would save the loop.
- `node(..., sub=)` with a subtitle at 13 pt is the right shape for "function name plus arguments"; it could accept a
  `sub_size`.

## Kept below the size guideline, on purpose

- Tool cards: name 15 pt, description 13 pt, schema 12 pt in a 2.1 by 0.7 card (see README.md, Decisions).
- Request-arrow labels at 13 pt, two lines, so they fit the 1.6-unit gap between the application and the model.
