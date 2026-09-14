"""Opening: the title, the spine in one sentence, the map of moves. One step; the first click enters move one."""
from lib.palette import *
from objects import *

MOVES = ["the parallel idea", "words become vectors", "every token reads every other",
         "the token thinks alone, many times", "one token at a time"]


class Opening(TalkSlide):
    def construct(self):
        t = label("Transformers", 60, TEXT).shift(UP * 1.1)
        s = label("how every token learns from every other", 28, MUTED).next_to(t, DOWN, buff=0.35)
        self.play(Write(t), run_time=1.0)
        self.play(FadeIn(s, shift=UP * 0.15))
        self.play(FadeOut(s), t.animate.to_edge(UP, buff=0.4).scale(0.6))
        spine = VGroup(
            label("A stack of identical layers.", 32, TOKEN),
            label("In each, every token gathers what it needs from every other token at once,", 26, ATTN),
            label("then thinks about it alone. Repeat, and the last token predicts the next word.", 26, TEXT),
        ).arrange(DOWN, buff=0.28).shift(UP * 0.5)
        for line in spine:
            self.play(FadeIn(line, shift=UP * 0.15))
        col = VGroup(*[label(f"{i + 1}   {x}", 21, MUTED) for i, x in enumerate(MOVES)]).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(spine, DOWN, buff=0.5)
        self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.15) for x in col], lag_ratio=0.12))
        self.finish("""This is for engineers who use language models and have never seen the computation inside one. The spine is one
        sentence: a transformer is a stack of identical layers; in each layer every token gathers what it needs from every
        other token in a single parallel step, then each token is transformed on its own; stack that thirty to a hundred
        times and the last position predicts the next word. Five moves. First, why "at once" is the whole idea.""")
