"""This talk's vocabulary on top of the shared library.

  DESIRED (blue)   records: the state you asked for, stored in etcd (Deployment, ReplicaSet, Pod, Service)
  ACTUAL  (yellow) what actually runs: containers on nodes, and the status they report back
  CONTROL (violet) the control plane: API server, controllers, scheduler; every loop that chases the gap
  NODE    (teal)   the machines: nodes, kubelet, kube-proxy; and etcd's members
  HOT     (red)    failure, absence, a gap between desired and actual

Text sizes: 15 and up for anything inside a box, 13 only for units. Legend-like words appear once ("observe, compare,
act" on the first loop, "watch" on the first line, "kube-proxy" on the first node); the others are recognised by
shape and colour. Sentences go in the notes.
"""
from lib.palette import *

DESIRED, ACTUAL, CONTROL, NODE, HOT = BLUE, YELLOW, VIOLET, TEAL, RED
set_thread({"desired": DESIRED, "record": DESIRED, "records": DESIRED, "running": ACTUAL, "actual": ACTUAL,
            "controller": CONTROL, "controllers": CONTROL, "scheduler": CONTROL, "node": NODE, "nodes": NODE, "kubelet": NODE})

# fixed furniture of the stage, on the library grid, shared by every scene so the picture never jumps. Three columns:
#   left   kubectl on top, the control loops under it            x -6.4 .. -3.4
#   middle the API server with etcd directly below it              x -2.6 .. 1.0
#   right  the three nodes                                          x  1.8 .. 5.2
# Every relation is axis-aligned: a dashed vertical bus runs down each side of the middle column, from a short stub on the
# API server's edge; each loop and each node reaches its bus with a short horizontal spoke. Pulses travel the same way, so
# nothing ever crosses a box.
X_CLIENT, X_CTRL, X_API, X_NODE = -4.9, -4.9, -0.8, 3.5
W_CTRL, W_API, W_NODE = 3.0, 3.6, 3.4
Y_CLIENT = 2.15                                      # kubectl at the top of the left column, its request goes straight right
Y_TOP = 1.95                                         # API server centre: 1.3 tall, its top edge on the 2.6 row line
Y_STORE = -0.625                                     # etcd: GAP below the API server, 3.35 tall, bottom on the -2.3 row line
NODE_YS = [1.615, -0.005, -1.625]                    # three nodes of 1.37 with GAP between, from 2.3 down to the -2.3 line
H_CTRL = 0.78                                        # four loops from 1.3 (under kubectl) down to -2.3, gaps of 0.16
CTRL_YS = {"deploy": 0.91, "rs": -0.03, "sched": -0.97, "extra": -1.91}
LBUS, RBUS = -3.0, 1.4                               # the two dashed buses, in the corridors beside the middle column
API_L, API_R = X_API - W_API / 2, X_API + W_API / 2
ATT_L, ATT_R = 1.55, 1.75                            # where each bus leaves the API server's edge
Y_COUNTERS = -2.75                                   # one row of counters under the -2.3 line, left edges on the column lines
Y_LABELS = 2.55                                      # a label above the node column (heartbeats, the open question)
CARD_W, CARD_H = 1.6, 0.8


def card(kind: str, detail: str = "", color: str = DESIRED) -> VGroup:
    """A record in the store: its kind, and one status line. card[0] frame, card[1] kind, card[2] status."""
    r = RoundedRectangle(corner_radius=0.08, width=CARD_W, height=CARD_H, stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=0.14)
    g = VGroup(r, label(kind, 16, TEXT).move_to(r.get_top() + DOWN * 0.24))
    g.add(label(detail if detail else " ", 15, MUTED).move_to(r.get_bottom() + UP * 0.22))
    return g


def set_detail(scene, c: VGroup, text: str, color: str = MUTED, run_time: float = 0.3):
    """Replace a card's status line (fade, never become: glyph counts differ)."""
    new = label(text, 15, color).move_to(c[2])
    scene.play(FadeOut(c[2]), FadeIn(new), run_time=run_time)
    c.remove(c[2]); c.add(new)
    return new


def apiserver() -> VGroup:
    """The API server: a box with three gates a request passes through. [0] box, [1] name, [2] gates, [3] gate names."""
    g = box(W_API, 1.3, "", CONTROL)
    name = label("API server", 18, CONTROL).move_to(g[0].get_top() + DOWN * 0.22)
    gates = VGroup(*[Rectangle(width=0.09, height=0.42, fill_color=DIM, fill_opacity=0.9, stroke_width=0) for _ in range(3)]).arrange(RIGHT, buff=1.08).move_to(g[0].get_center() + DOWN * 0.1)
    names = VGroup(*[label(s, 16, MUTED).next_to(gt, DOWN, buff=0.06) for s, gt in zip(("authenticate", "authorise", "admit"), gates)])
    g.add(name, gates, names)
    return g


def store(members: int = 3) -> VGroup:
    """etcd: a box that holds record cards, its members as dots on the top edge. [0] box, [1] name, [2] members."""
    g = box(W_API, 3.35, "", NODE)
    g[0].set_stroke(color=TEAL).set_fill(TEAL, 0.05)
    name = label("etcd", 18, TEAL).move_to(g[0].get_top() + DOWN * 0.22).align_to(g[0].get_left() + RIGHT * GAP, LEFT)
    dots = VGroup(*[Dot(radius=0.08, color=TEAL) for _ in range(members)]).arrange(RIGHT, buff=0.14).move_to(g[0].get_top() + DOWN * 0.22).align_to(g[0].get_right() + LEFT * GAP, RIGHT)
    g.add(name, dots)
    return g


def slot_positions(st: VGroup, n: int = 6):
    """Where record cards sit inside the store: two columns, three rows."""
    pitch_x, pitch_y = CARD_W + GAP, CARD_H + GAP_TIGHT                       # two columns, three rows, equal gaps
    x0, y0 = st[0].get_center()[0] - pitch_x / 2, st[0].get_top()[1] - 0.5 - CARD_H / 2
    return [[x0 + pitch_x * (i % 2), y0 - pitch_y * (i // 2), 0] for i in range(n)]


def controller(name: str, legend: bool = False) -> VGroup:
    """A control loop in a box: name on top, the loop as a circular arrow at the right (next to the bus it talks to),
    the three verbs to its left on the legend one. [0] box, [1] name, [2] loop arc, [3] verbs (empty if not legend)."""
    g = box(W_CTRL, H_CTRL, "", CONTROL)
    name = label(name, 16, CONTROL).move_to(g[0].get_top() + DOWN * 0.19).align_to(g[0].get_left() + RIGHT * GAP, LEFT)
    arc = Arc(radius=0.17, start_angle=PI / 2, angle=-1.7 * PI, color=CONTROL, stroke_width=2.4).move_to(g[0].get_center() + DOWN * 0.13 + RIGHT * (W_CTRL / 2 - 0.45))
    arc.add_tip(tip_length=0.11, tip_width=0.11)
    verbs = VGroup(label("observe, compare, act", 15, MUTED).next_to(arc, LEFT, buff=0.25)) if legend else VGroup()
    g.add(name, arc, verbs)
    return g


def node_box(name: str, used: float = 0.3) -> VGroup:
    """A node: box, name top-left, kubelet top-right, three pod slots bottom-left, the memory bar bottom-right with its
    word beside it; everything inside the box with GAP padding.
    [0] box, [1] name, [2] slots, [3] mem frame, [4] mem used, [5] kubelet, [6] mem label."""
    g = box(W_NODE, 1.37, "", NODE)
    left, right = g[0].get_left()[0] + GAP, g[0].get_right()[0] - GAP
    name = label(name, 16, TEAL).move_to([left, g[0].get_top()[1] - 0.22, 0], aligned_edge=LEFT)
    kub = label("kubelet", 16, MUTED).move_to([right, g[0].get_top()[1] - 0.22, 0], aligned_edge=RIGHT)
    slots = VGroup(*[Rectangle(width=0.48, height=0.48, stroke_color=DIM, stroke_width=1.3, fill_opacity=0) for _ in range(3)]).arrange(RIGHT, buff=GAP_TIGHT)
    slots.move_to([left, g[0].get_center()[1] - 0.24, 0], aligned_edge=LEFT)
    frame = Rectangle(width=0.9, height=0.18, stroke_color=DIM, stroke_width=1.3, fill_opacity=0).move_to([right, g[0].get_center()[1] - 0.3, 0], aligned_edge=RIGHT)
    fill = Rectangle(width=max(0.01, 0.9 * used), height=0.16, fill_color=DIM, fill_opacity=0.9, stroke_width=0).align_to(frame, LEFT).set_y(frame.get_y())
    ml = label("memory", 13, MUTED).next_to(frame, LEFT, buff=0.1)
    g.add(name, slots, frame, fill, kub, ml)
    return g


def pod(color: str = ACTUAL, side: float = 0.42) -> Square:
    return Square(side, fill_color=color, fill_opacity=0.92, stroke_width=0)


def _side(x: float) -> str:
    return "L" if x < API_L - 0.1 else ("R" if x > API_R + 0.1 else "M")


def watch(a: Mobject, b: Mobject = None, color: str = CONTROL, legend: bool = False) -> VGroup:
    """The dashed 'watch' relation between a loop or a node and the API server, axis-aligned: a stub from the API
    server's edge to the bus, the bus down to the watcher's row, a spoke into the watcher. Every watcher on a side
    redraws the same stub and bus from the same start, so the dashes coincide. [0] stub, [1] bus, [2] spoke."""
    y = a.get_center()[1]
    if _side(a.get_center()[0]) == "L":
        bus, att, edge, near = LBUS, ATT_L, API_L, a.get_right()[0]
    else:
        bus, att, edge, near = RBUS, ATT_R, API_R, a.get_left()[0]
    kw = dict(color=color, stroke_width=1.8, dash_length=0.1, stroke_opacity=0.7)
    stub = DashedLine([edge, att, 0], [bus, att, 0], **kw)
    vert = DashedLine([bus, att, 0], [bus, y, 0], **kw)
    spoke = DashedLine([bus, y, 0], [near, y, 0], **kw)
    g = VGroup(stub, vert, spoke)
    if legend:
        g.add(label("watch", 15, MUTED).move_to([bus + (0.1 if bus < 0 else -0.1), att + 0.24, 0]))   # above the bus corner, clear of both lines
    return g


def route(a, b) -> list:
    """The points a pulse travels between two things on the stage: straight inside one column; across columns by way
    of the API server, along the stubs, buses and spokes the watch lines drew, so it never crosses a box."""
    P = lambda m: (m.get_center() if hasattr(m, "get_center") else np.array(m, dtype=float))
    A, B = P(a), P(b)
    sa, sb = _side(A[0]), _side(B[0])
    if sa == sb or (sa == "L" and A[1] > ATT_L + 0.3) or (sb == "L" and B[1] > ATT_L + 0.3):   # one column, or kubectl's own row
        return [A, B]
    api_bottom = [X_API, Y_TOP - 0.65, 0]
    pts = [A]
    if sa == "L":
        pts += [[LBUS, A[1], 0], [LBUS, ATT_L, 0], [API_L, ATT_L, 0], [X_API, ATT_L, 0]]
    elif sa == "R":
        pts += [[RBUS, A[1], 0], [RBUS, ATT_R, 0], [API_R, ATT_R, 0], [X_API, ATT_R, 0]]
    else:                                                     # a card or the API server itself: up through the API server
        pts += ([api_bottom] if A[1] < api_bottom[1] else []) + [[X_API, ATT_L if sb == "L" else ATT_R, 0]]
    if sb == "L":
        pts += [[API_L, ATT_L, 0], [LBUS, ATT_L, 0], [LBUS, B[1], 0]]
    elif sb == "R":
        pts += [[API_R, ATT_R, 0], [RBUS, ATT_R, 0], [RBUS, B[1], 0]]
    else:
        pts += [api_bottom] if B[1] < api_bottom[1] else []
    pts.append(B)
    return pts


def pulse(scene, a, b, color=DESIRED, run_time=0.5):
    """A small dot from a to b and gone, along the stage's own lines: the unit of 'observe' and 'act'."""
    pts = route(a, b)
    path = VMobject().set_points_as_corners([np.array(p, dtype=float) for p in pts])
    d = Dot(color=color, radius=0.08).move_to(pts[0])
    scene.add(d)
    scene.play(MoveAlongPath(d, path), run_time=run_time)
    scene.play(FadeOut(d), run_time=0.1)


class Stage:
    """The one picture every scene draws: client, API server with its gates, etcd under it, a column of control loops,
    three nodes at the right, two counters. Scenes build it, add the parts they start from with scene.add(), and
    animate the rest. Nothing moves between scenes, so the audience keeps one mental picture."""

    def __init__(self, node_used=(0.3, 0.55, 0.95), controllers=()):
        self.client = node("kubectl", MUTED, w=1.5, h=0.85, size=18).move_to([X_CLIENT, Y_CLIENT, 0])
        self.api = apiserver().move_to([X_API, Y_TOP, 0])
        self.store = store().move_to([X_API, Y_STORE, 0])
        self.slots = slot_positions(self.store)
        self.nodes = VGroup(*[node_box(f"node {i + 1}", u).move_to([X_NODE, y, 0]) for i, (u, y) in enumerate(zip(node_used, NODE_YS))])
        self.ctrl = {k: controller(n, legend=(i == 0)).move_to([X_CTRL, CTRL_YS[k], 0]) for i, (k, n) in enumerate(controllers)}
        self.watches = {k: watch(c, self.api, legend=(i == 0)) for i, (k, c) in enumerate(self.ctrl.items())}
        self.desired = Counter("pods desired", 3, "", DESIRED, size=22).move_to([COLS[0], Y_COUNTERS, 0], aligned_edge=LEFT)
        self.running = Counter("pods running", 0, "", ACTUAL, size=22).move_to([COLS[1], Y_COUNTERS, 0], aligned_edge=LEFT)
        self.cards = {}

    def add_card(self, key: str, kind: str, detail: str, slot: int, color: str = DESIRED) -> VGroup:
        c = card(kind, detail, color).move_to(self.slots[slot])
        self.cards[key] = c
        return c

    def place_pod(self, node_i: int, slot_i: int, color: str = ACTUAL) -> Square:
        return pod(color).move_to(self.nodes[node_i][2][slot_i])

    def base(self, *extra):
        """Everything a scene starts from: the furniture plus whatever the previous move left."""
        return [self.client, self.api, self.store, self.nodes, self.desired, self.running, *extra]
