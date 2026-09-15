"""This talk's vocabulary and its one picture. The accent slots carry the meanings: the user A1, the model A3, tools
A2, what came back from the world A4, ALERT for a wall. The stage is fixed for the whole deck: the user at the left margin, the
application as a box holding the list of messages, the model top right, the tools in a column under the model, each
card carrying the device it reaches. Every scene adds the parts it starts from and grows from there.

Layout (scene units; frame 14.22 by 8, content band y 2.6 to -2.3):
  user          node at x -5.9, y 1.9
  application   box x -4.6 .. 1.6, y 2.55 .. -2.35, name top-left; the list of messages inside, blocks 5.6 by 0.36
  agent         from move four on, a frame inside the application around the list: the framework's object, which owns
                the list and the loop; the application's own code is what is left outside it
  model         box x 3.1 .. 6.7, y 2.45 .. 1.05
  tools         three cards 3.6 by 0.95 at y 0.25, -0.8, -1.85 in the model's column
  counters      one row at y -2.75: model calls at x 3.1, tool calls at x 5.2
"""
from lib.palette import *

USER, MODEL, TOOL, RESULT, PROBLEM = A1, A3, A2, A4, ALERT
SYSTEM = MUTED
set_thread({"user": USER, "model": MODEL, "tool": TOOL, "tools": TOOL, "result": RESULT, "results": RESULT, "api": TOOL})

KIND = {"user": USER, "assistant": MODEL, "tool_use": TOOL, "tool_result": RESULT, "system": SYSTEM, "summary": MODEL, "refused": PROBLEM}

APP_X0, APP_X1, APP_Y0, APP_Y1 = -4.6, 1.6, -2.35, 2.55
LIST_X, LIST_TOP = (APP_X0 + APP_X1) / 2, 2.1
BW, BH, BGAP = 5.6, 0.36, 0.06
AGENT_TOP, AGENT_LIST_TOP = 2.12, 1.66   # the agent frame's top edge, under the application's name; where its list starts
MODEL_C, MODEL_W, MODEL_H = [4.9, 1.75, 0], 3.6, 1.4
CARD_W, CARD_H, CARD_YS = 3.6, 0.95, [0.25, -0.8, -1.85]
COUNTER_Y = -2.75


def user_node() -> VGroup:
    return node("user", USER, w=1.6, h=0.7, size=20).move_to([-5.9, 1.9, 0])


def app_box() -> VGroup:
    g = box(APP_X1 - APP_X0, APP_Y1 - APP_Y0, "application", MUTED, size=18, fill=FILL * 0.4, name_align="left")
    return g.move_to([(APP_X0 + APP_X1) / 2, (APP_Y0 + APP_Y1) / 2, 0])


def model_box() -> VGroup:
    return box(MODEL_W, MODEL_H, "model", MODEL, size=22, fill=FILL).move_to(MODEL_C)


LINE = 0.28   # one more content block in a message, drawn as one more line


def message(kind: str, text: str, extra: str = None) -> VGroup:
    """One message in the list, coloured by its kind; the role in the block's colour. `extra` is a second content block
    in the same message (the frame the code fetched, beside the question), drawn as a second line in the colour of what
    came back from the world."""
    b = block(text, KIND[kind], w=BW, h=BH, size=17)
    if extra:
        add_line(b, extra)
    return b


def add_line(b: VGroup, text: str) -> Text:
    """Grow a one-line message by a second content block, statically: frame and bar stretch down from the same top edge
    and the new line sits under the first. Returns the new line, already in the block."""
    top, h = b[0].get_top()[1], b[0].height + LINE
    b[0].stretch_to_fit_height(h).move_to([b[0].get_center()[0], top - h / 2, 0])
    b[1].stretch_to_fit_height(h).move_to(b[0].get_left(), aligned_edge=LEFT)
    t = label(text, 17, RESULT).move_to([b[2].get_left()[0], b[2].get_center()[1] - LINE, 0], aligned_edge=LEFT)
    b.add(t)
    return t


def attach(scene, b: VGroup, text: str, frm: Mobject, run_time: float = 0.8) -> Text:
    """add_line, animated: the message grows a line while the new content flies in from what produced it, so the
    audience sees the frame join the question rather than a second message appear."""
    g = b.copy()
    t = add_line(g, text)
    final = t.get_center()
    t.scale(0.25).move_to(frm.get_center())
    scene.add(t)
    scene.play(Transform(b[0], g[0]), Transform(b[1], g[1]), t.animate.scale(4.0).move_to(final), run_time=run_time)
    scene.remove(t)
    b.add(t)
    return t


def messages(top: float = LIST_TOP) -> Stack:
    return Stack(LIST_X, top, h=BH, gap=BGAP)


def agent_frame() -> VGroup:
    """The framework's object, drawn as a frame inside the application around the list: from move four on, the loop and
    the list live in here, and the application's own code is whatever is outside it. frame[0] rectangle, [1] name."""
    w, h = APP_X1 - APP_X0 - 0.3, AGENT_TOP - (APP_Y0 + 0.12)
    g = box(w, h, "agent", MUTED, size=15, fill=FILL * 0.6, name_align="left")
    return g.move_to([LIST_X, AGENT_TOP - h / 2, 0])


def call_arrows(app: VGroup, model: VGroup) -> VGroup:
    """The two arrows between the application and the model, with what travels on each: the call carries the system
    prompt, the tools and every message; one reply comes back. Returns VGroup(call, reply)."""
    y_call, y_reply = 2.05, 1.35
    call = Arrow([APP_X1 + 0.08, y_call, 0], [MODEL_C[0] - MODEL_W / 2 - 0.08, y_call, 0], buff=0, color=MUTED, stroke_width=sw(0.88), tip_length=0.18)
    reply = Arrow([MODEL_C[0] - MODEL_W / 2 - 0.08, y_reply, 0], [APP_X1 + 0.08, y_reply, 0], buff=0, color=MODEL, stroke_width=sw(0.88), tip_length=0.18)
    cl = label("system prompt +\ntools + messages", 13, MUTED).next_to(call, UP, buff=0.05)   # two lines: it must fit between the boxes
    rl = label("one reply", 13, MODEL).next_to(reply, DOWN, buff=0.05)
    return VGroup(VGroup(call, cl), VGroup(reply, rl))


def device_link(device: VGroup, text: str = "the application's\ncode calls it") -> VGroup:
    """A horizontal dashed line from the application's right edge to a device, labelled underneath: the application's
    own code reaches this thing. Horizontal on purpose, so it never crosses the arrows to the model."""
    y = device.get_center()[1]
    ln = DashedLine([APP_X1 + 0.08, y, 0], [device.get_left()[0] - 0.08, y, 0], color=MUTED, stroke_width=sw(0.64), dash_length=0.1, stroke_opacity=0.7)
    return VGroup(ln, label(text, 13, MUTED).next_to(ln, DOWN, buff=0.05))


def device_box(name: str, y: float) -> VGroup:
    """A thing in the world the application can reach: a camera API, a thermometer, an archive. Sits where its tool
    card will later sit, so the API visibly becomes the tool."""
    return node(name, MUTED, w=CARD_W, h=CARD_H, size=17).move_to([MODEL_C[0], y, 0])


def tool_card(name: str, desc: str, schema: str, device: str, y: float) -> VGroup:
    """A tool definition as the model receives it: name, description, input schema; the device it reaches as a tag
    top-right. card[0] frame, [1] name, [2] description, [3] schema, [4] device tag."""
    r = RoundedRectangle(corner_radius=rad(0.53), width=CARD_W, height=CARD_H, fill_color=TOOL, fill_opacity=FILL, stroke_color=TOOL, stroke_width=sw(0.64)).move_to([MODEL_C[0], y, 0])
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
FRAME = "[frame from camera 2]"   # the second content block of a question in move one: the picture the code fetched
HIST_API = [("user", "user · anyone in the backyard?", FRAME), ("assistant", "assistant · yes, one person by the shed"),
            ("user", "user · warm enough to open the door?", FRAME), ("assistant", "assistant · I cannot read a temperature from a frame")]
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


GENERIC_TOOLS = [("bash", "run a shell command", "command: str", "shell", CARD_YS[0]),
                 ("read_file", "read a file from the repository", "path: str", "disk", CARD_YS[1]),
                 ("write_file", "write or edit a file", "path: str, content: str", "disk", CARD_YS[2])]
HIST_STATE = [("summary", "summary · door opened at 19 °C; one person by the shed"), ("assistant", "assistant · yes, one person by the shed"),
              ("tool_result", "user · tool_result: camera_history, 40,000 tokens of detections")]


# the labels one scene leaves for the next to start from; one string, two frames, so the seam cannot drift
STAYS_LABEL = "stays here: the code, the API, the credentials"
TO_MODEL_LABEL = "to the model: name, description, input schema"
WHICH_LABEL = "which tool does this question need?"
FRAMEWORK_LABEL = "the loop, the list and the hook: behind one call"
SUMMARY_LABEL = "summarisation: the oldest messages become one; the most recent stay verbatim"
WINDOW = 8   # messages the drawn context window holds; a real window is counted in tokens (the note says so)


def under_app(text: str, size: float = 14, color: str = MUTED, app: VGroup = None) -> Text:
    """A label under the application box, aligned to its left edge: where each move states its problem or its lesson."""
    ref = (app or app_box())[0]
    return label(text, size, color).next_to(ref, DOWN, buff=GAP_TIGHT).align_to(ref, LEFT)


def context_window(top: float = LIST_TOP) -> VGroup:
    """The context window drawn around the list: room for WINDOW messages, dashed, in the problem colour. Its label sits
    centred on the top edge over a background, so it reads across the application box's border and clear of the arrow
    labels. window[0] frame, [1] label."""
    h = WINDOW * (BH + BGAP)
    frame = DashedVMobject(RoundedRectangle(corner_radius=rad(0.53), width=BW + 0.2, height=h + 0.1, stroke_color=PROBLEM, stroke_width=sw(0.64), fill_opacity=0), num_dashes=60)
    frame.move_to([LIST_X, top - h / 2 + BGAP / 2, 0])
    lbl = label("context window", 14, PROBLEM).next_to(frame, UP, buff=GAP_TIGHT)
    return VGroup(frame, VGroup(BackgroundRectangle(lbl, color=BG, fill_opacity=1, buff=0.05), lbl))


def put_history(msgs: Stack, history) -> Stack:
    """Fill a list without animation, for a scene's first frame."""
    for entry in history:
        b = message(*entry); b.move_to(msgs.slot(len(msgs.blocks), b.height)); msgs.blocks.append(b); msgs.add(b)
    return msgs


def app_code():
    """The plain application's code, small, in the lower part of the application box."""
    return code(APP_SRC, "python", 13).move_to([LIST_X, -1.55, 0])


# the compact agent: the picture of move four, beside the code and then inside the application. A frame named agent holds
# the list as bare coloured rows and the tools as bare cards; the model is drawn outside it, because it is not part of it.
MINI_H, MINI_GAP = 0.18, 0.04
MINI_AGENT = (-4.55, 0.4, 1.0)          # beside the code: the frame's centre, and the drawing's scale
MINI_MODEL = [-5.0, 2.1, 0]
IN_APP = (LIST_X, -0.1, 1.3)            # inside the application: larger, since the box has the room
HIST_KINDS = [kind for kind, _ in HIST_LOOP]   # the two questions of move three, as the compact list shows them


def mini_block(kind: str, k: float = 1.0) -> VGroup:
    return block("", KIND[kind], w=2.6 * k, h=MINI_H * k, bare=True)


def compact_agent(kinds, cx: float, cy: float, k: float = 1.0) -> tuple:
    """The agent drawn small, centred at (cx, cy), scaled by k: (frame, list, cards). kinds: the list's message kinds."""
    frame = box(4.0 * k, 2.3 * k, "agent", MUTED, size=12 * k, fill=FILL * 0.6, name_align="left").move_to([cx, cy, 0])
    lst = Stack(cx - 0.45 * k, cy + 0.85 * k, h=MINI_H * k, gap=MINI_GAP * k)
    for kind in kinds:
        b = mini_block(kind, k).move_to(lst.slot(len(lst.blocks))); lst.blocks.append(b); lst.add(b)
    cards = VGroup(*[Rectangle(width=1.0 * k, height=0.26 * k, fill_color=TOOL, fill_opacity=FILL * 1.2, stroke_color=TOOL, stroke_width=sw(0.48))
                     .move_to([cx + 1.45 * k, cy + (0.77 - 0.36 * i) * k, 0]) for i in range(3)])
    return frame, lst, cards


def mini_stage(kinds) -> tuple:
    """Beside the code in move four: the small model above the compact agent. Returns (model, frame, list, cards)."""
    model = box(2.6, 0.8, "model", MODEL, size=16, fill=FILL).move_to(MINI_MODEL)
    return (model, *compact_agent(kinds, *MINI_AGENT))


def agent_in_app(kinds) -> tuple:
    """The compact agent inside the application box, where move four ends and move five begins."""
    return compact_agent(kinds, *IN_APP)
