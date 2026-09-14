"""This talk's vocabulary and its one picture. Colours: the user blue, the model violet, tools yellow, what came back
from the world teal, red for a wall. The stage is fixed for the whole deck: the user at the left margin, the
application as a box holding the list of messages, the model top right, the tools in a column under the model, each
card carrying the device it reaches. Every scene adds the parts it starts from and grows from there.

Layout (scene units; frame 14.22 by 8, content band y 2.6 to -2.3):
  user          node at x -5.9, y 1.9
  application   box x -4.6 .. 1.6, y 2.55 .. -2.35, name top-left; the list of messages inside, blocks 5.6 by 0.4
  model         box x 3.1 .. 6.7, y 2.45 .. 1.05
  tools         three cards 3.6 by 0.95 at y 0.25, -0.8, -1.85 in the model's column
  counters      one row at y -2.75: model calls at x 3.1, tool calls at x 5.2
"""
from lib.palette import *

USER, MODEL, TOOL, RESULT, PROBLEM = BLUE, VIOLET, YELLOW, TEAL, RED
SYSTEM = MUTED
set_thread({"user": USER, "model": MODEL, "tool": TOOL, "tools": TOOL, "result": RESULT, "results": RESULT, "api": TOOL})

KIND = {"user": USER, "assistant": MODEL, "tool_use": TOOL, "tool_result": RESULT, "system": SYSTEM, "summary": MODEL}

APP_X0, APP_X1, APP_Y0, APP_Y1 = -4.6, 1.6, -2.35, 2.55
LIST_X, LIST_TOP = (APP_X0 + APP_X1) / 2, 2.1
BW, BH, BGAP = 5.6, 0.42, 0.07
MODEL_C, MODEL_W, MODEL_H = [4.9, 1.75, 0], 3.6, 1.4
CARD_W, CARD_H, CARD_YS = 3.6, 0.95, [0.25, -0.8, -1.85]
COUNTER_Y = -2.75


def user_node() -> VGroup:
    return node("user", USER, w=1.6, h=0.7, size=20).move_to([-5.9, 1.9, 0])


def app_box() -> VGroup:
    g = box(APP_X1 - APP_X0, APP_Y1 - APP_Y0, "application", MUTED, size=18, fill=0.04, name_align="left")
    return g.move_to([(APP_X0 + APP_X1) / 2, (APP_Y0 + APP_Y1) / 2, 0])


def model_box() -> VGroup:
    return box(MODEL_W, MODEL_H, "model", MODEL, size=22, fill=0.10).move_to(MODEL_C)


def message(kind: str, text: str) -> VGroup:
    """One message in the list, coloured by its kind; the role in the block's colour."""
    return block(text, KIND[kind], w=BW, h=BH, size=17)


def messages() -> Stack:
    return Stack(LIST_X, LIST_TOP, h=BH, gap=BGAP)


def call_arrows(app: VGroup, model: VGroup) -> VGroup:
    """The two arrows between the application and the model, with what travels on each: the call carries the system
    prompt, the tools and every message; one reply comes back. Returns VGroup(call, reply)."""
    y_call, y_reply = 2.05, 1.35
    call = Arrow([APP_X1 + 0.08, y_call, 0], [MODEL_C[0] - MODEL_W / 2 - 0.08, y_call, 0], buff=0, color=MUTED, stroke_width=2.2, tip_length=0.18)
    reply = Arrow([MODEL_C[0] - MODEL_W / 2 - 0.08, y_reply, 0], [APP_X1 + 0.08, y_reply, 0], buff=0, color=MODEL, stroke_width=2.2, tip_length=0.18)
    cl = label("system prompt +\ntools + messages", 13, MUTED).next_to(call, UP, buff=0.05)   # two lines: it must fit between the boxes
    rl = label("one reply", 13, MODEL).next_to(reply, DOWN, buff=0.05)
    return VGroup(VGroup(call, cl), VGroup(reply, rl))


def device_link(device: VGroup, text: str = "the application's\ncode calls it") -> VGroup:
    """A horizontal dashed line from the application's right edge to a device, labelled underneath: the application's
    own code reaches this thing. Horizontal on purpose, so it never crosses the arrows to the model."""
    y = device.get_center()[1]
    ln = DashedLine([APP_X1 + 0.08, y, 0], [device.get_left()[0] - 0.08, y, 0], color=MUTED, stroke_width=1.6, dash_length=0.1, stroke_opacity=0.7)
    return VGroup(ln, label(text, 13, MUTED).next_to(ln, DOWN, buff=0.05))


def device_box(name: str, y: float) -> VGroup:
    """A thing in the world the application can reach: a camera API, a thermometer, an archive. Sits where its tool
    card will later sit, so the API visibly becomes the tool."""
    return node(name, MUTED, w=CARD_W, h=CARD_H, size=17).move_to([MODEL_C[0], y, 0])


def tool_card(name: str, desc: str, schema: str, device: str, y: float) -> VGroup:
    """A tool definition as the model receives it: name, description, input schema; the device it reaches as a tag
    top-right. card[0] frame, [1] name, [2] description, [3] schema, [4] device tag."""
    r = RoundedRectangle(corner_radius=0.08, width=CARD_W, height=CARD_H, fill_color=TOOL, fill_opacity=0.10, stroke_color=TOOL, stroke_width=1.6).move_to([MODEL_C[0], y, 0])
    x0 = r.get_left()[0] + 0.15
    n = label(name, 17, TOOL).move_to([x0, y + 0.29, 0], aligned_edge=LEFT)
    d = label(desc, 14, TEXT).move_to([x0, y, 0], aligned_edge=LEFT)
    sc = label(schema, 13, MUTED).move_to([x0, y - 0.29, 0], aligned_edge=LEFT)
    tag = label(device, 13, MUTED).move_to([r.get_right()[0] - 0.15, y + 0.29, 0], aligned_edge=RIGHT)
    return VGroup(r, n, d, sc, tag)


TOOLS = [("query_camera", "what a camera sees right now", "camera: int, question: str", "camera API", CARD_YS[0]),
         ("query_temperature", "outdoor temperature in °C", "no arguments", "thermometer", CARD_YS[1]),
         ("camera_history", "recordings from a camera since a time", "camera: int, since: str", "archive", CARD_YS[2])]


def tool_cards() -> VGroup:
    return VGroup(*[tool_card(*t) for t in TOOLS])


def counters() -> tuple:
    calls = Counter("model calls", 0, "", MODEL, size=22).move_to([3.1, COUNTER_Y, 0], aligned_edge=LEFT)
    tools = Counter("tool calls", 0, "", TOOL, size=22).move_to([5.2, COUNTER_Y, 0], aligned_edge=LEFT)
    return calls, tools


def call_model(scene, msgs: Stack, model: VGroup, extra=(), run_time: float = 0.8):
    """Every call sends the whole list: a copy of the list (and of anything in `extra`, the tool cards) shrinks into
    the model box, which lights while it works."""
    ghost = VGroup(msgs.copy(), *(m.copy() for m in extra)).set_opacity(0.6)
    scene.play(ghost.animate.scale(0.15).move_to(model[0].get_center()), run_time=run_time)
    scene.play(FadeOut(ghost), model[0].animate.set_fill(MODEL, 0.35), run_time=0.25)
    scene.play(model[0].animate.set_fill(MODEL, 0.10), run_time=0.2)


def reply(scene, msgs: Stack, model: VGroup, kind: str, text: str, run_time: float = 0.6) -> VGroup:
    """The model's reply comes out of the box and joins the list."""
    return msgs.append(scene, message(kind, text), frm=model[0], run_time=run_time)


def stop_label(text: str, model: VGroup, color: str) -> Text:
    """The stop reason, attached under the model box's left corner."""
    return label(text, 14, color).next_to(model[0], DOWN, buff=GAP_TIGHT).align_to(model[0], LEFT)


def stage():
    """The fixed picture every scene starts from, by name."""
    user, app, model = user_node(), app_box(), model_box()
    arrows = call_arrows(app, model)
    calls, tools = counters()
    return {"user": user, "app": app, "model": model, "arrows": arrows, "calls": calls, "tools": tools}


# ------------------------------------------------------------------------------------------------ what each scene leaves behind
# Every scene after the first rebuilds the previous scene's last frame from these, statically, so the seam is invisible.
HIST_API = [("user", "user · anyone in the backyard?"), ("user", "user · [frame from camera 2] + the question"),
            ("assistant", "assistant · yes, one person by the shed"), ("user", "user · warm enough to open the door?"),
            ("user", "user · [frame from camera 2] + the question"), ("assistant", "assistant · I cannot read a temperature from a frame")]
HIST_LOOP = [("user", "user · warm enough to open the door?"), ("tool_use", "assistant · tool_use: query_temperature()"),
             ("tool_result", "user · tool_result: 19 °C"), ("assistant", "assistant · 19 °C: yes, open it"),
             ("user", "user · anyone in the backyard?"), ("tool_use", 'assistant · tool_use: query_camera(2, "anyone there?")'),
             ("tool_result", "user · tool_result: a person by the shed"), ("assistant", "assistant · yes, one person by the shed")]
TITLES = {"api": ("An application with one model call", "1  a plain application"),
          "tool": ("The whole process becomes a tool", "2  from a process to tools"),
          "loop": ("The application runs the loop itself", "3  the agentic loop"),
          "code": ("The loop behind a framework call, and the hooks into it", "4  what a framework hides"),
          "state": ("The list is the only state", "5  the list is the only state"),
          "every": ("Every agent today works like this", "6  the same loop, generic tools")}

# the plain application of move one: one function, one model call, the frame fetched by the code every time
APP_SRC = '''def answer(question):
    frame = camera_api.frame(2)   # camera 2, always
    return llm(system, [frame, question])'''

FRAMEWORK_SRC = '''agent = Agent(
    model="claude-sonnet-5",
    system_prompt=system,
    tools=[query_camera,
           query_temperature,
           camera_history],
)
agent("warm enough to open the door?")'''

# the same definition with the hook of move four registered: one more line
FRAMEWORK_HOOKS_SRC = FRAMEWORK_SRC.replace("           camera_history],\n", "           camera_history],\n    hooks=[RefuseDeletions()],\n")

# the small list move four ends with: one question, two tool exchanges, an answer, then the refused call and its result
CODE_END_KINDS = ["user", "tool_use", "tool_result", "tool_use", "tool_result", "assistant", "tool_use", "tool_result"]

GENERIC_TOOLS = [("bash", "run a shell command", "command: str", "shell", CARD_YS[0]),
                 ("read_file", "read a file from the repository", "path: str", "disk", CARD_YS[1]),
                 ("write_file", "write or edit a file", "path: str, content: str", "disk", CARD_YS[2])]
HIST_STATE = [("summary", "summary · door opened at 19 °C; one person by the shed"), ("assistant", "assistant · yes, one person by the shed"),
              ("tool_result", "user · tool_result: camera_history, 40,000 tokens of detections")]


# the labels one scene leaves for the next to start from; one string, two frames, so the seam cannot drift
STAYS_LABEL = "stays here: the code, the API, the credentials"
TO_MODEL_LABEL = "to the model: name, description, input schema"
CHOOSES_LABEL = "the model chooses; the application runs it; then asks the model again"
FRAMEWORK_LABEL = "the loop, the list and the hook: behind one call"
SUMMARY_LABEL = "summarisation: the oldest messages become one; the most recent stay verbatim"
WINDOW = 8   # messages the drawn context window holds; a real window is counted in tokens (the note says so)


def under_app(text: str, size: float = 14, color: str = MUTED, app: VGroup = None) -> Text:
    """A label under the application box, aligned to its left edge: where each move states its problem or its lesson."""
    ref = (app or app_box())[0]
    return label(text, size, color).next_to(ref, DOWN, buff=GAP_TIGHT).align_to(ref, LEFT)


def context_window() -> VGroup:
    """The context window drawn around the list: room for WINDOW messages, dashed, in the problem colour. Its label sits
    centred on the top edge over a background, so it reads across the application box's border and clear of the arrow
    labels. window[0] frame, [1] label."""
    h = WINDOW * (BH + BGAP)
    frame = DashedVMobject(RoundedRectangle(corner_radius=0.08, width=BW + 0.3, height=h + 0.1, stroke_color=PROBLEM, stroke_width=1.6, fill_opacity=0), num_dashes=60)
    frame.move_to([LIST_X, LIST_TOP - h / 2 + BGAP / 2, 0])
    lbl = label("context window", 14, PROBLEM).next_to(frame, UP, buff=GAP_TIGHT)
    return VGroup(frame, VGroup(BackgroundRectangle(lbl, color=BG, fill_opacity=1, buff=0.05), lbl))


def put_history(msgs: Stack, history) -> Stack:
    """Fill a list without animation, for a scene's first frame."""
    for kind, text in history:
        b = message(kind, text).move_to(msgs.slot(len(msgs.blocks))); msgs.blocks.append(b); msgs.add(b)
    return msgs


# the reminder picture of move four: the same three things, small, on the left of the code
MINI_X, MINI_TOP, MINI_H, MINI_GAP = -5.0, 1.45, 0.18, 0.04


def app_code():
    """The plain application's code, small, in the lower part of the application box."""
    return code(APP_SRC, "python", 13).move_to([LIST_X, -1.55, 0])


def mini_stage(kinds) -> tuple:
    """The small model, list and cards that stand for the stage beside the code. kinds: the list's message kinds."""
    model = box(2.6, 0.8, "model", MODEL, size=16, fill=0.10).move_to([MINI_X, 2.1, 0])
    lst = Stack(MINI_X, MINI_TOP, h=MINI_H, gap=MINI_GAP)
    for k in kinds:
        b = block("", KIND[k], w=2.6, h=MINI_H, bare=True).move_to(lst.slot(len(lst.blocks))); lst.blocks.append(b); lst.add(b)
    cards = VGroup(*[Rectangle(width=1.0, height=0.26, fill_color=TOOL, fill_opacity=0.12, stroke_color=TOOL, stroke_width=1.2).move_to([-3.1, 1.3 - 0.36 * i, 0]) for i in range(3)])
    return model, lst, cards
