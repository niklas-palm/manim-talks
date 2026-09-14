"""A worked example scene that uses most of the library, to copy from and then delete. It is the first scene of the
deck, so it opens on the first picture: there is no title slide, the speaker introduces the talk over this frame.
Storyboard first, as a comment like this one:

  Final frame: a client (left), a server box with five slots (centre), a store (right); a gauge for the server's
  load at the far right; a counter of requests served at the bottom right; a quiet caption.
  Clicks: 1 the still picture: client, server, gauge, counter  2 one request travels and is served  3 five requests arrive together, slots fill,
  gauge climbs  4 camera zooms into the server, a slot opens to show what a request holds  5 back out; a store
  appears and the server writes to it, counter runs.

Every step: labels first, then the animation, then the note.
"""
from lib.palette import *
from objects import *

ZOOM = 0.45


class Example(TalkSlide):
    def construct(self):
        frame = self.camera.frame
        t = title(self, "A request through the system", "1  the problem")   # the deck's first frame: the only title that is written in
        # --- fixed furniture at fixed coordinates
        client = node("client", CLIENT, w=1.8).move_to([-4.6, 0.4, 0])
        server = machine("server").move_to([0.0, 0.4, 0])
        load = Gauge("load", HOTC, 1.6).move_to([5.0, 0.6, 0])
        served = Counter("requests served", 0, "", DATA, size=22).move_to([3.6, -2.0, 0], aligned_edge=LEFT)
        self.play(FadeIn(client), FadeIn(server), FadeIn(load), FadeIn(served), run_time=0.6)
        a1 = arrow(client, server, "one request", MUTED)
        self.play(Create(a1[0]), FadeIn(a1[1]), run_time=0.5)
        self.next_slide("""The still picture first, nothing moving: a client, a server with five slots, a load gauge, a counter. Name what
        is on screen; the first request travels on the next click.""")
        travel(self, client, server, CLIENT, flash=SERVER)          # the unit of motion: a dot from a to b
        self.play(server[2][0].animate.set_fill(CLIENT, 0.9), load.set(0.2), served.to(1), run_time=0.6)
        self.next_slide("""The simplest picture: one client, one server, one request. The request travels, the server takes it into a
        slot, the load gauge moves a little, the counter says one. Everything the talk will say is a change to this
        picture.""")
        # --- many at once: the same objects, more of them
        burst = tokens(5, CLIENT, side=0.22, gap=0.06).next_to(client, UP, buff=0.3)
        self.play(FadeIn(burst, shift=DOWN * 0.1), run_time=0.4)
        for k in range(1, 5):
            self.play(burst[k].animate.move_to(server[2][k].get_center()).scale(0.9), run_time=0.25)
            last = [FadeOut(burst[0])] if k == 4 else []   # fading a member restructures the group, so the group cannot be removed as one; fade the members
            self.play(server[2][k].animate.set_fill(CLIENT, 0.9), FadeOut(burst[k]), *last, load.set(0.2 + 0.2 * k), served.to(1 + k), run_time=0.2)
        self.next_slide("""Five requests arrive together. Same picture, more of it: each takes a slot, the gauge climbs with every one,
        and the fifth fills the server. The problem the next scene solves is now visible: the gauge is red.""")
        # --- zoom to open: the same box, its inside drawn where the audience was looking
        others = VGroup(client, a1, load, served, t)
        self.play(frame.animate.scale(ZOOM).move_to(server.get_center()), FadeOut(others), server[0].animate.stretch_to_fit_height(2.2), run_time=1.2)
        inside = VGroup(grid(4, 6, DATA, cell=0.07).move_to(server.get_center() + DOWN * 0.15),
                        small("what a request holds: 24 cells of state", STATE))
        inside[1].next_to(inside[0], UP, buff=0.06)
        self.play(FadeIn(inside), run_time=0.5)
        self.next_slide("""Zoom in and the box opens: this is what one request occupies while it is being served. Small text here is
        rendered large and scaled down, so it stays crisp.""")
        self.play(FadeOut(inside), run_time=0.4)                     # clear first, then pull back on a clean box
        self.play(frame.animate.scale(1 / ZOOM).move_to(ORIGIN), server[0].animate.stretch_to_fit_height(1.4), FadeIn(others), run_time=1.2)
        # --- grow: a new object joins the picture; nothing is replaced
        store = node("store", STATE, w=1.8, sub="durable").move_to([4.6, 0.4, 0])
        self.play(FadeIn(store), load.animate.shift(RIGHT * 1.4), run_time=0.6)
        a2 = arrow(server, store, "write", STATE)
        self.play(Create(a2[0]), FadeIn(a2[1]), run_time=0.5)
        cap = caption(self, "Every served request leaves a record in the store")
        for k in range(5):
            travel(self, server, store, DATA, run_time=0.3)
            self.play(server[2][k].animate.set_fill(DIM, 0.0), run_time=0.1)
        self.play(load.set(0.05), run_time=0.5)
        self.finish("""Back out, and the picture grows to the right: a store, and every served request leaves a record in it as its
        slot empties. The caption is one quiet line, set before the animation. The next scene starts from exactly this
        frame.""")
