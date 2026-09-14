"""Move 1: the problem the transformer solved. A recurrent network reads one token at a time, so its work cannot be
spread out; the transformer lets every token be processed at once. One picture: six tokens in a row; first a hidden
state crawls along them left to right, then all the pairwise connections light at once. A counter of sequential steps
falls from six to one; a counter of connections rises to show the cost.
"""
from lib.palette import *
from objects import *

WORDS = ["The", "cat", "sat", "on", "the", "mat"]
N = 6


class Sequential(TalkSlide):
    def construct(self):
        t = title(self, "The idea: read every token at once", "1  the parallel idea")
        toks = VGroup(*[VGroup(Square(0.7, fill_color=TOKEN, fill_opacity=0.85, stroke_width=0), label(w, 20, "#0f1116")) for w in WORDS])
        toks.arrange(RIGHT, buff=0.5).move_to([0, 1.4, 0])
        for g in toks:
            g[1].move_to(g[0])
        self.play(LaggedStart(*[FadeIn(g, shift=DOWN * 0.15) for g in toks], lag_ratio=0.1), run_time=1.0)
        steps = Counter("sequential steps to read the sentence", 0, "", RED, size=24).move_to([-6.4, -2.4, 0], aligned_edge=LEFT)
        self.play(FadeIn(steps))
        self.next_slide("""A sentence, six tokens. The question is how a network turns these into an understanding of the sentence. For
        years the answer was a recurrent network, and it had one property that shaped everything: it read the tokens in
        order, one at a time.""")
        # --- the recurrent crawl: a hidden state moves token by token
        h = VGroup(RoundedRectangle(corner_radius=0.1, width=0.9, height=0.9, stroke_color=ATTN, stroke_width=2.5, fill_color=ATTN, fill_opacity=0.15),
                   label("state", 15, ATTN))
        h[1].move_to(h[0])
        h.next_to(toks[0], DOWN, buff=1.1)
        self.play(FadeIn(h))
        for k in range(N):
            self.play(h.animate.next_to(toks[k], DOWN, buff=1.1), run_time=0.35)
            line = Line(toks[k][0].get_bottom(), h[0].get_top(), color=ATTN, stroke_width=2)
            self.play(Create(line), toks[k][0].animate.set_fill(ATTN, 0.85), steps.to(k + 1), run_time=0.3)
            self.play(FadeOut(line), toks[k][0].animate.set_fill(TOKEN, 0.85), run_time=0.15)
        self.next_slide("""The recurrent network carries a running state and updates it with one token at a time, left to right. Token six
        cannot be touched until token five is done. Reading a sentence of length six takes six steps in a row, a thousand
        tokens a thousand steps, and no amount of hardware shortens a line you must walk end to end. That is the sequential
        bottleneck, and it is why these networks were slow to train and forgot the far past.""")
        # --- the transformer: all connections at once
        self.play(FadeOut(h), steps.name.animate.set_opacity(0), run_time=0.4)
        steps2 = Counter("sequential steps to read the sentence", 1, "", GREEN, size=24).move_to([-6.4, -2.4, 0], aligned_edge=LEFT)
        conns = Counter("connections, every token to every token", 0, "", MUTED, size=24).move_to([-0.2, -2.4, 0], aligned_edge=LEFT)
        self.play(FadeOut(steps), FadeIn(steps2), FadeIn(conns))
        edges = VGroup()
        for a in range(N):
            for b in range(N):
                if a != b:
                    edges.add(Line(toks[a][0].get_bottom(), toks[b][0].get_bottom(), color=ATTN, stroke_width=1.2, stroke_opacity=0.5).set_points_as_corners(
                        [toks[a][0].get_bottom(), (toks[a][0].get_bottom() + toks[b][0].get_bottom()) / 2 + DOWN * 0.6, toks[b][0].get_bottom()]))
        self.play(LaggedStart(*[Create(e) for e in edges], lag_ratio=0.01), conns.to(N * (N - 1)), run_time=1.4)
        self.play(*[g[0].animate.set_fill(ATTN, 0.85) for g in toks], run_time=0.4)
        self.play(*[g[0].animate.set_fill(TOKEN, 0.85) for g in toks], run_time=0.4)
        self.finish("""The transformer throws out the running state. Every token looks at every other token directly, and all of those
        connections are computed in the same step, in parallel, however long the sentence. The sequential count drops to one.
        The cost is on the right: the connections grow with the square of the length, thirty here, a million at a thousand
        tokens, which is why long contexts are expensive and why the field keeps trying to thin this picture out. But it is
        work a GPU can do all at once, and that trade, more arithmetic for fewer steps, is the whole reason transformers won.
        The rest of the talk is how one of those connections actually works. First, the tokens have to become numbers.""")
