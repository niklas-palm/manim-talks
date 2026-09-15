"""Move 2: loops that chase the gap.

  Final frame: the stage from move one plus two control loops (Deployment controller, ReplicaSet controller) watching
  the API server; etcd holds Deployment, ReplicaSet and three Pod records marked "no node"; nodes still empty.
  Clicks: 1 the Deployment controller: observe, compare, act: a ReplicaSet record  2 the ReplicaSet controller, opened
  under a zoom: wants 3, has 0, gap 3  3 back out: it acts three times, three Pod records with no node  4 every line
  points at the API server.
"""
from lib.palette import *
from objects import *

ZOOM = 0.45


class Controllers(TalkSlide):
    def construct(self):
        frame = self.camera.frame
        t = title_still(self, "kubectl apply writes a record, not a process", "1  a record, not a process")   # move one's last frame, still
        S = Stage(controllers=[("deploy", "Deployment controller"), ("rs", "ReplicaSet controller")])
        S.add_card("deploy", "Deployment", "3 replicas, v1", 0)
        self.add(*S.base(S.cards["deploy"]))
        # --- the title changes as the Deployment controller appears: no cut
        c1, w1 = S.ctrl["deploy"], S.watches["deploy"]
        t = retitle(self, t, "Controllers: loops that chase the gap", "2  loops that chase the gap", extra=[FadeIn(c1), Create(w1[0]), FadeIn(w1[1])])
        self.next_slide("""Where the last scene ended: the Deployment record sits in etcd, the nodes are empty, three desired and
        none running. One new thing on screen, and it is not moving yet: the Deployment controller, a box with a loop drawn in
        it, hanging over the API server on a dashed line labelled watch. It has not done anything. Next click, it does.""")
        pulse(self, S.cards["deploy"], c1[2], run_time=0.6)            # observe, slowly the first time
        cmp = label("wants 1, has 0", 15, TEXT).next_to(c1, UP, buff=GAP_TIGHT).align_to(c1, LEFT)
        self.play(FadeIn(cmp), run_time=0.3)
        rs = card("ReplicaSet", "3 replicas, v1").scale(0.7).move_to(c1[2].get_center())
        self.play(FadeIn(rs), run_time=0.3)
        self.play(rs.animate.move_to(door(c1)), run_time=0.5)   # act: down into the API server, then into the store
        self.play(rs.animate.scale(1 / 0.7).move_to(S.slots[1]), run_time=0.6)
        S.cards["rs"] = rs
        cmp2 = label("wants 1, has 1", 15, MUTED).move_to(cmp)
        self.play(FadeOut(cmp), FadeIn(cmp2), run_time=0.3)
        self.next_slide("""A controller is a loop with three verbs: observe, compare, act. It watches the API server for records of one
        kind, compares what the records ask for with what exists, and if there is a gap, acts, by writing another record
        through the same API server. The Deployment controller observes our Deployment, compares: it should own one
        ReplicaSet with this template, it owns none, and acts: it creates that ReplicaSet record, replicas three, image
        v1. Then it observes again, and now there is nothing to do, so it waits. It never started a container; it wrote
        a record.""")
        # --- the ReplicaSet controller, opened under the zoom
        c2, w2 = S.ctrl["rs"], S.watches["rs"]
        self.play(FadeOut(cmp2), FadeIn(c2), Create(w2), run_time=0.7)
        pulse(self, rs, c2[2])
        wide = VGroup(t, *S.base(), c1, w1, w2, *S.cards.values())
        OPEN_W, OPEN_H = 3.2, 2.2                                             # the box opens downward and sideways over the faded stage
        cx, top = c2[0].get_center()[0], c2[0].get_top()[1]
        self.play(frame.animate.scale(ZOOM).move_to([cx, top - OPEN_H / 2, 0]), FadeOut(wide), FadeOut(c2[2]),
                  c2[0].animate.stretch_to_fit_height(OPEN_H).stretch_to_fit_width(OPEN_W).shift(DOWN * (OPEN_H - H_ROW) / 2),
                  c2[1].animate.shift(LEFT * (OPEN_W - W_CTRL) / 2), run_time=1.2)
        lx = cx - OPEN_W / 2 + 0.15
        verbs = label("observe, compare, act", 15, MUTED).scale(0.6).move_to([lx, top - 1.02, 0], aligned_edge=LEFT)   # the three verbs, named once, on the loop that is open
        wants = Counter("wants", 3, "", DESIRED, size=16).move_to([lx, top - 1.5, 0], aligned_edge=LEFT)
        has = Counter("has", 0, "", ACTUAL, size=16).move_to([lx + 0.95, top - 1.5, 0], aligned_edge=LEFT)
        gap = Counter("gap", 3, "", HOT, size=16).move_to([lx + 1.9, top - 1.5, 0], aligned_edge=LEFT)
        act = label("act: 3 Pod records", 20, CONTROL).scale(0.5).move_to([lx, top - 2.0, 0], aligned_edge=LEFT)
        self.play(FadeIn(verbs), run_time=0.4)
        self.play(FadeIn(wants), FadeIn(has), FadeIn(gap), run_time=0.5)
        self.play(FadeIn(act), run_time=0.4)
        self.wait(0.3)
        self.next_slide("""The ReplicaSet controller is the same loop for a different record. Open it up and read it: observe, compare,
        act. It wants three Pods that match the template, it has zero, so the gap is three, and the act it is about to take is
        three Pod records. Every controller in the cluster is this shape; only the record kind and the arithmetic differ.""")
        # --- back out, and the act lands: three Pod records
        self.play(FadeOut(VGroup(verbs, wants, has, gap, act)), run_time=0.3)
        self.play(frame.animate.scale(1 / ZOOM).move_to(ORIGIN), FadeIn(wide), FadeIn(c2[2]),
                  c2[0].animate.stretch_to_fit_height(H_ROW).stretch_to_fit_width(W_CTRL).shift(UP * (OPEN_H - H_ROW) / 2),
                  c2[1].animate.shift(RIGHT * (OPEN_W - W_CTRL) / 2), run_time=1.2)
        for i, name in enumerate("abc"):
            p = card(f"Pod {name}", "no node").scale(0.7).move_to(c2[2].get_center())
            p[2].set_color(HOT)
            self.play(FadeIn(p), run_time=0.15)
            self.play(p.animate.move_to(door(c2)), run_time=0.3)
            self.play(p.animate.scale(1 / 0.7).move_to(S.slots[2 + i]), run_time=0.35)
            S.cards[name] = p
        self.next_slide("""Back out, and the loop acts three times: three Pod records land in etcd. Read the status line on each: no
        node. A Pod record is still a description; nothing has been placed anywhere and nothing runs. The counter at the
        bottom still says zero. Two loops have run, and all they produced was more records.""")
        # --- every line points at the API server
        lines = VGroup(w1[0], w2[0])
        self.play(*[ln.animate.set_stroke(color=TEXT, opacity=1.0, width=3.2) for ln in lines], S.api[0].animate.set_stroke(width=4), run_time=0.6)
        self.wait(0.5)
        self.play(*[ln.animate.set_stroke(color=CONTROL, opacity=0.7, width=1.8) for ln in lines], S.api[0].animate.set_stroke(width=2.5), run_time=0.6)
        self.finish("""One more thing to see before anything runs: the lines. Both loops watch the API server and write to the API
        server. They do not talk to each other, they do not talk to nodes, they do not know the other exists. The
        Deployment controller does not know what a node is. That is why the pieces can be simple and can fail: kill the
        ReplicaSet controller and the records wait for it; restart it and it observes, compares, and carries on. The
        database is the coordination. Now: something has to turn a Pod record into a process.""")
