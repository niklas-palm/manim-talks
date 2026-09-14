"""DNS: how a name becomes an address. The talk's vocabulary on top of the shared library.

  NAME (blue)        a name, a question about a name, the client that asks
  ADDRESS (yellow)   an address, the answer that ends a lookup
  ZONE (violet)      a zone and the servers that are authoritative for it; a pointer to who to ask next (NS)
  REMEMBERED (teal)  a record held in a cache, with the time it may still be kept
  HOT (red)          a miss, an expired record, a name that does not exist

One picture for the whole talk: the client on the left, the recursive resolver with its cache in the middle, the
tree of zones on the right. Questions travel right, answers travel left; a violet answer is a pointer, a yellow one is
the address.
"""
from lib.palette import *

NAME, ADDRESS, ZONE, REMEMBERED, HOT = BLUE, YELLOW, VIOLET, TEAL, RED
set_thread({"name": NAME, "names": NAME, "address": ADDRESS, "addresses": ADDRESS, "zone": ZONE, "zones": ZONE,
            "pointer": ZONE, "pointers": ZONE, "cache": REMEMBERED, "cached": REMEMBERED, "caches": REMEMBERED, "ttl": REMEMBERED})

# Positions shared by every scene that shows the walk, so the picture is the same one growing.
X_CLIENT, X_RESOLVER, X_TREE = -5.6, -2.2, 3.7
Y_ROOT, Y_TLD, Y_AUTH = 1.9, 0.45, -1.0


def record(owner: str, rtype: str, value: str, ttl: str = "", color: str = ZONE, width: float = 4.8) -> VGroup:
    """One resource record as a row: owner, TYPE, value, and the TTL at the right. The type is the colour of what the
    record gives you: a pointer (NS, violet) or an address (A, yellow). rec[0] is the background strip."""
    bg = Rectangle(width=width, height=0.3, fill_color=color, fill_opacity=0.10, stroke_width=0)
    parts = VGroup(label(owner, 13, TEXT), label(rtype, 13, color), label(value, 13, TEXT if rtype != "A" else ADDRESS))
    parts[0].move_to(bg.get_left() + RIGHT * 0.08, aligned_edge=LEFT)
    parts[1].move_to(bg.get_left() + RIGHT * (width * 0.36), aligned_edge=LEFT)
    parts[2].move_to(bg.get_left() + RIGHT * (width * 0.45), aligned_edge=LEFT)
    g = VGroup(bg, *parts)
    if ttl:
        g.add(label(ttl, 12, REMEMBERED).move_to(bg.get_right() + LEFT * 0.08, aligned_edge=RIGHT))
    return g


def zone_box(name: str, sub: str, y: float, w: float = 5.6, h: float = 1.15, x: float = X_TREE) -> VGroup:
    """A zone: who is authoritative for one level of the name, with room for the records it holds. zb[0] box,
    zb[1] name, zb[2] subtitle."""
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=ZONE, stroke_width=2.2, fill_color=ZONE, fill_opacity=0.08).move_to([x, y, 0])
    n = label(name, 18, ZONE).move_to(r.get_corner(UL) + RIGHT * 0.15 + DOWN * 0.2, aligned_edge=UL)
    s = label(sub, 12, MUTED).next_to(n, DOWN, buff=0.05).align_to(n, LEFT)
    return VGroup(r, n, s)


def resolver_box(y: float = -0.1) -> VGroup:
    """The recursive resolver: a box with a cache area inside. rb[0] box, rb[1] name, rb[2] the 'cache' label; rows
    are added by the scene under rb[2]."""
    r = RoundedRectangle(corner_radius=0.15, width=3.6, height=4.2, stroke_color=ZONE, stroke_width=2.5, fill_color=ZONE, fill_opacity=0.06).move_to([X_RESOLVER, y, 0])
    n = label("recursive resolver", 18, TEXT).next_to(r.get_top(), DOWN, buff=0.15)
    c = label("cache", 13, REMEMBERED).next_to(n, DOWN, buff=0.2).align_to(r, LEFT).shift(RIGHT * 0.2)
    return VGroup(r, n, c)


def client_box(y: float = 0.3) -> VGroup:
    return node("your laptop", NAME, w=2.0, h=0.9, sub="app + stub resolver").move_to([X_CLIENT, y, 0])


def question(scene, a: Mobject, b: Mobject, text: str = "", run_time: float = 0.5):
    """A question travels from a to b: a blue dot with the name beside it."""
    d = Dot(color=NAME, radius=0.1).move_to(a.get_right() if a.get_x() < b.get_x() else a.get_left())
    lab = label(text, 12, NAME).next_to(d, UP, buff=0.06) if text else VGroup()
    g = VGroup(d, lab)
    scene.add(g)
    target = b.get_left() if a.get_x() < b.get_x() else b.get_right()
    scene.play(g.animate.move_to(target + (UP * 0.12 if text else 0)), run_time=run_time)
    scene.play(FadeOut(g, run_time=0.15))


def answer(scene, a: Mobject, b: Mobject, color: str, text: str = "", run_time: float = 0.5):
    """An answer travels back: violet for a pointer to who to ask next, yellow for the address, red for 'no'."""
    d = Dot(color=color, radius=0.1).move_to(a.get_left() if a.get_x() > b.get_x() else a.get_right())
    lab = label(text, 12, color).next_to(d, DOWN, buff=0.06) if text else VGroup()
    g = VGroup(d, lab)
    scene.add(g)
    target = b.get_right() if a.get_x() > b.get_x() else b.get_left()
    scene.play(g.animate.move_to(target + (DOWN * 0.12 if text else 0)), run_time=run_time)
    scene.play(FadeOut(g, run_time=0.15))


def cache_row(rec: VGroup, slot_y: float) -> VGroup:
    """Place a copy of a record inside the resolver's cache, tinted as remembered."""
    r = rec.copy().scale(0.68)
    r[0].set_fill(REMEMBERED, 0.14)
    r.move_to([X_RESOLVER, slot_y, 0])
    return r


def fuse(row: VGroup, fraction: float = 1.0) -> Rectangle:
    """The time a cached row may still be kept, as a thin teal bar under it; shrink it to show time passing."""
    w = row[0].width * fraction
    return Rectangle(width=max(0.01, w), height=0.035, fill_color=REMEMBERED, fill_opacity=0.9, stroke_width=0).move_to(row[0].get_bottom() + DOWN * 0.03, aligned_edge=LEFT).align_to(row[0], LEFT)
