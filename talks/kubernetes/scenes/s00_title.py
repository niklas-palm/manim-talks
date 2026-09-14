"""Opening: the title, the spine, the map. One step."""
from lib.palette import *
from objects import *

MOVES = ["a record, not a process", "loops that chase the gap", "from record to process", "a node dies", "a stable address, and change"]


class Opening(TalkSlide):
    def construct(self):
        t = label("Kubernetes: desired state, and the loops that chase it", 48, TEXT).shift(UP * 1.0)
        s = label("what happens between kubectl apply and a running container", 26, MUTED).next_to(t, DOWN, buff=0.35)
        self.play(Write(t), run_time=1.0)
        self.play(FadeIn(s, shift=UP * 0.15))
        self.play(FadeOut(s), t.animate.to_edge(UP, buff=0.4).scale(0.65))
        spine = VGroup(label("You write the state you want into one database.", 32, DESIRED),
                       label("Independent loops each watch it and take one step toward it, forever.", 32, CONTROL),
                       label("Everything Kubernetes does is one of those loops closing a gap.", 24, TEXT)).arrange(DOWN, buff=0.3).shift(UP * 0.5)
        for line in spine:
            self.play(FadeIn(line, shift=UP * 0.15))
        col = VGroup(*[label(f"{i + 1}   {x}", 21, MUTED) for i, x in enumerate(MOVES)]).arrange(DOWN, aligned_edge=LEFT, buff=0.14).next_to(spine, DOWN, buff=0.5)
        self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.15) for x in col], lag_ratio=0.12))
        self.finish("""This talk is for engineers who use kubectl every day and have never watched the machinery. In fifteen minutes we
        follow one command, kubectl apply of a Deployment with three replicas, from the moment it reaches the API server to
        three running containers, and then break a node to see the same machinery again. One sentence carries it: you
        write the state you want into one database, and independent loops each watch it and take one step toward it,
        forever. Blue is what you asked for, yellow is what actually runs, violet is the control plane closing the gap,
        teal is the machines. Five moves.""")
