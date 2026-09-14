"""Move 4: a node dies, and nothing new happens.

  Final frame: the stage with four loops (Deployment, ReplicaSet, scheduler, node controller); node 2 dark with a
  NotReady mark; its pod gone; a new pod d running on node 1; etcd holding the records; 3 desired, 3 running.
  Clicks: 1 heartbeats: every kubelet renews its lease every 10 s  2 node 2 stops; after 40 s the node controller
  marks it NotReady and taints it; the pod tolerates for 300 s, then its record is evicted  3 the ReplicaSet controller
  sees 2 of 3, the scheduler binds a new pod to node 1, the kubelet runs it: the same loops.
"""
from lib.palette import *
from objects import *


class NodeDies(TalkSlide):
    def construct(self):
        t = title(self, "A node dies: the same loops, nothing new", "4  a node dies")
        S = Stage(node_used=(0.8, 0.8, 0.95), controllers=[("deploy", "Deployment controller"), ("rs", "ReplicaSet controller"), ("sched", "scheduler"), ("extra", "node controller")])
        S.add_card("deploy", "Deployment web", "3 replicas, v1", 0)
        S.add_card("rs", "ReplicaSet web", "3 replicas, v1", 1)
        for i, (nm, where) in enumerate((("a", "node 1"), ("b", "node 2"), ("c", "node 1"))):
            c = S.add_card(nm, f"Pod web-7d4f-{nm}", f"{where}, Running", 2 + i)
            c[0].set_stroke(color=ACTUAL); c[2].set_color(ACTUAL)
        pods = {"a": S.place_pod(0, 0), "b": S.place_pod(1, 0), "c": S.place_pod(0, 1)}
        S.running.tracker.set_value(3)
        kw = [watch(n, S.api, NODE) for n in S.nodes]
        for n in S.nodes:
            n[5].set_color(TEAL)
        self.add(S.client, S.api, S.store, S.nodes, S.desired, S.running, *[S.ctrl[k] for k in ("deploy", "rs", "sched")], *[S.watches[k] for k in ("deploy", "rs", "sched")], *S.cards.values(), *pods.values(), *kw)
        # --- heartbeats
        hb = label("each kubelet renews its lease every 10 s", 13, MUTED).move_to([X_NODE, 2.55, 0])
        self.play(FadeIn(hb), run_time=0.3)
        for _ in range(2):
            dots = [Dot(color=TEAL, radius=0.06).move_to(n[5].get_center()) for n in S.nodes]
            self.add(*dots)
            self.play(*[d.animate.move_to(S.api[0].get_right()) for d in dots], run_time=0.6)
            self.play(*[FadeOut(d) for d in dots], run_time=0.15)
            self.wait(0.2)
        self.next_slide("""Three running, three desired, and the loops idle. One more loop was working all along, quietly: every kubelet
        tells the API server it is alive, renewing a lease every ten seconds, the teal dots. The node controller, part of
        the control plane, watches those leases. Nothing else on this picture depends on it, until a machine goes.""")
        # --- node 2 stops; 40 s to NotReady; 300 s toleration; eviction
        n2 = S.nodes[1]
        nc, wn = S.ctrl["extra"], S.watches["extra"]
        self.play(FadeIn(nc), Create(wn[0]), FadeIn(wn[1]), run_time=0.6)
        self.play(n2[0].animate.set_stroke(color=HOT), n2[5].animate.set_color(HOT), FadeOut(kw[1]), run_time=0.5)
        for _ in range(2):   # the other two keep beating
            dots = [Dot(color=TEAL, radius=0.06).move_to(n[5].get_center()) for n in (S.nodes[0], S.nodes[2])]
            self.add(*dots)
            self.play(*[d.animate.move_to(S.api[0].get_right()) for d in dots], run_time=0.5)
            self.play(*[FadeOut(d) for d in dots], run_time=0.1)
        since = Counter("since node 2's last heartbeat", 0, "s", HOT, size=20).move_to([X_NODE - 1.35, -2.55, 0], aligned_edge=LEFT)
        self.play(FadeIn(since), run_time=0.3)
        self.play(since.to(40), run_time=1.2)
        nr = label("NotReady, tainted", 11, HOT).next_to(n2, DOWN, buff=0.06)
        self.play(FadeIn(nr), n2[0].animate.set_fill(HOT, 0.08), run_time=0.4)
        tol = label("the pod tolerates the taint for 300 s", 11, MUTED).next_to(nr, RIGHT, buff=0.3)
        self.play(FadeIn(tol), run_time=0.3)
        self.play(since.to(340), run_time=1.8)
        pb = S.cards["b"]
        set_detail(self, pb, "evicted", HOT)
        self.play(FadeOut(pods["b"]), pb.animate.set_opacity(0.25), S.running.to(2), FadeOut(tol), run_time=0.6)
        self.next_slide("""Node two goes silent: a kernel panic, a pulled cable, a cloud instance retired. Nothing reports it. What the
        node controller sees is an absence: no lease renewal. It gives the node forty seconds of grace, then marks it
        NotReady and puts a taint on it. Pods carry a default toleration of three hundred seconds for that taint, so for
        five more minutes the picture waits, in case the node comes back. It does not; at three hundred and forty seconds
        the Pod on it is evicted: its record is marked for deletion. Now the counter says two. That is the only thing that
        happened: a record went away and a count dropped.""")
        # --- the same loops close the gap
        self.play(FadeOut(since), FadeOut(nr), run_time=0.3)
        rsc = S.ctrl["rs"]
        pulse = Dot(color=DESIRED, radius=0.07).move_to(S.cards["rs"].get_right())
        self.play(pulse.animate.move_to(rsc[2].get_center()), run_time=0.5)
        self.play(FadeOut(pulse), run_time=0.1)
        cmp = label("wants 3, has 2", 12, TEXT).next_to(rsc, DOWN, buff=0.08)
        self.play(FadeIn(cmp), run_time=0.3)
        pd = card("Pod web-7d4f-d", "no node").scale(0.7).move_to(rsc[2].get_center())
        pd[2].set_color(HOT)
        self.play(FadeIn(pd), run_time=0.2)
        self.play(pd.animate.move_to(S.api[0].get_right() + RIGHT * 0.3), run_time=0.35)
        self.play(pd.animate.scale(1 / 0.7).move_to(S.slots[5]), FadeOut(cmp), run_time=0.4)
        S.cards["d"] = pd
        sc = S.ctrl["sched"]
        ring = SurroundingRectangle(pd, color=CONTROL, buff=0.05, stroke_width=2)
        self.play(Create(ring), run_time=0.3)
        self.play(n2[0].animate.set_stroke(opacity=0.35), S.nodes[2][0].animate.set_stroke(opacity=0.35), run_time=0.4)   # filtered: NotReady, and no memory
        self.play(S.nodes[0][0].animate.set_stroke(color=CONTROL, width=3.5), run_time=0.3)
        set_detail(self, pd, "node 1", TEAL)
        self.play(FadeOut(ring), S.nodes[0][0].animate.set_stroke(color=NODE, width=2.5), S.nodes[2][0].animate.set_stroke(opacity=1.0), run_time=0.3)
        pulse = Dot(color=DESIRED, radius=0.07).move_to(pd.get_center())
        self.play(pulse.animate.move_to(S.nodes[0][2][2].get_center()), run_time=0.5)
        self.play(FadeOut(pulse), run_time=0.1)
        p_new = S.place_pod(0, 2)
        self.play(FadeIn(p_new, scale=0.5), S.nodes[0][4].animate.stretch_to_fit_width(0.8 * 0.95).align_to(S.nodes[0][3], LEFT), run_time=0.4)
        self.play(pd[0].animate.set_stroke(color=ACTUAL), S.running.to(3), run_time=0.4)
        set_detail(self, pd, "node 1, Running", ACTUAL)
        same = label("no new mechanism: the loops from moves two and three, closing a gap of one", 14, TEXT).move_to([-1.9, -2.55, 0], aligned_edge=LEFT)
        self.play(FadeIn(same), run_time=0.4)
        self.finish("""And here is the point of the move: nothing new happens. The ReplicaSet controller observes three Pod records
        where it wants three, but one is gone: wants three, has two, act once, a new Pod record with no node. The scheduler
        sees a Pod with no node: node two is filtered out for being NotReady, node three for memory, node one wins, bind.
        Node one's kubelet sees a Pod bound to it: pull, start, report. Three running. Self-healing is not a feature that
        was added; it is what loops do when the gap reopens. The same is true of scaling, of a deleted Pod, of a rollback:
        change a record, and the loops close the gap.""")
