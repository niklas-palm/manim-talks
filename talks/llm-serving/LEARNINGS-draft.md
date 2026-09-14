# Learnings draft: llm-serving text pass (2026-09-14)

- Forty-three on-screen sentences shortened to labels of at most twelve words; every original sentence folded into
  the note of the step it belonged to, so nothing the speaker needs was lost. The pictures already carried the
  claims; the captions had been saying them a second time.
- Two-line legends are fine as two `label()` calls in a `VGroup`; one long string is what the check flags, and it is
  also what wraps badly.
- `bin/check.py` false positives worth fixing: `swap_caption(self, ...)` contains the substring `caption(self`, so
  every swap counts as two caption changes in a step; label sizes are read from the first comma-number pair inside
  the string ("..., 3B active" reads as size 3); notes issued in a loop (`self.next_slide(NOTES[n])`) are counted
  once, so "12 steps but 10 notes" is not a missing note. The rest of its flags were real.
