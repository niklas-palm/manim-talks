# Alignment pass on talks/llm-serving (2026-09-14)

What moved: every fixed piece of furniture now sits on the grid (`COLS` -6.4/-3.2/0/3.2/6.4, `ROWS` 1.3/0/-1.3):
the GPU drawings at x -3.2 (ceiling, quantisation, fleet, batching measured), right-hand counter columns at x 0 and
3.2 with one counter per row, the fraction centred on y 0, the dense and mixture-of-experts stacks at x ±3.2, the
industry boxes at ±3.2 with their fronts under their left edges, the prefix-cache turns and blocks sharing one left
edge with the label at the margin, timelines starting at x -6.4, the Mechanics counters pulled in so "tokens produced"
no longer clips at the right edge.

Lessons:
- Two counters in one row need short names or two grid columns apart: "bytes read per token: the active part" at x 0
  ran into "memory bandwidth" at x 3.2. Names of counters that share a row stay under about 25 characters.
- Counter names change nothing the picture cannot say; the "all of it / the active part" qualifier belongs in the
  model line above, where it already was.
- Steps that leave a third of the frame empty by design (not redesigned here): the first two steps of Fleet (one
  engine and three counters), MixtureOfExperts (two stacks, bottom third), NoiseFloor and PrecisionCost (a 20 by 5
  grid in the upper half), Opening and Close (text only). A redesign would move the main object down and enlarge it;
  left for a picture pass, since this pass changed positions only.
- The Mechanics scene keeps its own coordinate system (the zoom choreography depends on it); only its counters moved.
