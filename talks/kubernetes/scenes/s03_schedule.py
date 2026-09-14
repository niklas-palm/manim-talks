"""Move 3: from record to process.

  Final frame: the stage with three control loops (Deployment, ReplicaSet, scheduler), etcd holding Deployment,
  ReplicaSet and three Pod records now bound to nodes and reported Running; three yellow pods on the nodes; 3 desired,
  3 running.
  Clicks: 1 the scheduler appears and picks a pod with no node  2 filtering: node 3 has no room  3 scoring and binding:
  node 1 wins, the record gets a node  4 the kubelet on node 1 sees a pod bound to it, pulls, starts, reports Running
  5 the other two at speed; desired equals running and the loops go quiet.
"""
from lib.palette import *
from objects import *


def score_of(node_g) -> int:
    """The least-allocated score, as a whole number: free memory as a percentage of the bar."""
    return int(round(100 * (1 - node_g[4].width / 0.8)))


class SchedulerKubelet(TalkSlide):
    def construct(self):
        t = title(self, "From record to process: the scheduler, then the kubelet", "3  from record to process")
        S = Stage(controllers=[("deploy", "Deployment controller"), ("rs", "ReplicaSet controller"), ("sched", "scheduler")])
        S.add_card("deploy", "Deployment web", "3 replicas, v1", 0)
        S.add_card("rs", "ReplicaSet web", "3 replicas, v1", 1)
        for i, nm in enumerate("abc"):
            S.add_card(nm, f"Pod web-7d4f-{nm}", "no node", 2 + i)[2].set_color(HOT)
        self.add(S.client, S.api, S.store, S.nodes, S.desired, S.running, S.ctrl["deploy"], S.ctrl["rs"], S.watches["deploy"], S.watches["rs"], *S.cards.values())
        # --- the scheduler picks a pod with no node
        sc, ws = S.ctrl["sched"], S.watches["sched"]
        self.play(FadeIn(sc), Create(ws[0]), FadeIn(ws[1]), run_time=0.7)
        pa = S.cards["a"]
        ring = SurroundingRectangle(pa, color=CONTROL, buff=0.05, stroke_width=2)
        self.play(Create(ring), run_time=0.4)
        pick = label("a Pod record with no node: the scheduler's whole job", 13, MUTED).next_to(sc, DOWN, buff=0.1)
        self.play(FadeIn(pick), run_time=0.3)
        self.next_slide("""The scheduler is another loop, and its trigger is the red line on those cards: a Pod record with no node. It
        watches for exactly those, takes one, and answers one question: which node? It does not start anything either.
        Its output will be one more field in the record.""")
        # --- filtering
        self.play(FadeOut(pick), run_time=0.2)
        fl = label("filter: nodes where the Pod fits", 13, TEXT).next_to(sc, DOWN, buff=0.1)
        self.play(FadeIn(fl), run_time=0.3)
        need = VGroup(*[Rectangle(width=0.8 * 0.25, height=0.12, stroke_color=DESIRED, stroke_width=1.5, fill_opacity=0).next_to(n[4], RIGHT, buff=0).set_y(n[3].get_y()) for n in S.nodes])
        nl = label("the Pod's memory request", 11, DESIRED).next_to(need[0], UP, buff=0.05)
        self.play(FadeIn(need), FadeIn(nl), run_time=0.5)
        n3 = S.nodes[2]
        self.play(n3[4].animate.set_fill(HOT, 0.9), need[2].animate.set_stroke(HOT), run_time=0.5)
        out = label("not enough memory: filtered out", 11, HOT).next_to(n3, DOWN, buff=0.06)
        self.play(FadeIn(out), n3[0].animate.set_stroke(opacity=0.35).set_fill(opacity=0.03), run_time=0.5)
        self.next_slide("""Two steps. First, filtering: which nodes could take this Pod at all? The Pod requests some memory, drawn in blue
        against each node's memory bar. Node three does not have that much left, so it is out; there are many such filters,
        for CPU, for ports, for node selectors and taints, and a node has to pass all of them to be feasible. Two remain.
        If none remained, the Pod would stay pending, with no node, and the loop would try again later.""")
        # --- scoring and binding
        fl2 = label("score: rank the feasible nodes", 13, TEXT).move_to(fl)
        self.play(FadeOut(fl), FadeIn(fl2), FadeOut(nl), run_time=0.3)
        scores = VGroup(*[label(f"score {score_of(S.nodes[i])}", 12, CONTROL).next_to(S.nodes[i], DOWN, buff=0.06) for i in range(2)])
        self.play(FadeIn(scores), run_time=0.5)
        self.play(S.nodes[0][0].animate.set_stroke(color=CONTROL, width=3.5), run_time=0.4)
        bind = Dot(color=CONTROL, radius=0.07).move_to(sc[2].get_center())
        self.play(bind.animate.move_to(S.api[0].get_right()), run_time=0.4)
        self.play(bind.animate.move_to(pa.get_center()), run_time=0.4)
        self.play(FadeOut(bind), run_time=0.1)
        set_detail(self, pa, "node 1", TEAL)
        self.play(FadeOut(ring), FadeOut(scores), FadeOut(need), FadeOut(fl2), S.nodes[0][0].animate.set_stroke(color=NODE, width=2.5), run_time=0.4)
        self.next_slide("""Second, scoring: the feasible nodes are ranked. One common rule prefers the node with the most free resources
        left, so the load spreads; others prefer spreading replicas across zones, or packing. Node one scores highest.
        Then the act, called binding: the scheduler writes the node's name into the Pod record through the API server.
        That is all it does. The card now says node 1. Still nothing runs; but now a record names a machine, and one
        machine is watching for exactly that.""")
        # --- the kubelet on node 1
        n1 = S.nodes[0]
        wk = watch(n1, S.api, NODE)
        self.play(Create(wk[0]), FadeIn(wk[1]), n1[5].animate.set_color(TEAL), run_time=0.6)
        pulse = Dot(color=DESIRED, radius=0.07).move_to(pa.get_center())
        self.play(pulse.animate.move_to(n1[2][0].get_center()), run_time=0.6)
        self.play(FadeOut(pulse), run_time=0.1)
        bar = Rectangle(width=0.01, height=0.06, fill_color=ACTUAL, fill_opacity=0.9, stroke_width=0).next_to(n1[2][0], DOWN, buff=0.05).align_to(n1[2][0], LEFT)
        bl = label("pull image", 11, MUTED).next_to(n1[2][0], DOWN, buff=0.14)
        self.add(bar)
        self.play(bar.animate.stretch_to_fit_width(0.36).align_to(n1[2][0], LEFT), FadeIn(bl), run_time=0.9)
        p1 = S.place_pod(0, 0)
        self.play(FadeOut(bar), FadeOut(bl), FadeIn(p1, scale=0.5), n1[4].animate.stretch_to_fit_width(0.8 * 0.55).align_to(n1[3], LEFT), run_time=0.5)
        rep = Dot(color=ACTUAL, radius=0.07).move_to(p1.get_center())
        self.play(rep.animate.move_to(S.api[0].get_right()), run_time=0.4)
        self.play(rep.animate.move_to(pa.get_center()), run_time=0.3)
        self.play(FadeOut(rep), pa[0].animate.set_stroke(color=ACTUAL), S.running.to(1), run_time=0.4)
        set_detail(self, pa, "node 1, Running", ACTUAL)
        self.next_slide("""The kubelet is the agent on every node, and it is a loop too: it watches the API server for Pod records bound to
        its own node. Node one's kubelet sees this one. Now, and only now, something happens on a machine: it asks the
        container runtime to pull the image, creates the container, and starts it. The yellow square is the first real
        process in this talk. Then it reports back, through the API server, into the same record: node 1, Running. The
        record and the world now agree, and the counter says one.""")
        # --- the other two, at speed
        for nm, ni, si, used in (("b", 1, 0, 0.8), ("c", 0, 1, 0.8)):
            pc, nd = S.cards[nm], S.nodes[ni]
            self.play(nd[0].animate.set_stroke(color=CONTROL, width=3.5), run_time=0.2)
            set_detail(self, pc, f"node {ni + 1}", TEAL, run_time=0.2)
            self.play(nd[0].animate.set_stroke(color=NODE, width=2.5), run_time=0.15)
            wkn = watch(nd, S.api, NODE) if ni != 0 else None
            if wkn:
                self.play(Create(wkn[0]), FadeIn(wkn[1]), nd[5].animate.set_color(TEAL), run_time=0.3)
            pp = S.place_pod(ni, si)
            self.play(FadeIn(pp, scale=0.5), nd[4].animate.stretch_to_fit_width(0.8 * used).align_to(nd[3], LEFT), run_time=0.3)
            self.play(pc[0].animate.set_stroke(color=ACTUAL), S.running.to(int(S.running.tracker.get_value()) + 1), run_time=0.3)
            set_detail(self, pc, f"node {ni + 1}, Running", ACTUAL, run_time=0.2)
        quiet = label("desired 3, running 3: every loop observes, compares, finds no gap, waits", 14, TEXT).move_to([-1.9, -2.55, 0], aligned_edge=LEFT)
        self.play(FadeIn(quiet), run_time=0.5)
        self.finish("""The other two Pods go the same way at speed: the scheduler binds b to node two, the least loaded now, and c
        back to node one; each kubelet sees its own, pulls, starts, reports. Three desired, three running. And now
        notice what the loops do: nothing. Each one observes, compares, finds no gap, and waits for the next change.
        A healthy cluster is a set of loops with nothing to do. The next move gives them something.""")
