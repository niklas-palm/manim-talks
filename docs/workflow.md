# Workflow: from a topic to a presented deck

Budget for a 45-minute talk built well: research half a day, script and storyboard a few hours, scenes two to
four days with rendering and review, presenter test an hour. A ten-minute talk scales down but skips nothing.

## 0. Agree the look

Ask, once, before anything is drawn: dark or bright (AGENTS.md, "Choosing the look"). `dark` is the default and what
most rooms want; `bright` is for a lit room, a screen share or a handout. If the answer is a company's own PowerPoint
template, import it with `bin/themes.py from-pptx` and render with that theme; it lands in `themes/local`, which is
never committed. Write the answer into `<talk>/.theme` (or the repository's `.theme` if it is the project's style) so
the render, the two pages and the PowerPoint export agree, and note it in the talk's README. Then look at one frame in it
(`bin/themes.py preview <talk> <Scene>`) before building the rest: a palette that reads on a laptop can lose a colour
on a projector, and finding that out at the end costs a re-review of every scene.

## 1. Research until you can state the spine

Read primary sources: official documentation, the RFC, the paper, the source code, measured numbers. Use the
fetch tools in this session; do not draw from memory alone. You are done researching when you can write the talk's
**spine**: one sentence that every later section is derived from ("a model reads the prompt once, then writes one
token at a time, and every hosting decision is about which of those two you are paying for"). Write down the five
to eight facts the spine rests on, each with its source. Note every simplification you will make and check it is a
simplification and not an error.

Where the documentation lives: many project sites are assembled in the browser and a fetch sees an empty shell
(kafka.apache.org, some SDK docs). The sources are then the markdown in the project's repository (`docs/` folders,
found with `gh api repos/<org>/<repo>/contents/<path>`), generated reference pages, or the paper's HTML rendering
(ar5iv for arXiv). Cite the URL you actually read, with the date.

## 2. Write `script.md`

```
# <Deck title>                      <- the first "# " line is the title the pages show
Spine: <one sentence>
Audience: <who, what they know, what they should be able to do afterwards>

## 1. <Move name> (<minutes>)
- <Scene>. <the problem it names> -> <the mechanism shown> -> <the way out> -> <what that costs / the next problem>
- ...
Sources: <urls, documents, measurements>
```

Each move is one continuous illustration. Each bullet is a scene or a group of steps within one, in the order they
unfold. The chain across moves is the red thread: every remedy introduces the next problem. Read the script aloud;
if a move does not follow from the previous one, fix the order before drawing anything.

## 3. Storyboard each scene: final frame first

For each scene, sketch (in a comment block at the top of the scene file) the final frame: every object that will
ever be on screen, its position band, its colour. Then list the clicks backwards from it: what appears, moves, or
opens at each click, one idea each. Decide the fixed furniture (title, gauges, counters, racks) and give it fixed
coordinates. Decide which words will be labels and where they sit. Decide where the camera zooms, if at all, and
what opens inside the zoom. Only then write code. Design for the half-size review sheet from the start: sizes that
look right in a full-frame
render (12 pt labels, 0.1-unit cells) are unreadable there and on a projector; blocks 0.35 units tall with 14 pt text,
cells 0.16 to 0.42, labels 15 to 18 are the sizes that survived review (docs/principles.md rule 11).

Layout bands (scene units; the frame is 14.22 by 8, origin at centre): title at the top edge with the move kicker
above it; content between y 2.6 and -2.3; a caption, if any, below -2.6. Left of x -5.5 and right of x 5.5 is the
margin where gauges and counters live.

## 4. Write the scene

- Start from `talks/_template/scenes/s01_example.py` for the shape of a scene and the idioms.
- Put the talk's colours and shared drawings in `scenes/objects.py`; import `from lib.palette import *` and
  `from objects import *` in every scene file.
- Start every scene after the first by rebuilding the previous scene's last frame with `self.add(...)` and
  `title_still()`; its first play is `retitle()` together with the first change. Run `bin/seams.py` to prove it.
- Set a caption or labels first, then animate, then `self.next_slide(note)`. Write the note now, not later.
- Build animations in the order they play; never build two `.animate` chains on the same object before playing the
  first (see `docs/manim.md`).
- Keep run times honest: a slow first demonstration (0.2 to 0.5 s per beat), then at speed for repetition (0.07).
- Every number on screen comes from `script.md`'s sources, with its unit and its clock in the label.

## 5. Render, look, fix

```bash
bin/render.sh <talk> ql <Scene>         # preview; a scene renders in seconds to a couple of minutes
THEME=<name> bin/render.sh <talk> ql <Scene>   # the same scene in another style, to check the deck is not tied to one
.venv/bin/python bin/shots.py <talk> ql   # then open <talk folder>/media/shots/<Scene>.png
.venv/bin/python bin/seams.py <talk> ql   # each scene's last frame beside the next scene's first: identical or title only
```

Look at the end frame of every step: collisions, clipped text, wrong colours, a label the animation left behind, a
counter that says the wrong thing. Then render once with `GUIDES=1` and look for anything that sits a little off the
grid lines, a label floating away from its object, unequal gaps, an empty third of the frame (docs/principles.md
rule 12). Then `bin/review.sh <talk> ql` for what happens mid-animation. Fix, render, look
again. Extract single frames with ffmpeg when a moment needs checking:

```bash
ffmpeg -y -ss 3.2 -i <talk folder>/media/videos/<file>/480p15/sections/<Scene>_0004_unnamed.mp4 -frames:v 1 /tmp/f.png
```

Keep tool output short; renders are chatty. Pipe to a log and `grep -c Traceback`.

## 6. Audit the pictures

Run `.venv/bin/python bin/check.py <talk> ql` first: it names the style the talk presents in and whether that style is
fit to present, and it flags any colour a scene named itself, missing files, an `objects.py` without `set_thread`,
scenes whose note count differs from their step count, a scene with no `finish()`, a scene file that does not import
`lib.palette`, a `script.md` without a title line, two scenes with one class name, a scene in a file that is not
`s*.py`, labels under size 12, sentences of more than 14 words on screen, a caption swapped twice in one step, and a
group animated together with one of its members. Below the flags it lists every transform to a rebuilt object, for
you to confirm by eye that the morph is intended. Fix those,
then do the part only eyes can do.


Walk every scene and ask: is anything on screen wrong, as opposed to simplified? Are all simplifications named in a
label or a note? Does every number carry unit and clock? Does every step add one idea? Can a viewer with no sound
say what each step showed? Fix, then run `docs/review.md`.

## 7. Render the deck and test the presenter

```bash
bin/render.sh <talk> qh                 # every scene, 1080p60, then the pages; tens of minutes for a full deck
.venv/bin/python bin/shots.py <talk> qh
bin/serve.sh <talk>                     # opens the presenter; click "open audience window"
```

In the presenter: step through the whole deck with the right arrow; the audience window must follow, hold on each
step's end frame, and the next-step preview must show where the next click lands. Check the timer and the notes.
This test is what catches a broken build; do not skip it.

## 8. Write it down

Update `talks/<talk>/README.md` (what the talk is, the moves, how to run it) and `LEARNINGS.md` at the repo root
(anything that cost time or changed a rule). If you added a helper to `lib/palette.py`, document it in
`docs/library.md` in the same commit.

## Working with sub-agents

A talk's scenes are independent once the script and `objects.py` exist, so scenes can be built in parallel by
several agents, each owning one scene file and rendering only that scene. Two constraints: renders must not overlap
within one talk (shared text cache under `talks/<talk>/media`), so agents building the same talk take turns
rendering; and one agent owns `objects.py` and `script.md`. Different talks can render at the same time.
