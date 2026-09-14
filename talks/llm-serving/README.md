# LLM serving, the talk

A 45-minute talk on how open-weight LLMs are served and what the hosting decisions actually do, built as
animated diagrams with [Manim Community Edition](https://github.com/ManimCommunity/manim), the engine
behind 3Blue1Brown's videos. Every number in the scenes was measured in the companion project,
[llm-serving](https://github.com/niklas-palm/llm-serving), whose `docs/tuning.md` is the source.

The talk has one spine: **a model reads the prompt once, then writes one token at a time, and every
hosting decision is about which of those two you are paying for.** Seven moves hang off it:

| Move | Scenes | Minutes |
|---|---|---|
| 1. Two jobs, two costs | `Mechanics` (one continuous picture: text, tokens, a layer up close, prefill, decode, text), `DecodeCeiling` (a dense model's ceiling first, then this model's) | 9 |
| 2. Why the engine batches | `Batching` (decode as a timeline of steps: one request, four sharing each read, continuous batching; then the measured curve) | 7 |
| 3. Three knobs: weights, experts, cache | `Quantisation`, `MixtureOfExperts`, `PrefixCache` (routing and offloading) | 8 |
| 4. More than one GPU | `Parallelism` (the whole vector on every GPU, a slice of every matrix each, the all-reduce animated between the GPUs; then the step timelines) | 6 |
| 5. What precision costs in answers | `Rounding` (the mechanism: fewer levels, small shifts, close calls flip), `NoiseFloor`, `PrecisionCost` | 7 |
| 6. The fleet | `Fleet` (first principles: engines add up, a new engine must load the model, the balancer sees latency but not why) | 5 |
| 7. Where the industry is | `Industry` (six fronts, re-validated against the engine and orchestration projects' own documentation), `Close` | 4 |

The speaker notes live in the scene code next to the step they belong to; `script.md` maps each move to the sections of `docs/tuning.md` behind it.

## Build and present

From the repository root:

```bash
bin/render.sh llm-serving ql      # quick preview, 480p; qm for 720p, qh for 1080p60 for the talk itself
bin/serve.sh llm-serving          # serves the talk on localhost:8765 and opens the presenter; "open audience window" opens present.html
bin/shots.py llm-serving qh       # the end state of every step, tiled per scene under media/shots/
bin/review.sh llm-serving ql      # one contact sheet per scene, a frame every two seconds
```

Each scene is a `TalkSlide`; `self.next_slide(note)` marks the end of a step and records the speaker note for it.
`bin/build.py` turns the clips and notes into `present.html` (audience) and `presenter.html` (speaker: notes, timer,
where the next click lands). How that works and why is in `docs/presenting.md`.

## Layout

```
scenes/objects.py    the talk's five accent slots with fixed meaning (prompt, output, weights, cache, hot),
                     the nouns they colour, and the GPU drawing (memory bar, compute grid, bus and compute gauges)
scenes/s00 .. s08    one file per move; scenes are presented in file order
script.md            the spine, the moves, the sources
```

## Pacing and seams

There is no title slide: the deck opens on the first picture, the sentence, and the speaker introduces the talk over it.
Every scene opens on a still (the previous scene's last frame) and the mechanism starts on the next click; the first
occurrence of a mechanism is slow enough to follow and repetitions play at speed inside one click. Scene boundaries are
invisible: the last step of every scene hands over to the next one (the stage folds into the GPU drawing, the measured
GPU becomes the 96 GB card, the weights bar grows into the dense stack, the grid of questions is cleared for the next
comparison, the two phases shrink to the top for the close), and the title changes in place as the picture changes.
`bin/seams.py llm-serving` reports every seam as identical or title only. 82 steps in 13 scenes.

## Style rules

Accents carry meaning across the whole talk and are never reused for something else: prompt, output,
weights, cache, hot. Titles and labels colour those four nouns wherever they appear,
so the legend is learned once. Every scene opens by naming a problem, shows why it exists on the picture
already on screen, then shows the way out; measurements support the argument and never lead it. One new idea
per step. Diagrams grow; nothing already on screen moves unless the movement is the point. Numbers appear
next to the thing they measure, and every number is one the companion repository measured. A line above each
title names the move, so the audience always knows where on the map they are. Words on screen are labels: a
few words next to the thing they name, never a sentence. Where a step still carries a footnote caption it is at
most a dozen words, set before the animation and left alone; the explanation is in the speaker notes.
