"""This talk's vocabulary on top of the shared library.

  USER (blue)     what the user says, and the user            TOOL (yellow)    tool definitions and tool calls
  MODEL (violet)  the model, and what it says in words        RESULT (teal)    what a tool returned
  PROBLEM (red)   a wall: no path to the world, a full window

The one picture every scene draws: the user on the left; the application, a box holding the list of messages and the
tool functions; the model on the right, a box the list goes into and a reply comes out of; the devices the tools reach,
further right. The list of messages is the state of the agent and it only ever grows.
"""
from lib.palette import *

USER, MODEL, TOOL, RESULT, PROBLEM = BLUE, VIOLET, YELLOW, TEAL, RED
set_thread({"user": USER, "model": MODEL, "tool": TOOL, "tools": TOOL, "result": RESULT, "results": RESULT})

KIND = {"user": USER, "assistant": MODEL, "tool_use": TOOL, "tool_result": RESULT, "system": MUTED, "summary": MODEL}
BW, BH, GAP = 3.4, 0.35, 0.05          # a message block: width, height, gap in the list
CODE_FONT = "Menlo"


def block(kind: str, text: str, s: float = 1.0, bare: bool = False) -> VGroup:
    """One message in the list: a rounded block in the colour of its kind, a solid bar at its left edge, one line of
    text. block[0] frame, block[1] bar, block[2] text. `s` scales the whole block (the code scene draws a small list)."""
    c = KIND[kind]
    r = RoundedRectangle(corner_radius=0.06, width=BW, height=BH, fill_color=c, fill_opacity=0.16, stroke_color=c, stroke_width=1.4)
    bar = Rectangle(width=0.09, height=BH, fill_color=c, fill_opacity=0.95, stroke_width=0).move_to(r.get_left(), aligned_edge=LEFT)
    if bare:                               # a small reminder picture: colour says the kind, no text
        return VGroup(r, bar).scale(s)
    role = text.split(" · ")[0] if " · " in text else ""
    t = label(text, 14, TEXT, **({"t2c": {f"[0:{len(role)}]": c}} if role else {}))   # the role in the block's colour
    if t.width > BW - 0.3:
        t.scale_to_fit_width(BW - 0.3)
    t.move_to(r).align_to(r.get_left() + RIGHT * 0.2, LEFT)
    return VGroup(r, bar, t).scale(s)


class Messages(VGroup):
    """The list of messages: blocks stacked downward from `top` at `x`. append() animates a block flying from a source
    into its slot. The list is a VGroup, so a copy of it can travel into the model as one thing."""

    def __init__(self, x: float, top: float, s: float = 1.0, **kw):
        super().__init__(**kw)
        self.x, self.top, self.s, self.blocks = x, top, s, []

    def slot(self, i: int):
        return [self.x, self.top - self.s * (BH / 2 + i * (BH + GAP)), 0]

    def append(self, scene, b: VGroup, frm=None, run_time: float = 0.45):
        target = self.slot(len(self.blocks))
        if frm is not None:
            b.move_to(frm.get_center())
            scene.add(b)
            scene.play(b.animate.move_to(target), run_time=run_time)
        else:
            b.move_to(target)
            scene.play(FadeIn(b, shift=DOWN * 0.15), run_time=run_time)
        self.blocks.append(b)
        self.add(b)
        return b


def app_box(w: float = 5.6, h: float = 4.7, s: float = 1.0) -> VGroup:
    g = box(w, h, "application", MUTED, size=18, fill=0.04)
    return g.scale(s)


def model_box(s: float = 1.0) -> VGroup:
    return box(2.4, 1.7, "model", MODEL, size=22, fill=0.10).scale(s)


def tool_card(name: str, desc: str, schema: str, s: float = 1.0) -> VGroup:
    """A tool definition as the model sees it: name, description, input schema. card[0] frame, [1] name, [2] desc, [3] schema."""
    r = RoundedRectangle(corner_radius=0.06, width=2.2, height=0.8, fill_color=TOOL, fill_opacity=0.10, stroke_color=TOOL, stroke_width=1.4)
    n = label(name, 15, TOOL).move_to(r.get_top() + DOWN * 0.15).align_to(r.get_left() + RIGHT * 0.1, LEFT)
    d = label(desc, 13, TEXT).next_to(n, DOWN, buff=0.03).align_to(n, LEFT)
    sc = label(schema, 12, MUTED).next_to(d, DOWN, buff=0.02).align_to(n, LEFT)
    for t in (d, sc):
        if t.width > 2.0:
            t.scale_to_fit_width(2.0)
    return VGroup(r, n, d, sc).scale(s)


def device(name: str, s: float = 1.0) -> VGroup:
    return node(name, MUTED, w=1.8, h=0.55, size=15).scale(s)


def call_model(scene, msgs: Messages, model: VGroup, run_time: float = 0.7, extra=None):
    """Every call sends the whole list: a copy of it (and of anything in `extra`, the system prompt and tools) shrinks
    into the model box, the box lights while it works, then dims."""
    ghost = VGroup(msgs.copy(), *(m.copy() for m in (extra or []))).set_opacity(0.55)
    scene.play(ghost.animate.scale(0.22).move_to(model[0].get_center()), run_time=run_time)
    scene.play(FadeOut(ghost), model[0].animate.set_fill(MODEL, 0.40), run_time=0.25)
    scene.play(model[0].animate.set_fill(MODEL, 0.10), run_time=0.2)


def reply(scene, msgs: Messages, model: VGroup, kind: str, text: str, run_time: float = 0.5) -> VGroup:
    """The model's reply comes out of the box and joins the list."""
    return msgs.append(scene, block(kind, text, msgs.s), frm=model[0], run_time=run_time)


def code_lines(lines, size: float = 16) -> VGroup:
    """Code as left-aligned monospaced lines; code[i] is line i."""
    g = VGroup(*[Text(l if l.strip() else " ", font=CODE_FONT, font_size=size, color=TEXT) for l in lines])
    g.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    return g
