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

# fixed furniture of the stage, shared by every scene so the picture never jumps between them
X_CLIENT, X_API, X_CTRL, X_NODE = -5.95, -2.6, 1.35, 4.95
Y_TOP = 1.95
NODE_YS = [1.75, 0.3, -1.15]
CTRL_YS = {"deploy": 1.95, "rs": 0.7, "sched": -0.55, "extra": -1.8}
CARD_W, CARD_H = 1.75, 0.62


def card(kind: str, detail: str = "", color: str = DESIRED) -> VGroup:
    """A record in the store: its kind, and one status line. card[0] frame, card[1] kind, card[2] status."""
    r = RoundedRectangle(corner_radius=0.08, width=CARD_W, height=CARD_H, stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=0.14)
    g = VGroup(r, label(kind, 15, TEXT).move_to(r.get_top() + DOWN * 0.19))
    g.add(label(detail if detail else " ", 14, MUTED).move_to(r.get_bottom() + UP * 0.17))
    return g


def set_detail(scene, c: VGroup, text: str, color: str = MUTED, run_time: float = 0.3):
    """Replace a card's status line (fade, never become: glyph counts differ)."""
    new = label(text, 14, color).move_to(c[2])
    scene.play(FadeOut(c[2]), FadeIn(new), run_time=run_time)
    c.remove(c[2]); c.add(new)
    return new


def apiserver() -> VGroup:
    """The API server: a box with three gates a request passes through. [0] box, [1] name, [2] gates, [3] gate names."""
    g = box(3.8, 1.2, "", CONTROL)
    name = label("API server", 18, CONTROL).move_to(g[0].get_top() + DOWN * 0.2)
    gates = VGroup(*[Rectangle(width=0.09, height=0.42, fill_color=DIM, fill_opacity=0.9, stroke_width=0) for _ in range(3)]).arrange(RIGHT, buff=1.15).move_to(g[0].get_center() + DOWN * 0.12)
    names = VGroup(*[label(s, 15, MUTED).next_to(gt, DOWN, buff=0.05) for s, gt in zip(("authenticate", "authorise", "admit"), gates)])
    g.add(name, gates, names)
    return g


def store(members: int = 3) -> VGroup:
    """etcd: a box that holds record cards, its members as dots on the top edge. [0] box, [1] name, [2] members."""
    g = box(3.8, 2.7, "", NODE)
    g[0].set_stroke(color=TEAL).set_fill(TEAL, 0.05)
    name = label("etcd", 18, TEAL).move_to(g[0].get_top() + DOWN * 0.2 + LEFT * 1.45)
    dots = VGroup(*[Dot(radius=0.08, color=TEAL) for _ in range(members)]).arrange(RIGHT, buff=0.14).move_to(g[0].get_top() + DOWN * 0.2 + RIGHT * 1.3)
    g.add(name, dots)
    return g


def slot_positions(st: VGroup, n: int = 6):
    """Where record cards sit inside the store: two columns, three rows."""
    x0, y0 = st[0].get_center()[0] - 0.93, st[0].get_top()[1] - 0.78
    return [[x0 + 1.86 * (i % 2), y0 - 0.7 * (i // 2), 0] for i in range(n)]


def controller(name: str, legend: bool = False) -> VGroup:
    """A control loop in a box: name on top, the loop as a circular arrow; the three verbs only on the legend one.
    [0] box, [1] name, [2] loop arc, [3] verbs (empty group if not legend)."""
    g = box(3.0, 1.05, "", CONTROL)
    name = label(name, 16, CONTROL).move_to(g[0].get_top() + DOWN * 0.2)
    arc = Arc(radius=0.24, start_angle=PI / 2, angle=-1.7 * PI, color=CONTROL, stroke_width=2.4).move_to(g[0].get_center() + DOWN * 0.15 + LEFT * (1.0 if legend else 0.0))
    arc.add_tip(tip_length=0.13, tip_width=0.13)
    verbs = VGroup(label("observe, compare, act", 15, MUTED).next_to(arc, RIGHT, buff=0.22)) if legend else VGroup()
    g.add(name, arc, verbs)
    return g


def node_box(name: str, used: float = 0.3) -> VGroup:
    """A node: box, name, three pod slots, a memory bar with its used portion, the kubelet.
    [0] box, [1] name, [2] slots, [3] mem frame, [4] mem used, [5] kubelet, [6] mem label."""
    g = box(3.2, 1.25, "", NODE)
    name = label(name, 15, TEAL).move_to(g[0].get_corner(UL) + RIGHT * 0.55 + DOWN * 0.2)
    slots = VGroup(*[Rectangle(width=0.42, height=0.42, stroke_color=DIM, stroke_width=1.3, fill_opacity=0) for _ in range(3)]).arrange(RIGHT, buff=0.1)
    slots.move_to(g[0].get_center() + DOWN * 0.17 + LEFT * 0.7)
    frame = Rectangle(width=1.0, height=0.16, stroke_color=DIM, stroke_width=1.3, fill_opacity=0).move_to(g[0].get_center() + RIGHT * 0.85 + DOWN * 0.02)
    fill = Rectangle(width=max(0.01, 1.0 * used), height=0.14, fill_color=DIM, fill_opacity=0.9, stroke_width=0).align_to(frame, LEFT).set_y(frame.get_y())
    kub = label("kubelet", 15, MUTED).move_to(g[0].get_corner(UR) + LEFT * 0.55 + DOWN * 0.2)
    ml = label("memory", 13, MUTED).next_to(frame, DOWN, buff=0.05)
    g.add(name, slots, frame, fill, kub, ml)
    return g


def pod(color: str = ACTUAL, side: float = 0.36) -> Square:
    return Square(side, fill_color=color, fill_opacity=0.92, stroke_width=0)


def watch(a: Mobject, b: Mobject, color: str = CONTROL, legend: bool = False) -> VGroup:
    """A dashed 'watch' line from a component to the API server. The word appears only on the legend line."""
    ln = DashedLine(a.get_boundary_point(b.get_center() - a.get_center()), b.get_boundary_point(a.get_center() - b.get_center()),
                    color=color, stroke_width=1.8, dash_length=0.1, stroke_opacity=0.7)
    g = VGroup(ln)
    if legend:
        g.add(label("watch", 15, MUTED).move_to(ln.get_center() + UP * 0.18))
    return g


def pulse(scene, a, b, color=DESIRED, run_time=0.5):
    """A small dot from a to b and gone: the unit of 'observe' and 'act'."""
    d = Dot(color=color, radius=0.08).move_to(a.get_center() if hasattr(a, "get_center") else a)
    scene.add(d)
    scene.play(d.animate.move_to(b.get_center() if hasattr(b, "get_center") else b), run_time=run_time)
    scene.play(FadeOut(d), run_time=0.1)


class Stage:
    """The one picture every scene draws: client, API server with its gates, etcd under it, a column of control loops,
    three nodes at the right, two counters. Scenes build it, add the parts they start from with scene.add(), and
    animate the rest. Nothing moves between scenes, so the audience keeps one mental picture."""

    def __init__(self, node_used=(0.3, 0.55, 0.95), controllers=()):
        self.client = node("kubectl", MUTED, w=1.6, h=0.85, size=18).move_to([X_CLIENT, Y_TOP, 0])
        self.api = apiserver().move_to([X_API, Y_TOP, 0])
        self.store = store().move_to([X_API, -0.25, 0])
        self.slots = slot_positions(self.store)
        self.nodes = VGroup(*[node_box(f"node {i + 1}", u).move_to([X_NODE, y, 0]) for i, (u, y) in enumerate(zip(node_used, NODE_YS))])
        self.ctrl = {k: controller(n, legend=(i == 0)).move_to([X_CTRL, CTRL_YS[k], 0]) for i, (k, n) in enumerate(controllers)}
        self.watches = {k: watch(c, self.api, legend=(i == 0)) for i, (k, c) in enumerate(self.ctrl.items())}
        self.desired = Counter("pods desired", 3, "", DESIRED, size=22).move_to([-6.7, -2.65, 0], aligned_edge=LEFT)
        self.running = Counter("pods running", 0, "", ACTUAL, size=22).move_to([-4.8, -2.65, 0], aligned_edge=LEFT)
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
