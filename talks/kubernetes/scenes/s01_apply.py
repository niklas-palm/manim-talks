"""Move 1: kubectl apply writes a record, not a process.

  Final frame: kubectl at the left, the API server with its three gates, etcd under it holding one Deployment card,
  three empty nodes at the right, two counters: 3 desired, 0 running.
  Clicks: 1 the stage and the request  2 zoom into the API server: the request passes the three gates  3 back out:
  written to etcd, three members, quorum of two  4 the nodes appear, empty: nothing runs yet.
"""
from lib.palette import *
from objects import *

ZOOM = 0.5


class ApplyRequest(TalkSlide):
    def construct(self):
        frame = self.camera.frame
        t = title(self, "kubectl apply writes a record, not a process", "1  a record, not a process")
        S = Stage()
        self.play(FadeIn(S.client), FadeIn(S.api), FadeIn(S.store), run_time=0.7)
        req = card("Deployment", "3 replicas, v1").move_to([X_CLIENT, 0.85, 0])
        self.play(FadeIn(req, shift=DOWN * 0.1), run_time=0.5)
        self.next_slide("""Start with the command everyone has typed: kubectl apply of a Deployment, three replicas of an image. Look at
        what the request is: not "start three containers", but a description of a state, replicas three, this image. The
        client sends that description to the API server, the only door into the cluster, and under the API server sits etcd,
        the database that will hold it. Nothing on the right yet; we get there.""")
        # --- zoom into the API server: three gates
        gates, gnames = S.api[2], S.api[3]
        self.play(frame.animate.scale(ZOOM).move_to(S.api.get_center() + DOWN * 0.1), FadeOut(t), FadeOut(S.store), FadeOut(S.client),
                  req.animate.scale(0.6).move_to(S.api[0].get_left() + LEFT * 0.6 + DOWN * 0.12), run_time=1.0)
        for k in range(3):
            self.play(req.animate.move_to(gates[k].get_center() + LEFT * 0.5), run_time=0.4)
            self.play(gates[k].animate.set_fill(DESIRED, 1.0), gnames[k].animate.set_color(TEXT), run_time=0.3)
        self.play(req.animate.move_to(S.api[0].get_right() + RIGHT * 0.6 + DOWN * 0.12), run_time=0.4)
        self.next_slide("""Inside the API server the request passes three gates, in this order. Authentication: who are you; a certificate,
        a token, a service account, and a failure is a 401. Authorisation: may this user do this to this object; RBAC, and
        a no is a 403. Admission: controllers that can change or reject the object itself; this is where defaults are
        filled in, quotas enforced, policies applied, and it runs only for writes. Then the object is validated and goes to
        the store.""")
        # --- back out: written to etcd, quorum of two
        self.play(frame.animate.scale(1 / ZOOM).move_to(ORIGIN), FadeIn(t), FadeIn(S.store), FadeIn(S.client), run_time=1.0)
        self.play(req.animate.scale(1 / 0.6).move_to(S.slots[0]), run_time=0.6)
        S.cards["deploy"] = req
        members = S.store[2]
        copies = VGroup(*[req[0].copy().scale(0.25).move_to(m) for m in members])
        self.play(LaggedStart(*[FadeIn(c) for c in copies], lag_ratio=0.3), run_time=0.7)
        ql = label("quorum: 2 of 3", 15, TEAL).next_to(S.store, DOWN, buff=0.12)
        self.play(FadeOut(copies), FadeIn(ql), run_time=0.4)
        ok = label("201 created", 15, DESIRED).next_to(S.client, DOWN, buff=0.2)
        self.play(FadeIn(ok), run_time=0.3)
        self.play(members[2].animate.set_color(HOT), run_time=0.4)
        copies = VGroup(*[req[0].copy().scale(0.25).move_to(m) for m in members[:2]])
        self.play(LaggedStart(*[FadeIn(c) for c in copies], lag_ratio=0.3), run_time=0.6)
        self.play(FadeOut(copies), members[2].animate.set_color(TEAL), run_time=0.4)
        self.next_slide("""The record lands in etcd, and etcd is not one machine. It is usually three, sometimes five, and a write counts as
        done when a majority has it: for n members, n over two plus one, so two of three. Only then does the client hear
        "created". Watch one member die: the write still lands on two, and nothing stops; five members tolerate two failures.
        That is why control planes come in odd numbers, and why the database is the only thing that has to be durable:
        everything else can be restarted and will rebuild itself from these records.""")
        # --- nothing runs yet
        self.play(FadeOut(ok), FadeOut(ql), FadeIn(S.nodes), FadeIn(S.desired), FadeIn(S.running), run_time=0.7)
        self.finish("""Here are the machines: three nodes, each with a kubelet, some memory already in use, empty slots for pods. And
        here is the punchline of move one: nothing has happened to them. The API server did not talk to a node. kubectl
        did not start anything. There is a record that says three, and a count of running pods that says zero. The whole
        of Kubernetes is what closes that gap, and it does it with loops.""")
