"""Move 5: a stable address for changing pods, and changing the pods themselves.

  Final frame: the stage with outlined (v2) pods on nodes 1 and 2, a Service and an EndpointSlice record in etcd,
  kube-proxy on every node, a frontend pod on node 2 reaching the web pods through the Service's cluster IP; two
  ReplicaSet records, the old at 0 and the new at 3.
  Clicks: 1 the problem: each pod has its own address and the set keeps changing  2 a Service record and the
  EndpointSlice the controller derives from it  3 kube-proxy programs every node; traffic to the cluster IP lands on a
  ready pod  4 kubectl set image: a new ReplicaSet, and the two limits (25%, rounded up and down)  5 the rollout at
  speed: two ReplicaSets scaling in opposite directions, the list following  6 rollback is the same loops.
"""
from lib.palette import *
from objects import *


class ServiceRollout(TalkSlide):
    def construct(self):
        t = title(self, "A stable address for changing pods, and changing the pods", "5  a stable address, and change")
        S = Stage(node_used=(0.95, 0.3, 0.95), controllers=[("deploy", "Deployment controller"), ("rs", "ReplicaSet controller"), ("sched", "scheduler"), ("extra", "EndpointSlice controller")])
        S.add_card("deploy", "Deployment", "3 replicas, v1", 0)
        S.add_card("rs", "ReplicaSet v1", "3 replicas", 1)
        rs2 = S.add_card("rs2", "ReplicaSet v2", "0 replicas", 4)
        pods = {"a": S.place_pod(0, 0), "c": S.place_pod(0, 1), "d": S.place_pod(0, 2)}
        S.running.tracker.set_value(3)
        for n in S.nodes:
            n[5].set_color(TEAL)
        self.add(*S.base(*[S.ctrl[k] for k in ("deploy", "rs", "sched")], *[S.watches[k] for k in ("deploy", "rs", "sched")], S.cards["deploy"], S.cards["rs"], *pods.values()))
        # --- the problem: which address?
        front = pod(DESIRED).move_to(S.nodes[1][2][0])
        fl = label("frontend", 15, DESIRED).next_to(front, DOWN, buff=0.06)
        self.play(FadeIn(front), FadeIn(fl), run_time=0.4)
        self.next_slide("""Node two is back and empty, and a new pod has landed on it: a frontend, drawn in blue because it is
        something the user asked for. The three web pods run on nodes one and three. The frontend needs to reach them, and
        that is the question of this scene.""")
        qs = VGroup(*[DashedLine(front.get_top(), p.get_bottom(), color=HOT, stroke_width=1.6, dash_length=0.08) for p in pods.values()])
        q = label("which address?", 16, HOT).move_to([COLS[3], Y_LABELS, 0], aligned_edge=LEFT)
        self.play(Create(qs), FadeIn(q), run_time=0.7)
        self.next_slide("""Node two is back, and on it runs a frontend that needs the web pods. Each pod has its own IP address, and the set
        changes: d replaced b in the last move and has a new address; the next rollout will replace all three. A client
        cannot keep a list. This is the problem a Service solves, and it is solved with, once more, a record and a loop.""")
        # --- a Service record and its EndpointSlice
        self.play(FadeOut(qs), FadeOut(q), run_time=0.3)
        svc = card("Service", "10.96.0.10").scale(0.7).move_to(S.client.get_center() + DOWN * 0.8)
        self.play(FadeIn(svc), run_time=0.3)
        self.play(svc.animate.move_to(S.api[0].get_left() + LEFT * 0.4), run_time=0.4)
        self.play(svc.animate.scale(1 / 0.7).move_to(S.slots[3]), run_time=0.5)
        S.cards["svc"] = svc
        ec, we = S.ctrl["extra"], S.watches["extra"]
        self.play(FadeIn(ec), Create(we[0]), run_time=0.5)
        pulse(self, svc.get_right(), ec[2])
        eps = card("EndpointSlice", "3 pod addresses", ACTUAL).scale(0.7).move_to(ec[2].get_center())
        self.play(FadeIn(eps), run_time=0.2)
        self.play(eps.animate.move_to(S.api[0].get_right() + RIGHT * 0.4), run_time=0.35)
        self.play(eps.animate.scale(1 / 0.7).move_to(S.slots[5]), run_time=0.4)
        S.cards["eps"] = eps
        for p in pods.values():   # the list points at the ready pods
            pulse(self, p, eps, color=ACTUAL, run_time=0.3)
        self.next_slide("""A Service is a record: a name, a selector, app equals web, and a virtual address the control plane assigns, the
        cluster IP, 10.96.0.10, which never changes while the Service exists. The EndpointSlice controller watches
        Services and Pods, and derives another record: the list of ready pod addresses that match the selector, right now.
        Every time a pod comes or goes, this list is rewritten. Nothing routes yet; a list exists.""")
        # --- kube-proxy on every node
        chips = VGroup(*[Rectangle(width=0.5, height=0.14, fill_color=TEAL, fill_opacity=0.8, stroke_width=0).move_to(n[0].get_top() + DOWN * 0.2) for n in S.nodes])
        kp = label("kube-proxy on every node", 15, TEAL).move_to([COLS[3], Y_LABELS, 0], aligned_edge=LEFT)
        self.play(LaggedStart(*[FadeIn(c) for c in chips], lag_ratio=0.2), FadeIn(kp), run_time=0.6)
        for target in ("c", "a"):
            d = Dot(color=DESIRED, radius=0.08).move_to(front.get_center())
            self.add(d)
            self.play(d.animate.move_to(chips[1].get_center()), run_time=0.35)
            self.play(d.animate.move_to(pods[target].get_center()), run_time=0.45)
            self.play(Flash(pods[target], color=ACTUAL, flash_radius=0.32, num_lines=6), FadeOut(d), run_time=0.3)
        self.next_slide("""kube-proxy runs on every node and is, again, a loop: it watches Services and EndpointSlices and programs the
        node's packet rules so that anything sent to the cluster IP is rewritten to one of the addresses in the list,
        chosen at random by default. The frontend talks to 10.96.0.10 and lands on c, then on a. It never learns a pod
        address, and when the list changes, the rules change under it. A stable address is a record plus a loop on every
        machine.""")
        # --- kubectl set image: the rollout limits
        set_detail(self, S.cards["deploy"], "3 replicas, v2", DESIRED)
        self.play(FadeIn(rs2), run_time=0.4)
        lim = VGroup(label("maxSurge 25%: 1 extra", 15, MUTED), label("maxUnavailable 25%: 0 missing", 15, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).move_to([COLS[2], Y_COUNTERS - 0.15, 0], aligned_edge=LEFT)
        self.play(FadeIn(lim), run_time=0.5)
        self.next_slide("""Now change what you want: kubectl set image to v2 edits one field of the Deployment record. The Deployment
        controller observes a template that no ReplicaSet matches and creates a second ReplicaSet, v2, at zero replicas.
        It will now scale the two in opposite directions, under two limits from the record's defaults: at most twenty-five
        percent extra pods, rounded up, so one above three; and at most twenty-five percent unavailable, rounded down, so
        zero below three. The old ReplicaSet stays, at zero, for rollback; ten are kept by default.""")
        # --- the rollout at speed: v2 up, v1 down, the list following
        nv1 = Counter("v1 pods", 3, "", ACTUAL, size=22).move_to([COLS[3], Y_COUNTERS, 0], aligned_edge=LEFT)
        nv2 = Counter("v2 pods (outlined)", 0, "", ACTUAL, size=22).move_to([X_NODE, Y_COUNTERS, 0], aligned_edge=LEFT)
        self.play(FadeIn(nv1), FadeIn(nv2), run_time=0.4)
        slots_new = [(1, 1), (1, 2), (0, 0)]
        old = ["a", "c", "d"]
        for k in range(3):
            ni, si = slots_new[k]
            v2 = pod(ACTUAL).move_to(S.nodes[ni][2][si]).set_stroke(color=TEXT, width=2.5)
            self.play(FadeIn(v2, scale=0.5), nv2.to(k + 1), run_time=0.35)                         # surge: one new pod
            set_detail(self, rs2, f"{k + 1} replicas", MUTED, run_time=0.15)
            pulse(self, v2, S.cards["eps"], color=ACTUAL, run_time=0.3)                            # ready: it enters the list
            set_detail(self, S.cards["eps"], "4 pod addresses", ACTUAL, run_time=0.15)
            o = old[k]
            pulse(self, S.cards["eps"], pods[o], color=HOT, run_time=0.3)                          # the old one leaves the list first
            set_detail(self, S.cards["eps"], "3 pod addresses", ACTUAL, run_time=0.15)
            self.play(FadeOut(pods[o]), nv1.to(2 - k), run_time=0.35)                              # then it is stopped
            set_detail(self, S.cards["rs"], f"{2 - k} replicas", MUTED, run_time=0.15)
        self.next_slide("""Watch the two ReplicaSets and the list. v2 scales to one: a new pod, outlined, is scheduled and started, and
        only when it is ready does it enter the EndpointSlice, four addresses. Then v1 scales to two: an old pod leaves the
        list first, three addresses, then is stopped. Then v2 to two, v1 to one, v2 to three, v1 to zero. At every moment
        three pods are ready and at most four exist: the two limits, kept by the controller step by step. The frontend
        never noticed; it kept sending to the same address, and the list under it changed six times.""")
        # --- rollback: the same loops
        set_detail(self, S.cards["deploy"], "3 replicas, v1", DESIRED)
        self.play(FadeOut(lim), S.cards["rs"][0].animate.set_stroke(color=CONTROL, width=3.5), run_time=0.5)
        self.play(S.cards["rs"][0].animate.set_stroke(color=DESIRED, width=2), run_time=0.4)
        self.finish("""And rollback is not a separate mechanism either. kubectl rollout undo sets the Deployment's template back to
        v1; the Deployment controller sees a template that the old ReplicaSet matches, and scales the two the other way
        under the same limits. Everything in this talk was one shape: write a record, and independent loops each take one
        step toward it. Apply, schedule, run, heal, expose, roll out, roll back: a gap between desired and actual, and a
        loop that closes it.""")
