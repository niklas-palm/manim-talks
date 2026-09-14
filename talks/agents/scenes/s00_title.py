"""Opening: the title, the spine, the map. One step."""
from lib.palette import *
from objects import *

MOVES = ["an application, an API, and one model call", "from an API to a tool", "the loop", "the same loop as code, and where to intercept it", "the list is the only state"]


class Opening(TalkSlide):
    def construct(self):
        t = label("How an agent works", 56, TEXT).shift(UP * 1.0)
        s = label("a model, a list of messages, and a loop", 28, MUTED).next_to(t, DOWN, buff=0.35)
        self.play(Write(t), run_time=1.0)
        self.play(FadeIn(s, shift=UP * 0.15))
        self.play(FadeOut(s), t.animate.to_edge(UP, buff=0.4).scale(0.65))
        spine = VGroup(label("A model, called in a loop, over a growing list of messages.", 30, TEXT),
                       label("It may answer with a tool request instead of an answer;", 26, TOOL),
                       label("the application runs the tool, appends the result, calls again.", 26, RESULT)).arrange(DOWN, buff=0.28).shift(UP * 0.5)
        for line in spine:
            self.play(FadeIn(line, shift=UP * 0.15))
        col = VGroup(*[label(f"{i + 1}   {x}", 21, MUTED) for i, x in enumerate(MOVES)]).arrange(DOWN, aligned_edge=LEFT, buff=0.14).next_to(spine, DOWN, buff=0.55)
        self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.15) for x in col], lag_ratio=0.12))
        self.finish("""This talk is for engineers who have used a chat assistant and want to see what an agent actually is, in the
        machinery rather than the marketing. One sentence carries it: an agent is a model called in a loop over a growing list
        of messages, where the model may answer with a request to run a tool instead of an answer, and the application runs
        the tool, appends the result and calls the model again. Everything on screen for the next twelve minutes is one
        picture of that sentence, growing. Five moves: an application that already calls an API, that API turned into a tool,
        the loop, the loop as code with the places you can intercept it, and the one thing the loop carries, the list, which
        is also its limit.""")
