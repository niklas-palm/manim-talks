"""The shared look and vocabulary for every talk: a dark, few-colour style in the spirit of 3Blue1Brown, built with
Manim Community Edition. Import it in every scene file with `from lib.palette import *`.

What lives here
  colours       a small palette; a talk assigns each colour one meaning and keeps it for the whole deck
  TalkSlide     a Scene whose steps are clicks; each step carries a speaker note (next_slide / finish)
  text          label, title, small, caption, swap_caption, pin, thread colouring of a talk's nouns
  objects       tokens, box, node, arrow, column, grid, dot_grid, Counter, Gauge, Bars, travel
  layout        the frame constants and the bands titles, pictures and captions live in

Rules the helpers encode (see docs/principles.md for the why):
  * text never below font size 12; small text is rendered at 20 and scaled, because Pango's layout breaks at 6 pt
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
FONT = "Helvetica"                 # Helvetica Neue through Pango had uneven word spacing at small sizes

# ------------------------------------------------------------------------------------------------ layout
# The frame is 14.22 by 8 scene units, centred on the origin. Fixed furniture goes in fixed bands so scenes look alike.
FRAME_W, FRAME_H = 14.22, 8.0
TITLE_Y = 3.3                      # title baseline band (title() puts the title at the top edge with buff 0.5)
CONTENT_TOP, CONTENT_BOTTOM = 2.6, -2.3
CAPTION_Y = -3.3

# ------------------------------------------------------------------------------------------------ the scene

class TalkSlide(MovingCameraScene):
    """A scene is a sequence of steps; a step is what one click plays. next_slide(note) ends the current step and
    records the speaker note for it; finish(note) does the same for the last step. Manim writes one clip per step
    (--save_sections) and a JSON index of durations; bin/build.py strings clips and notes into the audience and
    presenter pages. Notes are one paragraph of plain prose, written for the speaker to read aloud."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self._notes = []

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
        chars = int(width * 185 / size)
        s = "\n".join(textwrap.fill(par, chars) for par in s.split("\n"))
    if thread:
        kw["t2c"] = thread_colours(s)
    t = Text(s, font=FONT, font_size=size, color=color, line_spacing=1.1, **kw)
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


def box(w: float, h: float, name: str = "", color: str = VIOLET, size: float = 22, fill: float = 0.10) -> VGroup:
    """A rounded box with an optional name inside its top edge: a machine, an engine, a service. box[0] is the
    rectangle; add members with .add() so they move with it."""
    r = RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=color, stroke_width=2.5, fill_color=color, fill_opacity=fill)
    g = VGroup(r)
    if name:
        g.add(label(name, size, color=color).next_to(r.get_top(), DOWN, buff=0.15))
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


def arrow(a: Mobject, b: Mobject, text: str = "", color: str = MUTED, buff: float = 0.12, size: float = 14, above: bool = True) -> VGroup:
    """An arrow from the edge of a to the edge of b with a small label beside its middle. Build it after both ends are
    in their final positions (an arrow built before a move points at the old place)."""
    ar = Arrow(a.get_center(), b.get_center(), buff=0, color=color, stroke_width=2.2, tip_length=0.18)
    start = a.get_boundary_point(ar.get_unit_vector()) + ar.get_unit_vector() * buff
    end = b.get_boundary_point(-ar.get_unit_vector()) - ar.get_unit_vector() * buff
    ar = Arrow(start, end, buff=0, color=color, stroke_width=2.2, tip_length=0.18)
    g = VGroup(ar)
    if text:
        side = UP if above else DOWN
        if abs(ar.get_unit_vector()[1]) > 0.7:   # a vertical arrow: label to its right
            side = RIGHT
        g.add(label(text, size, color).next_to(ar.get_center(), side, buff=0.08))
    return g


def travel(scene, path_from: Mobject, path_to: Mobject, color: str = BLUE, radius: float = 0.09, run_time: float = 0.5, flash: str = ""):
    """A dot travels from one object to another and vanishes; optionally the destination flashes. The unit of
    motion in every system picture: a request, a packet, a message, a token on its way."""
    d = Dot(color=color, radius=radius).move_to(path_from.get_center())
    scene.add(d)
    scene.play(d.animate.move_to(path_to.get_center()), run_time=run_time)
    anims = [FadeOut(d, run_time=0.15)]
    if flash:
        anims.append(Flash(path_to, color=flash, flash_radius=max(path_to.width, path_to.height) / 2 + 0.15, num_lines=8, run_time=0.3))
    scene.play(*anims)


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
        # The name is the anchor: it moves with the group, so the digits follow wherever the counter is placed.
        self.num.add_updater(lambda m: m.become(label(self.fmt(self.tracker.get_value()), size * 1.25, color))
                             .next_to(self.name, UP, buff=0.08).align_to(self.name, LEFT))
        self.unit.add_updater(lambda m: m.next_to(self.num, RIGHT, buff=0.1, aligned_edge=DOWN))

    def _layout(self):
        self.unit.next_to(self.num, RIGHT, buff=0.1, aligned_edge=DOWN)
        self.name.next_to(VGroup(self.num, self.unit), DOWN, buff=0.08).align_to(self.num, LEFT)

    def to(self, value: float):
        return self.tracker.animate.set_value(value)


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
