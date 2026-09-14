"""This talk's vocabulary on top of the shared library.

  DESIRED (blue)   records: the state you asked for, stored in etcd (Deployment, ReplicaSet, Pod, Service)
  ACTUAL  (yellow) what actually runs: containers on nodes, and the status they report back
  CONTROL (violet) the control plane: API server, controllers, scheduler; every loop that chases the gap
  NODE    (teal)   the machines: nodes, kubelet, kube-proxy
  HOT     (red)    failure, absence, a gap between desired and actual

Shared drawings: a record card, the etcd store, the API server with its three gates, a node with pod slots and
a memory bar, and the reconcile loop.
"""
from lib.palette import *

DESIRED, ACTUAL, CONTROL, NODE, HOT = BLUE, YELLOW, VIOLET, TEAL, RED
set_thread({"desired": DESIRED, "record": DESIRED, "records": DESIRED, "running": ACTUAL, "actual": ACTUAL,
            "controller": CONTROL, "controllers": CONTROL, "scheduler": CONTROL, "node": NODE, "nodes": NODE, "kubelet": NODE})

# fixed furniture of the stage, shared by every scene so the picture never jumps between them
X_CLIENT, X_API, X_CTRL, X_NODE = -5.7, -2.5, 1.2, 4.7
Y_TOP = 1.95
NODE_YS = [1.75, 0.3, -1.15]


def card(kind: str, detail: str = "", color: str = DESIRED, w: float = 1.5) -> VGroup:
    """A record in the store: kind on top, a detail line under it. card[0] frame, card[1] kind, card[2] detail."""
    r = RoundedRectangle(corner_radius=0.08, width=w, height=0.52, stroke_color=color, stroke_width=1.8, fill_color=color, fill_opacity=0.14)
    g = VGroup(r, label(kind, 13, TEXT).move_to(r.get_top() + DOWN * 0.15))
    g.add(label(detail if detail else " ", 12, MUTED).move_to(r.get_bottom() + UP * 0.14))
    return g


def set_detail(scene, c: VGroup, text: str, color: str = MUTED, run_time: float = 0.3):
    """Replace a card's detail line (fade, never become: glyph counts differ)."""
    new = label(text, 12, color).move_to(c[2])
    scene.play(FadeOut(c[2]), FadeIn(new), run_time=run_time)
    c.remove(c[2]); c.add(new)
    return new


def apiserver() -> VGroup:
    """The API server: a box with three thin gates a request passes through. [0] box, [1] name, [2] gates (3), [3] gate labels."""
    g = box(3.2, 1.0, "", CONTROL)
    name = label("API server", 16, CONTROL).move_to(g[0].get_top() + DOWN * 0.17)
    gates = VGroup(*[Rectangle(width=0.08, height=0.42, fill_color=DIM, fill_opacity=0.9, stroke_width=0) for _ in range(3)]).arrange(RIGHT, buff=1.0).move_to(g[0].get_center() + DOWN * 0.12)
    names = VGroup(*[label(s, 11, MUTED).next_to(gt, DOWN, buff=0.05) for s, gt in zip(("authenticate", "authorise", "admit"), gates)])
    g.add(name, gates, names)
    return g


def store(members: int = 3) -> VGroup:
    """etcd: a box that holds record cards, with its members as dots on the top edge. [0] box, [1] name, [2] members."""
    g = box(3.5, 2.5, "", NODE)
    g[0].set_stroke(color=TEAL).set_fill(TEAL, 0.05)
    name = label("etcd", 16, TEAL).move_to(g[0].get_top() + DOWN * 0.17 + LEFT * 1.3)
    dots = VGroup(*[Dot(radius=0.07, color=TEAL) for _ in range(members)]).arrange(RIGHT, buff=0.12).move_to(g[0].get_top() + DOWN * 0.17 + RIGHT * 1.15)
    g.add(name, dots)
    return g


def slot_positions(st: VGroup, n: int = 6):
    """Where record cards sit inside the store: two columns, three rows."""
    x0, y0 = st[0].get_center()[0] - 0.82, st[0].get_top()[1] - 0.72
    return [[x0 + 1.64 * (i % 2), y0 - 0.62 * (i // 2), 0] for i in range(n)]


def controller(name: str, w: float = 2.7) -> VGroup:
    """A control loop in a box: name on top, the loop drawn as a circular arrow with 'observe, compare, act'.
    [0] box, [1] name, [2] loop arc, [3] loop labels."""
    g = box(w, 1.0, "", CONTROL)
    name = label(name, 15, CONTROL).move_to(g[0].get_top() + DOWN * 0.17)
    arc = Arc(radius=0.22, start_angle=PI / 2, angle=-1.7 * PI, color=CONTROL, stroke_width=2.2).move_to(g[0].get_center() + DOWN * 0.12 + LEFT * 0.95)
    arc.add_tip(tip_length=0.12, tip_width=0.12)
    words = label("observe   compare   act", 11, MUTED).next_to(arc, RIGHT, buff=0.18)
    g.add(name, arc, words)
    return g


def node_box(name: str, used: float = 0.3, w: float = 2.7, h: float = 1.15) -> VGroup:
    """A node: box, name, three pod slots, a memory bar with a used portion, the kubelet label.
    [0] box, [1] name, [2] slots, [3] mem frame, [4] mem used, [5] kubelet, [6] mem label."""
    g = box(w, h, "", NODE)
    name = label(name, 14, TEAL).move_to(g[0].get_corner(UL) + RIGHT * 0.5 + DOWN * 0.17)
    slots = VGroup(*[Rectangle(width=0.36, height=0.36, stroke_color=DIM, stroke_width=1.2, fill_opacity=0) for _ in range(3)]).arrange(RIGHT, buff=0.1)
    slots.move_to(g[0].get_center() + DOWN * 0.15 + LEFT * 0.55)
    frame = Rectangle(width=0.8, height=0.14, stroke_color=DIM, stroke_width=1.2, fill_opacity=0).move_to(g[0].get_center() + RIGHT * 0.75 + DOWN * 0.02)
    fill = Rectangle(width=max(0.01, 0.8 * used), height=0.12, fill_color=DIM, fill_opacity=0.9, stroke_width=0).align_to(frame, LEFT).set_y(frame.get_y())
    kub = label("kubelet", 11, MUTED).move_to(g[0].get_corner(UR) + LEFT * 0.45 + DOWN * 0.17)
    ml = label("memory", 11, MUTED).next_to(frame, DOWN, buff=0.04)
    g.add(name, slots, frame, fill, kub, ml)
    return g


def pod(color: str = ACTUAL, side: float = 0.3) -> Square:
    return Square(side, fill_color=color, fill_opacity=0.92, stroke_width=0)


def watch(a: Mobject, b: Mobject, color: str = CONTROL) -> VGroup:
    """A dashed 'watch' line from a component to the API server: every component talks only to the API server."""
    ln = DashedLine(a.get_boundary_point(b.get_center() - a.get_center()), b.get_boundary_point(a.get_center() - b.get_center()),
                    color=color, stroke_width=1.6, dash_length=0.1, stroke_opacity=0.7)
    return VGroup(ln, label("watch", 11, MUTED).move_to(ln.get_center() + UP * 0.14))


class Stage:
    """The one picture every scene draws: client, API server with its gates, etcd under it, a column of control loops,
    three nodes at the right, two counters at the bottom. Scenes build it, add the parts they start from with
    scene.add(), and animate the rest. Nothing moves between scenes, so the audience keeps one mental picture."""

    def __init__(self, node_used=(0.3, 0.55, 0.95), controllers=()):
        self.client = node("kubectl", MUTED, w=1.6, h=0.8, size=17).move_to([X_CLIENT, Y_TOP, 0])
        self.api = apiserver().move_to([X_API, Y_TOP, 0])
        self.store = store().move_to([X_API, -0.35, 0])
        self.slots = slot_positions(self.store)
        self.nodes = VGroup(*[node_box(f"node {i + 1}", u).move_to([X_NODE, y, 0]) for i, (u, y) in enumerate(zip(node_used, NODE_YS))])
        ys = {"deploy": 1.95, "rs": 0.6, "sched": -0.75, "extra": -2.1}
        self.ctrl = {k: controller(n).move_to([X_CTRL, ys[k], 0]) for k, n in controllers}
        self.watches = {k: watch(c, self.api) for k, c in self.ctrl.items()}
        self.desired = Counter("pods desired", 3, "", DESIRED, size=22).move_to([-6.4, -2.55, 0], aligned_edge=LEFT)
        self.running = Counter("pods running", 0, "", ACTUAL, size=22).move_to([-4.3, -2.55, 0], aligned_edge=LEFT)
        self.cards = {}

    def add_card(self, key: str, kind: str, detail: str, slot: int, color: str = DESIRED) -> VGroup:
        c = card(kind, detail, color).move_to(self.slots[slot])
        self.cards[key] = c
        return c

    def place_pod(self, node_i: int, slot_i: int, color: str = ACTUAL) -> Square:
        return pod(color).move_to(self.nodes[node_i][2][slot_i])
