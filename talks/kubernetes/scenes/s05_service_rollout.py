"""Move 5: a stable address for changing pods, and changing the pods themselves.

  Final frame: the stage with pods of the new version on nodes 1 and 2, a Service and an EndpointSlice record in etcd,
  kube-proxy rules on every node, a frontend pod on node 2 reaching the web pods through the Service's cluster IP; two
  ReplicaSet records, the old at 0 and the new at 3.
  Clicks: 1 the problem: each pod has its own IP and the set keeps changing  2 a Service record and the EndpointSlice
  the controller derives from it  3 kube-proxy programs every node; traffic to the cluster IP lands on a ready pod
  4 kubectl set image: a new ReplicaSet, and the surge and unavailability limits (25%, rounded up and down)
  5 the rollout at speed: two ReplicaSets scaling in opposite directions, the EndpointSlice following
  6 rollback is the same loops with the old ReplicaSet.
"""
from lib.palette import *
from objects import *

IPS = {"a": "10.1.0.4", "c": "10.1.0.9", "d": "10.1.0.12"}


class ServiceRollout(TalkSlide):
    def construct(self):
        t = title(self, "A stable address for changing pods, and changing the pods", "5  a stable address, and change")
        S = Stage(node_used=(0.95, 0.3, 0.95), controllers=[("deploy", "Deployment controller"), ("rs", "ReplicaSet controller"), ("sched", "scheduler"), ("extra", "EndpointSlice controller")])
        S.add_card("deploy", "Deployment web", "3 replicas, v1", 0)
        S.add_card("rs", "ReplicaSet web v1", "3 replicas", 1)
        rs2 = S.add_card("rs2", "ReplicaSet web v2", "0 replicas", 4)
        pods = {"a": S.place_pod(0, 0), "c": S.place_pod(0, 1), "d": S.place_pod(0, 2)}
        ips = {k: label(v, 10, ACTUAL).next_to(p, DOWN, buff=0.04) for (k, p), v in zip(pods.items(), IPS.values())}
        S.running.tracker.set_value(3)
        for n in S.nodes:
            n[5].set_color(TEAL)
        self.add(S.client, S.api, S.store, S.nodes, S.desired, S.running, *[S.ctrl[k] for k in ("deploy", "rs", "sched")],
                 *[S.watches[k] for k in ("deploy", "rs", "sched")], S.cards["deploy"], S.cards["rs"], *pods.values(), *ips.values())
        # --- the problem: which IP?
        front = pod(DESIRED).move_to(S.nodes[1][2][0])
        fl = label("frontend", 10, DESIRED).next_to(front, DOWN, buff=0.04)
        self.play(FadeIn(front), FadeIn(fl), run_time=0.4)
        qs = VGroup(*[DashedLine(front.get_top(), p.get_bottom(), color=HOT, stroke_width=1.4, dash_length=0.08) for p in pods.values()])
        q = label("which address? they change every time a pod is replaced", 12, HOT).move_to([X_NODE, 2.55, 0])
        self.play(Create(qs), FadeIn(q), run_time=0.7)
        self.next_slide("""Node two is back, and on it runs a frontend that needs the web pods. Each pod has its own IP address, and the set
        changes: d replaced b in the last move and has a new address; the next rollout will replace all three. A client
        cannot keep a list. This is the problem a Service solves, and it is solved with, once more, a record and a loop.""")
        # --- a Service record and its EndpointSlice
        self.play(FadeOut(qs), FadeOut(q), run_time=0.3)
        svc = card("Service web", "10.96.0.10, app=web").scale(0.7).move_to(S.client.get_center() + DOWN * 0.7)
        self.play(FadeIn(svc), run_time=0.3)
        self.play(svc.animate.move_to(S.api[0].get_left() + LEFT * 0.35), run_time=0.4)
        self.play(svc.animate.scale(1 / 0.7).move_to(S.slots[3]), run_time=0.5)
        S.cards["svc"] = svc
        ec, we = S.ctrl["extra"], S.watches["extra"]
        self.play(FadeIn(ec), Create(we[0]), FadeIn(we[1]), run_time=0.5)
        pulse = Dot(color=DESIRED, radius=0.07).move_to(svc.get_right())
        self.play(pulse.animate.move_to(ec[2].get_center()), run_time=0.5)
        self.play(FadeOut(pulse), run_time=0.1)
        eps = card("EndpointSlice web", ".4  .9  .12", ACTUAL).scale(0.7).move_to(ec[2].get_center())
        self.play(FadeIn(eps), run_time=0.2)
        self.play(eps.animate.move_to(S.api[0].get_right() + RIGHT * 0.3), run_time=0.35)
        self.play(eps.animate.scale(1 / 0.7).move_to(S.slots[5]), run_time=0.4)
        S.cards["eps"] = eps
        self.next_slide("""A Service is a record: a name, a selector, app equals web, and a virtual address the control plane assigns, the
        cluster IP, which never changes while the Service exists. The EndpointSlice controller watches Services and Pods,
        and derives another record: the list of ready pod addresses that match the selector, right now. Every time a pod
        comes or goes, this list is rewritten. Nothing routes yet; a list exists.""")
        # --- kube-proxy on every node
        rules = VGroup(*[label("kube-proxy rules", 10, TEAL).move_to(n[0].get_corner(DR) + LEFT * 0.62 + UP * 0.14) for n in S.nodes])
        self.play(LaggedStart(*[FadeIn(r) for r in rules], lag_ratio=0.2), run_time=0.6)
        for target in ("c", "a"):
            d = Dot(color=DESIRED, radius=0.07).move_to(front.get_center())
            self.add(d)
            self.play(d.animate.move_to(rules[1].get_center()), run_time=0.35)
            self.play(d.animate.move_to(pods[target].get_center()), run_time=0.45)
            self.play(Flash(pods[target], color=ACTUAL, flash_radius=0.3, num_lines=6), FadeOut(d), run_time=0.3)
        self.next_slide("""kube-proxy runs on every node and is, again, a loop: it watches Services and EndpointSlices and programs the
        node's packet rules so that anything sent to the cluster IP is rewritten to one of the addresses in the list,
        chosen at random by default. The frontend talks to 10.96.0.10 and lands on c, then on a. It never learns a pod
        address, and when the list changes, the rules change under it. A stable address is a record plus a loop on every
        machine.""")
        # --- kubectl set image: the rollout limits
        set_detail(self, S.cards["deploy"], "3 replicas, v2", DESIRED)
        self.play(FadeIn(rs2), run_time=0.4)
        lim = VGroup(label("maxSurge 25% of 3, rounded up: 1 extra pod allowed", 12, MUTED),
                     label("maxUnavailable 25% of 3, rounded down: 0 may be missing", 12, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.06).move_to([X_CTRL - 1.35, -2.45, 0], aligned_edge=LEFT)
        self.play(FadeIn(lim), run_time=0.5)
        self.next_slide("""Now change what you want: kubectl set image to v2 edits one field of the Deployment record. The Deployment
        controller observes a template that no ReplicaSet matches and creates a second ReplicaSet, v2, at zero replicas.
        It will now scale the two in opposite directions, under two limits from the record's defaults: at most twenty-five
        percent extra pods, rounded up, so one above three; and at most twenty-five percent unavailable, rounded down, so
        zero below three. The old ReplicaSet stays, at zero, for rollback; ten are kept by default.""")
        # --- the rollout at speed: v2 up, v1 down, the slice following
        nv1 = Counter("v1 pods", 3, "", ACTUAL, size=18).move_to([X_NODE - 1.35, -2.55, 0], aligned_edge=LEFT)
        nv2 = Counter("v2 pods", 0, "", ACTUAL, size=18).move_to([X_NODE + 0.25, -2.55, 0], aligned_edge=LEFT)
        self.play(FadeIn(nv1), FadeIn(nv2), FadeOut(lim), run_time=0.4)
        slots_new = [(1, 1), (1, 2), (0, 0)]
        old = ["a", "c", "d"]
        new_pods = []
        slice_text = [".4  .9  .12  .21", ".9  .12  .21", ".9  .12  .21  .23", ".12  .21  .23", ".12  .21  .23  .25", ".21  .23  .25"]
        for k in range(3):
            ni, si = slots_new[k]
            v2 = pod(ACTUAL).move_to(S.nodes[ni][2][si])
            tag = label("v2", 9, BG).move_to(v2)
            self.play(FadeIn(v2, scale=0.5), FadeIn(tag), nv2.to(k + 1), run_time=0.35)      # surge: one new pod, ready
            set_detail(self, eps, slice_text[2 * k], ACTUAL, run_time=0.2)
            set_detail(self, rs2, f"{k + 1} replicas", MUTED, run_time=0.15)
            new_pods.append(VGroup(v2, tag))
            o = old[k]
            set_detail(self, eps, slice_text[2 * k + 1], ACTUAL, run_time=0.2)             # then the old one leaves the list
            self.play(FadeOut(pods[o]), FadeOut(ips[o]), nv1.to(2 - k), run_time=0.35)      # and is scaled away
            set_detail(self, S.cards["rs"], f"{2 - k} replicas", MUTED, run_time=0.15)
            if k == 2:
                # the last new pod takes the slot the first old pod freed on node 1
                pass
        never = label("never fewer than 3 ready, never more than 4: the two limits", 13, TEXT).move_to([-1.9, -2.55, 0], aligned_edge=LEFT)
        self.play(FadeIn(never), run_time=0.4)
        self.next_slide("""Watch the two ReplicaSets and the list. v2 scales to one: a new pod is scheduled and started, and only when it is
        ready does it enter the EndpointSlice. Then v1 scales to two: an old pod leaves the list first, then is stopped.
        Then v2 to two, v1 to one, v2 to three, v1 to zero. At every moment three pods are ready and at most four exist:
        the two limits, kept by the controller step by step. The frontend never noticed; it kept sending to the same
        address, and the list under it changed six times.""")
        # --- rollback: the same loops
        set_detail(self, S.cards["deploy"], "3 replicas, v1", DESIRED)
        back = label("rollback = set the Deployment back: the same two ReplicaSets, scaled the other way", 13, MUTED).move_to(never)
        self.play(FadeOut(never), FadeIn(back), run_time=0.4)
        self.finish("""And rollback is not a separate mechanism either. kubectl rollout undo sets the Deployment's template back to
        v1; the Deployment controller sees a template that the old ReplicaSet matches, and scales the two the other way
        under the same limits. Everything in this talk was one shape: write a record, and independent loops each take one
        step toward it. Apply, schedule, run, heal, expose, roll out, roll back: a gap between desired and actual, and a
        loop that closes it.""")
