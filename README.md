# manim-talks

A starting point for educational talks in which the pictures do the teaching: continuous illustrations that
unfold click by click, in the style of a 3Blue1Brown video, built with
[Manim Community Edition](https://github.com/ManimCommunity/manim) and presented from a browser with a speaker
window driving an audience window. No slides, no bullets, no presenter software.

Agents building a talk start at `AGENTS.md`. Humans start here.

## What is in the box

```
AGENTS.md            the entry point for an agent building a talk: rules, workflow, definition of done
docs/                principles, workflow, the library, Manim traps, the review checklist, presenting
lib/palette.py       the illustration library: colours with meaning, TalkSlide, text, counters, gauges, grids ...
bin/                 render.sh, build.py, shots.py, review.sh, check.py, serve.sh, serve.py, export_pptx.py
talks/_template/     copy this to start a talk: title scene, a worked example scene, objects.py, script.md
talks/llm-serving/   the reference deck: 45 minutes on how open-weight LLMs are served, 76 steps, 14 scenes
talks/<others>/      shorter example decks built with the same rules: dns, kubernetes, kafka, transformers, agents
LEARNINGS.md         the living log of what cost time and what changed a rule
```

## Quick start

```bash
brew install ffmpeg cairo pango pkg-config          # once
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
bin/render.sh llm-serving ql                         # preview render of the reference deck (480p)
bin/serve.sh llm-serving                             # opens the presenter; click "open audience window"
```

To start your own: `cp -r talks/_template talks/my-talk`, then follow `docs/workflow.md`.

## How a talk is built

A talk is a folder of Manim scenes. Each scene is one continuous picture; `self.next_slide(note)` marks a click
and records the speaker note. Manim writes one clip per click, `bin/build.py` strings the clips and notes into two
pages: `present.html` for the audience and `presenter.html` for the speaker, with notes, a timer and a preview of
where the next click lands. `bin/serve.sh` serves the talk over local http so the two windows can talk and the
video can seek. `bin/export_pptx.py` writes the same deck as a PowerPoint file, one autoplaying clip per slide with the
note in the slide notes, for rooms that insist on it.

## Style, in five lines

The picture is the argument; words only name what is visible. One continuous illustration per chapter; nothing
is replaced, it grows. One idea per click. Colours are vocabulary: each has one meaning for the whole deck. Every
number carries its unit and its clock, and traces to a source.
