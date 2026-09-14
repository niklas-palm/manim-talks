"""Move 1: the problem. Names have to become addresses, and the obvious design, one list everybody holds, fails in
two ways as it grows: the list is too big to give everyone, and a change has to reach every copy.

  Final frame: the laptop on the left; a list of large name -> address rows in the centre that has run off the bottom
  of the frame; a counter of names; three copies of the list at the right, two of them stale after an edit.
  Clicks: 1 one laptop, one short list, a lookup succeeds  2 the list grows past the frame, the counter says how far
  3 copies on other machines; one change reaches some of them
"""
from lib.palette import *
from objects import *

HOSTS = [("www.example.com", "104.20.23.154"), ("mail.example.com", "104.20.23.160"), ("intranet", "10.0.0.7"),
         ("printer", "10.0.0.9"), ("git", "10.0.0.12"), ("wiki", "10.0.0.15")]


def hosts_list(rows, x: float, y: float, width: float = 6.2, size: float = 16) -> VGroup:
    g = VGroup(*[record(n, "", a, color=ADDRESS, width=width, size=size) for n, a in rows]).arrange(DOWN, buff=0.05).move_to([x, y, 0])
    for r in g:
        r[0].set_fill(TEXT, 0.07)
    return g


class OneList(TalkSlide):
    def construct(self):
        t = title(self, "One list for the whole internet", "1  one list for the whole internet")
        client = client_box(0.4)
        lst = hosts_list(HOSTS, -0.9, 0.4)
        ll = label("a list every machine holds: name, address", 16, MUTED).next_to(lst, UP, buff=GAP_TIGHT).align_to(lst, LEFT)
        self.play(FadeIn(client), FadeIn(lst), FadeIn(ll), run_time=0.6)
        question(self, client, lst, "www.example.com?")
        self.play(lst[0][0].animate.set_fill(ADDRESS, 0.4), run_time=0.3)
        answer(self, lst, client, ADDRESS, "104.20.23.154")
        self.play(lst[0][0].animate.set_fill(TEXT, 0.07), run_time=0.3)
        self.next_slide("""Start with the job. A program has a name, www.example.com, and needs an address, because packets are sent to
        addresses, not names. The first design, and the one the early internet ran on, is a list: every machine keeps a
        file of names and addresses and looks the name up. It works, and it is what your laptop still does first: the
        hosts file is that list, a few lines long today.""")
        # --- the list grows past the frame
        more = hosts_list([(f"host{i:03d}.example.net", f"203.0.113.{i}") for i in range(10)], -0.9, 0.0).next_to(lst, DOWN, buff=0.05).align_to(lst, LEFT)
        count = Counter("names in the list", 6, "", TEXT, size=30).move_to([3.0, 2.3, 0], aligned_edge=LEFT)
        cl = label("every one of them, on every machine", 16, MUTED).next_to(count, DOWN, buff=0.1).align_to(count, LEFT)
        self.play(FadeIn(count), run_time=0.3)
        self.play(FadeIn(more, lag_ratio=0.05), count.to(340_000_000), run_time=2.2)
        self.play(FadeIn(cl), run_time=0.3)
        self.next_slide("""Now the internet grows. Hundreds of millions of names under .com alone; the list runs off the bottom of the frame
        and keeps going. Every machine needs the whole of it, because any machine may ask for any name. That is the first
        failure: size. Nobody can hold the list, and nobody can hand it out fast enough to keep it current.""")
        # --- copies and a change
        short = [("www", "104.20.23.154"), ("mail", "104.20.23.160")]
        copies = VGroup(*[hosts_list(short, 4.6, y, width=3.2, size=15) for y in (0.7, -0.55, -1.8)])
        cpl = label("copies on other machines", 15, MUTED).next_to(copies, UP, buff=GAP_TIGHT).align_to(copies, LEFT)
        self.play(FadeIn(copies, lag_ratio=0.1), FadeIn(cpl), run_time=0.8)
        new = label("104.20.24.1", 16, HOT).move_to(lst[0][3], aligned_edge=LEFT)
        self.play(Transform(lst[0][3], new), lst[0][0].animate.set_fill(HOT, 0.25), run_time=0.6)
        c = copies[0]
        self.play(c[0][0].animate.set_fill(HOT, 0.25), Transform(c[0][3], label("104.20.24.1", 15, HOT).move_to(c[0][3], aligned_edge=LEFT)), run_time=0.4)
        stale = label("still the old address", 15, HOT).next_to(copies, DOWN, buff=GAP_TIGHT).align_to(copies, LEFT)
        self.play(FadeIn(stale), copies[1][0][0].animate.set_fill(DIM, 0.35), copies[2][0][0].animate.set_fill(DIM, 0.35), run_time=0.5)
        self.finish("""The second failure is change. The owner of example.com moves it to a new address and edits the master list. Every
        copy in the world is now wrong until it is replaced, and there is no way to know which copies have been. One copy
        here has the new address; two still have the old one, and will send traffic to a machine that is gone. So a design
        that scales has to do two things: split the list so that nobody holds all of it, and make the answer say how long
        it may be trusted. Those are the two rules of the talk, and the next move is the first.""")
