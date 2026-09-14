# Presenting: two windows, one control

`bin/build.py` writes two pages into the talk folder. `present.html` is the audience window: only the picture, full
screen with `f`. `presenter.html` is the speaker's window: the current picture, the note for the step in large type,
a timer, a step counter, and a small paused video showing the **end state of the next step**, so the speaker knows
where the next click lands. The presenter drives the audience window; share the audience window in the meeting and
keep the presenter on your own screen.

```bash
bin/render.sh <talk> qh        # renders and builds the pages
bin/serve.sh <talk>            # serves the repository on http://localhost:8765 and opens talks/<talk>/presenter.html
```

In the presenter click **open audience window**, move that window to the shared screen, press `f` in it for full
screen. Keys in the presenter: right arrow or space for next, left for back, Home for the first step, `t` resets the
timer. The audience window also answers to its own keys and clicks, and reports its position back, so the two stay
in step whichever one you drive.

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
  `/talks/<name>/`; starting it for a second talk reuses the running server, so the first talk's windows keep
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

```bash
.venv/bin/pip install python-pptx      # once
bin/export_pptx.py <talk> qh            # -> talks/<talk>/<talk>.pptx
```

One slide per step: the step's clip fills the slide and is set to start automatically when the slide appears, so a
click in PowerPoint does what a click in the presenter does; the clip holds on its last frame; the speaker note is in
the slide's notes with the scene name and step number. The poster frame is the clip's first frame, so a slide looks
like the end of the previous one until it plays. This is a convenience for people who must present from PowerPoint;
the web presenter remains the reference, and the two-window flow, the timer and the next-step preview exist only
there. The autoplay is the timing XML PowerPoint writes for "Start: Automatically"; open the file once in PowerPoint
before relying on it, and if a slide does not start by itself, set the video to start automatically in the Playback
tab and report the case in `LEARNINGS.md`.
