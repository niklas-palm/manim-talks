"""Move 3: from record to process.

  Final frame: the stage with three control loops (Deployment, ReplicaSet, scheduler), etcd holding Deployment,
  ReplicaSet and three Pod records bound to nodes and reported Running; three yellow pods on the nodes; 3 desired,
  3 running.
  Clicks: 1 the scheduler appears and picks a pod with no node  2 zoom into the nodes: filtering, node 3 has no room
  3 scoring, then binding: the record gets a node  4 zoom into node 1: the kubelet pulls, starts, reports Running
  5 the other two at speed; desired equals running and the loops go quiet.
"""
from lib.palette import *
from objects import *

ZN = 0.55   # zoom on the node column
ZK = 0.5    # zoom on one node


def score_of(node_g) -> int:
    """The least-allocated score, as a whole number: free memory as a percentage of the bar."""
    return int(round(100 * (1 - node_g[4].width / 1.0)))


class SchedulerKubelet(TalkSlide):
    def construct(self):
        frame = self.camera.frame
        t = title_still(self, "Controllers: loops that chase the gap", "2  loops that chase the gap")   # move two's last frame, still
        S = Stage(controllers=[("deploy", "Deployment controller"), ("rs", "ReplicaSet controller"), ("sched", "scheduler")])
        S.add_card("deploy", "Deployment", "3 replicas, v1", 0)
        S.add_card("rs", "ReplicaSet", "3 replicas, v1", 1)
        for i, nm in enumerate("abc"):
            S.add_card(nm, f"Pod {nm}", "no node", 2 + i)[2].set_color(HOT)
        self.add(*S.base(S.ctrl["deploy"], S.ctrl["rs"], S.watches["deploy"], S.watches["rs"], *S.cards.values()))
        # --- the scheduler picks a pod with no node
        sc, ws = S.ctrl["sched"], S.watches["sched"]
        t = retitle(self, t, "From record to process: the scheduler, then the kubelet", "3  from record to process", extra=[FadeIn(sc), Create(ws[0])])
        self.next_slide("""Three Pod records in etcd, each with a red line: no node. The two controllers from the last scene are idle;
        their gap is closed. A third loop has appeared under them, the scheduler, watching the API server like the others. The
        nodes on the right are still empty. Nothing moves until the next click.""")
        pa = S.cards["a"]
        ring = SurroundingRectangle(pa, color=CONTROL, buff=0.06, stroke_width=2.2)
        pulse(self, pa.get_right(), sc[2], color=HOT, run_time=0.6)
        self.play(Create(ring), run_time=0.4)
        self.next_slide("""The scheduler is another loop, and its trigger is the red line on those cards: a Pod record with no node. It
        watches for exactly those, takes one, and answers one question: which node? It does not start anything either.
        Its output will be one more field in the record.""")
        # --- zoom into the nodes: filtering
        wide = VGroup(t, S.client, S.api, S.store, S.desired, S.running, sc, ws, *[S.ctrl[k] for k in ("deploy", "rs")], *[S.watches[k] for k in ("deploy", "rs")], *S.cards.values(), ring)
        self.play(frame.animate.scale(ZN).move_to([X_NODE, NODE_YS[1], 0]), FadeOut(wide), run_time=1.0)
        need = VGroup(*[Rectangle(width=0.25, height=0.14, stroke_color=DESIRED, stroke_width=1.6, fill_opacity=0).next_to(n[4], RIGHT, buff=0).set_y(n[3].get_y()) for n in S.nodes])
        nl = label("the Pod's request", 15, DESIRED).scale(ZN).next_to(S.nodes[0][3], UP, buff=0.08)
        self.play(FadeIn(need), FadeIn(nl), run_time=0.5)
        n3 = S.nodes[2]
        self.play(n3[4].animate.set_fill(HOT, 0.9), need[2].animate.set_stroke(HOT), run_time=0.5)
        out = label("no room", 15, HOT).scale(ZN).next_to(n3[3], UP, buff=0.08)
        self.play(FadeIn(out), n3[0].animate.set_stroke(opacity=0.35).set_fill(opacity=0.03), run_time=0.5)
        self.next_slide("""Two steps. First, filtering: which nodes could take this Pod at all? The Pod requests some memory, the blue box
        against each node's memory bar. Node three does not have that much left, so it is out; there are many such filters,
        for CPU, for ports, for node selectors and taints, and a node has to pass all of them to be feasible. Two remain.
        If none remained, the Pod would stay pending, with no node, and the loop would try again later.""")
        # --- scoring, then back out to bind
        scores = VGroup(*[label(f"score {score_of(S.nodes[i])}", 15, CONTROL).scale(ZN).next_to(S.nodes[i][2], DOWN, buff=0.06) for i in range(2)])
        self.play(FadeIn(scores), FadeOut(nl), run_time=0.5)
        self.play(S.nodes[0][0].animate.set_stroke(color=CONTROL, width=4), run_time=0.4)
        self.wait(0.3)
        self.play(FadeOut(scores), FadeOut(need), FadeOut(out), run_time=0.3)
        self.play(frame.animate.scale(1 / ZN).move_to(ORIGIN), FadeIn(wide), run_time=1.0)
        pulse(self, sc[2], S.api[0].get_right(), color=CONTROL, run_time=0.4)
        pulse(self, S.api[0].get_right(), pa, color=CONTROL, run_time=0.4)
        set_detail(self, pa, "node 1", TEAL)
        self.play(FadeOut(ring), S.nodes[0][0].animate.set_stroke(color=NODE, width=2.5), run_time=0.4)
        self.next_slide("""Second, scoring: the feasible nodes are ranked. One common rule prefers the node with the most free resources
        left, so the load spreads; others prefer spreading replicas across zones, or packing. Node one scores highest.
        Then the act, called binding: the scheduler writes the node's name into the Pod record through the API server.
        That is all it does. The card now says node 1. Still nothing runs; but now a record names a machine, and one
        machine is watching for exactly that.""")
        # --- zoom into node 1: the kubelet
        n1 = S.nodes[0]
        wk = watch(n1, S.api, NODE)
        self.play(Create(wk[0]), n1[5].animate.set_color(TEAL), run_time=0.5)
        pulse(self, pa, n1[5], color=DESIRED, run_time=0.6)
        wide2 = VGroup(t, S.client, S.api, S.store, S.desired, S.running, S.nodes[1], S.nodes[2], *S.ctrl.values(), *S.watches.values(), *S.cards.values(), wk)
        self.play(frame.animate.scale(ZK).move_to(n1.get_center()), FadeOut(wide2), run_time=1.0)
        bar = Rectangle(width=0.01, height=0.07, fill_color=ACTUAL, fill_opacity=0.9, stroke_width=0).next_to(n1[2][0], DOWN, buff=0.06).align_to(n1[2][0], LEFT)
        bl = label("pull image", 15, MUTED).scale(ZK).next_to(bar, DOWN, buff=0.05).align_to(n1[2][0], LEFT)
        self.add(bar)
        self.play(bar.animate.stretch_to_fit_width(0.42).align_to(n1[2][0], LEFT), FadeIn(bl), run_time=1.0)
        p1 = S.place_pod(0, 0)
        sl = label("start container", 15, MUTED).scale(ZK).move_to(bl)
        self.play(FadeOut(bar), FadeOut(bl), FadeIn(sl), FadeIn(p1, scale=0.5), n1[4].animate.stretch_to_fit_width(0.55).align_to(n1[3], LEFT), run_time=0.6)
        self.wait(0.3)
        self.play(FadeOut(sl), run_time=0.2)
        self.play(frame.animate.scale(1 / ZK).move_to(ORIGIN), FadeIn(wide2), run_time=1.0)
        pulse(self, p1, S.api[0].get_right(), color=ACTUAL, run_time=0.5)
        pulse(self, S.api[0].get_right(), pa, color=ACTUAL, run_time=0.3)
        self.play(pa[0].animate.set_stroke(color=ACTUAL), S.running.to(1), run_time=0.4)
        set_detail(self, pa, "node 1, Running", ACTUAL)
        self.next_slide("""The kubelet is the agent on every node, and it is a loop too: it watches the API server for Pod records bound to
        its own node. Node one's kubelet sees this one. Now, and only now, something happens on a machine: it asks the
        container runtime to pull the image, creates the container, and starts it. The yellow square is the first real
        process in this talk. Then it reports back, through the API server, into the same record: node 1, Running. The
        record and the world now agree, and the counter says one.""")
        # --- the other two, at speed
        for nm, ni, si, used in (("b", 1, 0, 0.8), ("c", 0, 1, 0.8)):
            pc, nd = S.cards[nm], S.nodes[ni]
            self.play(nd[0].animate.set_stroke(color=CONTROL, width=4), run_time=0.2)
            set_detail(self, pc, f"node {ni + 1}", TEAL, run_time=0.2)
            self.play(nd[0].animate.set_stroke(color=NODE, width=2.5), run_time=0.15)
            if ni != 0:
                wkn = watch(nd, S.api, NODE)
                self.play(Create(wkn[0]), nd[5].animate.set_color(TEAL), run_time=0.3)
            pp = S.place_pod(ni, si)
            self.play(FadeIn(pp, scale=0.5), nd[4].animate.stretch_to_fit_width(used).align_to(nd[3], LEFT), run_time=0.3)
            self.play(pc[0].animate.set_stroke(color=ACTUAL), S.running.to(int(S.running.tracker.get_value()) + 1), run_time=0.3)
            set_detail(self, pc, f"node {ni + 1}, Running", ACTUAL, run_time=0.2)
        self.finish("""The other two Pods go the same way at speed: the scheduler binds b to node two, the least loaded now, and c
        back to node one; each kubelet sees its own, pulls, starts, reports. Three desired, three running. And now
        notice what the loops do: nothing. Each one observes, compares, finds no gap, and waits for the next change.
        A healthy cluster is a set of loops with nothing to do. The next move gives them something.""")
