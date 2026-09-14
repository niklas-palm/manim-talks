"""Move 2: delegation. The name is a path from the root; each level is a zone owned by someone who holds only pointers to
the levels below; a lookup walks the path, and every answer on the way is a pointer until the last one is the address.

  Final frame (move three starts from it): the laptop (left), the recursive resolver (centre) with three cached rows,
  three zone boxes stacked on the right (root, com, example.com) with their records and the pointers between them.
  Clicks: 1 move one's picture gives way to one large name  2 the name is split into labels, right to left, and becomes a path  2 each level is a zone with its owner,
  holding pointers (NS records) to the level below  3 the two actors: stub asks one question, the resolver walks
  4 hop one: the root answers with a pointer to com  5 hop two: com answers with a pointer to example.com
  6 hop three: example.com answers with the address; it travels home
"""
from lib.palette import *
from objects import *


class Delegation(TalkSlide):
    def construct(self):
        # --- the last frame of move one, rebuilt: nothing may look different at the boundary
        t = title_still(self, "One list for the whole internet", "1  one list for the whole internet")
        e = list_end_state()
        client = e["client"]
        self.add(*e.values())
        # --- the first change: the lists go, and the first name of the list grows into the name we will read
        name = label("www.example.com.", 60, NAME).move_to([0, 1.1, 0])
        seed = e["lst"][0][1].copy()
        e["count"].num.clear_updaters()   # a counter redraws its digits every frame; without this it survives its own fade
        gone = VGroup(e["lst"], e["ll"], e["more"], e["count"], e["cl"], e["copies"], e["cpl"], e["stale"])
        t = retitle(self, t, "Delegation: the name is a path", "2  delegation: the name is a path", extra=[FadeOut(gone), ReplacementTransform(seed, name)], run_time=0.9)
        self.next_slide("""The list is gone; one name from it stays and grows, with the dot at the end that is usually invisible, and the
        laptop that wanted its address is still there. Nothing else yet. Look at the name itself before the machinery:
        it is not one word, it is a path, and the next click reads it the way DNS does.""")
        parts = [("www", 0, 3), ("example", 4, 11), ("com", 12, 15), (".", 15, 16)]
        boxes = VGroup()
        for text, a, b in reversed(parts):
            sub = VGroup(*name[a:b])
            br = SurroundingRectangle(sub, color=ZONE, buff=0.06, stroke_width=sw(0.6))
            boxes.add(br)
            self.play(Create(br), run_time=0.3)
        dot_note = label("read from the right: the last dot is the root", 20, MUTED).next_to(name, DOWN, buff=GAP_WIDE)
        self.play(FadeIn(dot_note), run_time=0.4)
        self.next_slide("""Split the list along the name itself. A name is read from the right: the final dot, usually invisible, is the
        root of the whole tree; then com, one of 1,393 top-level domains; then example, a name registered under com;
        then www, a host inside it. Each label is one level, and the levels nest, so a name is a path from the root down
        to the thing you want. RFC 1034 wrote the tree this way in 1987, and it has not changed.""")
        # --- each level is a zone with an owner, holding pointers to the level below
        self.play(FadeOut(boxes), FadeOut(dot_note), FadeOut(name), run_time=0.7)
        (root, tld, auth), (r_root, r_tld, r_auth) = tree()
        self.play(FadeIn(root), run_time=0.4)
        self.play(FadeIn(r_root), run_time=0.4)
        self.play(FadeIn(tld), FadeIn(r_tld), run_time=0.5)
        self.play(FadeIn(auth), FadeIn(r_auth), run_time=0.5)
        ptrs = delegation_pointers(VGroup(r_root, r_tld, r_auth), VGroup(root, tld, auth))
        self.play(Create(ptrs[0]), Create(ptrs[1]), run_time=0.6)
        self.next_slide("""Each level is a zone: a piece of the name space that one party is authoritative for, served from that party's
        servers. The root zone is run by twelve organisations on thirteen server names, spread today over 2,045 anycast
        instances. The com zone is run by a registry. The example.com zone is run by whoever registered it, on servers
        they chose. Look at what each zone holds. The root does not know the address of www.example.com; it holds one kind
        of record about com: an NS record, a pointer saying "com's servers are these". The com zone holds the same kind of
        pointer for example.com. Only the bottom zone holds the address, an A record. A zone holds the pointers to the
        zones below it and nothing else about them: that is delegation, and it is why nobody has to hold the whole list.
        The number at the right of each record is its time to live; hold that thought for move three.""")
        # --- the two actors: the laptop moves to its place beside the resolver
        res = resolver_box()
        self.play(client.animate.move_to([X_CLIENT, Y_RESOLVER, 0]), FadeIn(res), run_time=0.6)
        a1 = client_link(client, res)
        al = label("one question, one answer", 15, MUTED).next_to(client, DOWN, buff=GAP_TIGHT)
        self.play(Create(a1[0]), FadeIn(al), run_time=0.5)
        self.next_slide("""Two actors do the asking. Your laptop's stub resolver, a library inside the operating system, asks exactly one
        question and waits for one answer: it sets the recursion-desired bit and lets someone else do the work. That
        someone is the recursive resolver, usually run by your network, your company, or a public service such as
        1.1.1.1 or 8.8.8.8. It walks the tree on your behalf, and it has a cache, which is the whole of move three. Watch
        the walk.""")
        # --- hop one: the root
        question(self, res[1], r_root, "www.example.com?")
        self.play(r_root[0].animate.set_fill(ZONE, 0.35), run_time=0.3)
        c1 = cache_row(r_root, CACHE_Y[0])
        answer(self, r_root, res, ZONE, "not mine: ask com's servers", becomes=c1)   # the pointer lands on the row it becomes
        self.play(r_root[0].animate.set_fill(ZONE, 0.10), run_time=0.2)
        self.next_slide("""Hop one. The resolver knows the root servers' addresses by configuration; that is the one list everyone does
        hold, and it is thirteen lines long. It asks a root server the full question. The root is not authoritative for
        the name and says so with a referral: an NS record, a pointer to com's servers, with their addresses attached as
        glue so the resolver does not need a second lookup to find them. The resolver keeps the pointer; it will be worth a
        great deal.""")
        # --- hop two: com
        question(self, res[1], r_tld, "www.example.com?")
        self.play(r_tld[0].animate.set_fill(ZONE, 0.35), run_time=0.3)
        c2 = cache_row(r_tld, CACHE_Y[1])
        answer(self, r_tld, res, ZONE, "not mine: ask example.com's servers", becomes=c2)
        self.play(r_tld[0].animate.set_fill(ZONE, 0.10), run_time=0.2)
        self.next_slide("""Hop two. The same question to one of com's servers. Com is not authoritative for www.example.com either; it
        holds the pointer to example.com's servers, hera and elliott at Cloudflare in this case, and returns it. Another
        referral, another record kept. Every answer so far has been a pointer to who to ask next: rule one.""")
        # --- hop three: the address
        question(self, res[1], r_auth, "www.example.com?")
        self.play(r_auth[0].animate.set_fill(ADDRESS, 0.35), run_time=0.3)
        c3 = cache_row(r_auth, CACHE_Y[2])
        answer(self, r_auth, res, ADDRESS, "104.20.23.154", becomes=c3)
        self.play(r_auth[0].animate.set_fill(ADDRESS, 0.10), run_time=0.2)
        answer(self, c3, client, ADDRESS, "104.20.23.154")   # from the row that holds it to the laptop that asked
        self.play(Flash(client[0], color=ADDRESS, flash_radius=1.2, num_lines=8), run_time=0.4)
        self.finish("""Hop three. The example.com servers are authoritative for the name: they hold the A record and return the address.
        The resolver keeps it and sends it home to the laptop, which never saw the walk: one question out, one answer
        back. Three round trips to three different organisations to turn one name into one address, and none of them held
        the whole list. That is delegation. It solved size. It made every lookup three times slower than a table scan, and
        the root servers would answer every lookup on earth. Rule two fixes both.""")
