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

The look is chosen before anything is drawn: read "Choosing the look, before you draw" below first.

Then study `talks/llm-serving`, the reference deck: 82 steps, 13 scenes, every pattern in the library in use.
Read a scene file next to its shots (`talks/llm-serving/media/shots/<Scene>.png` after rendering) to see how
code becomes picture. The other talks under `talks/` are shorter examples built with the same rules: `dns` (a
name becomes an address), `kubernetes` (desired state and the loops that chase it), `kafka` (a log you can replay),
`transformers` (every token learns from every other), `agents` (a model, a list of messages, and a loop). Each has a
`script.md` with its spine, moves and sources, and a `README.md`, and each has a `-bright` sibling that is the same
deck in the other style (see "One deck, two styles" below), so `talks/` holds twelve deck folders for six talks,
beside `_template`.

## Two kinds of talk, and where they live

    talks/<slug>/     the samples in this repository, written to be read as examples by the next agent
    out/<slug>/       a real talk for a real audience: git ignores the whole folder

Both are talks in every other respect, and every tool takes a name and finds it in either (`lib/talks.py`; `out/` is
searched first, so a real deck may take a sample's name and shadow it). Put a deck in `out/` when it is for an
audience rather than for this repository: a company's theme, a customer's numbers, a version of a sample edited for
one room. Nothing under `out/` is ever committed, so a real deck can carry things this repository should not.

Starting one from a sample is a copy, on purpose:
`mkdir -p out/<name> && cp -R talks/<sample>/{scenes,script.md,README.md} out/<name>/`, then write its style into
`out/<name>/.theme`. It is free to diverge, and the sample stays as the worked example.

## What you are making

A talk is a folder (`talks/<slug>/` or `out/<slug>/`) with:

```
scenes/objects.py     the talk's vocabulary: which accent slot means what (set_thread), shared drawings
scenes/s00_*.py ...   one file per move, one or more TalkSlide classes each; presented in file order
script.md             the spine sentence, the moves, the sources; its first "# " line is the deck title
.theme                one line naming this talk's style, if it differs from the project's (see below)
README.md             what the talk is, for a human
media/                rendered clips, notes, shots (generated, ignored by git)
present.html          the audience window (generated)
presenter.html        the speaker window with notes, timer and next-step preview (generated)
```

A scene is a Python class deriving from `TalkSlide`. Inside `construct`, animations play; `self.next_slide(note)`
ends a step (one click of the presenter) and records the note the speaker reads for the step that just played;
`self.finish(note)` ends the scene. Manim writes one clip per step; `bin/build.py` strings clips and notes into
the two pages.

## Choosing the look, before you draw

The look is a theme, not something a scene knows about: every colour, font, corner radius and stroke width comes from
one theme file, so the same deck presents in either style without a scene changing (`lib/theme.py`, `themes/*.json`,
the tokens are in `docs/library.md`).

There are two styles and one way in:

| theme | mode | what it is |
|---|---|---|
| `dark` | dark | Near-black blue-grey, six saturated accents, Helvetica and Menlo. The default, for a room with the lights down. |
| `bright` | light | Warm off-white, thin lines, small corners, a dusty palette of blue, mustard and moss. For a lit room, a screen share or a printed handout. |
| `local/<name>` | either | A company's own PowerPoint theme, imported (below). Never committed. |

Two is on purpose. Earlier there were ten, and the honest finding was that a deck is judged on whether the picture
teaches: a shelf of styles is a way of not deciding. `bright` is not `dark` with the colours swapped, though. It has
thinner lines, smaller corners and fainter fills, because weight reads differently on a pale ground.

**Ask the person you are building for, once, before the first scene: dark or bright?** Dark is the default and what
most rooms want. If they have no preference use `dark` and tell them that is what you did.

How the theme is chosen, first hit wins:

- `THEME=bright bin/render.sh <talk> ql` — one render, for trying the other style
- `<talk>/.theme` — one line naming a style; that talk always presents in it. Every sample has a `-bright` sibling
  that holds nothing but this file, a README and symlinks to the same `scenes/` and `script.md` (see below), so each
  subject exists as a deck in each style
- `.theme` at the repository root — the project's style, which every talk without its own follows
- nothing — `dark`

```bash
bin/themes.py list                        the styles, with the active one
bin/themes.py check [name ...]            contrast, accent distance, installed fonts; run it after editing a theme
bin/themes.py preview <talk> <Scene>      one frame of a real deck in every style, tiled -> media/themes/
bin/themes.py from-pptx <file> <name>     a company's PowerPoint theme -> themes/local/<name>.json
```

**A company's own theme.** `bin/themes.py from-pptx company.pptx acme` reads the file's colour scheme, its body
typeface and its slide master's background; matches its six accents to what each accent slot means, so a deck
keeps its vocabulary in someone else's colours; lifts each away from the background until it can be seen from the back
row; pushes them apart until no two read as one; derives an alert red of the palette's own character; and writes
`themes/local/acme.json`. Render with `THEME=local/acme`. Logos, picture backgrounds and slide layouts are not
imported: a talk here is a picture that unfolds, not a slide inside a brand frame. **`themes/local/` is ignored by git
and must stay that way**, and an imported theme is never committed: a company's palette belongs to them, not to this
repository. Look at the result before presenting it.

**One deck, two styles.** A style variant is its own talk folder with no scenes of its own:

```
talks/transformers-bright/
    scenes -> ../transformers/scenes      a symlink: one source of truth for the drawing
    script.md -> ../transformers/script.md
    .theme                                one line: bright
    README.md                             what it is, in three lines
```

Every tool takes its name like any other talk, and it keeps its own `media/`, its own two pages and its own PowerPoint
export, so both styles can exist rendered at the same time. Never copy the scenes to make a variant: two copies of a
drawing drift within a day. The samples are rendered dark; their `-bright` siblings are rendered at preview quality, and
`bin/render.sh <talk>-bright qh` promotes one when it is going into a room.

**Editing a style.** Change `themes/dark.json` or `themes/bright.json` and run `bin/themes.py check`. It refuses a
theme whose body text is under 7:1 against its background, whose accents are under 3:1, or whose accents are within 22
of each other in Lab, because a deck whose two meanings look alike teaches nothing. Then look at both styles of a real
deck: `bin/themes.py preview <talk> <Scene>` for one frame, or render the `-bright` sibling and read its shot sheets.

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
- **Colours are vocabulary, and they are named by meaning.** A talk uses four to six accents, each with one meaning
  for the whole deck, declared in `objects.py` with `set_thread` so titles and labels colour the nouns automatically.
  Never reuse a colour for a second meaning. Name the slot, never the hue: `USER, MODEL, TOOL = A1, A3, A2`, not
  `= BLUE, VIOLET, YELLOW`. The theme decides what A1 looks like; every slot keeps its character in every theme
  (A1 cool, A2 warm, A3 deep, A4 fresh, A5 growth, A6 spice, ALERT wrong). The same goes for corners, strokes and
  fills: `rad()`, `sw()`, `FILL`, `SOLID`, never a number of your own. `bin/check.py` refuses a scene that names one of Manim's
  colour constants or writes a literal `"#RRGGBB"`; a corner, stroke or fill typed as a number is found by eye. When a picture needs more colours than the six slots, because they identify things
  rather than mean things (twelve requests sharing a step), `identity(n)` gives that many, told apart from each other
  and from the accents, out of the active theme.
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
bin/render.sh <talk> ql [Scene ...]      # preview render (480p), then the pages; qm 720p, qh 1080p60 for the talk
bin/review.sh <talk> ql                  # a frame every two seconds per scene, for motion and collisions mid-step
bin/serve.sh <talk>                      # one local server for the repository; opens the talk's presenter window
P=.venv/bin/python                       # the Python tools want the project's interpreter, as the wrappers above do
$P bin/shots.py <talk> ql                # the frame every step holds on, tiled per scene: media/shots/<Scene>.png
$P bin/check.py <talk> ql                # structural checks: files, notes per step, text sizes, on-screen sentences,
                                         # colours a scene named itself, whether the talk's style is fit to present, and a
                                         # list of transforms to a rebuilt object: confirm by eye that each morph is intended
$P bin/seams.py <talk> ql                # every scene boundary: last frame beside first frame, with a difference score
$P bin/export_pptx.py <talk> qh          # optional: one slide per step, the clip autoplaying, the note in the notes
$P bin/themes.py list|check|preview|from-pptx    # the styles a deck can be presented in; see "Choosing the look"
THEME=<name> bin/render.sh <talk> ql     # render in another style without changing anything
```

Never run two renders of the same talk at once: they share that talk's rasterised-text cache under its `media/`.
Different talks, including a sample and its `-bright` sibling, render in parallel safely. Render one scene while you
work on it; render everything once at the end. Keep terminal output short: renders are chatty, pipe them to a log and
grep for `Traceback`.

## Starting a new talk

```bash
cp -r talks/_template talks/<slug>        # a sample this repository will carry
cp -r talks/_template out/<slug>          # a talk for an audience, which git ignores
```

Then follow `docs/workflow.md`. The template has one worked example scene that uses most of the library, a second
scene that shows how to continue the previous frame without a cut, an `objects.py` to fill in, and a `script.md` skeleton.

## Definition of done

A deck is done when every item in `docs/review.md` holds, the deck was reviewed in the style it will be presented
in (`bin/check.py` names it, and it must be the one the speaker asked for), the 1080p60 render exists, the presenter
drives the audience window in a real browser, every step has a note, `script.md` cites the sources, `README.md`
says what the talk is, and `LEARNINGS.md` has what you learned. Report what you built, what you could not verify,
and what you left out and why.
