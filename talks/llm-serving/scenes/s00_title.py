"""Opening: the title, the spine in one sentence, the map."""
from lib.palette import *
from objects import *


class Opening(TalkSlide):
    def construct(self):
        t = label("Serving open-weight LLMs", 56, TEXT).shift(UP * 1.0)
        s = label("what the GPU is doing, and what that decides", 28, DIM).next_to(t, DOWN, buff=0.35)
        self.play(Write(t), run_time=1.0)
        self.play(FadeIn(s, shift=UP * 0.15))
        self.play(FadeOut(s), t.animate.to_edge(UP, buff=0.4).scale(0.65))
        spine = VGroup(label("A model reads your prompt once,", 34, PROMPT), label("then writes one token at a time.", 34, OUTPUT),
                       label("Every hosting decision is about which of those two you are paying for.", 26, TEXT)).arrange(DOWN, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(spine[0], shift=UP * 0.15))
        self.play(FadeIn(spine[1], shift=UP * 0.15))
        self.play(FadeIn(spine[2], shift=UP * 0.15))
        steps = ["two jobs, two costs", "why the engine batches", "three knobs: weights, experts, cache", "more than one GPU",
                 "what precision costs in answers", "the fleet", "where the industry is"]
        col = VGroup(*[label(f"{i + 1}   {x}", 21, DIM) for i, x in enumerate(steps)]).arrange(DOWN, aligned_edge=LEFT, buff=0.14).next_to(spine, DOWN, buff=0.55)
        self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.15) for x in col], lag_ratio=0.12))
        self.finish("""This talk is for engineers who will host a model, or buy hosting, and want to know what they are paying for.
        No product, no vendor; one stack we built to measure things, and the numbers it produced. One sentence carries the
        whole talk: reading the prompt and writing the answer are different jobs with different costs, and every decision,
        from the instance type to the quantisation to the load balancer setting, is a decision about one of them. Seven moves. The first two build the picture of the machine; three and four are the knobs; five is the cost in
        answers, from the mechanism to the measurement; six and seven are what to do about it and what is coming.""")
