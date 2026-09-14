"""Move 1: the problem. Names have to become addresses, and the obvious design, one list everybody holds, fails in
two ways as it grows: the list is too big to give everyone, and a change has to reach every copy.

  Final frame: the laptop on the left asking for a name; a list of name -> address rows in the centre that has grown
  off the frame; three more copies of the list around it, one of them stale after an edit; a counter of names.
  Clicks: 1 one laptop, one small list, a lookup succeeds  2 the list grows to the size of the internet
  3 copies everywhere, and one change must reach all of them
"""
from lib.palette import *
from objects import *

HOSTS = [("www.example.com", "104.20.23.154"), ("mail.example.com", "104.20.23.160"), ("intranet", "10.0.0.7"), ("printer", "10.0.0.9")]


def hosts_list(rows, x: float, y: float, width: float = 3.4) -> VGroup:
    g = VGroup(*[record(n, "", a, color=ADDRESS, width=width) for n, a in rows]).arrange(DOWN, buff=0.04).move_to([x, y, 0])
    for r in g:
        r[0].set_fill(TEXT, 0.06)
    return g


class OneList(TalkSlide):
    def construct(self):
        t = title(self, "One list for the whole internet", "1  one list for the whole internet")
        client = client_box(0.3)
        lst = hosts_list(HOSTS, -1.2, 0.3)
        ll = label("a list every machine holds: name, address", 14, MUTED).next_to(lst, UP, buff=0.12)
        self.play(FadeIn(client), FadeIn(lst), FadeIn(ll), run_time=0.6)
        question(self, client, lst, "www.example.com?")
        self.play(lst[0][0].animate.set_fill(ADDRESS, 0.35), run_time=0.3)
        answer(self, lst, client, ADDRESS, "104.20.23.154")
        self.play(lst[0][0].animate.set_fill(TEXT, 0.06), run_time=0.3)
        self.next_slide("""Start with the job. A program has a name, www.example.com, and needs an address, because packets are sent to
        addresses, not names. The first design, and the one the early internet ran on, is a list: every machine keeps a
        file of names and addresses and looks the name up. The lookup is a table scan. It works, and it is what your
        laptop still does first: the hosts file is that list, four lines long today.""")
        # --- the list grows
        more = hosts_list([(f"host{i:03d}.example.net", f"203.0.113.{i % 250}") for i in range(30)], -1.2, 0.3)
        big = VGroup(*lst, *more).arrange(DOWN, buff=0.04).move_to([-1.2, -5.0, 0], aligned_edge=UP).shift(UP * 3.1)
        count = Counter("names in the list", 4, "", TEXT, size=24).move_to([2.6, 1.6, 0], aligned_edge=LEFT)
        cl = label("every one of them on every machine", 14, MUTED).next_to(count, DOWN, buff=0.08).align_to(count, LEFT)
        self.play(FadeIn(count), run_time=0.3)
        self.play(FadeIn(more, lag_ratio=0.02), count.to(340_000_000), run_time=2.0)
        self.play(FadeIn(cl), run_time=0.3)
        self.next_slide("""Now the internet grows. Hundreds of millions of names under .com alone. The list is the size of the internet and
        every machine needs the whole of it, because any machine may ask for any name. That is the first failure: size.
        Nobody can hold the list, and nobody can hand it out fast enough to keep it current.""")
        # --- copies and a change
        copies = VGroup(*[hosts_list(HOSTS[:3], x, y, width=2.2).scale(0.75) for x, y in ((3.6, 0.9), (5.6, 0.0), (3.6, -1.1), (5.6, -2.0))])
        cpl = label("copies", 13, MUTED).next_to(copies, UP, buff=0.1)
        self.play(FadeIn(copies, lag_ratio=0.1), FadeIn(cpl), run_time=0.8)
        edit = lst[0][3]
        new = label("104.20.24.1", 13, HOT).move_to(edit, aligned_edge=LEFT)
        self.play(Transform(edit, new), lst[0][0].animate.set_fill(HOT, 0.2), run_time=0.6)
        for c in copies[:2]:
            self.play(c[0][0].animate.set_fill(HOT, 0.25), Transform(c[0][3], label("104.20.24.1", 13, HOT).scale(0.75).move_to(c[0][3], aligned_edge=LEFT)), run_time=0.35)
        stale = label("still the old address", 13, HOT).next_to(copies[3], RIGHT, buff=0.15)
        self.play(FadeIn(stale), copies[2][0][0].animate.set_fill(DIM, 0.3), copies[3][0][0].animate.set_fill(DIM, 0.3), run_time=0.5)
        self.finish("""The second failure is change. The owner of example.com moves it to a new address and edits the master list. Every
        copy in the world is now wrong until it is replaced, and there is no way to know which copies have been replaced.
        Two copies here have the new address; two still have the old one, and will send traffic to a machine that is
        gone. So a design that scales has to do two things: split the list so that nobody holds all of it, and make the
        answer say how long it may be trusted. Those are the two rules of the talk, and the next move is the first.""")
