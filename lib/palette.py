"""The shared look and vocabulary for every talk: a dark, few-colour style in the spirit of 3Blue1Brown, built with
Manim Community Edition. Import it in every scene file with `from lib.palette import *`.

What lives here
  colours       a small palette; a talk assigns each colour one meaning and keeps it for the whole deck
  TalkSlide     a Scene whose steps are clicks; each step carries a speaker note (next_slide / finish)
  text          label, title, title_still, retitle, small, caption, swap_caption, pin, thread colouring of a talk's nouns
  objects       tokens, box, node, arrow, dashed, column, grid, dot_grid, Counter, Gauge, Bars, travel
  vectors       vector, shades, restore, dot_product, sweep: the picture of a matrix multiplication
  lists         Log and Pointer (a row of cells with offsets and a reader), Stack and block (a list that grows)
  code          code (syntax-highlighted block) and highlight_line (a bar that walks the lines)
  layout        the frame constants and the bands titles, pictures and captions live in

Rules the helpers encode (see docs/principles.md for the why):
  * all text is laid out at BASE_SIZE (48) and scaled to its size, because Pango rounds glyph positions to pixels at
    small sizes (spaces vanish, letters crowd); text below size 12 is still too small to read from the back row
  * grey text uses MUTED, never DIM: DIM is for shapes out of focus and is unreadable as text on a projector
  * captions are a quiet footnote pinned to the frame bottom; one per step, set before the animation, never swapped
    while something moves
"""
import json
import os
import textwrap

from manim import *

# ------------------------------------------------------------------------------------------------ colours
# Six accents. A talk picks the ones it needs and gives each ONE meaning (see set_thread). Never reuse a colour for
# something else inside a deck: the audience learns the legend once and then reads the pictures without one.
BLUE = "#58C4DD"
YELLOW = "#FFD166"
VIOLET = "#9A86C8"
TEAL = "#2EC4B6"
RED = "#FF5D5D"
GREEN = "#8BD17C"
ORANGE = "#F4845F"

DIM = "#4A4F5C"                    # shapes that are not in focus (outlines, empty slots, faded members)
MUTED = "#8B93A5"                  # small text: names, units, axis labels
TEXT = "#E8E8E8"                   # body text, titles
CAPTION = "#B9BFCC"                # the footnote at the bottom of a step
BG = "#0f1116"                     # the background; also set in manim.cfg; needed for masks that hide things
HI = "#F4F6FA"                     # the momentary highlight of a cell being read or a line being run: neutral, never a meaning
FONT = "Helvetica"                 # Helvetica Neue through Pango had uneven word spacing at small sizes
CODE_FONT = "Menlo"                # code: renders cleanly through Pango; about 0.13 units per character at size 18
BASE_SIZE = 48                     # every text is laid out at this size and scaled down: Pango rounds glyph positions to whole
                                   # pixels at small sizes, so 14 to 20 pt text drawn directly loses its spaces and crowds letters

# ------------------------------------------------------------------------------------------------ layout
# The frame is 14.22 by 8 scene units, centred on the origin. Fixed furniture goes in fixed bands so scenes look alike.
FRAME_W, FRAME_H = 14.22, 8.0
TITLE_Y = 3.3                      # title baseline band (title() puts the title at the top edge with buff 0.5)
CONTENT_TOP, CONTENT_BOTTOM = 2.6, -2.3
CAPTION_Y = -3.3
MARGIN = 6.4                       # nothing closer to the frame edge than this (x); the columns below are the alignment grid
COLS = [-6.4, -3.2, 0.0, 3.2, 6.4]  # five column lines; align edges and centres of fixed furniture to these
ROWS = [2.6, 1.3, 0.0, -1.3, -2.3]  # row lines inside the content band
GAP_TIGHT, GAP, GAP_WIDE = 0.12, 0.25, 0.5   # the three gaps a scene uses: label to object, object to object, group to group


def guides() -> VGroup:
    """The alignment grid as faint lines, for review renders only: GUIDES=1 bin/render.sh <talk> ql <Scene>.
    Titles, content band, caption band, the five columns. Nothing in a deck should sit a little off these lines."""
    g = VGroup(*[Line([x, -4, 0], [x, 4, 0], color=MUTED, stroke_width=1, stroke_opacity=0.5) for x in COLS],
               *[Line([-7.1, y, 0], [7.1, y, 0], color=MUTED, stroke_width=1, stroke_opacity=0.5) for y in ROWS + [CAPTION_Y, 3.3]])
    return g.set_z_index(-5)

# ------------------------------------------------------------------------------------------------ the scene

class TalkSlide(MovingCameraScene):
    """A scene is a sequence of steps; a step is what one click plays. next_slide(note) ends the current step and
    records the speaker note for it; finish(note) does the same for the last step. Manim writes one clip per step
    (--save_sections) and a JSON index of durations; bin/build.py strings clips and notes into the audience and
    presenter pages. Notes are one paragraph of plain prose, written for the speaker to read aloud."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self._notes = []

    def setup(self):
        if os.environ.get("GUIDES"):
            self.add(guides())

    def next_slide(self, note: str = ""):
        self._notes.append(" ".join(note.split()))
        self.next_section()

    def finish(self, note: str = ""):
        self._notes.append(" ".join(note.split()))
        self.wait(0.4)

    def tear_down(self):
        super().tear_down()
        folder = os.path.join(str(config.media_dir), "notes")
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, f"{type(self).__name__}.json"), "w") as f:
            json.dump(self._notes, f, indent=1)


# ------------------------------------------------------------------------------------------------ text

THREAD: dict = {}   # the talk's nouns -> colour; filled by set_thread() in the talk's objects module


def set_thread(mapping: dict):
    """Register the talk's recurring nouns and their colours. Titles and captions then colour those words wherever
    they appear (whole words, case-insensitive), so the legend is taught by the text itself. Keys are lower case."""
    THREAD.clear()
    THREAD.update({k.lower(): v for k, v in mapping.items()})


def thread_colours(s: str) -> dict:
    """t2c entries as index ranges into the string. Plain t2c keys are substrings (so 'cache' would half-colour
    'cached') and overlapping keys are refused; index ranges from whole-word matches avoid both. Manim's glyph list
    keeps a placeholder for every space and newline, so string indices map onto it directly."""
    import re
    if not THREAD:
        return {}
    pat = r"\b(" + "|".join(re.escape(k) for k in sorted(THREAD, key=len, reverse=True)) + r")\b"
    return {f"[{m.start()}:{m.end()}]": THREAD[m.group(1).lower()] for m in re.finditer(pat, s, re.IGNORECASE)}


def label(s: str, size: float = 30, color: str = TEXT, width: float = 0.0, thread: bool = False, **kw) -> Text:
    """Text in the talk font. `width` wraps onto lines that fit (scene units; the frame is about 14 wide).
    `thread` colours the talk's nouns. Text asked for in DIM is drawn in MUTED, which reads on a projector."""
    if color == DIM:
        color = MUTED
    if width:
        chars = int(width * 175 / size)
        s = "\n".join(textwrap.fill(par, chars) for par in s.split("\n"))
    if thread:
        kw["t2c"] = thread_colours(s)
    t = Text(s, font=FONT, font_size=BASE_SIZE, color=color, line_spacing=1.1, disable_ligatures=True, **kw).scale(size / BASE_SIZE)
    if t.width > config.frame_width - 0.6:
        t.scale_to_fit_width(config.frame_width - 0.6)
    return t


def small(s: str, color: str = TEXT) -> Text:
    """Text for a zoomed-in view: rendered at 20 and scaled to 0.3, so Pango lays it out properly. Use inside a
    camera zoom of about 0.4, where it reads like 15 pt."""
    return label(s, 20, color).scale(0.3)


def title(scene, s: str, move: str = "") -> VGroup:
    """The scene title at the top, with the move it belongs to in small type above it ("3  three knobs"), so the
    audience always knows where on the map they are. Returns VGroup(title[, kicker])."""
    t = label(s, 38, thread=True).to_edge(UP, buff=0.5)
    g = VGroup(t)
    if move:
        g.add(label(move, 15, MUTED).next_to(t, UP, buff=0.1))
    scene.play(Write(t), FadeIn(g[1:]), run_time=0.7)
    return g


def title_still(scene, s: str, move: str = "") -> VGroup:
    """The same title as title(), added without animation: for a scene's first frame, which must be the previous
    scene's last frame. Build the previous picture with self.add(...) too, then change it with animations."""
    t = label(s, 38, thread=True).to_edge(UP, buff=0.5)
    g = VGroup(t)
    if move:
        g.add(label(move, 15, MUTED).next_to(t, UP, buff=0.1))
    scene.add(g)
    return g


def retitle(scene, old: VGroup, s: str, move: str = "", extra=(), run_time: float = 0.7) -> VGroup:
    """Change the title in place: the old one fades out as the new one fades in, in the same play as the first change
    to the picture (`extra` animations), so a new move announces itself without a cut. Returns the new title group."""
    t = label(s, 38, thread=True).to_edge(UP, buff=0.5)
    g = VGroup(t)
    if move:
        g.add(label(move, 15, MUTED).next_to(t, UP, buff=0.1))
    scene.play(FadeOut(old, run_time=run_time * 0.6), FadeIn(g, run_time=run_time), *extra)
    return g


def pin(scene, m: Mobject, buff: float = 0.4) -> Mobject:
    """Keep a mobject at the bottom of the camera frame, scaled with it, so a caption survives a zoom."""
    f = scene.camera.frame
    base = m.width

    def upd(x):
        k = f.width / config.frame_width
        x.set_width(base * k)
        x.move_to(f.get_bottom() + UP * (buff * k + x.height / 2))
    m.add_updater(upd)
    upd(m)
    return m


def caption(scene, s: str, size: float = 22, color: str = TEXT) -> Text:
    """One quiet line at the bottom: the claim the picture has just made. Set it before the step's animation and
    leave it; the explanation belongs in the note. Prefer a label placed next to the thing it names when there is
    room: the redesigned scenes in talks/llm-serving have no captions at all."""
    t = pin(scene, label(s, size, color=CAPTION if color == TEXT else color, width=12.8, thread=(color == TEXT)), buff=0.3)
    scene.play(FadeIn(t, shift=UP * 0.15), run_time=0.5)
    return t


def swap_caption(scene, old, s: str, size: float = 22, color: str = TEXT) -> Text:
    """Replace the caption at a step boundary. Never call it while something else is animating."""
    t = pin(scene, label(s, size, color=CAPTION if color == TEXT else color, width=12.8, thread=(color == TEXT)), buff=0.3)
    scene.play(FadeOut(old, run_time=0.3), FadeIn(t, shift=UP * 0.15, run_time=0.5))
    return t


# ------------------------------------------------------------------------------------------------ objects

def tokens(n: int, color: str = BLUE, side: float = 0.36, gap: float = 0.08) -> VGroup:
    """A row of n squares: tokens, messages, requests, records. Colour says what they are."""
    return VGroup(*[Square(side_length=side, fill_color=color, fill_opacity=0.9, stroke_width=0) for _ in range(n)]).arrange(RIGHT, buff=gap)


def box(w: float, h: float, name: str = "", color: str = VIOLET, size: float = 22, fill: float = 0.10, name_align: str = "center") -> VGroup:
    """A rounded box with an optional name inside its top edge: a machine, an engine, a service. box[0] is the
    rectangle; add members with .add() so they move with it. name_align="left" keeps the top-right corner free for
    markers that ride along the top edge."""
    r = RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=2.5, fill_color=color, fill_opacity=fill)
    g = VGroup(r)
    if name:
        t = label(name, size, color=color).next_to(r.get_top(), DOWN, buff=0.15)
        if name_align == "left":
            t.align_to(r.get_left() + RIGHT * 0.2, LEFT)
        g.add(t)
    return g


def node(name: str, color: str = BLUE, w: float = 2.2, h: float = 0.8, size: float = 20, sub: str = "") -> VGroup:
    """A named component in a system picture: rectangle with the name centred and an optional small subtitle.
    node[0] rectangle, node[1] name, node[2] subtitle if given."""
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=color, stroke_width=2.2, fill_color=color, fill_opacity=0.12)
    g = VGroup(r, label(name, size, TEXT).move_to(r))
    if sub:
        g[1].shift(UP * 0.13)
        g.add(label(sub, 13, MUTED).next_to(g[1], DOWN, buff=0.06))
    return g


def edge_point(m: Mobject, towards) -> np.ndarray:
    """Where the line from m's centre towards a point leaves m's bounding box. Manim's get_boundary_point returns the
    extreme point in a direction, which for a diagonal is a corner and makes lines between boxes look skewed; this
    meets the edge on the way to the other object, so a line between two boxes is straight and lands where it looks
    like it should."""
    c, t = m.get_center(), np.array(towards, dtype=float)
    d = t - c
    if abs(d[0]) < 1e-9 and abs(d[1]) < 1e-9:
        return c
    hw, hh = m.width / 2, m.height / 2
    k = min(hw / abs(d[0]) if abs(d[0]) > 1e-9 else np.inf, hh / abs(d[1]) if abs(d[1]) > 1e-9 else np.inf)
    return c + d * k


def arrow(a: Mobject, b: Mobject, text: str = "", color: str = MUTED, buff: float = 0.12, size: float = 14, above: bool = True) -> VGroup:
    """An arrow from the edge of a to the edge of b with a small label beside its middle. Build it after both ends are
    in their final positions (an arrow built before a move points at the old place). Ends meet the boxes where the
    centre-to-centre line crosses their edges, so the arrow is straight; align the two objects on one axis when the
    picture allows it and the arrow is horizontal or vertical."""
    u = (b.get_center() - a.get_center()); u = u / max(np.linalg.norm(u), 1e-9)
    start = edge_point(a, b.get_center()) + u * buff
    end = edge_point(b, a.get_center()) - u * buff
    ar = Arrow(start, end, buff=0, color=color, stroke_width=2.2, tip_length=0.18)
    g = VGroup(ar)
    if text:
        side = UP if above else DOWN
        if abs(ar.get_unit_vector()[1]) > 0.7:   # a vertical arrow: label to its right
            side = RIGHT
        g.add(label(text, size, color).next_to(ar.get_center(), side, buff=0.08))
    return g


def travel(scene, path_from: Mobject, path_to: Mobject, color: str = BLUE, radius: float = 0.09, run_time: float = 0.5, flash: str = "",
           carry: Mobject = None, text: str = "", edges: bool = False):
    """A dot travels from one object to another and vanishes; optionally the destination flashes. The unit of
    motion in every system picture: a request, a packet, a message, a token on its way. `carry` sends a shrunken copy
    of that object instead of a dot (a record travelling to its reader keeps its colour); `text` rides above the dot
    (a question, an answer, a call name); `edges=True` starts at the sender's near edge and stops at the receiver's,
    for objects that sit side by side."""
    start, end = path_from.get_center(), path_to.get_center()
    if edges:
        u = (end - start) / max(np.linalg.norm(end - start), 1e-6)
        start = edge_point(path_from, path_to.get_center()) + u * 0.1
        end = edge_point(path_to, path_from.get_center()) - u * 0.1
    d = carry.copy().scale(0.6) if carry is not None else Dot(color=color, radius=radius)
    d.move_to(start)
    if text:
        d = VGroup(d, label(text, 13, color).next_to(d, UP, buff=0.06))
    scene.add(d)
    scene.play(d.animate.move_to(end + (UP * 0.12 if text else 0)), run_time=run_time)
    anims = [FadeOut(d, run_time=0.15)]
    if flash:
        anims.append(Flash(path_to, color=flash, flash_radius=max(path_to.width, path_to.height) / 2 + 0.15, num_lines=8, run_time=0.3))
    scene.play(*anims)


def dashed(a: Mobject, b: Mobject, text: str = "", color: str = MUTED) -> VGroup:
    """A dashed line between two objects' edges with a small label at its middle: a watch, a subscription, a
    heartbeat, any standing relation that is not a flow. Hub-and-spoke systems (a control plane, a broker) are drawn
    as one hub and several of these."""
    ln = DashedLine(edge_point(a, b.get_center()), edge_point(b, a.get_center()), color=color, stroke_width=1.6, dash_length=0.1, stroke_opacity=0.7)
    g = VGroup(ln)
    if text:
        g.add(label(text, 12, MUTED).move_to(ln.get_center() + UP * 0.14))
    return g


def column(n: int = 8, color: str = BLUE, cell: float = 0.08, op: float = 0.9) -> VGroup:
    """A vector: a thin column of cells."""
    return VGroup(*[Square(cell, fill_color=color, fill_opacity=op, stroke_width=0) for _ in range(n)]).arrange(DOWN, buff=0.012)


def grid(rows: int, cols: int, color: str = VIOLET, cell: float = 0.08, op: float = 0.6) -> VGroup:
    """A matrix or a memory: a grid of cells, indexed row * cols + col."""
    return VGroup(*[Square(cell, fill_color=color, fill_opacity=op, stroke_width=0) for _ in range(rows * cols)]).arrange_in_grid(rows=rows, cols=cols, buff=0.012)


def dot_grid(n: int = 100, cols: int = 20, color: str = DIM, radius: float = 0.12) -> VGroup:
    """n dots in rows: a population (questions, requests, users) whose members change colour one by one."""
    return VGroup(*[Dot(radius=radius, color=color) for _ in range(n)]).arrange_in_grid(rows=n // cols, cols=cols, buff=0.2)


class Gauge(VGroup):
    """A vertical gauge with a name; set(level) returns an animation filling it 0..1. Red above 0.9. Two gauges
    side by side (e.g. a bus and a compute unit, or latency and load) carry an argument better than any label."""

    def __init__(self, name: str, color: str, height: float = 1.6, **kw):
        super().__init__(**kw)
        self.frame = RoundedRectangle(corner_radius=0.06, width=0.36, height=height, stroke_color=DIM, stroke_width=2, fill_opacity=0)
        self.fill = Rectangle(width=0.30, height=0.01, fill_color=color, fill_opacity=0.9, stroke_width=0).move_to(self.frame.get_bottom() + UP * 0.03, aligned_edge=DOWN)
        self.name = label(name, 15, DIM).next_to(self.frame, DOWN, buff=0.1)
        self.color, self.h = color, height - 0.06
        self.add(self.frame, self.fill, self.name)

    def set(self, level: float):
        level = max(0.006, min(1.0, level))
        target = Rectangle(width=0.30, height=self.h * level, fill_color=RED if level > 0.9 else self.color, fill_opacity=0.9, stroke_width=0)
        target.move_to(self.frame.get_bottom() + UP * 0.03, aligned_edge=DOWN)
        return self.fill.animate.become(target)


class Counter(VGroup):
    """A number with a unit and a name: bytes per step, requests per second, hits. Text, not LaTeX (none here): the
    value is a ValueTracker and the digits redraw as it changes, so to(value) returns an animation that counts.
    Give every counter a name that says its unit AND its clock ("tokens/s, each request, while decoding")."""

    def __init__(self, name: str, value: float, unit: str, color: str = TEXT, size: float = 30, decimals: int = 0, **kw):
        super().__init__(**kw)
        self.tracker = ValueTracker(value)
        self.fmt = lambda v: f"{v:,.{decimals}f}"
        self.num = label(self.fmt(value), size * 1.25, color)
        self.unit = label(unit, size * 0.6, color)
        self.name = label(name, 15, DIM)
        self.size, self.color = size, color
        self._layout()
        self.add(self.num, self.unit, self.name)
        # The name is the anchor: it moves with the group, so the digits follow wherever the counter is placed. The redraw
        # keeps the digits' current opacity, so a counter can be faded in and out like anything else.
        def redraw(m):
            op = m.get_fill_opacity()
            m.become(label(self.fmt(self.tracker.get_value()), size * 1.25, color)).next_to(self.name, UP, buff=0.08).align_to(self.name, LEFT)
            m.set_opacity(op)
        self.num.add_updater(redraw)
        self.unit.add_updater(lambda m: m.next_to(self.num, RIGHT, buff=0.1, aligned_edge=DOWN))

    def _layout(self):
        self.unit.next_to(self.num, RIGHT, buff=0.1, aligned_edge=DOWN)
        self.name.next_to(VGroup(self.num, self.unit), DOWN, buff=0.08).align_to(self.num, LEFT)

    def to(self, value: float):
        return self.tracker.animate.set_value(value)

    def stop(self):
        """Freeze the digits: call before fading a counter out. The digit updater redraws the number at full opacity
        every frame, so a FadeOut of a live counter leaves its digits on screen."""
        self.num.clear_updaters(); self.unit.clear_updaters()
        return self


class Bars(VGroup):
    """A small bar chart: heights in scene units, one colour, the tallest optionally emphasised. bars[i] is a
    Rectangle; use Transform(bars, Bars(new_heights, ...)) to redraw. Good for a distribution (next-token
    probabilities), a histogram, a comparison of a few quantities."""

    def __init__(self, heights, width: float = 0.16, gap: float = 0.05, color: str = YELLOW, emphasise_max: bool = True, **kw):
        super().__init__(**kw)
        top = max(heights)
        for h in heights:
            op = 0.35 + 0.6 * (h == top) if emphasise_max else 0.9
            self.add(Rectangle(width=width, height=max(0.04, h), fill_color=color, fill_opacity=op, stroke_width=0))
        self.arrange(RIGHT, buff=gap, aligned_edge=DOWN)


def timeline(y: float, x0: float, segments, colors: dict, height: float = 0.3, scale: float = 1.0) -> VGroup:
    """A horizontal bar made of labelled segments: (kind, length) pairs coloured by `colors[kind]`. The picture of
    a step, a request's life, a pipeline: time along x, so a longer thing is a wider block without a word."""
    g, x = VGroup(), x0
    for kind, length in segments:
        w = length * scale
        g.add(Rectangle(width=w - 0.03, height=height, fill_color=colors[kind], fill_opacity=0.85, stroke_width=0).move_to([x + w / 2, y, 0]))
        x += w
    return g

# ------------------------------------------------------------------------------------------------ vectors and matrices
# The vocabulary two decks share: a vector is a thin column of shaded cells (the shades stand for different numbers,
# so two vectors look different), a matrix is a grid, and a multiplication is one row of the matrix lighting up against
# the vector, the products collapsing into one output cell, then the sweep of the remaining rows. The sweep is the
# point: one output vector, the whole matrix read.

def vector(seed: int, color: str = BLUE, n: int = 8, cell: float = 0.16) -> VGroup:
    """A vector whose cells carry different shades, so two vectors are told apart. Same seed, same vector."""
    import random
    rnd = random.Random(seed)
    return VGroup(*[Square(cell, fill_color=color, fill_opacity=0.3 + 0.7 * rnd.random(), stroke_width=0) for _ in range(n)]).arrange(DOWN, buff=cell * 0.15)


def shades(v: VGroup) -> list:
    """The fill opacities of a vector's cells, to restore after a highlight."""
    return [c.get_fill_opacity() for c in v]


def restore(v: VGroup, ops: list, color: str) -> list:
    """Animations that put a vector's shades back after a highlight."""
    return [c.animate.set_fill(color, o) for c, o in zip(v, ops)]


def dot_product(scene, vec, vcolor, mat, i: int, out, color: str, cols: int = 8, hi: str = HI, beat: float = 0.09):
    """One output number, slowly: the vector's cells and the matrix row's cells light up in pairs, then the products
    fly to the output cell and it fills. The audience should see this once; then use sweep()."""
    ops = shades(vec)
    row = [mat[i * cols + j] for j in range(cols)]
    for j in range(cols):
        scene.play(vec[j].animate.set_fill(hi, 1.0), row[j].animate.set_fill(hi, 1.0), run_time=beat)
    prods = VGroup(*[Square(row[0].width * 0.7, fill_color=hi, fill_opacity=1.0, stroke_width=0).move_to(c) for c in row])
    scene.add(prods)
    scene.play(*[p.animate.move_to(out) for p in prods], run_time=0.5)
    scene.play(FadeOut(prods), out.animate.set_fill(color, 0.95), *restore(vec, ops, vcolor), *[m.animate.set_fill(mat[0].get_fill_color(), 0.6) for m in row], run_time=0.3)


def sweep(scene, vec, vcolor, jobs, cols: int = 8, rt: float = 0.14, hi: str = HI, mat_color: str = VIOLET):
    """Multiply at speed: for each output cell its row of the matrix lights up with the vector and the cell fills.
    jobs = [(matrix, out_vector, colour)]; every matrix in the list is swept at the same time, one row per beat.
    The dim-again animations are built after the light-up play on purpose (see docs/manim.md, .animate targets)."""
    ops = shades(vec)
    for i in range(len(jobs[0][1])):
        rows = [[mat[i * cols + j] for j in range(cols)] for mat, _, _ in jobs]
        on = [c.animate.set_fill(hi, 1.0) for c in vec]
        for row, (_, out, color) in zip(rows, jobs):
            on += [m.animate.set_fill(hi, 1.0) for m in row] + [out[i].animate.set_fill(color, 0.95)]
        scene.play(*on, run_time=rt)
        off = [m.animate.set_fill(mat_color, 0.6) for row in rows for m in row]
        scene.play(*off, *restore(vec, ops, vcolor), run_time=rt * 0.4)


# ------------------------------------------------------------------------------------------------ lists that grow
# Two shapes of the same idea, found independently by three decks: state drawn as a list that only grows. Horizontal
# with offsets when position is the point (a log, a queue, a buffer, a timeline of discrete items); vertical blocks
# when the items carry words (messages, records, events). A reader is a pointer under the row: replay is the pointer
# moving back, and every "consumer" concept becomes a pointer movement.

class Log(VGroup):
    """An append-only row of cells with their offsets beneath, on a rail of `capacity` slots. append(scene, colour,
    source) drops a cell into the next slot from `source`; put(colour) places one without animation for a picture that
    starts filled. cells[i] is the item at offset base + i, offs[i] its label; the rail is log.rail."""

    def __init__(self, x0: float, y: float, capacity: int = 12, base: int = 0, name: str = "", cell: float = 0.42, gap: float = 0.08, **kw):
        super().__init__(**kw)
        self.x0, self.y, self.capacity, self.base, self.side, self.pitch = x0, y, capacity, base, cell, cell + gap
        self.rail = Rectangle(width=capacity * self.pitch + gap, height=cell + 0.16, stroke_color=DIM, stroke_width=1.2, fill_opacity=0)
        self.rail.move_to([x0 + (capacity * self.pitch + gap) / 2, y, 0])
        self.cells, self.offs = VGroup(), VGroup()
        self.add(self.rail, self.cells, self.offs)
        if name:
            self.name = label(name, 15, MUTED).next_to(self.rail, UP, buff=0.08).align_to(self.rail, LEFT)
            self.add(self.name)

    def slot(self, i: int):
        return [self.x0 + (self.pitch - self.side) + self.side / 2 + i * self.pitch, self.y, 0]

    def _cell(self, i: int, color: str) -> Square:
        return Square(self.side, fill_color=color, fill_opacity=0.9, stroke_width=0).move_to(self.slot(i))

    def _off(self, i: int) -> Text:
        return label(str(self.base + i), 14, MUTED).move_to([self.slot(i)[0], self.y - self.side / 2 - 0.22, 0])

    def append(self, scene, color: str, source=None, rt: float = 0.35, extra=()):
        """Animate an item arriving at the next slot (from `source`, a mobject or a point); returns the cell."""
        i = len(self.cells)
        cell, off = self._cell(i, color), self._off(i)
        if source is not None:
            cell.move_to(source.get_center() if hasattr(source, "get_center") else source)
            scene.add(cell)
            scene.play(cell.animate.move_to(self.slot(i)), *extra, run_time=rt)
            scene.play(FadeIn(off), run_time=0.15)
        else:
            scene.play(FadeIn(cell, shift=DOWN * 0.15), FadeIn(off), *extra, run_time=rt)
        self.cells.add(cell); self.offs.add(off)
        return cell

    def put(self, color: str) -> Square:
        i = len(self.cells)
        cell, off = self._cell(i, color), self._off(i)
        self.cells.add(cell); self.offs.add(off)
        return cell

    def below(self, i: int, dy: float = 0.78):
        """The point under offset i where a reader's pointer sits. Budget 0.45 units below the offsets for a pointer
        and its tag, and 1.4 units between stacked logs that each carry one."""
        return [self.slot(i)[0], self.y - dy, 0]


class Pointer(VGroup):
    """A reader's position: a small triangle under a Log pointing at the next item, with the reader's name beneath.
    place(log, i) sets it; to(log, i) returns the Transform that moves it. The offset it holds is one integer."""

    def __init__(self, name: str, color: str = TEAL, **kw):
        super().__init__(**kw)
        self.tri = Triangle(color=color, fill_color=color, fill_opacity=1.0, stroke_width=0).scale(0.13)
        self.tag = label(name, 15, color).next_to(self.tri, DOWN, buff=0.05)
        self.add(self.tri, self.tag)

    def place(self, log: Log, i: int, dy: float = 0.78):
        self.tri.move_to(log.below(i, dy)); self.tag.next_to(self.tri, DOWN, buff=0.05)
        return self

    def to(self, log: Log, i: int, dy: float = 0.78):
        return Transform(self, self.copy().place(log, i, dy))


def block(text: str, color: str, w: float = 3.4, h: float = 0.35, size: float = 14, bare: bool = False) -> VGroup:
    """One item of a Stack: a rounded block in its colour with a solid bar at the left and one line of text.
    block[0] frame, block[1] bar, block[2] text. bare=True draws colour only, for a small reminder picture. If the
    text starts with "role · ", the role is coloured like the block."""
    r = RoundedRectangle(corner_radius=0.06, width=w, height=h, fill_color=color, fill_opacity=0.16, stroke_color=color, stroke_width=1.4)
    bar = Rectangle(width=0.09, height=h, fill_color=color, fill_opacity=0.95, stroke_width=0).move_to(r.get_left(), aligned_edge=LEFT)
    if bare:
        return VGroup(r, bar)
    role = text.split(" · ")[0] if " · " in text else ""
    t = label(text, size, TEXT, **({"t2c": {f"[0:{len(role)}]": color}} if role else {}))
    if t.width > w - 0.3:
        t.scale_to_fit_width(w - 0.3)
    t.move_to(r).align_to(r.get_left() + RIGHT * 0.2, LEFT)
    return VGroup(r, bar, t)


class Stack(VGroup):
    """A list that grows downward from `top` at `x`: messages in a conversation, events, records. append(scene,
    block, frm) flies a block in from a source (the thing that produced it) into the next slot. The whole list is one
    VGroup, so a copy of it can travel somewhere as one thing ("every call sends the whole list")."""

    def __init__(self, x: float, top: float, h: float = 0.35, gap: float = 0.08, **kw):
        super().__init__(**kw)
        self.x, self.top, self.h, self.gap, self.blocks = x, top, h, gap, []

    def slot(self, i: int):
        return [self.x, self.top - (self.h / 2 + i * (self.h + self.gap)), 0]

    def append(self, scene, b: VGroup, frm=None, run_time: float = 0.45):
        target = self.slot(len(self.blocks))
        if frm is not None:                       # born small at its source, growing into its slot: the audience sees where it came from
            b.scale(0.25).move_to(frm.get_center())
            scene.add(b)
            scene.play(b.animate.scale(4.0).move_to(target), run_time=run_time)
        else:
            b.move_to(target)
            scene.play(FadeIn(b, shift=DOWN * 0.15), run_time=run_time)
        self.blocks.append(b)
        self.add(b)
        return b


def code(source, language: str = "python", size: float = 18, width: float = 0.0) -> VGroup:
    """Syntax-highlighted code as a block: a dark panel with the lines highlighted by Pygments (monokai: plain names stay
    white, keywords, function names and strings each take one colour; one-dark painted every identifier red), no
    line numbers, laid out at BASE_SIZE and scaled to `size` so the spacing is exact. `source` is a string or a list
    of lines. The block's lines are `block.lines` (a VGroup, one per line) for walking through with highlight_line();
    the panel is `block.panel`. `width` scales the block to that many units if given. Indentation is kept."""
    text = source if isinstance(source, str) else "\n".join(source)
    c = Code(code_string=text, language=language, formatter_style="monokai", add_line_numbers=False, background="rectangle",
             background_config={"fill_color": "#171A21", "fill_opacity": 1.0, "stroke_color": DIM, "stroke_width": 1.2, "corner_radius": 0.12, "buff": 0.45},
             paragraph_config={"font": CODE_FONT, "font_size": BASE_SIZE, "line_spacing": 0.6, "disable_ligatures": True})
    c.scale(size / BASE_SIZE)
    if width:
        c.scale_to_fit_width(width)
    c.background.set_z_index(-1)   # so a highlight bar added later sits between the panel and the text
    g = VGroup(c)
    g.panel, g.lines = c.background, c.code_lines
    return g


def highlight_line(block: VGroup, i: int, color: str = HI) -> Rectangle:
    """A translucent bar behind line i of a code block, to move down the code while the picture does each step:
    `bar = highlight_line(code, 0); ...; self.play(bar.animate.move_to(highlight_line(code, 3)))`."""
    line = block.lines[i]
    r = Rectangle(width=block.panel.width - 0.2, height=line.height + 0.12, fill_color=color, fill_opacity=0.13, stroke_width=0)
    return r.move_to([block.panel.get_center()[0], line.get_center()[1], 0])
