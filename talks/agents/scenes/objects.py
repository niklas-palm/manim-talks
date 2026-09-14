"""This talk's vocabulary on top of the shared library.

  USER (blue)     what the user says, and the user            TOOL (yellow)    tool definitions and tool calls
  MODEL (violet)  the model, and what it says in words        RESULT (teal)    what came back from the world
  PROBLEM (red)   a wall: no path to the world, a full window

The one picture every scene draws, on the grid (lib.palette COLS and ROWS): the user at the left column line; the
application, a box holding the list of messages and, in a second column, the functions it can run; the model, a box
top right that the list goes into and one reply comes out of; the devices the functions reach, at the right margin,
each on the same row as the function that reaches it. The list of messages is the state of the agent and only grows.
"""
from lib.palette import *

USER, MODEL, TOOL, RESULT, PROBLEM = BLUE, VIOLET, YELLOW, TEAL, RED
set_thread({"user": USER, "model": MODEL, "tool": TOOL, "tools": TOOL, "result": RESULT, "results": RESULT, "api": TOOL})

KIND = {"user": USER, "assistant": MODEL, "tool_use": TOOL, "tool_result": RESULT, "system": MUTED, "summary": MODEL}
BW, BH, BGAP = 3.1, 0.38, 0.05          # a message block: width, height, gap in the Stack (15 pt text)

# ------------------------------------------------------------------------------------------------ the grid
USER_AT = [-5.9, 1.3, 0]                # user node, 1.0 wide: its left edge on the -6.4 column line, on the 1.3 row
APP_AT, APP_W, APP_H = [-2.15, 0.15, 0], 5.9, 4.8        # x -5.1 .. 0.8, y -2.25 .. 2.55
LIST_X, SYS_Y, LIST_TOP = -3.35, 1.95, 1.71               # the list column: GAP inside the application's left edge
CARD_X, CARD_W, CARD_H = -0.55, 2.1, 0.7                  # the functions column inside the application
ROWS3 = (0.4, -0.5, -1.4)                                 # the three function/device rows (pitch 0.9, gap 0.2)
MODEL_AT, MODEL_W, MODEL_H = [3.4, 1.85, 0], 2.0, 1.3     # x 2.4 .. 4.4, y 1.2 .. 2.5
DEV_X, DEV_W = 5.6, 1.6                                   # x 4.8 .. 6.4: the right edge on the 6.4 column line
APP_R, MODEL_L = 0.8, 2.4                                 # the arrows run between these
REQ_Y, REP_Y = 2.2, 1.5
STOP_AT = [3.4, 0.95, 0]
COUNTERS_Y = -2.2
CALLS_X, TCALLS_X, SENT_X = 2.4, 3.75, 5.0


def app_box() -> VGroup:
    return box(APP_W, APP_H, "application", MUTED, size=18, fill=0.04, name_align="left").move_to(APP_AT)


def model_box() -> VGroup:
    return box(MODEL_W, MODEL_H, "model", MODEL, size=20, fill=0.10).move_to(MODEL_AT)


def user_node() -> VGroup:
    return node("user", USER, w=1.0, h=0.5, size=16).move_to(USER_AT)


def device(name: str, row: int) -> VGroup:
    return node(name, MUTED, w=DEV_W, h=0.55, size=15).move_to([DEV_X, ROWS3[row], 0])


def function_node(name: str, row: int, color: str = MUTED, sub: str = "camera, question") -> VGroup:
    """A function the application can run, before it is a tool: a plain named box in the functions column."""
    return node(name, color, w=CARD_W, h=0.6, size=15, sub=sub).move_to([CARD_X, ROWS3[row], 0])


def tool_card(name: str, desc: str, schema: str, row: int) -> VGroup:
    """A tool definition as the model sees it: name, description, input schema. card[0] frame, [1] name, [2] desc,
    [3] schema. Sits in the functions column on the row of the device it reaches. The description and schema lines are
    13 and 12 pt on purpose: three lines must fit a 0.7 card, the name is the line the audience reads, the rest is read
    aloud (talks/agents/README.md, Decisions)."""
    r = RoundedRectangle(corner_radius=0.06, width=CARD_W, height=CARD_H, fill_color=TOOL, fill_opacity=0.10, stroke_color=TOOL, stroke_width=1.4)
    n = label(name, 15, TOOL).move_to(r.get_top() + DOWN * 0.14).align_to(r.get_left() + RIGHT * GAP_TIGHT, LEFT)
    d = label(desc, 13, TEXT).next_to(n, DOWN, buff=0.03).align_to(n, LEFT)
    sc = label(schema, 12, MUTED).next_to(d, DOWN, buff=0.02).align_to(n, LEFT)
    for t in (d, sc):
        if t.width > CARD_W - 2 * GAP_TIGHT:
            t.scale_to_fit_width(CARD_W - 2 * GAP_TIGHT)
    return VGroup(r, n, d, sc).move_to([CARD_X, ROWS3[row], 0])


TOOLS = [("query_camera", "what a camera sees right now", "camera: int, question: str"),
         ("query_temperature", "outdoor temperature in °C", "no arguments"),
         ("camera_history", "recordings from a camera since a time", "camera: int, since: str")]
DEVICES = ["camera API", "thermometer", "camera archive"]


def arrows():
    """The request arrow into the model and the reply arrow out of it, with their labels; the request label is the
    thing that changes as the talk goes on (messages; plus system prompt; plus tools)."""
    req = Arrow([APP_R, REQ_Y, 0], [MODEL_L, REQ_Y, 0], buff=0, color=MUTED, stroke_width=2.2, tip_length=0.18)
    rep = Arrow([MODEL_L, REP_Y, 0], [APP_R, REP_Y, 0], buff=0, color=MUTED, stroke_width=2.2, tip_length=0.18)
    rep_l = label("one reply", 13, MUTED).next_to(rep, DOWN, buff=GAP_TIGHT)
    return req, rep, rep_l


def req_label(text: str) -> Text:
    """What the call carries, above the request arrow; two short lines so it fits the gap between the boxes."""
    return label(text, 13, MUTED).next_to(Line([APP_R, REQ_Y, 0], [MODEL_L, REQ_Y, 0]), UP, buff=GAP_TIGHT)


def counters(with_sent: bool = False):
    calls = Counter("model calls", 0, "", MODEL, size=22).move_to([CALLS_X, COUNTERS_Y, 0], aligned_edge=LEFT)
    tcalls = Counter("tool calls", 0, "", TOOL, size=22).move_to([TCALLS_X, COUNTERS_Y, 0], aligned_edge=LEFT)
    out = [calls, tcalls]
    if with_sent:
        out.append(Counter("sent this call", 0, "", TEXT, size=22).move_to([SENT_X, COUNTERS_Y, 0], aligned_edge=LEFT))
    return out


def furniture():
    """Everything a full-size scene starts from: user, application, model, the two arrows, the reply label."""
    return user_node(), app_box(), model_box(), *arrows()


def preload(msgs: Stack, items):
    """Put blocks into a Stack without animation, for a scene that starts where the last one ended."""
    for kind, text in items:
        b = block(text, KIND[kind], w=BW, h=BH, size=15).move_to(msgs.slot(len(msgs.blocks)))
        msgs.blocks.append(b); msgs.add(b)


def msg(kind: str, text: str) -> VGroup:
    return block(text, KIND[kind], w=BW, h=BH, size=15)


def call_model(scene, msgs: Stack, model: VGroup, run_time: float = 0.7, extra=None):
    """Every call sends the whole list: a copy of it (and of anything in `extra`, the system prompt and tools) shrinks
    into the model box, the box lights while it works, then dims."""
    ghost = VGroup(msgs.copy(), *(m.copy() for m in (extra or []))).set_opacity(0.55)
    scene.play(ghost.animate.scale(0.22).move_to(model[0].get_center()), run_time=run_time)
    scene.play(FadeOut(ghost), model[0].animate.set_fill(MODEL, 0.40), run_time=0.25)
    scene.play(model[0].animate.set_fill(MODEL, 0.10), run_time=0.2)


def reply(scene, msgs: Stack, model: VGroup, kind: str, text: str, run_time: float = 0.5) -> VGroup:
    """The model's reply comes out of the box and joins the list."""
    return msgs.append(scene, msg(kind, text), frm=model[0], run_time=run_time)


def to_user(scene, b: VGroup, user: VGroup, *extra, run_time: float = 0.5):
    """The last reply is shown to the user: a copy of the block shrinks into the user node."""
    out = b.copy()
    scene.play(out.animate.scale(0.5).move_to(user.get_center()).set_opacity(0), *extra, run_time=run_time)
    scene.remove(out)


def wall(a: Mobject, b: Mobject) -> VGroup:
    """No path from a to b: a dashed line with a red cross on it."""
    line = DashedLine(a.get_right() + RIGHT * 0.1, b.get_left() + LEFT * 0.1, color=DIM, stroke_width=2)
    cross = VGroup(Line(UP * 0.14 + LEFT * 0.14, DOWN * 0.14 + RIGHT * 0.14), Line(UP * 0.14 + RIGHT * 0.14, DOWN * 0.14 + LEFT * 0.14)).set_stroke(PROBLEM, 3).move_to(line.get_center())
    return VGroup(line, cross)
