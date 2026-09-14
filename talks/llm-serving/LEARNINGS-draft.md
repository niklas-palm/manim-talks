# Learnings from the no-cuts pass on talks/llm-serving (2026-09-14)

- The cheapest exact seam is a hand-over at the END of the previous scene: it retitles and transforms its picture into
  the next scene's still, and the next scene rebuilds that still statically with the same `start_<scene>()` function.
  Both sides call one builder, so the frames are pixel-identical; `bin/seams.py` reported 0.0 to 0.6 on every seam.
  Rebuilding the previous scene's complex last frame in the next scene would have meant duplicating hundreds of lines.
- The still that used to be a scene's first click is now the previous scene's last frame, so its note moves into the
  previous scene's finish note ("Then the picture hands over: ..."). The speaker still gets a still to talk over.
- Start functions take `add=False` so the previous scene can build the arriving objects without adding them and fade
  them in; the next scene calls the same function with `add=True`.
- Gauges and cache segments set through `.set()` return animations; the static start needs `gauge_at`/`cache_at`
  helpers that `become()` the target directly (in objects.py; candidates for the library).
- A loop variable named `t` shadowed the title in Batching and broke the hand-over with "Animation only works on
  Mobjects"; keep `t` for the title or rename the counter.
- A duplicated definition (`prefill = Counter(...)` left behind after the still was moved) put a stray counter on the
  last frame of a scene; `bin/seams.py` caught it as 0.5 where 0.0 was expected. Read the seam numbers, not only the
  verdicts.
- Travel rule check: the routing dots in PrefixCache landed on the engines' top edges; they now land in the cache slot
  they read. All other travellers (keys and values into cells, queue squares into slots, partial sums between GPUs, the
  sampled token into the sentence) already started at their producer and ended at their receiver.
- Library wishes: `gauge_at`, `cache_at`, `caption_still`, and a `handover(scene, old_title, title, kicker, leaving,
  arriving)` helper, all written in this talk's objects.py; the template's `stage()` pattern plus these covers most decks.
