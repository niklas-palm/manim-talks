# Principles: what an unfolding illustration is

The reference is a 3Blue1Brown video. Watch one with the sound off and you can still follow the argument: a single
picture appears, something happens to it, the consequence is visible, the camera moves in to show a detail, moves
out, and the same objects carry the next idea. Words appear only as labels on things you can see. The narration
explains; the picture proves. That is what every scene here is trying to be. The rules below are the operational
form of that goal, in the order they matter.

## 1. The picture is the argument

Every claim a step makes must be visible as something happening to an object on screen. "Decode is bound by
memory bandwidth" is not drawn as a sentence; it is drawn as the same matrix being read in full for one column of
work where a moment ago it was read once for five, with a gauge that fills. If you cannot find the picture, you have
not understood the claim yet, or it belongs in the speaker's note rather than on screen.

Test: could a viewer with the sound off say what the step showed? If not, the step is not done.

## 2. One continuous illustration per move

A move (a chapter of the talk, five to ten minutes) is one picture that grows. The first click puts the first
object down; every later click adds, moves, opens, or highlights; nothing is replaced by a different picture. When
the audience needs to see inside something, the camera zooms and the object opens up; when the detail is done, the
contents fade and the camera pulls back to the untouched wide view. Slides that replace each other make the
audience rebuild their mental model each time; a growing picture lets them keep it.

Consequences:
- Design the final frame of the move first. Everything that will ever be on screen has a place in it. Then work
  backwards to the sequence of clicks that grows it.
- Fixed furniture (title, gauges, counters, racks) goes at fixed coordinates, not in `next_to` chains that drift.
- When a picture repeats (layer two after layer one; the second request after the first), replay it at speed inside
  the same click, without a new click. Repetition is learned by seeing it, not by being told.
- Clear a zoomed view before pulling back, then zoom out on a clean object. The two in one motion looks broken.
- **No cuts between scenes.** Scenes are separate videos, so a scene's first frame must be the previous scene's last
  frame: build that picture with `self.add(...)` (the stage plus whatever the previous scene left) and `title_still()`,
  then make the first change with `retitle()` in the same play as the first animation. The audience sees one picture
  whose title changes as it starts to move, never a black frame with a new header. `bin/seams.py <talk>` measures
  every seam; anything above "title only" is a cut. There are no title slides: the deck opens on the first picture,
  and the speaker introduces the talk over it.

## 3. One idea per click

After every click the audience must be able to say in one sentence what changed. If the sentence needs an "and",
split the step. If nothing visible changed, the step has no reason to exist. A 45-minute talk is sixty to eighty
clicks; a ten-minute one is fifteen to twenty.

## 3b. Open on a still picture; start slow, then speed up

The first click of a scene shows the starting picture and nothing moves: the title, the furniture, the objects the
scene begins with. The speaker names what is on screen; the mechanism starts on the next click. Within a scene the
first time something happens it happens slowly enough to follow (0.3 to 0.6 s per beat, one thing at a time); when
the same thing happens again it plays at speed inside one click (0.07 to 0.15 s per beat). A scene that opens
already moving, or a mechanism that runs fast the first time, teaches nothing; a mechanism that runs slowly the
third time bores. The presenter's next-step preview shows the speaker where the animation will end, so a still
first step costs nothing.

## 4. Colours are vocabulary

Pick four to six accent colours and give each one meaning for the whole deck: in the reference deck prompt blue,
output yellow, weights violet, cache teal, hot red. Declare them in `objects.py` with `set_thread`, and the titles
and labels colour those words automatically wherever they appear. The audience learns the legend in the first
scene and reads every later picture without one. Never reuse a colour for a second meaning, not even in a different
scene. Grey (`DIM`) means "not in focus"; `MUTED` is for small text; `RED`/hot means saturated, wrong, or the
problem.

## 5. Words on screen name things that are visible

Labels sit next to the object they name and stay there. Counters carry their unit and their clock in their name.
A caption at the bottom, if a scene uses one at all, is one quiet line, set before the animation of the step and
never changed while something moves: a caption that changes under an animation is read by nobody and pulls eyes
off the picture. The scenes rebuilt latest in the reference deck have no captions at all; every word is a label.
Never a bullet list, never a paragraph, never a sentence that explains. Explanation is the speaker's job and lives
in the note.

## 6. Every scene names a problem, shows why it exists, then shows the way out

The red thread of a talk is a chain of problems and remedies, each remedy creating the next problem. A scene opens
by naming the problem on the picture already on screen (a gauge pegged, a queue forming, a cell that does not fit),
shows the mechanism that causes it, then the remedy, then what the remedy costs. Measurements and examples arrive
as support for that argument, never as the reason for the scene. If a scene is "here is what we measured", rewrite
it as "here is the mechanism, and here is the measurement that confirms it".

## 7. Define a word on screen before using it

If the talk depends on a term (latency, throughput, quorum, partition), the first scene that needs it shows two
things that make the term concrete and writes the definition next to them once. In the reference deck, latency and
throughput are defined with one request, where they are the same number, so that batching in the next scene is
visibly the knob between them.

## 8. Named simplifications, no wrong pictures

Every drawing simplifies. Simplify by leaving things out and say so in the label ("drawn as 8 experts with 2
chosen; the model has 128 with 8"). Never simplify by drawing a mechanism differently from how it works: an
audience of engineers will remember the wrong picture longer than the right sentence. Audit every scene for this
before calling it done: is anything on screen outright wrong?

## 9. Time along x

When the subject is a schedule, a pipeline, a stream or a queue, draw time along the horizontal axis and let
duration be width. A longer step is a wider block; load shows as wider columns without a word. Scroll the past
off to the left under a mask rather than fading it. Each request, message or job keeps its colour from arrival to
completion so it can be followed.

## 10. Zoom to open, not to enlarge

A camera zoom is a chance to open an object and show its parts in the same place the audience was looking at:
the layer box stretches and the three matrices, the attention read and the feed-forward appear inside it. Small
text in a zoom is rendered large and scaled down (`small()`). Everything drawn in the zoom goes into one group that
fades on the way out, and the box shrinks back so the wide view is untouched.

## 11. Fill the frame

The content band is about 14 by 5 scene units and the audience sits far from it. The main object of a scene should
span at least half the band; cells in an unzoomed grid or vector are 0.14 to 0.25 units, never 0.08; labels are
size 15 or larger. A small drawing surrounded by empty canvas reads as a diagram in a paper, not as a picture that
teaches. If the mechanism needs small parts, zoom the camera into the part (rule 10) rather than drawing it small.
Check the shots at half size: if you have to lean in, the audience cannot see it.

## 12. Aligned and organised

A frame is read as professional or as sloppy in the first second, before anything moves. The rules:
- One grid. Fixed furniture sits on the column lines `COLS` (x = -6.4, -3.2, 0, 3.2, 6.4) and the row lines `ROWS`
  (y = 2.6, 1.3, 0, -1.3, -2.3) from the library; nothing sits a little off a line. Render with `GUIDES=1` to see the
  grid while you work.
- Three gaps, not thirty: `GAP_TIGHT` (0.12) between a label and its object, `GAP` (0.25) between objects, `GAP_WIDE`
  (0.5) between groups. Equal things have equal gaps.
- Every text is attached: a label aligns to its object's left edge (`align_to(obj, LEFT)`) or is centred on it;
  numbers in a column share a right edge; a row of boxes shares a y and a height. No text floats in empty space.
- Related things are enclosed or aligned, never both loose: a group of tool cards shares a column and a box; a set of
  counters sits in one row at one y.
- Use the whole content band. The main object is centred in the space left after the fixed furniture; empty thirds
  of the frame mean the drawing is too small or the furniture is in the wrong place.
- Nothing within 0.3 units of the frame edge; nothing overlapping unless the overlap is the point.
- Symmetry where the content is symmetric (two things compared side by side), and left-to-right flow where it is a
  process (source on the left, result on the right).

## 13. The speaker's note is the explanation

Each step's note is one paragraph the speaker can read aloud: what the audience is looking at, what just changed,
why it matters, and the one fact or number that anchors it. Notes carry the nuance, the caveats, the measured
figures and the sources. Write them as you write the step; notes written afterwards drift from the picture.

## 14. Teach, do not report

The audience is engineers who want to understand a system, not an account of your experiments. Every example,
measurement and product name is there because it makes a mechanism concrete. Say what is generally true; then say
what you measured that confirms it; then stop.

## 15. Review with your eyes

Render at preview quality, look at the end frame of every step (`bin/shots.py`), then at the contact sheet of
frames through the animation (`bin/review.sh`). Every collision, clipped label, colour mistake and mistimed reveal
in the reference deck was found this way and none from reading code. Do this per scene while building and once
more for the whole deck at 1080p60 before calling it done.
