"""Move 4: the price of remembering. Three consequences of rule two, each on the same picture. A change at the owner
reaches resolvers only as their copies expire, so propagation time is the TTL and the trick is to lower it before the
change. A name that does not exist is the most expensive kind of miss, so the "no" is cached too, for the zone's SOA
minimum. An alias (CNAME) is a pointer to another name, and the resolver starts the walk again for that name.

  Final frame: the owner's zone with a changed address; a row of five resolvers around the world, each with its copy and
  its fuse, some stale; the negative record; the alias chain.
  Clicks: 1 the owner changes the address; resolvers keep the old one until their copy expires  2 the trick: lower the
  TTL first, wait one old TTL, then change  3 a name that does not exist: the walk to authority and the answer 'no',
  cached for the SOA minimum  4 an alias: CNAME points to another name, and the walk restarts there
"""
from lib.palette import *
from objects import *

RES_X = [-5.0, -1.7, 1.6, 4.9]


def resolver_small(x: float, y: float, name: str) -> VGroup:
    g = box(3.2, 1.3, name, ZONE, size=16)
    g.move_to([x, y, 0])
    return g


class Price(TalkSlide):
    def construct(self):
        t = title(self, "The price of remembering", "4  the price of remembering")
        auth = zone_box("example.com.", "the owner's zone", 1.85, w=6.6, h=1.65, x=0.6)
        r_auth = record("www.example.com.", "A", "104.20.23.154", "5 min", ADDRESS).move_to([0.6, 1.78, 0])
        self.play(FadeIn(auth), FadeIn(r_auth), run_time=0.5)
        rl = label("resolvers around the world, each with its own copy", 16, MUTED).move_to([0, 0.6, 0])
        rs = VGroup(*[resolver_small(x, -0.3, n) for x, n in zip(RES_X, ("Stockholm", "Dublin", "Virginia", "Tokyo"))])
        copies = VGroup(*[record("www", "", "104.20.23.154", "", ADDRESS, width=2.9, size=15).move_to(r[0].get_center() + DOWN * 0.18) for r in rs])
        fuses = VGroup(*[fuse(c, f) for c, f in zip(copies, (0.9, 0.3, 0.6, 0.15))])
        self.play(FadeIn(rl), FadeIn(rs), FadeIn(copies), FadeIn(fuses), run_time=0.7)
        # --- the change
        new_val = label("104.20.24.1", 16, HOT).move_to(r_auth[3], aligned_edge=LEFT)
        self.play(Transform(r_auth[3], new_val), r_auth[0].animate.set_fill(HOT, 0.25), run_time=0.6)
        stale = label("stale: the old address, until each copy expires", 16, HOT).move_to([0, -1.35, 0])
        self.play(FadeIn(stale), *[c[0].animate.set_fill(HOT, 0.2) for c in copies], run_time=0.5)
        clock = label("time passes", 15, MUTED).move_to([-6.2, -1.9, 0])
        self.play(FadeIn(clock), run_time=0.2)
        order = sorted(range(4), key=lambda i: (0.9, 0.3, 0.6, 0.15)[i])
        for i in order:
            fresh = label("104.20.24.1", 15, ADDRESS).move_to(copies[i][3], aligned_edge=LEFT)
            self.play(Transform(fuses[i], fuse(copies[i], 0.0)), run_time=0.35, rate_func=linear)
            self.play(Transform(copies[i][3], fresh), copies[i][0].animate.set_fill(ADDRESS, 0.15), Transform(fuses[i], fuse(copies[i], 1.0)), run_time=0.3)
        self.next_slide("""The owner moves www.example.com to a new address and changes the record. Nothing tells the resolvers. Each keeps
        its copy of the old address until that copy's time runs out, and their clocks started at different moments, so
        they expire one by one: Tokyo first, then Dublin, Virginia, Stockholm. Until then, users behind a stale
        resolver reach the old machine. There is no propagation mechanism in DNS; there is only expiry. "Propagation
        time" is the time to live of the record you changed, as seen from the slowest cache.""")
        # --- the trick
        self.play(FadeOut(stale), FadeOut(clock), run_time=0.3)
        trick = VGroup(label("1  TTL to 60 s; wait one old TTL", 16, TEXT), label("2  change the address", 16, TEXT),
                       label("3  TTL back up", 16, TEXT)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([-6.2, -2.0, 0], aligned_edge=LEFT)
        ttl_lab = label("60 s", 14, REMEMBERED).move_to(r_auth[4], aligned_edge=RIGHT)
        self.play(FadeIn(trick[0]), Transform(r_auth[4], ttl_lab), run_time=0.5)
        self.play(*[Transform(f, fuse(c, 0.2)) for f, c in zip(fuses, copies)], run_time=0.8)
        self.play(FadeIn(trick[1]), run_time=0.3)
        newer = label("104.20.25.9", 16, ADDRESS).move_to(r_auth[3], aligned_edge=LEFT)
        self.play(Transform(r_auth[3], newer), r_auth[0].animate.set_fill(ADDRESS, 0.15), run_time=0.4)
        self.play(*[Transform(f, fuse(c, 0.0)) for f, c in zip(fuses, copies)], run_time=0.5, rate_func=linear)
        self.play(*[Transform(c[3], label("104.20.25.9", 15, ADDRESS).move_to(c[3], aligned_edge=LEFT)) for c in copies],
                  *[Transform(f, fuse(c, 1.0)) for f, c in zip(fuses, copies)], run_time=0.5)
        self.play(FadeIn(trick[2]), Transform(r_auth[4], label("5 min", 14, REMEMBERED).move_to(r_auth[4], aligned_edge=RIGHT)), run_time=0.4)
        self.next_slide("""So the trick every operator learns. Before a planned move, lower the record's time to live to a minute and wait
        at least one old time to live, so that every cached copy in the world has been refreshed with the short value.
        Then change the address: every copy now expires within a minute and the whole internet follows. Then raise the
        time to live again, because a short one means many misses and misses are what makes lookups slow. The time to
        live is a dial between how fast you can change and how cheap lookups are, and the owner of the zone holds it.""")
        # --- a name that does not exist
        self.play(FadeOut(trick), FadeOut(rl), FadeOut(rs), FadeOut(copies), FadeOut(fuses), run_time=0.5)
        client = client_box(-0.6).shift(RIGHT * 0.3)
        res = box(5.8, 2.4, "recursive resolver", ZONE, size=18).move_to([-0.3, -0.8, 0])
        self.play(FadeIn(client), FadeIn(res), run_time=0.4)
        question(self, client, res, "wwww.example.com?")
        question(self, res, auth, "wwww.example.com?")
        soa = record("example.com.", "SOA", "minimum 1800 s", "30 min", ZONE).move_to([0.6, 1.3, 0])
        self.play(FadeIn(soa), run_time=0.4)
        answer(self, auth, res, HOT, "no such name (NXDOMAIN)")
        neg = record("wwww.example.com.", "does not exist", "", "30 min", HOT).scale(0.9).move_to(res[0].get_center() + DOWN * 0.25)
        nf = fuse(neg)
        self.play(FadeIn(neg), FadeIn(nf), run_time=0.4)
        answer(self, res, client, HOT, "no such name")
        nl = label("the 'no' is cached too: for the zone's SOA minimum, 30 min here", 16, MUTED).move_to([0, -2.75, 0])
        self.play(FadeIn(nl), run_time=0.4)
        self.next_slide("""The most expensive miss is a name that does not exist: a typo, a decommissioned host, a probe. Nothing is cached,
        so every such question walks to the authoritative servers, which answer "no such name". If the resolver forgot
        that "no" at once, the same typo from the next user would walk again. So the answer "no" is cached as well, and
        its time to live comes from the zone's SOA record, the record that describes the zone itself: its minimum field,
        redefined by RFC 2308 to mean exactly this, thirty minutes for example.com today, with one to three hours the
        suggested range. Negative caching is why a misspelt name is fast the second time, and why a name you have just
        created can take half an hour to exist for someone who asked for it a minute too early.""")
        # --- an alias
        self.play(FadeOut(neg), FadeOut(nf), FadeOut(nl), run_time=0.3)
        cname = record("www.example.com.", "CNAME", "edge.cdn.example.net.", "1 h", ZONE).move_to([0.6, 1.78, 0])
        self.play(Transform(r_auth, cname), run_time=0.6)
        question(self, client, res, "www.example.com?")
        question(self, res, auth, "www.example.com?")
        answer(self, auth, res, ZONE, "it is an alias for edge.cdn.example.net")
        far = zone_box("cdn.example.net.", "another zone: another walk, root, net, example.net", -2.75, w=6.6, h=0.8, x=3.0)
        self.play(FadeIn(far), run_time=0.4)
        question(self, res, far, "edge.cdn.example.net?")
        answer(self, far, res, ADDRESS, "203.0.113.20")
        answer(self, res, client, ADDRESS, "203.0.113.20")
        al = label("an alias is a pointer to another name: the walk restarts there", 16, MUTED).move_to([-2.4, -3.35, 0])
        self.play(FadeIn(al), run_time=0.4)
        self.finish("""One more kind of pointer, and it is rule one again. Instead of an address, a name can hold an alias, a CNAME,
        that says "this name is really that other name". Content networks live on it: www.example.com points at a
        name in the network's own zone, so the network can change addresses without touching the customer's zone. The
        resolver treats the alias as a pointer and restarts the walk for the new name, possibly through a different
        top-level domain, with its own pointers and its own times to live; both answers come back together. A name
        with a CNAME may hold nothing else, which is why the apex of a zone cannot be an alias, a rule that has cost
        many people an afternoon. Rule one, applied to names instead of servers.""")
