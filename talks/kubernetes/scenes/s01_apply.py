"""Move 1: kubectl apply writes a record, not a process.

  Final frame: kubectl at the left, the API server with its three gates, etcd under it holding one Deployment card,
  three empty nodes at the right, two counters: 3 desired, 0 running.
  Clicks: 1 the stage and the request  2 the request passes the three gates and is written to etcd  3 etcd is three
  members and a write needs two of them  4 the nodes appear, empty: nothing runs yet.
"""
from lib.palette import *
from objects import *


class ApplyRequest(TalkSlide):
    def construct(self):
        t = title(self, "kubectl apply writes a record, not a process", "1  a record, not a process")
        S = Stage()
        self.play(FadeIn(S.client), FadeIn(S.api), FadeIn(S.store), run_time=0.7)
        req = card("Deployment web", "replicas: 3, image v1").next_to(S.client, DOWN, buff=0.35)
        rl = label("the request: a description of the state you want", 13, MUTED).next_to(req, DOWN, buff=0.1)
        self.play(FadeIn(req, shift=DOWN * 0.1), FadeIn(rl), run_time=0.5)
        self.next_slide("""Start with the command everyone has typed: kubectl apply of a Deployment, three replicas of an image. Look at
        what the request is: not "start three containers", but a description of a state, replicas three, this image. The
        client sends that description to the API server, the only door into the cluster, and under the API server sits etcd,
        the database that will hold it. Nothing on the right yet; we get there.""")
        # --- through the gates, into the store
        gates, gnames = S.api[2], S.api[3]
        self.play(FadeOut(rl), req.animate.scale(0.75).move_to(S.api[0].get_left() + LEFT * 0.35 + DOWN * 0.12), run_time=0.6)
        for k in range(3):
            self.play(req.animate.move_to(gates[k].get_center() + LEFT * 0.38), run_time=0.35)
            self.play(gates[k].animate.set_fill(DESIRED, 1.0), gnames[k].animate.set_color(TEXT), run_time=0.25)
        new_detail = label("replicas 3, v1, defaults filled", 12, MUTED).move_to(req[2])
        self.play(FadeOut(req[2]), FadeIn(new_detail), run_time=0.3)
        req.remove(req[2]); req.add(new_detail)
        self.play(req.animate.scale(1 / 0.75).move_to(S.slots[0]), run_time=0.7)
        S.cards["deploy"] = req
        self.play(LaggedStart(*[Flash(d, color=TEAL, flash_radius=0.18, num_lines=6) for d in S.store[2]], lag_ratio=0.3), run_time=0.7)
        ok = label("201 created", 12, DESIRED).next_to(S.client, DOWN, buff=0.2)
        self.play(FadeIn(ok), run_time=0.3)
        self.next_slide("""The request passes three gates inside the API server, in this order. Authentication: who are you; a certificate,
        a token, a service account. Authorisation: may this user do this to this object; RBAC, and a no is a 403.
        Admission: controllers that can change or reject the object itself; this is where defaults are filled in, quotas
        enforced, policies applied, and it runs only for writes. Then the object is validated and written to etcd, and the
        client hears "created". That is the whole of what kubectl apply did: a record now exists.""")
        # --- three members, quorum of two
        members = S.store[2]
        ql = label("3 members: a write is done when 2 have it (quorum = n/2 + 1)", 12, MUTED).next_to(S.store, DOWN, buff=0.12)
        self.play(FadeIn(ql), run_time=0.4)
        copies = VGroup(*[req[0].copy().scale(0.25).move_to(m) for m in members])
        self.play(LaggedStart(*[FadeIn(c) for c in copies], lag_ratio=0.3), run_time=0.7)
        self.play(FadeOut(copies), run_time=0.3)
        self.play(members[2].animate.set_color(HOT), run_time=0.4)
        fl = label("one member down: still 2 of 3, writes continue", 12, MUTED).move_to(ql)
        self.play(FadeOut(ql), FadeIn(fl), run_time=0.3)
        copies = VGroup(*[req[0].copy().scale(0.25).move_to(m) for m in members[:2]])
        self.play(LaggedStart(*[FadeIn(c) for c in copies], lag_ratio=0.3), run_time=0.6)
        self.play(FadeOut(copies), members[2].animate.set_color(TEAL), FadeOut(fl), run_time=0.4)
        self.next_slide("""etcd is not one machine. It is usually three, sometimes five, and a write counts as done when a majority has it:
        for n members, n over two plus one. Three members means one can die and every write still lands; five tolerates two.
        That is why control planes come in odd numbers, and why everything Kubernetes knows survives a lost machine. Hold
        on to this: the database is the only thing that has to be durable. Everything else can be restarted and will
        rebuild itself from these records.""")
        # --- nothing runs yet
        self.play(FadeOut(ok), FadeIn(S.nodes), FadeIn(S.desired), FadeIn(S.running), run_time=0.7)
        gap = label("nothing runs yet: a record in a database, three empty nodes", 15, HOT).move_to([1.0, -2.55, 0], aligned_edge=LEFT)
        self.play(FadeIn(gap), run_time=0.4)
        self.finish("""Here are the machines: three nodes, each with a kubelet, some memory in use already, empty slots for pods. And
        here is the punchline of move one: nothing has happened to them. The API server did not talk to a node. kubectl
        did not start anything. There is a record that says three, and a count of running pods that says zero. The whole
        of Kubernetes is what closes that gap, and it does it with loops.""")
