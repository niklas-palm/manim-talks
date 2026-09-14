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
BW, BH, GAP = 3.4, 0.35, 0.05          # a message block in this deck: width, height, gap in the Stack (the library's block and Stack draw them)


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


def call_model(scene, msgs: Stack, model: VGroup, run_time: float = 0.7, extra=None):
    """Every call sends the whole list: a copy of it (and of anything in `extra`, the system prompt and tools) shrinks
    into the model box, the box lights while it works, then dims."""
    ghost = VGroup(msgs.copy(), *(m.copy() for m in (extra or []))).set_opacity(0.55)
    scene.play(ghost.animate.scale(0.22).move_to(model[0].get_center()), run_time=run_time)
    scene.play(FadeOut(ghost), model[0].animate.set_fill(MODEL, 0.40), run_time=0.25)
    scene.play(model[0].animate.set_fill(MODEL, 0.10), run_time=0.2)


def reply(scene, msgs: Stack, model: VGroup, kind: str, text: str, run_time: float = 0.5) -> VGroup:
    """The model's reply comes out of the box and joins the list."""
    return msgs.append(scene, block(text, KIND[kind]), frm=model[0], run_time=run_time)
