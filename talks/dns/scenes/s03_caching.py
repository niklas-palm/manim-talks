"""Move 3: caching. The resolver keeps every answer for as long as the answer said. A second lookup of the same name is
one hop; a lookup of a different name under com skips the root; the pointers near the top of the tree live for days,
the address at the bottom for minutes, so the expensive part of the walk is the part remembered longest. Time passes,
the address expires, and one lookup pays the walk again.

  Final frame: the same picture as move two (laptop, resolver with three cached rows and their fuses, three zones),
  plus a second laptop, a counter of hops per lookup, and a compressed clock.
  Clicks: 1 the same name again: answered from cache in one hop  2 a different name under com: the root is skipped,
  and the TTLs say why (pointers live for days, the address for minutes)  3 time passes: the address expires, the next
  lookup walks the bottom again; a miss costs about 130 ms, a hit about nothing  4 caches at every level: browser, OS,
  resolver, and the record's TTL counting down in each
"""
from lib.palette import *
from objects import *


class Caching(TalkSlide):
    def construct(self):
        t = title(self, "Caching: remember what you were told", "3  caching: remember what you were told")
        # --- the picture move two left behind
        (root, tld, auth), (r_root, r_tld, r_auth) = tree()
        client = client_box()
        res = resolver_box()
        rows = VGroup(cache_row(r_root, CACHE_Y[0]), cache_row(r_tld, CACHE_Y[1]), cache_row(r_auth, CACHE_Y[2]))
        fuses = VGroup(*[fuse(r) for r in rows])
        hops = Counter("hops into the tree", 3, "", ZONE, size=24).move_to([-MARGIN, -2.4, 0], aligned_edge=LEFT)
        self.play(FadeIn(root), FadeIn(tld), FadeIn(auth), FadeIn(r_root), FadeIn(r_tld), FadeIn(r_auth), FadeIn(client), FadeIn(res), FadeIn(rows), FadeIn(fuses), FadeIn(hops), run_time=0.8)
        # --- the same name again: one hop
        question(self, client, res, "www.example.com?")
        self.play(rows[2][0].animate.set_fill(REMEMBERED, 0.45), hops.to(0), run_time=0.3)
        answer(self, res, client, ADDRESS, "104.20.23.154")
        self.play(rows[2][0].animate.set_fill(REMEMBERED, 0.14), run_time=0.2)
        self.next_slide("""Rule two. The walk left three records in the resolver's cache, each with the time to live its zone attached: the
        teal bar under each row is that time, running out. Now the same laptop, or any of the thousands of others behind
        this resolver, asks for www.example.com again. The address is in the cache and its time has not run out, so the
        answer comes straight back: zero hops into the tree, no root server, no registry, no example.com server involved.
        This is why the root servers are not answering every lookup on earth.""")
        # --- a different name under com: the root is skipped
        client2 = client_box(y=-1.1, name="another laptop", sub="same resolver")
        self.play(FadeIn(client2), run_time=0.4)
        question(self, client2, res, "mail.other.com?")
        self.play(rows[0][0].animate.set_fill(REMEMBERED, 0.45), run_time=0.3)
        skip = label("root skipped: com's servers already known", 15, REMEMBERED).next_to(res, DOWN, buff=GAP_TIGHT).align_to(res, LEFT)
        self.play(FadeIn(skip), run_time=0.3)
        question(self, res, tld, "mail.other.com?")
        answer(self, tld, res, ZONE, "ask other.com's servers")
        other = record("other.com.", "NS", "ns1.other.com.", "2 days", ZONE)
        c4 = cache_row(other, CACHE_Y[3])
        self.play(FadeIn(c4), FadeIn(fuse(c4)), hops.to(1), rows[0][0].animate.set_fill(REMEMBERED, 0.14), run_time=0.4)
        far = box(W_TREE, 0.6, "other.com.   another owner's zone", ZONE, size=16).move_to([X_TREE, -2.5, 0])
        self.play(FadeIn(far), run_time=0.3)
        question(self, res, far, "mail.other.com?")
        answer(self, far, res, ADDRESS, "198.51.100.7")
        c5 = cache_row(record("mail.other.com.", "A", "198.51.100.7", "5 min", ADDRESS), CACHE_Y[4])
        self.play(FadeIn(c5), FadeIn(fuse(c5)), hops.to(2), run_time=0.4)
        answer(self, res, client2, ADDRESS, "198.51.100.7")
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
        question(self, client, res, "www.example.com?")
        question(self, res, auth, "www.example.com?")
        answer(self, auth, res, ADDRESS, "104.20.23.154")
        fresh = cache_row(r_auth, CACHE_Y[2])
        self.play(FadeOut(rows[2]), FadeOut(fuses[2]), FadeIn(fresh), FadeIn(fuse(fresh)), hops.to(1), run_time=0.5)
        answer(self, res, client, ADDRESS, "104.20.23.154")
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
        marks = VGroup(*[Rectangle(width=0.1, height=0.2, fill_color=REMEMBERED, fill_opacity=0.9, stroke_width=0).next_to(s_, LEFT, buff=0.1) for s_ in stack])
        self.play(FadeIn(stack, lag_ratio=0.2), FadeIn(marks, lag_ratio=0.2), run_time=0.8)
        cd = label("the same TTL counts down in every cache: 300 s, then 281 s", 16, MUTED).move_to([0, -3.3, 0])
        self.play(FadeOut(cost), FadeIn(cd), run_time=0.4)
        self.finish("""The resolver is not the only cache. The browser keeps answers, the operating system's stub keeps answers, and
        each of them counts the same time to live down from where it received it: a record that left the resolver with
        300 seconds arrives in the browser with 281, and the browser may keep it for 281 more, not 300. The answer carries
        its own expiry and every party respects it. So a lookup is answered by the nearest cache that still holds a
        fresh copy, and the tree is consulted only for what nobody nearby remembers. That is rule two at work, and it
        makes the system fast. It is also, exactly, what makes changes slow.""")
