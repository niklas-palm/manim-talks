"""This talk's vocabulary on top of the shared library.

  DESIRED (blue)   records: the state you asked for, stored in etcd (Deployment, ReplicaSet, Pod, Service)
  ACTUAL  (yellow) what actually runs: containers on nodes, and the status they report back
  CONTROL (violet) the control plane: API server, controllers, scheduler; every loop that chases the gap
  NODE    (teal)   the machines: nodes, kubelet, kube-proxy; and etcd's members
  HOT     (red)    failure, absence, a gap between desired and actual

Text sizes: 15 and up for anything inside a box, 13 only for units. Legend-like words appear once ("watch" on the
first line, "observe, compare, act" when the first loop is opened under the zoom, "kube-proxy" on the first node); the
others are recognised by shape and colour. Sentences go in the notes.
"""
from lib.palette import *

DESIRED, ACTUAL, CONTROL, NODE, HOT = A1, A2, A3, A4, ALERT
set_thread({"desired": DESIRED, "record": DESIRED, "records": DESIRED, "running": ACTUAL, "actual": ACTUAL,
            "controller": CONTROL, "controllers": CONTROL, "scheduler": CONTROL, "node": NODE, "nodes": NODE, "kubelet": NODE})

# The stage is three bands. The API server is a bar across the whole width in the middle: the one door everything
# passes through. Above it, in one row, kubectl and the control loops; below it, etcd at the left, the three nodes at
# the right, and the two counters in the gap between them. Every relation is one short vertical dashed line between
# facing edges (a loop's bottom edge to the bar's top, a node's top edge to the bar's bottom), so nothing is skewed and
# nothing crosses anything. A record travels the same way: down from kubectl into the bar, then down into the store.
X_L, X_R = -6.4, 6.4                                 # the stage's outer edges, on the outer column lines
H_ROW, H_API, H_NODE = 1.1, 0.8, 2.0                 # the three bands: 2.6..1.5, 1.0..0.2, -0.3..-2.3, with GAP_WIDE between
Y_ROW, Y_API, Y_NODE = 2.05, 0.6, -1.3               # their centres; the bottom band is centred on the -1.3 row line
W_CLIENT, W_CTRL, W_STORE, W_NODE = 1.3, 2.2, 5.6, 1.7
X_CLIENT = X_L + W_CLIENT / 2
CTRL_X0 = X_CLIENT + W_CLIENT / 2 + GAP_WIDE + W_CTRL / 2
CTRL_XS = {k: CTRL_X0 + i * (W_CTRL + GAP) for i, k in enumerate(("deploy", "rs", "sched", "extra"))}   # -3.5, -1.05, 1.4, 3.85
X_STORE = X_L + W_STORE / 2                          # etcd: x -6.4 .. -0.8
NODE_XS = [X_R - W_NODE / 2 - i * (W_NODE + GAP) for i in (2, 1, 0)]                                   # x 0.8 .. 6.4
X_NODES_L = NODE_XS[0] - W_NODE / 2
X_COUNTERS = X_STORE + W_STORE / 2 + GAP              # the two counters, left-aligned in the gap between store and nodes
Y_DESIRED, Y_RUNNING = -0.95, -1.65
X_GATES = [-3.9, -2.55, -1.2]                        # the three gates inside the bar, right of its name
Y_LABELS = -2.75                                     # one row for labels under the bottom band (leases, kube-proxy, limits)
CARD_W, CARD_H = 1.6, 0.66


def card(kind: str, detail: str = "", color: str = DESIRED) -> VGroup:
    """A record in the store: its kind, and one status line. card[0] frame, card[1] kind, card[2] status."""
    r = RoundedRectangle(corner_radius=rad(0.53), width=CARD_W, height=CARD_H, stroke_color=color, stroke_width=sw(0.8), fill_color=color, fill_opacity=FILL * 1.4)
    g = VGroup(r, label(kind, 16, TEXT).move_to(r.get_top() + DOWN * 0.19))
    g.add(label(detail if detail else " ", 15, MUTED).move_to(r.get_bottom() + UP * 0.19))
    return g


def set_detail(scene, c: VGroup, text: str, color: str = MUTED, run_time: float = 0.3):
    """Replace a card's status line (fade, never become: glyph counts differ)."""
    new = label(text, 15, color).move_to(c[2])
    scene.play(FadeOut(c[2]), FadeIn(new), run_time=run_time)
    c.remove(c[2]); c.add(new)
    return new


def apiserver() -> VGroup:
    """The API server: a bar across the stage, its name at the left end, three gates a request passes through beside
    it. [0] box, [1] name, [2] gates, [3] gate names."""
    g = box(X_R - X_L, H_API, "", CONTROL)
    name = label("API server", 18, CONTROL).move_to([X_L + GAP, Y_API, 0], aligned_edge=LEFT)
    gates = VGroup(*[Rectangle(width=0.09, height=0.36, fill_color=DIM, fill_opacity=SOLID, stroke_width=0).move_to([x, Y_API + 0.1, 0]) for x in X_GATES])
    names = VGroup(*[label(s, 16, MUTED).next_to(gt, DOWN, buff=0.05) for s, gt in zip(("authenticate", "authorise", "admit"), gates)])
    g.move_to([0, Y_API, 0])
    g.add(name, gates, names)
    return g


def store(members: int = 3) -> VGroup:
    """etcd: a box that holds record cards, its members as dots in its top-right corner. [0] box, [1] name, [2] members."""
    g = box(W_STORE, H_NODE, "", NODE)
    g[0].set_stroke(color=TEAL).set_fill(TEAL, 0.05)
    name = label("etcd", 18, TEAL).move_to(g[0].get_top() + DOWN * 0.2).align_to(g[0].get_left() + RIGHT * GAP, LEFT)
    dots = VGroup(*[Dot(radius=0.08, color=TEAL) for _ in range(members)]).arrange(RIGHT, buff=0.14).move_to(g[0].get_top() + DOWN * 0.2).align_to(g[0].get_right() + LEFT * GAP, RIGHT)
    g.add(name, dots)
    return g


def slot_positions(st: VGroup, n: int = 6):
    """Where record cards sit inside the store: three columns, two rows, under the name row."""
    pitch_x, pitch_y = CARD_W + GAP, CARD_H + GAP_TIGHT
    x0, y0 = st[0].get_left()[0] + 0.15 + CARD_W / 2, st[0].get_top()[1] - 0.4 - CARD_H / 2
    return [[x0 + pitch_x * (i % 3), y0 - pitch_y * (i // 3), 0] for i in range(n)]


def controller(name: str) -> VGroup:
    """A control loop in a box: its name on two lines at the left, the loop as a circular arrow at the right, both
    inside the box with padding. [0] box, [1] name, [2] loop arc."""
    g = box(W_CTRL, H_ROW, "", CONTROL)
    nm = label(name.replace(" ", "\n", 1), 15, CONTROL).move_to(g[0].get_left() + RIGHT * 0.15, aligned_edge=LEFT)
    arc = Arc(radius=0.17, start_angle=PI / 2, angle=-1.7 * PI, color=CONTROL, stroke_width=sw(0.96)).move_to(g[0].get_right() + LEFT * 0.34)
    arc.add_tip(tip_length=0.11, tip_width=0.11)
    g.add(nm, arc)
    return g


def node_box(name: str, used: float = 0.3) -> VGroup:
    """A node: name top-left, kubelet top-right, three pod slots in a row, room under them for what the kubelet does,
    then the memory bar with its word above it; everything inside the box with padding.
    [0] box, [1] name, [2] slots, [3] mem frame, [4] mem used, [5] kubelet, [6] mem label."""
    g = box(W_NODE, H_NODE, "", NODE)
    left, right, top = g[0].get_left()[0] + 0.15, g[0].get_right()[0] - 0.15, g[0].get_top()[1]
    name = label(name, 15, TEAL).move_to([left, top - 0.24, 0], aligned_edge=LEFT)
    kub = label("kubelet", 15, MUTED).move_to([right, top - 0.24, 0], aligned_edge=RIGHT)
    slots = VGroup(*[Rectangle(width=0.38, height=0.38, stroke_color=DIM, stroke_width=sw(0.52), fill_opacity=0) for _ in range(3)]).arrange(RIGHT, buff=0.13)
    slots.move_to([left, top - 0.64, 0], aligned_edge=LEFT)
    ml = label("memory", 13, MUTED).move_to([left, top - 1.26, 0], aligned_edge=LEFT)
    frame = Rectangle(width=right - left - 0.05, height=0.16, stroke_color=DIM, stroke_width=sw(0.52), fill_opacity=0).move_to([left, top - 1.45, 0], aligned_edge=LEFT)
    fill = Rectangle(width=max(0.01, frame.width * used), height=0.14, fill_color=DIM, fill_opacity=SOLID, stroke_width=0).align_to(frame, LEFT).set_y(frame.get_y())
    g.add(name, slots, frame, fill, kub, ml)
    return g


def pod(color: str = ACTUAL, side: float = 0.34) -> Square:
    return Square(side, fill_color=color, fill_opacity=SOLID, stroke_width=0)


def watch(a: Mobject, color: str = CONTROL, legend: bool = False) -> VGroup:
    """The dashed 'watch' relation between a loop or a node and the API server: one vertical line from the watcher's
    facing edge to the bar's facing edge, at the watcher's centre. [0] line, [1] the word 'watch' on the legend one."""
    x = a.get_center()[0]
    above = a.get_center()[1] > Y_API
    y0, y1 = (a.get_bottom()[1], Y_API + H_API / 2) if above else (a.get_top()[1], Y_API - H_API / 2)
    ln = DashedLine([x, y0, 0], [x, y1, 0], color=color, stroke_width=sw(0.72), dash_length=0.1, stroke_opacity=0.7)
    g = VGroup(ln)
    if legend:
        g.add(label("watch", 15, MUTED).move_to([x + 0.1, (y0 + y1) / 2, 0], aligned_edge=LEFT))
    return g


def door(m) -> np.ndarray:
    """The point inside the API server straight above or below a thing: where its requests enter the bar."""
    x = m.get_center()[0] if hasattr(m, "get_center") else m[0]
    return np.array([x, Y_API, 0])


def route(a, b) -> list:
    """The points a pulse travels between two things on the stage: straight into the bar, along it, straight out to the
    other thing; the API server is on the way of every exchange, and the path never crosses a box."""
    P = lambda m: (m.get_center() if hasattr(m, "get_center") else np.array(m, dtype=float))
    A, B = P(a), P(b)
    in_bar = lambda p: abs(p[1] - Y_API) <= H_API / 2
    if in_bar(A):                                    # from the API server itself: straight out to the thing
        return [door(B), B]
    if in_bar(B):                                    # to the API server itself: straight in
        return [A, door(A)]
    return [A, door(A), door(B), B]


def pulse(scene, a, b, color=DESIRED, run_time=0.5):
    """A small dot from a to b and gone, by way of the API server: the unit of 'observe' and 'act'."""
    pts = route(a, b)
    path = VMobject().set_points_as_corners([np.array(p, dtype=float) for p in pts])
    d = Dot(color=color, radius=0.08).move_to(pts[0])
    scene.add(d)
    scene.play(MoveAlongPath(d, path), run_time=run_time)
    scene.play(FadeOut(d), run_time=0.1)


def mem(node_g: VGroup, used: float):
    """The animation that sets a node's memory bar to a fraction of its frame."""
    return node_g[4].animate.stretch_to_fit_width(node_g[3].width * used).align_to(node_g[3], LEFT)


def beat(scene, nodes, run_time=0.5):
    """Every kubelet renews its lease at once: a teal dot from each kubelet straight up into the bar."""
    dots = [Dot(color=TEAL, radius=0.07).move_to(n[5].get_center()) for n in nodes]
    scene.add(*dots)
    scene.play(*[d.animate.move_to(door(d)) for d in dots], run_time=run_time)
    scene.play(*[FadeOut(d) for d in dots], run_time=0.12)


class Stage:
    """The one picture every scene draws: kubectl and the loops above the API server, etcd and the nodes below it, the
    two counters between store and machines. Scenes build it, add the parts they start from with scene.add(), and
    animate the rest. Nothing moves between scenes, so the audience keeps one mental picture."""

    def __init__(self, node_used=(0.3, 0.55, 0.95), controllers=()):
        self.client = node("kubectl", MUTED, w=W_CLIENT, h=H_ROW, size=18).move_to([X_CLIENT, Y_ROW, 0])
        self.api = apiserver()
        self.store = store().move_to([X_STORE, Y_NODE, 0])
        self.slots = slot_positions(self.store)
        self.nodes = VGroup(*[node_box(f"node {i + 1}", u).move_to([x, Y_NODE, 0]) for i, (u, x) in enumerate(zip(node_used, NODE_XS))])
        self.ctrl = {k: controller(n).move_to([CTRL_XS[k], Y_ROW, 0]) for k, n in controllers}
        self.watches = {k: watch(c, legend=(i == 0)) for i, (k, c) in enumerate(self.ctrl.items())}
        self.desired = Counter("pods desired", 3, "", DESIRED, size=22).move_to([X_COUNTERS, Y_DESIRED, 0], aligned_edge=LEFT)
        self.running = Counter("pods running", 0, "", ACTUAL, size=22).move_to([X_COUNTERS, Y_RUNNING, 0], aligned_edge=LEFT)
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
