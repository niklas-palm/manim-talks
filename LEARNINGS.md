# Learnings

The living log. Add an entry whenever something cost time or changed a rule, written as a first principle: what is
generally true, why, and what to do instead, in words that outlive the deck it came from. No dates, no company names,
no "in the agents deck"; if a lesson needs an example, the example is one clause of it. The older sections, written
before that rule, still name the sample decks they came from; those decks are in this repository, so the reference stands. The technical Manim entries are consolidated
in `docs/manim.md`, the style rules in `docs/principles.md`; this file is where they arrive first.

## From the reference deck (talks/llm-serving)
- Prefill and decode are the same picture with a different number of columns, so draw them that way: the first
  zoom takes the whole block through the layer (one row lit, five columns multiplied), the second takes one column
  through the same stages. The contrast does the teaching; no caption has to say "compute-bound".
- When the second look at a mechanism must say "this is the same computation", show every stage again, not the one
  that carries the point. The decode zoom that swept only the feed-forward read as "decode skips attention".
- Name what a number is spent on. "Bytes per step" hid two reads with different behaviour: weights, fixed per step,
  and cache, growing with every token and every request. Label both where they are read.
- Name the two words before using them. Latency and throughput defined on screen with one request, where they are
  the same number, is what turns batching from a feature into a knob between the two.
- Every number on screen carries its unit and its clock: "tokens/s" alone was read three ways.
- A conveyor with time along x is the honest picture of a scheduler: step width is step time, so load shows as
  wider columns without a word. Slide old columns under a background-coloured mask instead of animating opacity.
- One click per measured point. A curve drawn in one go is a picture; a curve drawn point by point is an argument.
- A caption that changes under an animation is not read. Captions became a quiet footnote, and the scenes rebuilt
  last have none: the words sit next to the thing they name and stay.
- Titles in plain words. "Do not read what you already read" and "the ceiling you can read off a spec sheet" were
  replaced by "reusing the KV cache across turns and engines" and "GPU latency and throughput". Catchy costs
  comprehension.
- Show the speaker the end state of the next step, not its first frame. It answers the question the speaker has.
- Draw the machine, not a box for the machine: a memory bar and two gauges did more teaching than any label.
- When a picture repeats (layer two after layer one), replay it at speed inside the same step, without a click.
- Screenshot the end of every step and review the sheet. Every collision was found there and none in the code.
- Clear a zoomed view before zooming out. The block that lingered over the collapsed box looked like a bug because
  it was one.
- A mobject in two groups animated in one play (a fade-in group and a shifting row) ends where the fade started.
  Keep the groups disjoint. The cell created inside a zoom must be added to the row group that shifts back.
- Never run two renders of the same talk at once; the shared text cache kills the longer one.
- Ask what the audience will read a number as. "330,000 tokens of context" read as tiny until the label said "about
  40 conversations of 8k tokens, or one request at the model's full context".

## Tooling
- Never script the user's PowerPoint to verify an export. An AppleScript that opened a test file and then closed
  "the active presentation" without saving closed the user's own open deck instead. Verify a .pptx by re-reading it
  with python-pptx and inspecting the slide XML; leave opening it to the user, and say so in the report.
- The PowerPoint export is one autoplaying clip per step with the note in the slide notes; 76 steps of 1080p60 came
  to 44 MB. It is a convenience for rooms that demand PowerPoint; the web presenter stays the reference.
- The themes name fonts that come with one operating system. On a machine without them Pango substitutes a family of
  its own choosing, and `bin/themes.py check` says so. Aliasing the family in fontconfig (a `fonts.conf` that prefers a
  metric-compatible family, such as Liberation Sans for Helvetica and DejaVu Sans Mono for Menlo) makes the substitution
  a choice rather than an accident; the check keeps reporting the family as missing, because it asks Pango which families
  are installed, not fontconfig which one it would use. Look at the shots before trusting either answer.
- The two pages `bin/build.py` writes embed the player data: every scene's clip path and every step. Anything that hosts
  a rendered talk elsewhere can read that list and copy exactly those files, instead of guessing which quality folder
  under `media/` the pages play.

## From the example decks (talks/dns, kubernetes, kafka, transformers, agents)
Five decks built in parallel by agents from the same instructions. What they found in common, then per deck.

Common to all five:
- The scale trap. Every first pass drew the mechanism correctly at 12 pt labels and cells of 0.06 to 0.12 units and read
  as a paper figure at half size. The second pass scaled up (cells 0.16 to 0.42, labels 15 to 18, blocks 0.35 tall with
  14 pt text) and moved sentences to notes, changing nothing about the mechanism and everything about legibility.
  Design for the half-size review sheet from the start; the rule is now principles.md rule 11 and check.py flags the text.
- On-screen sentences crept in as labels ("min.insync.replicas = 2: the write is refused, not stored on one disk").
  A label is a clause of a few words next to the thing; the sentence is in the note. check.py flags labels over 14 words.
- Primary documentation is often assembled in the browser; fetching the site gives a shell. The sources are the
  repository's markdown (`gh api repos/<org>/<repo>/contents/<path>`), generated reference pages, ar5iv for arXiv papers,
  the RFCs and IANA for DNS. Some learning sites return 403 to a fetcher; the primary source is better anyway.
- State drawn as a list that only grows (a log with offsets, a stack of message blocks) was found independently by
  three decks; it is now `Log`, `Pointer`, `Stack` and `block` in the library.
- End every step on a settled picture; the presenter holds on the last frame.

DNS:
- `Text[a:b]` indexes glyphs without spaces; colouring by string index lands one character left per preceding space.
  Use `thread=True` with `set_thread`, or the library's `"[a:b]"` t2c keys.
- Two texts on one row need one anchor relative to the other's edge, not two fractions of the row.
- Name anything created inline that must later leave the screen; an anonymous `FadeIn(fuse(row))` cannot be faded out.
- A helper that rebuilds the previous scene's final frame in one call is what makes a deck one continuous illustration
  across scene files (the stage pattern, now in the template).
- Live numbers (`dig +trace`: a TTL read at 300 s in one cache and 281 s in another) teach better than textbook ones.
- Six large rows and a counter running to 340,000,000 said "the size of the internet" better than thirty small rows.

Kubernetes:
- A stage object holding the whole fixed picture at fixed coordinates was the single most useful thing in the deck.
- Card text at 12 pt is about 0.072 units per character; a 1.5-unit card holds about 18 characters.
- Space the objects to the labels, not the labels to the objects, when labels sit under thin gates.
- A control loop is three verbs and a gap (wants 3, has 0, gap 3) inside an opened box, under a zoom.
- "Nothing new happens" only teaches after the mechanism has been shown once in full.
- Time the audience cannot feel (40 s, 300 s) is a counter counting through the thresholds with labels at each.
- Rule 11 was met by removing words and adding zooms rather than by enlarging everything.

Kafka:
- One row of cells with offsets served as the vocabulary for a partition, a segment, the offsets topic and the
  metadata log; reusing it for the system's own state made the closing point visible without a word.
- A reader is a triangle under the log; replay, rebalance and offset reset are all pointer movements.
- Budget 0.45 units under the offsets for a pointer and its tag, 1.4 units between stacked logs.
- `group.animate.set_opacity` fills a stroke-only member; dim cells and labels separately (docs/manim.md).
- Ghost copies (`copy().set_opacity(0.25)`) are the cheapest picture of a machine that exists but is idle.
- A gauge in the margin needs a short two-line name ("write\nload"); a long name clips at the frame edge.

Transformers:
- Show the sum, not the label: value copies flying into the new vector scaled by their weights, filling it cumulatively.
- A stack of identical layers is the same picture repeated smaller, not text in boxes.
- A residual is the update's cells landing one by one on the vector.
- Illustrative scores are fine when the operation is exact and the note says the numbers are chosen.
- The sweep highlight must not be a semantic accent; the neutral `HI` is now the library default.
- Arcs bow toward the side the sign of `angle` says; a loop-back arrow with a positive angle crosses the title.

Agents:
- "Every call sends the whole list" as one animation (a copy of the list shrinking into the model) is what makes the
  model's statelessness land.
- A code scene works when the highlight runs against the picture; keep the picture as a colour-only reminder.
- Menlo at 18 pt is about 0.13 units per character; shorten identifiers before shrinking the font.
- A member change and a group move in one play lose the member (docs/manim.md).
- Two-line labels beat wrapping beside a box.
- Switching a deck from its own helpers to the library versions is cheap to verify: compare the end frames of every
  step before and after (mean pixel difference), not the code. Kafka's migration measured under 2/255 everywhere.
- Uneven letter spacing and vanished spaces in small labels, seen in every deck, came from Pango rounding glyph
  positions to pixels at the requested size. Laying out at 48 and scaling down fixed it everywhere at once; the lesson
  is that text must always go through the library, never `Text()` directly, so a fix like this lands in one place.

## From the quality passes and the agents rebuild
First principles that the passes confirmed, written to outlast the decks they came from:
- The audience re-orients every time the picture changes. One fixed stage per deck, built by one function in
  `objects.py` and added by every scene, is what makes six scene files one illustration; the alternative, a fresh
  layout per scene, cost every deck a second pass.
- Reserve the space the picture will grow into. An empty list inside its box, an empty rack, an empty column: the
  audience reads the emptiness as "something goes here", and later steps have somewhere to go without moving what is
  already placed.
- Open on a still and let the speaker name what is there. Every deck had at least one scene that started moving before
  the audience knew what it was looking at. Splitting the first click costs one note and buys the whole scene.
- Alignment is not decoration. Frames that sat a little off a grid, with labels floating and unequal gaps, read as
  sloppy before anything moved; the same frames on the grid read as professional with no other change. The grid
  overlay (`GUIDES=1`) made the difference visible in one render.
- Text must go through one place. Uneven letter spacing in every deck had one cause (Pango's pixel rounding at small
  sizes) and one fix (lay out at 48 and scale), which landed everywhere at once only because every label came from
  `label()`. Any text built directly would have kept the defect.
- Code on screen is code: highlighted, indented, large, on its own panel, and walked line by line against the picture.
  Plain monospaced text read as a paragraph and was skipped.
- When a thing changes role, morph it; do not replace it. The camera API box becoming the tag on the first tool card is
  the whole point of "from an API to a tool"; a new card appearing beside an old box would have said nothing.
- Standing relations are dashed and horizontal; flows are arrows. A diagonal dashed link across the flow arrows made
  one frame unreadable.
- The group-and-member trap bites experienced hands too: it recurred in the rebuilt deck despite being documented. It is
  now a checker rule, which is where a lesson that keeps recurring belongs.
- Review by looking, at half size, before the 1080p render, and again after. Every pass found something the previous one
  had called done.

## From the pacing pass
- A still first step is cheap when a scene builds its furniture in one play: insert the click after that play and write
  a note that names what is on screen. Where the opening was an animation of the object itself, a FadeIn of the
  finished object is the still and the reveal becomes the first mechanism.
- The still step needs its own anchor for the eye: a claim line or a label, otherwise the frame reads as unfinished.
- When a first click is split, ask whether the moved animation belongs to the next step's idea; merging it there keeps
  one idea per click without adding a step.
- First occurrences at 0.3 to 0.6 s per beat, repeats at 0.07 to 0.3 s, is the shape that held in every deck.
- A long value in a fixed-column row is shortened, not shrunk: "cdn.example.net." fit where a longer alias did not.
- A row that sat at y -0.35 left the bottom third empty; at y -1.0 the same picture used the band. Where a picture
  does not grow into the lower band, move it down rather than leave the band empty.
- A picture that runs past the frame edge on purpose (a list too long to show) should fade towards the edge; cut off
  rows read as overflow, faded rows read as "it continues".
- Known imperfections left on purpose in the reference deck: the Industry scene is a labelled list of fronts around the
  two-phase picture, and the Fleet scene's first two steps use the upper half. Both would be better as pictures that
  grow; recorded here rather than redesigned in this pass.

## No cuts between scenes
- The seams were the last place the decks still cut: every scene opened on a black frame with its title being written,
  because a scene is its own video. The rule that fixed it is mechanical: a scene's first frame is the previous scene's
  last frame, rebuilt statically (`self.add`, `title_still`), and its first play is `retitle()` with the first change.
  `bin/seams.py` puts the two frames side by side and scores the difference, so the rule can be checked, not argued.
- Title slides went with it. A talk opens on its first picture and the speaker introduces it over that frame; the
  agenda lives in the kicker above each title and in the notes.
- A picture that hands over to the next move (the stage shrinking into a reminder beside the code, then growing back)
  is the same illustration continuing; the audience keeps its bearings and the red thread is literally visible as the
  same objects changing role.
- The first frame of a scene must be sampled at t = 0 when measuring seams: the retitle starts at once, and 0.05 s in,
  the objects being transformed are already a little faded, which reads as a jump that the audience never sees.
- What each scene leaves behind belongs in `objects.py` as data (message histories, titles), so the next scene rebuilds
  it from the same source and the two frames cannot drift apart.
- A dot that flew from the thermometer to the application box's edge, followed by the result block flying from the
  thermometer into the list, told the audience the result went somewhere else first. One motion per exchange, from the
  producer to the exact slot, is now principle 3a and a checklist line; every deck was checked for it.
- Both sides of a seam must come from one builder (`start_<scene>()` or `<scene>_end()` in `objects.py`); two hand-written
  copies of "the previous frame" drift within a day. The reference deck's twelve seams and the examples' twenty all read
  identical once the builders were shared.
- A hand-over can be the last step of a scene or the first of the next; the identical frame at the seam is what matters.
  Doing it last lets the speaker close a move on the picture that opens the next one; doing it first ties "click" to
  "new move". Pick one per deck and keep it.
- A scene with no producer drawn has nowhere for a new record to come from (the tombstone in Kafka's retention scene).
  Every object that arrives needs a visible source; if the source is not in the picture, draw it or have the object
  come from where it would be.
- `bin/review.sh` at half-second spacing still misses where a dot starts and lands; sample eight frames across the
  step's clip with ffmpeg when checking a travel.

## PowerPoint export, verified
- The export was broken until now: python-pptx writes its own `<p:timing>` when it adds a movie, and the autoplay
  timing was appended as a second one. PowerPoint silently refused to open such a file (no repair prompt, no window,
  no presentation listed). Replacing the existing element fixed it. Lesson: re-reading a file with the library that
  wrote it proves nothing about the consumer; validate against the real consumer.
- Verification without touching anything else in PowerPoint: open the one file, address the presentation by its
  name, read `count of slides`, `media type` and `play on entry of play settings of animation settings` of the movie
  shape, close that presentation by name. `active presentation` is never used.
- `--click` exports clips that start on click, for speakers who want to talk over the still first.

## Containment and routing pass
- Manim's `get_boundary_point(direction)` returns the extreme point in that direction, a corner for any diagonal, so
  every arrow between two boxes not on one axis looked skewed. `edge_point()` in the library now meets the box where
  the centre-to-centre line crosses it, and `arrow`, `dashed` and `travel(edges=True)` use it. Better still: put the two
  objects on one axis and draw the line horizontal or vertical.
- A picture with many relations wants a bus, not a fan: Kubernetes' API server became a full-width bar with the loops
  above and the store and nodes below, so every watch is one vertical dashed line into the bar and no line crosses a
  box. Fleet's balancer fan became a trunk, a rail and vertical drops. Routing along a shared rail is how a dense
  system picture stays legible.
- Things that arrive land inside the box that receives them, with padding, never on its border; a loop arc, a memory
  bar, a card, a pull all needed their container enlarged or themselves shrunk. Reserve the row inside the box where
  they will land.
- A code highlighting style must keep plain identifiers neutral; one-dark paints them red and a whole loop read as
  an error. Monokai is the library default now, for every language Pygments knows.
- An exceptional object drawn differently (a taller block for a long tool result) reads as a mistake; draw it like its
  peers and let its words and where it lands carry the point.
- Zoom frames computed from the content they open (box width from the matrices inside it) stop the contents from
  touching the box; hide the tail of a row a zoom never reaches rather than let the frame cut it.
- Fresh agents with a written brief did this pass as well as forks with the whole session in context, and the forks
  started to fail once the session grew past the model's input limit. Long sessions should hand work to fresh agents
  with `AGENTS.md` and the docs as their context; that is what the docs are for.

## The argument, not only the mechanism

- A deck can draw every mechanism correctly and still lack its argument. Before touching scenes, write the red thread as one
  paragraph in the script: each move must be a sentence of it, and the hinge the speaker says out loud (the moment one
  thing turns into another) must be a click the audience can see, not a sentence in a note.
- The thread is visible only when the same object changes role: the code that becomes the named unit, the box that
  becomes a tag on a card, the mechanism run by hand before it is shown as code, the code that folds into one call. A new
  object appearing next to an old one says nothing about how they relate.
- If a click adds no new object and names no new problem, it is a sentence, not a step. A step that only restated a
  mechanism already shown in passing was cut by the speaker on first viewing; the fact moved into the previous note.
- Name a product before showing its features. A feature that belongs to one framework, shown before that framework is
  on screen, reads as a property of the mechanism itself and misleads. The order that holds: the mechanism by hand, the
  product that hides it, the product opened up, then the product's features on the opened picture.
- Show the abstraction working before opening it: one run at speed with nothing to read, then the same run slowly with
  the code. The fast run is the claim ("this is hidden"); the slow one is the proof. Rewinding the picture to the same
  starting state between the two keeps the walk honest.
- When code is walked against a picture, the first pass wants one line per click with a note per line; only the
  repetitions run inside one click. A single click that walks all the lines at reading speed is watched, not followed.
- Blank lines between the blocks of a code panel cost nothing and make the walk legible. Keep a small map from the beat's
  name to its line number so the scene stays readable when the source changes; highlight only non-blank lines.
- A label placed on a connector must fit between the boxes at its ends, not only clear of other labels; a short arrow
  wants a two-line label. A label that sits on a frame's edge needs a background so it breaks the line rather than
  lying across it.
- Whatever one scene leaves for the next, a string or a drawing, belongs in the shared objects file even when it is one
  line: the second hand-written copy is where a seam starts to drift.
- A session that grows past the model's input limit should hand the work to a fresh agent with the entry document, the
  docs, the scene files and the shot sheets. The repository is the memory; if a fresh agent cannot continue from it,
  the missing knowledge belongs in the docs.

## The look belongs in one file, not in the drawings

- A house style that lives in the drawing code is a house style you cannot change. Colour, type, corner radius, stroke
  width and fill opacity are one layer; the drawings are another. Put the first in a data file the library reads once,
  have every helper derive its values from it, and a deck written for one room can be presented in another, or in
  someone else's palette, without a scene changing.
- A style is not only its palette. Square corners with heavy strokes and no fills read as one thing; soft corners, thin
  strokes and low contrast read as another; capitals in the titles change the register again. Give the style layer those
  numbers too, and derive the smaller variants from them proportionally so everything squares off or thickens together.
- Name meanings, never hues. A drawing that says "the cool accent" survives a change of palette; one that says "blue"
  becomes a lie the first time the palette changes. Keep the slots' character fixed (one cool, one warm, one deep, one
  for wrong) so a reader of the code can still picture what a scene looks like.
- A style layer needs a validator, or it will quietly ruin a deck: body text far enough from the ground to read at the
  back, every accent far enough from the ground to be seen, and no two accents close enough to be read as one colour.
  Perceptual distance, not hex distance. Refuse the style rather than let two meanings look alike.
- Importing a style from a document format is mostly repair work: the palettes real organisations use are three blues
  and two greys on a ground they were never meant to be seen against. Lift each colour away from the ground until it
  passes, then push the set apart until no two collide, and keep whichever colour means "wrong" fixed while you do it.
  Import colour and type only; a logo or a picture background belongs to a slide, not to a picture that unfolds.
- Anything imported from someone else's brand is theirs. Write it where the repository ignores it, say so in the tool's
  own output, and never commit it.
- Prove a style layer is a no-op before trusting it: render the same frames before and after and compare them as
  images. Any difference must be one you can name.
- The second style is what finds the bugs the first one hid. Assumptions about a dark ground (a near-white fill used as
  a highlight, an opacity that only looks faint because the ground is dark) are invisible until the ground flips, so
  build a light style early and render a whole deck in it, not one frame.
- Probing the system for installed fonts during a render can perturb the text engine enough to move every glyph by a
  fraction of a pixel. Check the environment in the checker, not in the thing that draws.
- The pages and exports around a deck are part of the look: a light picture inside a dark frame reads as a mistake.
  Derive their chrome from the same file by mixing the ground with the ink, so they follow any style without a table of
  their own.

## Samples and real work want different homes

- A repository of worked examples and the real decks built from them are not the same thing. Examples are written to be
  read and must stay readable; a real deck carries a client's palette, a customer's numbers, an audience's in-jokes, and
  should never be committed beside them. Two roots and one lookup that searches both cost about thirty lines and stop the
  two from mixing.
- Make every tool take a name and resolve it, rather than teaching each tool a path. When the second root arrived, the
  scripts that already resolved through one helper needed one line each; the ones that had built paths inline needed
  reading first.
- Starting a real deck as a copy of a sample is right, not lazy: the copy diverges the moment it meets an audience, and
  the sample must not follow it. Say so in the copy's own README so the next reader knows which is which.

## Breadth of style is not depth of teaching

- A shelf of styles is a way of not deciding. A set of them looked like variety and read as one deck in different
  colours, because what makes an illustration teach is the picture: what is drawn, what moves, what the audience can
  follow. Two styles, one for a room with the lights down and one for a lit room, carry everything a talk needs.
- Keep those two genuinely different where the difference is physical, not decorative: a pale ground shows weight
  differently, so the bright one wants thinner lines, smaller corners and fainter fills rather than the dark palette
  inverted.
- When a knob exists only for variants that have been dropped, drop it with them. Anything left behind is read by the
  next person as a feature to maintain.
- Prove a style on every deck, not on one frame. Render the whole set in both and look at the sheets; the frames that
  break under a new ground are never the ones a single preview happens to show.

## What a review loop finds that a pass does not

- One question, one implementation. When three tools each re-derived which style a deck presents in, two of them got a
  different answer and wrote artefacts in the wrong style into files that are committed. A question the whole system
  asks belongs in one function that takes what it needs as an argument, and every caller passes it.
- A tool that deletes its previous output must first prove it can produce new output. Two of them cleared a folder,
  found nothing to put in it, and exited zero: the failure looked exactly like success, and the loss was silent.
- A check that validates a substituted value validates nothing. A font check that first replaced a missing family with
  an installed one, and then tested the installed one, could never fail; the render meanwhile used the missing name.
  Check what will actually be used.
- A threshold taken from intuition rather than from the standard is wrong in the middle of the range, which is where
  nobody looks. Light and dark do not divide at half the luminance; the crossover is much darker, and a mid grey ground
  wants dark ink.
- Any string that becomes a file name is validated before it is joined to a path. An imported style named with a parent
  directory would have overwritten a shipped one.
- A tool that writes something unusable must exit non-zero, or nothing can be built on top of it.
- Parallel reviewers with one narrow role each find what a single careful pass does not. The reviewer looking only for
  dead code found the split implementation; the one comparing new code against its siblings found the hand-written
  colours a mechanical migration had skipped. Give each one a role and forbid it from fixing anything.
- Every automated rewrite needs to know where the code is. A prose re-wrap that did not track fenced blocks broke the
  commands inside them into unrunnable halves, and the diff looked innocent.
- The fix for a class of defect is a check, not a patch. Literal colours came back into scene files after a migration
  removed them, so the checker now refuses a scene that names a colour at all; that is what stops the third recurrence.

## What the second round found that the first did not

- A fix creates its own defects, so review the fixes. The round that reviewed the previous round's work found a helper
  that wrote a file before validating it, a shared reader that trusted half of a render, and a colour helper whose
  colours were not as distinguishable as its docstring claimed. None of that existed before the repair.
- "Something was produced" is not "the thing was produced". A reader that accepted an index as proof of a render let a
  page be written pointing at a video that was never finished; a tool must check the artefact it is about to reference,
  not a sibling of it.
- Validate before you replace. An import that overwrites its destination and then reports that the result is unusable
  has destroyed the file a human edited by hand. Write to a temporary name, validate that, and move it into place.
- Evenly spaced by construction is not evenly spaced to an eye. Colours picked at equal steps around a hue circle
  collide in pairs, and one of them will land on the colour that already means "wrong". Pick each one as the candidate
  whose nearest neighbour is furthest away, and count the vocabulary among its neighbours.
- Ink on a coloured mark cannot be one fixed colour. Whichever of the ground and the body colour the eye can read
  against that mark is the right one, and which that is changes with the style.
- A guard that runs inside the loop is not a guard. Probe every input first, then destroy the old output, then write:
  three tools cleared their previous work and failed on the second item.
- A default that differs between the tool that produces and the tool that consumes is a trap. When one defaults to a
  middle quality and the next to the highest, the ordinary sequence of the two fails. Infer it when there is exactly
  one candidate, and ask when there is not.
- Anything a command line interpolates must be quoted and validated, including the ones that look harmless. An
  unquoted port let a second word redirect what a local server exposed.
- A tool run by its shebang is not run by the project interpreter. If a check can only answer under one of them, it
  must say which it is and that it could not answer, never pass by default.
- Write down the threshold once. The same perceptual distance was a literal in the validator and a default argument in
  the repair routine; either could drift from the other and the drift would be invisible.

## What the third round found, and where a loop should stop

- An escape that covers one way out of a construct covers one way out. Text placed inside a script element needs both
  the closing sequence and the comment-opening sequence escaped: the second puts the parser in a state where the
  closing tag is read as text, the page loads looking correct, and nothing works after the first click. The browser
  logs nothing. Verify a generated page by driving it, not by reading it.
- A helper that picks the better of two options should also check that the better one is good enough. Ink chosen as
  "the ground or the body colour, whichever reads" still fell under the bar for small text on a mid-toned mark; the
  choice now has a floor, and both styles clear it everywhere.
- A partial render is a different failure from no render. Pairing a scene with the one after the gap and calling the
  difference a jump sends a reviewer after a defect that does not exist; a tool that reads a render should say what is
  missing before it says what is wrong.
- Shell arithmetic reads a leading zero as octal, so a range check on a port can pass a value the program then refuses.
  Anchor numeric patterns to exclude it, and remember that a process match on a number matches longer numbers too.
- `export X=$(cmd)` returns success even when the command fails. Assign, then export, or the failure is invisible.
- SystemExit is not an Exception; catching Exception around a call that exits leaves the exit unhandled, which is how a
  survey command stopped surveying at its first bad input.
- Stop when the findings change character. Three rounds took the same target from "silently writes the wrong artefact"
  to "raises an ugly traceback on a file corrupted on purpose". That second kind is worth a sentence in the code and
  not another round: convergence is the goal, not the absence of imperfection.

## Reviewing and editing at the same time

- Never let a review run while the work it reviews is being edited. A reviewer told to leave the tree as it found it
  restored the tree, and an hour of uncommitted repairs went with it: five tools were left importing a helper whose
  definition had just been deleted. Commit before the next round starts, or give the reviewers a copy.
- The recovery is the same either way: the last commit is a known good state, so go back to it first and reapply from
  there. A tree that half-works is worse than a tree that is one commit behind.
- An edit script that asserts on every anchor before writing anything is what makes reapplying safe. Each of these
  passes either applied whole or changed nothing, which is why nothing was left half-converted.
- When several edits are independent, apply them independently and report each one skipped. A single abort in the middle
  of a batch silently drops the rest, and the ones that did land look like the whole batch.

## Following one request through a system

- An architecture deck that shows the parts and their connections tells an audience what exists; one that follows a
  single request through the parts tells them how it works. When the audience is the team that will build on the system,
  the second is the one to make: keep the actors fixed on screen, and let one request move.
- Give every step the same beats, and the audience learns the choreography once. Run, look inside, look at what was
  written and what came back: by the third step nobody watches the mechanics of the deck any more, only the content.
- A zoom is a shape that grows out of the thing being examined and shrinks back into it. A panel that appears beside the
  thing reads as a new slide; the same panel opened out of the step's own outline reads as looking closer.
- Draw the finished design when the audience will build it, and keep the gaps for the notes or another talk. A picture
  that mixes what exists with what is missing teaches neither.
- Monospaced text is wide: a code line of sixty characters at a readable size is wider than most panels, and a group
  fitted to a panel shrinks every label in it to match the code. Keep code lines under about fifty characters, or set
  the code in plain proportional type when it is quoted rather than run.
- A transform between two groups of different shapes redraws the whole target: the audience sees a box melt and
  re-form when only a label should have appeared. Change the parts in place, and keep transforms for the moments
  when the morph is the point. It is invisible on a shot sheet, which shows only end frames, so it belongs on the
  checklist as a thing to watch for in motion.
- The orchestration belongs on screen, not only in the notes. A running line in the orchestrator's own box saying what it
  is doing between two calls is what makes an agent visible as an actor rather than a label.

## What a deck claims, and how it was checked

- A described picture is a specification. When the person asking says where the actors sit and what each click does,
  build that picture; an analysis that suggests a better one has to be argued, not substituted. The first version of a
  deck built from the analysis rather than the description was thrown away whole.
- A summary is a claim about a source. When a note quotes a number, read the file that produces it: two figures taken
  from a well-written overview were wrong, one a list of field names and one a latency that held for three uploads out of
  thirty-six. The audience that knows the system will notice exactly those.
- The spoken length is the word count of the notes, not a guess per move. Count them at about 130 words a minute before
  writing a duration anywhere; the first estimate was two thirds of the truth.
- Hierarchy needs guides, not spaces. A tree drawn by indenting names read as a list; the same names with a thin
  vertical line per enclosing level read as a file browser at a glance.
- Text that must fit a box goes through one helper that scales it into the box, and every box uses the helper. Checking
  twenty-six frames by eye found the spills once; the helper finds them every time, including in the frames nobody
  looked at.
- A title wider than the frame is scaled down silently by the text helper, so a long title looks slightly smaller than its
  neighbours rather than wrong. Shorten it instead: the scaling is a safety net, not a layout.
- State that a later step must act on is carried as a tag on the object, not inferred back from a property. Recolouring
  "whatever is currently the fresh colour" missed lines whose colour had been read differently; tagging the lines when they
  were added and clearing the tag when settled cannot miss.
- Stop a background render before editing the files it reads. A scene file changed while an earlier scene renders is
  what the render reaches next, and the frames then disagree with the code that claims to have produced them.

## Where a protocol detail belongs

- Draw a protocol's shape where it is true and explain it where it matters, not before. A plain application that sends a
  picture with a question sends one message with two content blocks; drawing it as two user messages was accurate about
  nothing and taught the audience the wrong shape early. Later, when a tool result arrives in the user's role, that is the
  one place the protocol surprises, so it gets a click of its own with the label on the role; the same fact appended to a
  click about running the tool was read by nobody.
- A preview of the next move's mechanism is a cut in disguise. A move that ends by ghosting the tool cards into the model,
  to say "and then the model chooses", showed a motion whose meaning the next move was about to draw properly; ending on
  the named problem instead, with the answer in the note, lets the next move's first call carry the whole idea.
- A list of blocks must lay each one under the real height of those above it, or a block cannot grow a line; the library's
  Stack does now, and equal heights give the same positions as before.

## A zoom is read only if the speaker owns its end

- A camera zoom exists so that something inside a box can be read. If the same click also pulls the camera back, the
  opened view was on screen for about a second, under an animation, and nobody read it; two decks had this and the
  speaker noticed before the review did. The opened view is a click of its own, the pull-back is the next one, and
  the checker now flags a step that scales the camera twice. The general form: whenever an animation reveals something
  to be read, the step ends there, and the speaker decides when it goes away.

## When who runs the loop changes, the picture must gain a layer

- A talk that moves from "the application's own code decides" to "a framework runs the loop inside the application" has
  changed what the box is, and the box must show it. The same application box holding the same list in both halves made
  the audience see nothing change. The general form: whenever the owner of a mechanism changes, draw the new owner as a
  container, not as a label.
- The way to introduce the new owner is the drawing the audience already trusts, made small. The compact picture (the
  list as bare coloured rows, the tools as bare cards, in a frame with the owner's name) had already carried the code
  walk; placing that same small picture inside the application and running the familiar two questions through it at
  speed said "the application now runs an agent" in one click, with nothing new to learn. Then the next move opens it up
  to full size where the words are needed again. Small is for showing where something lives and how it moves; full size
  is for reading it.

## Before publishing

- A generated page committed next to media that is not makes a fresh clone look broken: the page opens and every clip
  is dead. Guard on the artifact the page plays, not on the page, and never commit a generated file whose source is
  ignored unless it is useful on its own.
- A script invoked bare in the documentation runs under whatever interpreter the reader's machine has first. If the
  project has its own interpreter, every documented command names it; a command that worked by luck on the author's
  machine is the one that fails first elsewhere.
- A checker that claims to cover a list must be tested against that list. A pattern matching fifteen base names was
  described as covering the eighty-nine constants a library removes, and passed seventy-four of them. Derive the set
  from the source of truth, or widen the pattern and count.
- Review the history, not only the tree, before a repository goes public: a file deleted long ago is still one command
  away. Search every revision for the names that must not appear, and for the kinds of file that never should have been
  committed.
