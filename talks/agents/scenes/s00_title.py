"""Opening: the title, the spine, the map. One click; the first move starts on the next."""
from lib.palette import *
from objects import *

MOVES = ["an application, an API, one model call", "from an API to a tool", "the loop", "the same loop as code, and where to intercept it",
         "the list is the only state"]


class Opening(TalkSlide):
    def construct(self):
        t = label("How an agent works", 56, TEXT).shift(UP * 1.0)
        s = label("a model, a list of messages, and a loop", 28, MUTED).next_to(t, DOWN, buff=0.35)
        self.play(Write(t), run_time=1.0)
        self.play(FadeIn(s, shift=UP * 0.15))
        self.play(FadeOut(s), t.animate.to_edge(UP, buff=0.4).scale(0.65))
        spine = VGroup(label("A model is called in a loop over a growing list of messages.", 32, TEXT),
                       label("It may answer with a request to run a tool instead of an answer;", 32, TOOL),
                       label("the application runs it, appends the result, and calls again.", 32, RESULT)).arrange(DOWN, buff=0.28).shift(UP * 0.55)
        for line in spine:
            self.play(FadeIn(line, shift=UP * 0.15), run_time=0.6)
        col = VGroup(*[label(f"{i + 1}   {x}", 21, MUTED) for i, x in enumerate(MOVES)]).arrange(DOWN, aligned_edge=LEFT, buff=0.14).next_to(spine, DOWN, buff=0.6)
        self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.15) for x in col], lag_ratio=0.12))
        self.finish("""This talk is for engineers who have used a chat assistant and want to see what an agent actually is, in the
        machinery rather than the marketing. One sentence carries it, in three parts: a model is called in a loop over a
        growing list of messages; it may answer with a request to run a tool instead of an answer; the application runs
        the tool, appends the result, and calls the model again. Everything on screen for the next twelve minutes is one
        picture of that sentence, growing. Five moves: an application that calls an API and one model call, and why that
        is not enough; turning that API into a tool; the loop; the same loop as ten lines of code with the places you can
        intercept it; and the one thing the loop carries, the list, which is also its limit.""")
