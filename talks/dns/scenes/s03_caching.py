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
        root = zone_box(".  the root zone", "13 server names, 12 operators, 2,045 anycast instances", Y_ROOT)
        tld = zone_box("com.", "one of 1,393 top-level domains; run by a registry", Y_TLD)
        auth = zone_box("example.com.", "the owner's own zone, on the owner's chosen servers", Y_AUTH)
        r_root = record("com.", "NS", "a.gtld-servers.net.", "2 days", ZONE).move_to([X_TREE, Y_ROOT - 0.27, 0])
        r_tld = record("example.com.", "NS", "hera.ns.cloudflare.com.", "2 days", ZONE).move_to([X_TREE, Y_TLD - 0.27, 0])
        r_auth = record("www.example.com.", "A", "104.20.23.154", "5 min", ADDRESS).move_to([X_TREE, Y_AUTH - 0.27, 0])
        client = client_box(0.3)
        res = resolver_box(-0.1)
        rows = VGroup(cache_row(r_root, 0.7), cache_row(r_tld, 0.3), cache_row(r_auth, -0.1))
        fuses = VGroup(*[fuse(r) for r in rows])
        hops = Counter("hops for this lookup", 3, "", ZONE, size=22).move_to([-6.6, -2.1, 0], aligned_edge=LEFT)
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
        client2 = node("another laptop", NAME, w=2.0, h=0.9, sub="behind the same resolver").move_to([X_CLIENT, -1.3, 0])
        self.play(FadeIn(client2), run_time=0.4)
        question(self, client2, res, "mail.other.com?")
        self.play(rows[0][0].animate.set_fill(REMEMBERED, 0.45), run_time=0.3)
        skip = label("root skipped: com's servers are already known", 12, REMEMBERED).next_to(rows[0], RIGHT, buff=0.2).shift(RIGHT * 0.2)
        self.play(FadeIn(skip), run_time=0.3)
        question(self, res, tld, "mail.other.com?")
        answer(self, tld, res, ZONE, "ask other.com's servers")
        other = record("other.com.", "NS", "ns1.other.com.", "2 days", ZONE)
        c4 = cache_row(other, -0.5)
        self.play(FadeIn(c4), FadeIn(fuse(c4)), hops.to(1), rows[0][0].animate.set_fill(REMEMBERED, 0.14), run_time=0.4)
        far = zone_box("other.com.", "another owner's zone", -2.3, h=0.7)
        self.play(FadeIn(far), run_time=0.3)
        question(self, res, far, "mail.other.com?")
        answer(self, far, res, ADDRESS, "198.51.100.7")
        c5 = cache_row(record("mail.other.com.", "A", "198.51.100.7", "5 min", ADDRESS), -0.9)
        self.play(FadeIn(c5), FadeIn(fuse(c5)), hops.to(2), run_time=0.4)
        answer(self, res, client2, ADDRESS, "198.51.100.7")
        ttls = label("pointers near the top live for days; the address at the bottom for minutes", 14, REMEMBERED).move_to([X_TREE, -2.95, 0])
        self.play(FadeOut(skip), FadeIn(ttls), run_time=0.4)
        self.next_slide("""A different name, mail.other.com, under com as well. The resolver already holds the pointer to com's servers,
        so it does not ask the root: it goes straight to com, gets the pointer to other.com, asks other.com, gets the
        address. Two hops instead of three, and the root was not involved. Now read the times to live the zones chose.
        The root tells resolvers to keep its pointers for six days; com says two days for its pointers; example.com says
        five minutes for the address. The pointers near the top change almost never and are wanted by almost every
        lookup, so they are remembered longest; the address at the bottom changes when the owner moves servers, so it is
        remembered briefly. The expensive part of the walk is the part that is cached longest. That is the design.""")
        # --- time passes: the address expires, one lookup walks the bottom again
        clock = label("five minutes pass", 14, MUTED).move_to([X_RESOLVER, -2.6, 0])
        self.play(FadeIn(clock), run_time=0.3)
        for r, f, frac in ((rows[0], fuses[0], 0.999), (rows[1], fuses[1], 0.998), (rows[2], fuses[2], 0.0)):
            pass
        self.play(Transform(fuses[2], fuse(rows[2], 0.0)), Transform(fuses[0], fuse(rows[0], 0.998)), Transform(fuses[1], fuse(rows[1], 0.996)), run_time=1.6, rate_func=linear)
        self.play(rows[2][0].animate.set_fill(HOT, 0.3), run_time=0.3)
        expired = label("expired: may not be used", 12, HOT).next_to(rows[2], RIGHT, buff=0.2).shift(RIGHT * 0.2)
        self.play(FadeIn(expired), run_time=0.3)
        question(self, client, res, "www.example.com?")
        question(self, res, auth, "www.example.com?")
        answer(self, auth, res, ADDRESS, "104.20.23.154")
        fresh = cache_row(r_auth, -0.1)
        self.play(FadeOut(rows[2]), FadeOut(fuses[2]), FadeIn(fresh), FadeIn(fuse(fresh)), hops.to(1), FadeOut(expired), run_time=0.5)
        answer(self, res, client, ADDRESS, "104.20.23.154")
        cost = VGroup(label("a hit: answered from memory, no network", 13, REMEMBERED),
                      label("a miss: about 130 ms on average across the internet's servers; 4 to 6% of them time out", 13, HOT)).arrange(DOWN, aligned_edge=LEFT, buff=0.06).move_to([X_RESOLVER + 0.4, -2.95, 0]).align_to(res, LEFT)
        self.play(FadeOut(clock), FadeIn(cost), run_time=0.4)
        self.next_slide("""Time passes; five minutes here, compressed. The address's time to live runs out and the row may no longer be used;
        the pointers above it have barely aged. The next lookup for the name is a miss: the resolver still knows
        example.com's servers, so it asks them directly and gets a fresh address with a fresh five minutes, one hop, not
        three. A hit costs no network at all; a miss costs a round trip to a server somewhere on the internet, on average
        about 130 milliseconds by Google's measurement of its resolvers, and a few percent of those servers do not answer
        in time. Cache misses are the dominant cause of slow lookups. Everything about the times to live is a trade
        between that cost and the next move's problem.""")
        # --- caches at every level
        stack = VGroup(label("browser cache", 12, REMEMBERED), label("operating system cache", 12, REMEMBERED), label("recursive resolver cache", 12, REMEMBERED)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        stack.next_to(client, UP, buff=0.35).align_to(client, LEFT)
        marks = VGroup(*[Rectangle(width=0.08, height=0.16, fill_color=REMEMBERED, fill_opacity=0.9, stroke_width=0).next_to(s_, LEFT, buff=0.08) for s_ in stack])
        self.play(FadeIn(stack, lag_ratio=0.2), FadeIn(marks, lag_ratio=0.2), run_time=0.8)
        cd = label("the same record, its TTL counting down in each: 300 s at the resolver, 281 s a moment later in the browser", 13, MUTED).move_to([0, -2.6, 0])
        self.play(FadeOut(cost), FadeIn(cd), run_time=0.4)
        self.finish("""The resolver is not the only cache. The browser keeps answers, the operating system's stub keeps answers, and
        each of them counts the same time to live down from where it received it: a record that left the resolver with
        300 seconds arrives in the browser with 281, and the browser may keep it for 281 more, not 300. The answer carries
        its own expiry and every party respects it. So a lookup is answered by the nearest cache that still holds a
        fresh copy, and the tree is consulted only for what nobody nearby remembers. That is rule two at work, and it
        makes the system fast. It is also, exactly, what makes changes slow.""")
