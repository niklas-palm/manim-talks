"""The second scene: how a scene continues the previous one without a cut. Its first frame rebuilds the last frame
of s01_example (the stage plus what that scene left behind) with self.add and title_still, so the video boundary is
invisible; its first play is retitle() with the first change. Run bin/seams.py to see the two frames side by side."""
from lib.palette import *
from objects import *


class Next(TalkSlide):
    def construct(self):
        # --- the previous scene's last frame, rebuilt statically: nothing animates yet
        t = title_still(self, "A request through the system", "1  the problem")
        parts = stage()
        client, server, store = parts["client"], parts["server"], parts["store"]
        load = Gauge("load", HOTC, 1.6).move_to([6.4, 0.6, 0])
        served = Counter("requests served", 5, "", DATA, size=22).move_to([3.6, -2.0, 0], aligned_edge=LEFT)
        cap = caption(self, "Every served request leaves a record in the store")
        self.remove(cap); self.add(cap)                      # caption() plays a FadeIn; for a still frame add it directly
        self.add(client, server, store, parts["client_to_server"], parts["server_to_store"], load, served)
        # --- the first change: the title becomes this move's, and the store starts to fill
        records = tokens(5, DATA, side=0.22, gap=0.06).move_to(store[0].get_center() + DOWN * 0.15)
        t = retitle(self, t, "What the store has to keep", "2  the mechanism", extra=[FadeOut(cap), FadeIn(records)])
        self.next_slide("""The picture did not change at the scene boundary; only the title did, and the records the last move wrote appear
        inside the store. The speaker names the new move over the same picture the audience already understands.""")
        # --- and the move continues to grow the same picture
        self.play(store[0].animate.stretch_to_fit_height(2.0), records.animate.arrange_in_grid(rows=2, cols=3, buff=0.06).move_to(store[0].get_center() + DOWN * 0.3), run_time=0.8)
        self.finish("""The store grows to make room, the records rearrange inside it, and the move goes on from here. Delete these two
        scenes when the real talk's scenes exist; keep their shape.""")
