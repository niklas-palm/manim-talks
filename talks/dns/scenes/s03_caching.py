"""Move 3: caching. The resolver keeps every answer for as long as the answer said. A second lookup of the same name is
one hop; a lookup of a different name under com skips the root; the pointers near the top of the tree live for days,
the address at the bottom for minutes, so the expensive part of the walk is the part remembered longest. Time passes,
the address expires, and one lookup pays the walk again.

  Final frame (move four starts from it): the picture of move two plus fuses under the cached rows, a second laptop,
  two more cached rows, the far zone, the hop counter, the browser and OS caches.
  Clicks: 1 move two's picture gains the fuses and the hop counter  2 the same name again: answered from cache in one hop  2 a different name under com: the root is skipped,
  and the TTLs say why (pointers live for days, the address for minutes)  3 time passes: the address expires, the next
  lookup walks the bottom again; a miss costs about 130 ms, a hit about nothing  4 caches at every level: browser, OS,
  resolver, and the record's TTL counting down in each
"""
from lib.palette import *
from objects import *


class Caching(TalkSlide):
    def construct(self):
        # --- the last frame of move two, rebuilt
        t = title_still(self, "Delegation: the name is a path", "2  delegation: the name is a path")
        d = delegation_end_state()
        (root, tld, auth), (r_root, r_tld, r_auth) = d["boxes"], d["recs"]
        client, res, rows = d["client"], d["res"], d["rows"]
        self.add(*d.values())
        # --- the first change: the cached rows get their time to live, and the hop counter says what the walk cost
        fuses = VGroup(*[fuse(r) for r in rows])
        hops = Counter("hops into the tree", 3, "", ZONE, size=24).move_to([-MARGIN, -2.4, 0], aligned_edge=LEFT)
        upd = hops.num.updaters[0]; hops.num.clear_updaters()   # the digit updater redraws at full opacity and would show the counter before its fade
        t = retitle(self, t, "Caching: remember what you were told", "3  caching: remember what you were told", extra=[FadeIn(fuses), FadeIn(hops), FadeOut(d["al"])])
        hops.num.add_updater(upd)
        self.next_slide("""Same picture, one addition: under each record the resolver kept, a teal bar, its time to live, running out from
        the moment it arrived; and at the bottom left the hop counter, at three, what the first walk cost. Watch what the
        second question costs.""")
        # --- the same name again: one hop
        question(self, client, res[1], "www.example.com?", run_time=0.6)
        self.play(rows[2][0].animate.set_fill(REMEMBERED, 0.45), hops.to(0), run_time=0.3)
        answer(self, rows[2], client, ADDRESS, "104.20.23.154")   # from the cached row itself
        self.play(rows[2][0].animate.set_fill(REMEMBERED, 0.14), run_time=0.2)
        self.next_slide("""Rule two. The walk left three records in the resolver's cache, each with the time to live its zone attached: the
        teal bar under each row is that time, running out. Now the same laptop, or any of the thousands of others behind
        this resolver, asks for www.example.com again. The address is in the cache and its time has not run out, so the
        answer comes straight back: zero hops into the tree, no root server, no registry, no example.com server involved.
        This is why the root servers are not answering every lookup on earth.""")
        # --- a different name under com: the root is skipped
        client2 = client_box(y=-1.1, name="another laptop", sub="same resolver")
        self.play(FadeIn(client2), run_time=0.4)
        question(self, client2, res[1], "mail.other.com?")
        self.play(rows[0][0].animate.set_fill(REMEMBERED, 0.45), run_time=0.3)
        skip = label("root skipped: com's servers already known", 15, REMEMBERED).next_to(res, DOWN, buff=GAP_TIGHT).align_to(res, LEFT)
        self.play(FadeIn(skip), run_time=0.3)
        question(self, res[1], r_tld, "mail.other.com?")
        other = record("other.com.", "NS", "ns1.other.com.", "2 days", ZONE)
        c4 = cache_row(other, CACHE_Y[3])
        answer(self, r_tld, res, ZONE, "ask other.com's servers", becomes=c4)
        self.play(FadeIn(fuse(c4)), hops.to(1), rows[0][0].animate.set_fill(REMEMBERED, 0.14), run_time=0.4)
        far = box(W_TREE, 0.6, "other.com.   another owner's zone", ZONE, size=16).move_to([X_TREE, -2.5, 0])
        self.play(FadeIn(far), run_time=0.3)
        question(self, res[1], far[1], "mail.other.com?")
        c5 = cache_row(record("mail.other.com.", "A", "198.51.100.7", "5 min", ADDRESS), CACHE_Y[4])
        answer(self, far[1], res, ADDRESS, "198.51.100.7", becomes=c5)
        self.play(FadeIn(fuse(c5)), hops.to(2), run_time=0.4)
        answer(self, c5, client2, ADDRESS, "198.51.100.7")
        ttls = label("pointers near the top: days; the address: minutes", 16, REMEMBERED).move_to([X_TREE - W_TREE / 2, -3.25, 0], aligned_edge=LEFT)
        self.play(FadeOut(skip), FadeIn(ttls), run_time=0.4)
        self.next_slide("""A different name, mail.other.com, under com as well. The resolver already holds the pointer to com's servers,
        so it does not ask the root: it goes straight to com, gets the pointer to other.com, asks other.com, gets the
        address. Two hops instead of three, and the root was not involved. Now read the times to live the zones chose.
        The root tells resolvers to keep its pointers for six days; com says two days for its pointers; example.com says
        five minutes for the address. The pointers near the top change almost never and are wanted by almost every
        lookup, so they are remembered longest; the address at the bottom changes when the owner moves servers, so it is
        remembered briefly. The expensive part of the walk is the part that is cached longest. That is the design.""")
        # --- time passes: the address expires, one lookup walks the bottom again
        clock = label("five minutes pass", 16, MUTED).next_to(res, DOWN, buff=GAP_TIGHT).align_to(res, LEFT)
        self.play(FadeIn(clock), run_time=0.3)
        self.play(Transform(fuses[2], fuse(rows[2], 0.0)), Transform(fuses[0], fuse(rows[0], 0.998)), Transform(fuses[1], fuse(rows[1], 0.996)), run_time=1.6, rate_func=linear)
        self.play(rows[2][0].animate.set_fill(HOT, 0.3), run_time=0.3)
        question(self, client, res[1], "www.example.com?")
        self.play(FadeOut(rows[2]), FadeOut(fuses[2]), run_time=0.3)   # the expired row leaves before the walk refreshes it
        question(self, res[1], r_auth, "www.example.com?")
        fresh = cache_row(r_auth, CACHE_Y[2])
        answer(self, r_auth, res, ADDRESS, "104.20.23.154", becomes=fresh)
        self.play(FadeIn(fuse(fresh)), hops.to(1), run_time=0.4)
        answer(self, fresh, client, ADDRESS, "104.20.23.154")
        cost = VGroup(label("hit: no network, about 0 ms", 16, REMEMBERED), label("miss: about 130 ms; 4 to 6% time out", 16, HOT)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).move_to([X_RESOLVER - W_RESOLVER / 2, -2.55, 0], aligned_edge=LEFT)
        self.play(FadeOut(clock), FadeOut(ttls), FadeIn(cost), run_time=0.4)
        self.next_slide("""Time passes; five minutes here, compressed. The address's time to live runs out and the row may no longer be used;
        the pointers above it have barely aged. The next lookup for the name is a miss: the resolver still knows
        example.com's servers, so it asks them directly and gets a fresh address with a fresh five minutes, one hop, not
        three. A hit costs no network at all; a miss costs a round trip to a server somewhere on the internet, on average
        about 130 milliseconds by Google's measurement of its resolvers, and a few percent of those servers do not answer
        in time. Cache misses are the dominant cause of slow lookups. Everything about the times to live is a trade
        between that cost and the next move's problem.""")
        # --- caches at every level
        stack = VGroup(label("browser cache", 15, REMEMBERED), label("OS cache", 15, REMEMBERED)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        stack.next_to(client, UP, buff=0.3).align_to(client, LEFT)
        marks = VGroup(*[Rectangle(width=0.1, height=0.2, fill_color=REMEMBERED, fill_opacity=SOLID, stroke_width=0).next_to(s_, LEFT, buff=0.1) for s_ in stack])
        self.play(FadeIn(stack, lag_ratio=0.2), FadeIn(marks, lag_ratio=0.2), run_time=0.8)
        cd = label("the same TTL counts down in every cache: 300 s, then 281 s", 16, MUTED).move_to([0, -3.3, 0])
        self.play(FadeOut(cost), FadeIn(cd), run_time=0.4)
        self.finish("""The resolver is not the only cache. The browser keeps answers, the operating system's stub keeps answers, and
        each of them counts the same time to live down from where it received it: a record that left the resolver with
        300 seconds arrives in the browser with 281, and the browser may keep it for 281 more, not 300. The answer carries
        its own expiry and every party respects it. So a lookup is answered by the nearest cache that still holds a
        fresh copy, and the tree is consulted only for what nobody nearby remembers. That is rule two at work, and it
        makes the system fast. It is also, exactly, what makes changes slow.""")
