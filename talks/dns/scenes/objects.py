"""DNS: how a name becomes an address. The talk's vocabulary on top of the shared library.

  NAME (blue)        a name, a question about a name, the client that asks
  ADDRESS (yellow)   an address, the answer that ends a lookup
  ZONE (violet)      a zone and the servers that are authoritative for it; a pointer to who to ask next (NS)
  REMEMBERED (teal)  a record held in a cache, and the bar under it: the time it may still be kept
  HOT (red)          a miss, an expired record, a name that does not exist

One picture for the whole talk: the client on the left, the recursive resolver with its cache in the middle, the
tree of zones on the right. Questions travel right, answers travel left; a violet answer is a pointer, a yellow one is
the address. Sizes are for a projector: rows at 16 pt, boxes that span the frame.
"""
from lib.palette import *

NAME, ADDRESS, ZONE, REMEMBERED, HOT = BLUE, YELLOW, VIOLET, TEAL, RED
set_thread({"name": NAME, "names": NAME, "address": ADDRESS, "addresses": ADDRESS, "zone": ZONE, "zones": ZONE,
            "pointer": ZONE, "pointers": ZONE, "remembers": REMEMBERED, "cache": REMEMBERED, "cached": REMEMBERED,
            "caches": REMEMBERED, "ttl": REMEMBERED})

# The grid every scene shares, so the picture is the same one growing. Three columns inside the margins (x -6.4 to 6.4):
# the client [-6.4, -4.4], the resolver [-4.1, 0.5], the tree [0.8, 6.4]; GAP between neighbours. The three zones stack
# from CONTENT_TOP with GAP between them; the resolver spans the same height.
X_CLIENT, W_CLIENT = -5.4, 2.0
X_RESOLVER, W_RESOLVER, H_RESOLVER = -1.8, 4.6, 4.55
X_TREE, W_TREE, H_ZONE = 3.6, 5.6, 1.35
Y_ROOT = CONTENT_TOP - H_ZONE / 2
Y_TLD = Y_ROOT - H_ZONE - GAP
Y_AUTH = Y_TLD - H_ZONE - GAP
Y_RESOLVER = CONTENT_TOP - H_RESOLVER / 2
W_RECORD, W_CACHE_ROW = 5.3, 4.25
ROW_H = 0.42
COL_TYPE, COL_VALUE = 0.38, 0.45   # record columns as fractions of the row width, the same in every box


def record(owner: str, rtype: str, value: str, ttl: str = "", color: str = ZONE, width: float = W_RECORD, size: float = 15) -> VGroup:
    """One resource record as a row: owner, TYPE, value, and the TTL at the right. The type is the colour of what the
    record gives you: a pointer (NS, violet) or an address (A, yellow). rec[0] is the background strip; rec[1..3] the
    owner, type and value; rec[4] the TTL text when given."""
    bg = Rectangle(width=width, height=ROW_H, fill_color=color, fill_opacity=0.12, stroke_width=0)
    parts = VGroup(label(owner, size, TEXT), label(rtype, size, color), label(value, size, TEXT if rtype != "A" else ADDRESS))
    parts[0].move_to(bg.get_left() + RIGHT * 0.12, aligned_edge=LEFT)
    parts[1].move_to(bg.get_left() + RIGHT * (width * COL_TYPE), aligned_edge=LEFT)
    parts[2].move_to(bg.get_left() + RIGHT * (width * COL_VALUE), aligned_edge=LEFT)
    if parts[1].get_left()[0] < parts[0].get_right()[0] + 0.15:   # a long owner pushes the type right; two texts on a row anchor to each other
        parts[1].next_to(parts[0], RIGHT, buff=0.15)
    if parts[2].get_left()[0] < parts[1].get_right()[0] + 0.15:   # a long type name (CNAME) pushes the value right
        parts[2].next_to(parts[1], RIGHT, buff=0.15)
    g = VGroup(bg, *parts)
    if ttl:
        g.add(label(ttl, max(14, size - 2), REMEMBERED).move_to(bg.get_right() + LEFT * 0.12, aligned_edge=RIGHT))
    return g


def zone_box(name: str, sub: str, y: float, w: float = W_TREE, h: float = H_ZONE, x: float = X_TREE) -> VGroup:
    """A zone: who is authoritative for one level of the name, with room for the record it holds. zb[0] box,
    zb[1] name, zb[2] subtitle."""
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=ZONE, stroke_width=2.4, fill_color=ZONE, fill_opacity=0.08).move_to([x, y, 0])
    n = label(name, 20, ZONE).move_to(r.get_corner(UL) + RIGHT * 0.2 + DOWN * 0.2, aligned_edge=UL)
    s = label(sub, 15, MUTED).next_to(n, DOWN, buff=0.04).align_to(n, LEFT)
    return VGroup(r, n, s)


def resolver_box(y: float = Y_RESOLVER) -> VGroup:
    """The recursive resolver: a box spanning the tree's height, with a cache area inside. rb[0] box, rb[1] name,
    rb[2] the 'cache' label; cached rows go at CACHE_Y[i]."""
    r = RoundedRectangle(corner_radius=0.15, width=W_RESOLVER, height=H_RESOLVER, stroke_color=ZONE, stroke_width=2.6, fill_color=ZONE, fill_opacity=0.06).move_to([X_RESOLVER, y, 0])
    n = label("recursive resolver", 20, TEXT).move_to(r.get_corner(UL) + RIGHT * 0.2 + DOWN * 0.2, aligned_edge=UL)
    c = label("cache", 15, REMEMBERED).next_to(n, DOWN, buff=0.04).align_to(n, LEFT)
    return VGroup(r, n, c)


CACHE_Y = [Y_RESOLVER + H_RESOLVER / 2 - 1.05 - i * (ROW_H * 0.8 + 0.2) for i in range(6)]   # rows inside the resolver, top down


def client_box(y: float = Y_RESOLVER, name: str = "your laptop", sub: str = "app + stub resolver") -> VGroup:
    return node(name, NAME, w=W_CLIENT, h=1.0, sub=sub).move_to([X_CLIENT, y, 0])


def question(scene, a: Mobject, b: Mobject, text: str = "", run_time: float = 0.5):
    """A question travels from a to b: a blue dot with the name beside it."""
    right = a.get_x() < b.get_x()
    d = Dot(color=NAME, radius=0.12).move_to(a.get_right() if right else a.get_left())
    lab = label(text, 14, NAME).next_to(d, UP, buff=0.06) if text else VGroup()
    g = VGroup(d, lab)
    scene.add(g)
    target = b.get_left() if right else b.get_right()
    scene.play(g.animate.move_to(target + (UP * 0.14 if text else 0)), run_time=run_time)
    scene.play(FadeOut(g, run_time=0.15))


def answer(scene, a: Mobject, b: Mobject, color: str, text: str = "", run_time: float = 0.5):
    """An answer travels back: violet for a pointer to who to ask next, yellow for the address, red for 'no'."""
    left = a.get_x() > b.get_x()
    d = Dot(color=color, radius=0.12).move_to(a.get_left() if left else a.get_right())
    lab = label(text, 14, color).next_to(d, DOWN, buff=0.06) if text else VGroup()
    g = VGroup(d, lab)
    scene.add(g)
    target = b.get_right() if left else b.get_left()
    scene.play(g.animate.move_to(target + (DOWN * 0.14 if text else 0)), run_time=run_time)
    scene.play(FadeOut(g, run_time=0.15))


def cache_row(rec: VGroup, slot_y: float) -> VGroup:
    """Place a copy of a record inside the resolver's cache, tinted as remembered, at the cache row width so its
    columns line up with the other cached rows."""
    r = rec.copy().scale(W_CACHE_ROW / rec[0].width)
    r[0].set_fill(REMEMBERED, 0.16)
    r.move_to([X_RESOLVER, slot_y, 0])
    return r


def fuse(row: VGroup, fraction: float = 1.0) -> Rectangle:
    """The time a cached row may still be kept, as a teal bar under it; Transform it to a shorter one to show time
    passing, to zero when it expires."""
    w = row[0].width * fraction
    return Rectangle(width=max(0.01, w), height=0.07, fill_color=REMEMBERED, fill_opacity=0.9, stroke_width=0).move_to(row[0].get_bottom() + DOWN * 0.05, aligned_edge=LEFT).align_to(row[0], LEFT)


def tree():
    """The three zones of the walk with the record each holds. Returns (boxes, records) so scenes start from the same
    picture in one call."""
    root = zone_box(".  the root zone", "13 server names, 12 operators, 2,045 anycast instances", Y_ROOT)
    tld = zone_box("com.", "one of 1,393 top-level domains; run by a registry", Y_TLD)
    auth = zone_box("example.com.", "the owner's own zone, on the owner's chosen servers", Y_AUTH)
    recs = VGroup(record("com.", "NS", "a.gtld-servers.net.", "2 days", ZONE).move_to([X_TREE, Y_ROOT - 0.34, 0]),
                  record("example.com.", "NS", "hera.ns.cloudflare.com.", "2 days", ZONE).move_to([X_TREE, Y_TLD - 0.34, 0]),
                  record("www.example.com.", "A", "104.20.23.154", "5 min", ADDRESS).move_to([X_TREE, Y_AUTH - 0.34, 0]))
    return VGroup(root, tld, auth), recs


# ------------------------------------------------------------------------------------------------ end states
# The last frame of each scene, rebuilt statically by the next scene so the video boundary is invisible (docs/principles.md,
# rule 2). Each returns the objects by name so the next scene can move, fade or grow them in its first play.

HOSTS = [("www.example.com", "104.20.23.154"), ("mail.example.com", "104.20.23.160"), ("intranet", "10.0.0.7"),
         ("printer", "10.0.0.9"), ("git", "10.0.0.12"), ("wiki", "10.0.0.15")]
MORE_HOSTS = [(f"host{i:03d}.example.net", f"203.0.113.{i}") for i in range(10)]
SHORT = [("www", "104.20.23.154"), ("mail", "104.20.23.160")]
NEW_ADDRESS = "104.20.24.1"


def hosts_list(rows, x: float, y: float, width: float = 6.2, size: float = 16) -> VGroup:
    g = VGroup(*[record(n, "", a, color=ADDRESS, width=width, size=size) for n, a in rows]).arrange(DOWN, buff=0.05).move_to([x, y, 0])
    for r in g:
        r[0].set_fill(TEXT, 0.07)
    return g


def fade_below(rows: VGroup, y0: float = -2.2, span: float = 1.0):
    """A list that continues past the frame fades towards the edge instead of being cut."""
    for r in rows:
        y = r.get_y()
        if y < y0:
            r.set_opacity(max(0.0, 1 - (y0 - y) / span))


def list_end_state() -> dict:
    """Where move one ends: the laptop, the long list with one changed address, the counter, three copies of which two
    are stale."""
    client = client_box(0.4)
    lst = hosts_list(HOSTS, -0.9, 0.4)
    ll = label("a list every machine holds: name, address", 16, MUTED).next_to(lst, UP, buff=GAP_TIGHT).align_to(lst, LEFT)
    more = hosts_list(MORE_HOSTS, -0.9, 0.0).next_to(lst, DOWN, buff=0.05).align_to(lst, LEFT)
    fade_below(more)
    count = Counter("names in the list", 340_000_000, "", TEXT, size=30).move_to([3.0, 2.3, 0], aligned_edge=LEFT)
    cl = label("every one of them, on every machine", 16, MUTED).next_to(count, DOWN, buff=0.1).align_to(count, LEFT)
    copies = VGroup(*[hosts_list(SHORT, 4.6, y, width=3.2, size=15) for y in (0.7, -0.55, -1.8)])
    cpl = label("copies on other machines", 15, MUTED).next_to(copies, UP, buff=GAP_TIGHT).align_to(copies, LEFT)
    stale = label("still the old address", 15, HOT).next_to(copies, DOWN, buff=GAP_TIGHT).align_to(copies, LEFT)
    # the change: the master row and the first copy carry the new address, the other two copies are stale
    lst[0][3].become(label(NEW_ADDRESS, 16, HOT).move_to(lst[0][3], aligned_edge=LEFT)); lst[0][0].set_fill(HOT, 0.25)
    copies[0][0][3].become(label(NEW_ADDRESS, 15, HOT).move_to(copies[0][0][3], aligned_edge=LEFT)); copies[0][0][0].set_fill(HOT, 0.25)
    copies[1][0][0].set_fill(DIM, 0.35); copies[2][0][0].set_fill(DIM, 0.35)
    return {"client": client, "lst": lst, "ll": ll, "more": more, "count": count, "cl": cl, "copies": copies, "cpl": cpl, "stale": stale}


def delegation_pointers(recs: VGroup, boxes: VGroup) -> VGroup:
    """The two arrows from a zone's NS record to the zone it points at."""
    return VGroup(Arrow(recs[0][2].get_bottom(), boxes[1][1].get_top() + RIGHT * 0.3, color=ZONE, stroke_width=2, buff=0.05, tip_length=0.15),
                  Arrow(recs[1][2].get_bottom(), boxes[2][1].get_top() + RIGHT * 0.3, color=ZONE, stroke_width=2, buff=0.05, tip_length=0.15))


def delegation_end_state() -> dict:
    """Where move two ends: the tree with its pointers, the laptop, the resolver with the three records of the walk."""
    boxes, recs = tree()
    ptrs = delegation_pointers(recs, boxes)
    client, res = client_box(), resolver_box()
    a1 = arrow(client, res, "", MUTED)
    al = label("one question, one answer", 15, MUTED).next_to(client, DOWN, buff=GAP_TIGHT)
    rows = VGroup(cache_row(recs[0], CACHE_Y[0]), cache_row(recs[1], CACHE_Y[1]), cache_row(recs[2], CACHE_Y[2]))
    return {"boxes": boxes, "recs": recs, "ptrs": ptrs, "client": client, "res": res, "a1": a1, "al": al, "rows": rows}


def caching_end_state() -> dict:
    """Where move three ends: the delegation picture plus a second laptop, five cached rows with their fuses, the far
    zone, the hop counter at one, the browser and OS caches, and the countdown line."""
    d = delegation_end_state()
    rows = d["rows"]
    c4 = cache_row(record("other.com.", "NS", "ns1.other.com.", "2 days", ZONE), CACHE_Y[3])
    c5 = cache_row(record("mail.other.com.", "A", "198.51.100.7", "5 min", ADDRESS), CACHE_Y[4])
    fuses = VGroup(fuse(rows[0], 0.998), fuse(rows[1], 0.996), fuse(rows[2], 1.0), fuse(c4), fuse(c5))
    client2 = client_box(y=-1.1, name="another laptop", sub="same resolver")
    far = box(W_TREE, 0.6, "other.com.   another owner's zone", ZONE, size=16).move_to([X_TREE, -2.5, 0])
    hops = Counter("hops into the tree", 1, "", ZONE, size=24).move_to([-MARGIN, -2.4, 0], aligned_edge=LEFT)
    stack = VGroup(label("browser cache", 15, REMEMBERED), label("OS cache", 15, REMEMBERED)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
    stack.next_to(d["client"], UP, buff=0.3).align_to(d["client"], LEFT)
    marks = VGroup(*[Rectangle(width=0.1, height=0.2, fill_color=REMEMBERED, fill_opacity=0.9, stroke_width=0).next_to(s_, LEFT, buff=0.1) for s_ in stack])
    cd = label("the same TTL counts down in every cache: 300 s, then 281 s", 16, MUTED).move_to([0, -3.3, 0])
    d.update({"c4": c4, "c5": c5, "fuses": fuses, "client2": client2, "far": far, "hops": hops, "stack": stack, "marks": marks, "cd": cd})
    return d


def owner_zone() -> VGroup:
    """The owner's zone as move four draws it: large, top centre."""
    return zone_box("example.com.", "the owner's zone", CONTENT_TOP - 0.825, w=6.6, h=1.65, x=0.0)


def price_end_state() -> dict:
    """Where move four ends: the owner's zone with the alias and SOA records, the laptop, the resolver, the alias's zone."""
    auth = owner_zone()
    cname = record("www.example.com.", "CNAME", "cdn.example.net.", "1 h", ZONE).move_to([0.0, 1.72, 0])
    soa = record("example.com.", "SOA", "minimum 1800 s", "30 min", ZONE).move_to([0.0, 1.25, 0])
    client = client_box(y=-0.9)
    res = box(W_RESOLVER, 2.2, "recursive resolver", ZONE, size=18, name_align="left").move_to([X_RESOLVER, -0.9, 0])
    far = zone_box("cdn.example.net.", "another zone: another walk, root, net, example.net", -0.9, w=W_TREE, h=1.1, x=X_TREE)
    al = label("an alias is a pointer to another name: the walk restarts there", 16, MUTED).move_to([0, -3.3, 0])
    return {"auth": auth, "cname": cname, "soa": soa, "client": client, "res": res, "far": far, "al": al}
