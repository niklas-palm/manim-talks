# Building an educational talk in this repository

You are building a presentation in which the pictures do the teaching. The model is a 3Blue1Brown video: one
continuous illustration per idea that unfolds as the speaker talks, where every claim is something the audience
can see happening, and words on screen only name what is already visible. The speaker's explanation lives in
notes the presenter window shows; the audience window shows only the picture.

This file is the entry point. Read it whole, then read the documents it points to, in order, before writing a
scene. They are short and every rule in them was paid for.

1. `docs/principles.md`   what an unfolding illustration is and the rules that make one work
2. `docs/workflow.md`     from a topic to a presented deck, step by step, with the review loop
3. `docs/library.md`      the illustration library in `lib/palette.py`: every helper, when to use it, the patterns
4. `docs/manim.md`        the Manim traps that cost days, each with its fix
5. `docs/review.md`       the checklist a deck must pass before it is called done
6. `docs/presenting.md`   the two-window presenter, how it works, how to test it
7. `LEARNINGS.md`         the living log; add to it whenever something cost you time or changed your mind

Then study `talks/llm-serving`, the reference deck: 82 steps, 13 scenes, every pattern in the library in use.
Read a scene file next to its shots (`talks/llm-serving/media/shots/<Scene>.png` after rendering) to see how
code becomes picture. The other talks under `talks/` are shorter examples built with the same rules: `dns` (a
name becomes an address), `kubernetes` (desired state and the loops that chase it), `kafka` (a log you can replay),
`transformers` (every token learns from every other), `agents` (a model, a list of messages, and a loop). Each has a
`script.md` with its spine, moves and sources, and a `README.md`.

## What you are making

A talk is a folder `talks/<slug>/` with:

```
scenes/objects.py     the talk's vocabulary: which colour means what (set_thread), shared drawings
scenes/s00_*.py ...   one file per move, one or more TalkSlide classes each; presented in file order
script.md             the spine sentence, the moves, the sources; its first "# " line is the deck title
README.md             what the talk is, for a human
media/                rendered clips, notes, shots (generated, ignored by git)
present.html          the audience window (generated)
presenter.html        the speaker window with notes, timer and next-step preview (generated)
```

A scene is a Python class deriving from `TalkSlide`. Inside `construct`, animations play; `self.next_slide(note)`
ends a step (one click of the presenter) and records the note the speaker reads for the step that just played;
`self.finish(note)` ends the scene. Manim writes one clip per step; `bin/build.py` strings clips and notes into
the two pages.

## The workflow, in one paragraph

Research the topic until you can state its spine in one sentence and derive every section from it. Write
`script.md`: the spine, the moves, the one problem each move names and the way out it shows, the sources. For each
scene, design the final frame first, then work backwards to the sequence of clicks that grows it, one new idea
per click. Write the scene, render at preview quality, look at the shots of every step, fix what collides or
lies, render again. Write the notes as you go, next to the step. When every scene passes `docs/review.md`, render
at 1080p60, test the presenter and audience windows in a browser, and commit. Details in `docs/workflow.md`.

## The rules that are not negotiable

- **The picture is the argument.** If a claim cannot be drawn as something happening, it does not go on screen;
  it goes in the note or it goes away. Never a bullet list. Never a paragraph on screen.
- **One continuous illustration per move, and no cuts between moves.** Nothing already on screen is replaced; it
  grows, moves, opens up under a camera zoom, or fades because its job is done. A scene's first frame is the previous
  scene's last frame (`self.add` the picture, `title_still`), and its first play is `retitle()` with the first change.
  There are no title slides. `bin/seams.py` proves it.
- **One idea per click.** If you need two sentences to say what a step showed, it is two steps.
- **Open still, start slow, speed up.** A scene's first click shows the starting picture and nothing moves; the
  mechanism begins on the next click. The first time something happens, it is slow enough to follow; repetitions
  play at speed inside one click.
- **Colours are vocabulary.** A talk uses four to six accent colours, each with one meaning for the whole deck,
  declared in `objects.py` with `set_thread`, so titles and labels colour the nouns automatically. Never reuse a
  colour for a second meaning.
- **Words on screen name things that are visible.** Labels sit next to the object they name and stay. A caption,
  if used at all, is one quiet line set before the animation and never changed while something moves. The
  explanation is in the note.
- **Every number carries its unit and its clock.** "Tokens per second" alone was read three ways by one audience.
- **Named simplifications, no wrong pictures.** Drawing 8 experts where the model has 128 is fine if the label says
  so. Drawing a mechanism that does not work that way is not fine, however pretty.
- **Research before drawing.** Facts come from primary sources (documentation, papers, RFCs, measured numbers) that
  you fetched and read in this session, cited in `script.md`. Do not draw from memory alone.
- **Teach, do not report.** Measurements and examples support the mechanism; they are never the centrepiece.
- **Review with your eyes.** Render, look at the shots, then decide. Do not declare a scene done from code.
- **Add to LEARNINGS.md** when something cost you time or a rule changed. The next agent starts from it.

## Commands

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt   # once; ffmpeg, cairo and pango via Homebrew
bin/render.sh <talk> ql [Scene ...]     # preview render (480p), then build the pages; qm 720p, qh 1080p60 for the talk itself
bin/shots.py <talk> ql                  # the frame every step holds on, tiled per scene: media/shots/<Scene>.png
bin/review.sh <talk> ql                 # a frame every two seconds per scene, for motion and collisions mid-step
bin/check.py <talk> ql                  # structural checks: files, set_thread, notes per step, text sizes, sentences on screen
bin/seams.py <talk> ql                  # every scene boundary: last frame beside first frame, with a difference score
bin/serve.sh <talk>                     # one local server for the repository; opens the talk's presenter window
bin/export_pptx.py <talk> qh            # optional: one PowerPoint slide per step, clip autoplaying, note in the notes; generated, not committed
```

Never run two renders at once (shared text cache). Render one scene while you work on it; render everything once
at the end. Keep terminal output short: renders are chatty, pipe them to a log and grep for `Traceback`.

## Starting a new talk

```bash
cp -r talks/_template talks/<slug>
```

Then follow `docs/workflow.md`. The template has a title scene, one worked example scene that uses most of the
library, an `objects.py` to fill in, and a `script.md` skeleton.

## Definition of done

A deck is done when every item in `docs/review.md` holds, the 1080p60 render exists, the presenter drives the
audience window in a real browser, every step has a note, `script.md` cites the sources, `README.md` says what the
talk is, and `LEARNINGS.md` has what you learned. Report what you built, what you could not verify, and what you
left out and why.
