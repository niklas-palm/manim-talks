# Presenting: two windows, one control

`bin/build.py` writes two pages into the talk folder. `present.html` is the audience window: only the picture, full
screen with `f`. `presenter.html` is the speaker's window: the current picture, the note for the step in large type,
a timer, a step counter, and a small paused video showing the **end state of the next step**, so the speaker knows
where the next click lands. The presenter drives the audience window; share the audience window in the meeting and
keep the presenter on your own screen.

```bash
bin/render.sh <talk> qh        # renders and builds the pages
bin/serve.sh <talk>            # serves the repository on http://localhost:8765 and opens the talk's presenter.html
```

In the presenter click **open audience window**, move that window to the shared screen, press `f` in it for full
screen. Keys in the presenter: right arrow or space for next, left for back, Home for the first step, `t` resets the
timer. The audience window also answers to its own keys and clicks, and reports its position back, so the two stay
in step whichever one you drive.

Both pages are dressed in the talk's own style: `bin/build.py` reads the theme the talk presents in (the same
resolution the render uses) and mixes the page chrome from its ground and its ink, so a bright deck is not served
inside a dark frame. Rebuilding the pages without re-rendering (`bin/build.py <talk> <quality>`) is safe for the same
reason.

## How it works, and why it is built this way

- **One video per scene with pause points at the step boundaries**, not one clip per step. Swapping a video's
  source between clips redraws the element and flickers; pausing and resuming one source is seamless. The
  boundaries come from the per-step durations Manim writes into the section index.
- **Two stacked `<video>` elements**, the next scene preloaded in the hidden one; a scene change swaps their
  z-index. Without this the first frame of each scene arrived late as a black flash.
- **A third, paused video for the next-step preview**, seeked to the next boundary minus a few milliseconds.
- **The two windows talk over a `BroadcastChannel` and a direct `postMessage`** to the window the presenter opened.
  Two `file://` pages have opaque origins and may not share a channel, so the pages must be served over http.
- **One server for all talks.** `bin/serve.sh` serves the repository root and opens the talk's page under
  `/talks/<name>/` or `/out/<name>/`; starting it for a second talk reuses the running server, so the first talk's windows keep
  working. (An earlier version served one talk folder per port, and starting a second talk turned the first one's
  windows black after the current scene: every later video request was a 404.)
- **The server answers byte-range requests** (`bin/serve.py`), including suffix ranges. Python's `http.server` does not, and Chrome then
  treats the video as unseekable: every `currentTime` assignment is ignored, each step replays the scene from its
  start, and the hold at the boundary leaves a blank frame. Forty lines of standard library fix it.
- **Browsers block autoplay without a click**, so the audience page has a start screen; the first click starts it.

## Before the talk

Step through the whole deck in the presenter with the audience window open, once, at the quality you will present.
Check that every step holds on its end frame, that back works, and that the next-step preview shows the right
frame. Check the notes read well in the presenter's type size. Close other tabs that play media. Keep the laptop on
power: a 1080p60 video plus a preview video is real decoding work.

## Exporting to PowerPoint

The PowerPoint file is generated, never committed: `talks/*/*.pptx` is in `.gitignore`, like the rendered videos, and
everything under `out/` is ignored wholesale.
Render the deck first, then export; regenerate after every render, since the file embeds the clips.

```bash
.venv/bin/pip install python-pptx                 # once
bin/render.sh <talk> qh                           # the clips the export embeds
.venv/bin/python bin/export_pptx.py <talk> qh   # -> <talk folder>/<talk>.pptx  (a minute or two; 12 to 45 MB per deck)
.venv/bin/python bin/export_pptx.py <talk> qh out.pptx --click   # elsewhere, and clips that wait for a click instead of starting
```

One slide per step: the step's clip fills the slide and is set to start automatically when the slide appears, so a
click in PowerPoint does what a click in the presenter does; the clip holds on its last frame; the speaker note is in
the slide's notes with the scene name and step number. The poster frame is the clip's first frame, so a slide looks
like the end of the previous one until it plays. This is a convenience for people who must present from PowerPoint;
the web presenter remains the reference, and the two-window flow, the timer and the next-step preview exist only
there. The autoplay is the timing XML PowerPoint writes for "Start: Automatically", and it is verified: PowerPoint
opens the file without repair and reports the clips' play-on-entry as true through its object model. Pass `--click`
for clips that wait for a click instead. python-pptx writes a bare timing node of its own when it adds a movie; the
export replaces it rather than adding a second, because two timing elements make the file unopenable.

## Exporting to PDF

The file people ask for after a talk is the pictures without the notes. `bin/export_pdf.py` writes one page per scene,
showing the settled picture the scene ends on, which is everything the move drew; nothing from the notes goes in. Like
the PowerPoint file it is generated from the render and never committed (`*.pdf` is in `.gitignore`).

```bash
bin/render.sh <talk> qh                           # the frames come from the render
.venv/bin/python bin/export_pdf.py <talk> qh      # -> <talk folder>/<talk>.pdf, one page per scene
.venv/bin/python bin/export_pdf.py <talk> qh out.pdf --steps   # elsewhere, and one page per step instead
```

`--steps` gives the frame every step holds on, the same frames `bin/shots.py` tiles for review: a fuller record, at the
price of many pages that differ by one detail.
