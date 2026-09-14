"""Move 5: what keeps it standing, and the two rules once more. The thirteen root names are 2,045 machines: a question
goes to the nearest by anycast routing. A question is one small UDP packet; a long answer sets a flag and the client
asks again over TCP. Then the whole picture once more, with the two rules written on it.

  Clicks: 1 thirteen names, two thousand machines: a question goes to the nearest  2 the packet: 512 bytes over UDP,
  the truncation flag, TCP behind it  3 the picture and the two rules
"""
from lib.palette import *
from objects import *


class Standing(TalkSlide):
    def construct(self):
        t = title(self, "What keeps it standing", "5  what keeps it standing")
        # --- anycast
        names = VGroup(*[label(f"{c}.root-servers.net.", 15, ZONE) for c in "abcdefghijklm"]).arrange(DOWN, aligned_edge=LEFT, buff=0.045).move_to([-6.6, 0.1, 0], aligned_edge=LEFT)
        nl = label("13 server names, 12 operators", 16, MUTED).next_to(names, UP, buff=0.15).align_to(names, LEFT)
        self.play(FadeIn(names, lag_ratio=0.05), FadeIn(nl), run_time=0.8)
        import random
        random.seed(3)
        world = Ellipse(width=9.0, height=4.8, color=DIM, stroke_width=1.5).move_to([2.3, 0.05, 0])
        sites = VGroup(*[Dot(radius=0.06, color=ZONE).move_to([2.3 + random.uniform(-4.2, 4.2), 0.05 + random.uniform(-2.1, 2.1), 0]) for _ in range(200)])
        sites = VGroup(*[d for d in sites if ((d.get_x() - 2.3) / 4.5) ** 2 + ((d.get_y() - 0.05) / 2.4) ** 2 < 1])
        sl = label("2,045 anycast instances of those 13 names; one dot per about 12", 15, MUTED).next_to(world, DOWN, buff=0.12)
        self.play(FadeIn(world), FadeIn(sites, lag_ratio=0.005), FadeIn(sl), run_time=1.4)
        you = Dot(radius=0.12, color=NAME).move_to([4.6, -1.7, 0])
        yl = label("a resolver in Sydney asks a.root-servers.net", 14, NAME).next_to(you, DOWN, buff=0.08)
        nearest = min(sites, key=lambda d: np.linalg.norm(d.get_center() - you.get_center()))
        self.play(FadeIn(you), FadeIn(yl), run_time=0.4)
        path = Line(you.get_center(), nearest.get_center(), color=NAME, stroke_width=2)
        self.play(Create(path), nearest.animate.set_color(ADDRESS).scale(2.2), run_time=0.6)
        al = label("one address, announced from many places: the packet reaches the nearest", 16, MUTED).move_to([0.3, -3.2, 0])
        self.play(FadeIn(al), run_time=0.4)
        self.next_slide("""The root of the tree is the one list everyone holds, thirteen server names run by twelve organisations, and if
        thirteen machines answered the world the system would not stand. They do not. Each of the thirteen addresses is
        announced into the internet's routing from many places at once, anycast, so a packet sent to a.root-servers.net
        from Sydney reaches an instance in Sydney. Today the thirteen names are 2,045 instances. The same is true of the
        big top-level domains and the large public resolvers. The tree's top is small in names and enormous in
        machines, which is what lets its pointers be cached for days without anyone worrying about load.""")
        # --- the packet
        self.play(FadeOut(VGroup(names, nl, world, sites, sl, you, yl, path, al)), run_time=0.5)
        pkt = VGroup(Rectangle(width=9.0, height=1.0, stroke_color=NAME, stroke_width=2.4, fill_color=NAME, fill_opacity=0.08),
                     label("header: id, flags (RD, RA, TC), counts", 18, TEXT), label("question: name, type, class", 18, NAME))
        pkt[1].move_to(pkt[0].get_center() + UP * 0.22); pkt[2].move_to(pkt[0].get_center() + DOWN * 0.22)
        pkt.move_to([0, 1.5, 0])
        pl = label("a question: one UDP packet to port 53", 16, MUTED).next_to(pkt, UP, buff=0.15)
        self.play(FadeIn(pkt), FadeIn(pl), run_time=0.6)
        ans = VGroup(Rectangle(width=9.0, height=1.6, stroke_color=ADDRESS, stroke_width=2.4, fill_color=ADDRESS, fill_opacity=0.08),
                     label("answer records", 18, ADDRESS), label("authority records: the NS pointers", 18, ZONE), label("additional records: glue, the servers' addresses", 18, ZONE))
        for i, m in enumerate(ans[1:]):
            m.move_to(ans[0].get_center() + UP * (0.45 - 0.45 * i))
        ans.move_to([0, -0.6, 0])
        limit = label("512 bytes in the classic UDP answer; longer sets the TC flag, and the client asks again over TCP", 16, MUTED).next_to(ans, DOWN, buff=0.2)
        self.play(FadeIn(ans), run_time=0.6)
        self.play(FadeIn(limit), run_time=0.4)
        self.next_slide("""The messages themselves are small. A question is a single UDP packet to port 53: a header with an id and a few
        flags, and one question: a name, a type, a class. An answer carries three lists: the answer records, the
        authority records, which is where the pointers of a referral travel, and the additional records, which is where
        the glue addresses of those servers travel so that the resolver need not look them up. The classic limit is 512
        bytes; a server with more to say sets the truncation flag, and the client repeats the question over TCP. One
        packet each way is why a cache hit at the resolver is answered in the time it takes a packet to cross a building.""")
        # --- the two rules on the picture
        self.play(FadeOut(VGroup(pkt, pl, ans, limit)), run_time=0.5)
        root = zone_box(".  the root zone", "pointers to 1,393 top-level domains, kept for 6 days", Y_ROOT)
        tld = zone_box("com.", "pointers to its names' servers, kept for 2 days", Y_TLD)
        auth = zone_box("example.com.", "the addresses, kept for 5 minutes", Y_AUTH)
        client = client_box(0.4)
        res = resolver_box(-0.1)
        self.play(FadeIn(root), FadeIn(tld), FadeIn(auth), FadeIn(client), FadeIn(res), run_time=0.7)
        rules = VGroup(label("every answer is the address, or a pointer to who to ask next", 20, TEXT, thread=True),
                       label("every level remembers what it heard for exactly as long as it was told to", 20, TEXT, thread=True)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([0, -2.95, 0])
        self.play(FadeIn(rules[0]), run_time=0.5)
        for a, b, col in ((res, root, ZONE), (res, tld, ZONE), (res, auth, ADDRESS)):
            question(self, a, b, run_time=0.25)
            answer(self, b, a, col, run_time=0.25)
        self.play(FadeIn(rules[1]), run_time=0.5)
        self.finish("""The whole picture once more, with the two rules written under it. A name is a path; each level of the path is a
        zone someone owns, holding pointers to the level below; a lookup walks the pointers until one answer is the
        address. Every party that hears an answer keeps it for exactly as long as the answer said, so the top of the
        tree is asked rarely and the bottom often, changes arrive by expiry and never by push, and a "no" is remembered
        like a "yes". When a name resolves differently in two offices, when a change takes an hour to land, when a typo
        is slow once and fast after: you are watching the two rules. Thank you.""")
