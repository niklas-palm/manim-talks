"""Move 2: delegation. The name is a path from the root; each level is a zone owned by someone who holds only pointers to
the levels below; a lookup walks the path, and every answer on the way is a pointer until the last one is the address.

  Final frame: the laptop (left), the recursive resolver (centre) with an empty cache area, three zone boxes stacked on
  the right (root, com, example.com) each holding the records it is authoritative for; the two actors named.
  Clicks: 1 the name is split into labels, right to left, and becomes a path  2 each level is a zone with its owner,
  holding pointers (NS records) to the level below  3 the two actors: stub asks one question, the resolver walks
  4 hop one: the root answers with a pointer to com  5 hop two: com answers with a pointer to example.com
  6 hop three: example.com answers with the address; it travels home
"""
from lib.palette import *
from objects import *


class Delegation(TalkSlide):
    def construct(self):
        t = title(self, "Delegation: the name is a path", "2  delegation: the name is a path")
        # --- the name, split into labels right to left
        name = label("www.example.com.", 48, NAME).move_to([0, 1.4, 0])
        self.play(Write(name), run_time=0.8)
        parts = [("www", 0, 3), ("example", 4, 11), ("com", 12, 15), (".", 15, 16)]
        boxes = VGroup()
        for text, a, b in reversed(parts):
            sub = VGroup(*name[a:b])
            br = SurroundingRectangle(sub, color=ZONE, buff=0.06, stroke_width=1.5)
            boxes.add(br)
            self.play(Create(br), run_time=0.3)
        dot_note = label("read from the right: the last dot is the root", 18, MUTED).next_to(name, DOWN, buff=0.4)
        self.play(FadeIn(dot_note), run_time=0.4)
        self.next_slide("""Split the list along the name itself. A name is read from the right: the final dot, usually invisible, is the
        root of the whole tree; then com, one of 1,393 top-level domains; then example, a name registered under com;
        then www, a host inside it. Each label is one level, and the levels nest, so a name is a path from the root down
        to the thing you want. RFC 1034 wrote the tree this way in 1987, and it has not changed.""")
        # --- each level is a zone with an owner, holding pointers to the level below
        self.play(FadeOut(boxes), FadeOut(dot_note), name.animate.scale(0.6).to_edge(UP, buff=1.15), run_time=0.7)
        (root, tld, auth), (r_root, r_tld, r_auth) = tree()
        self.play(FadeIn(root), run_time=0.4)
        self.play(FadeIn(r_root), run_time=0.4)
        self.play(FadeIn(tld), FadeIn(r_tld), run_time=0.5)
        self.play(FadeIn(auth), FadeIn(r_auth), run_time=0.5)
        ptr1 = Arrow(r_root[2].get_bottom(), tld[1].get_top() + RIGHT * 0.3, color=ZONE, stroke_width=2, buff=0.05, tip_length=0.15)
        ptr2 = Arrow(r_tld[2].get_bottom(), auth[1].get_top() + RIGHT * 0.3, color=ZONE, stroke_width=2, buff=0.05, tip_length=0.15)
        self.play(Create(ptr1), Create(ptr2), run_time=0.6)
        self.next_slide("""Each level is a zone: a piece of the name space that one party is authoritative for, served from that party's
        servers. The root zone is run by twelve organisations on thirteen server names, spread today over 2,045 anycast
        instances. The com zone is run by a registry. The example.com zone is run by whoever registered it, on servers
        they chose. Look at what each zone holds. The root does not know the address of www.example.com; it holds one kind
        of record about com: an NS record, a pointer saying "com's servers are these". The com zone holds the same kind of
        pointer for example.com. Only the bottom zone holds the address, an A record. A zone holds the pointers to the
        zones below it and nothing else about them: that is delegation, and it is why nobody has to hold the whole list.
        The number at the right of each record is its time to live; hold that thought for move three.""")
        # --- the two actors
        client = client_box(0.4)
        res = resolver_box(-0.1)
        self.play(FadeIn(client), FadeIn(res), run_time=0.6)
        a1 = arrow(client, res, "", MUTED)
        al = label("one question, one answer", 15, MUTED).next_to(client, DOWN, buff=0.12)
        self.play(Create(a1[0]), FadeIn(al), run_time=0.5)
        self.next_slide("""Two actors do the asking. Your laptop's stub resolver, a library inside the operating system, asks exactly one
        question and waits for one answer: it sets the recursion-desired bit and lets someone else do the work. That
        someone is the recursive resolver, usually run by your network, your company, or a public service such as
        1.1.1.1 or 8.8.8.8. It walks the tree on your behalf, and it has a cache, which is the whole of move three. Watch
        the walk.""")
        # --- hop one: the root
        question(self, res, root, "www.example.com?")
        self.play(r_root[0].animate.set_fill(ZONE, 0.35), run_time=0.3)
        answer(self, root, res, ZONE, "not mine: ask com's servers")
        self.play(r_root[0].animate.set_fill(ZONE, 0.10), run_time=0.2)
        c1 = cache_row(r_root, 0.85)
        self.play(FadeIn(c1), run_time=0.4)
        self.next_slide("""Hop one. The resolver knows the root servers' addresses by configuration; that is the one list everyone does
        hold, and it is thirteen lines long. It asks a root server the full question. The root is not authoritative for
        the name and says so with a referral: an NS record, a pointer to com's servers, with their addresses attached as
        glue so the resolver does not need a second lookup to find them. The resolver keeps the pointer; it will be worth a
        great deal.""")
        # --- hop two: com
        question(self, res, tld, "www.example.com?")
        self.play(r_tld[0].animate.set_fill(ZONE, 0.35), run_time=0.3)
        answer(self, tld, res, ZONE, "not mine: ask example.com's servers")
        self.play(r_tld[0].animate.set_fill(ZONE, 0.10), run_time=0.2)
        c2 = cache_row(r_tld, 0.3)
        self.play(FadeIn(c2), run_time=0.4)
        self.next_slide("""Hop two. The same question to one of com's servers. Com is not authoritative for www.example.com either; it
        holds the pointer to example.com's servers, hera and elliott at Cloudflare in this case, and returns it. Another
        referral, another record kept. Every answer so far has been a pointer to who to ask next: rule one.""")
        # --- hop three: the address
        question(self, res, auth, "www.example.com?")
        self.play(r_auth[0].animate.set_fill(ADDRESS, 0.35), run_time=0.3)
        answer(self, auth, res, ADDRESS, "104.20.23.154")
        self.play(r_auth[0].animate.set_fill(ADDRESS, 0.10), run_time=0.2)
        c3 = cache_row(r_auth, -0.25)
        self.play(FadeIn(c3), run_time=0.4)
        answer(self, res, client, ADDRESS, "104.20.23.154")
        self.play(Flash(client[0], color=ADDRESS, flash_radius=1.2, num_lines=8), run_time=0.4)
        self.finish("""Hop three. The example.com servers are authoritative for the name: they hold the A record and return the address.
        The resolver keeps it and sends it home to the laptop, which never saw the walk: one question out, one answer
        back. Three round trips to three different organisations to turn one name into one address, and none of them held
        the whole list. That is delegation. It solved size. It made every lookup three times slower than a table scan, and
        the root servers would answer every lookup on earth. Rule two fixes both.""")
