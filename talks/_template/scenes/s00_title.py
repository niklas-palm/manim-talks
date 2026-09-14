"""Opening: the title, the spine in one sentence, the map of moves. One step: the presenter starts here and the
first click goes straight into the first move."""
from lib.palette import *
from objects import *

MOVES = ["the problem", "the mechanism", "the knobs", "at scale", "where it is going"]   # the kicker names, in order


class Opening(TalkSlide):
    def construct(self):
        t = label("Talk title", 56, TEXT).shift(UP * 1.0)
        s = label("what the audience will be able to do afterwards, in one line", 28, MUTED).next_to(t, DOWN, buff=0.35)
        self.play(Write(t), run_time=1.0)
        self.play(FadeIn(s, shift=UP * 0.15))
        self.play(FadeOut(s), t.animate.to_edge(UP, buff=0.4).scale(0.65))
        spine = VGroup(label("First half of the spine sentence,", 34, CLIENT), label("second half of the spine sentence.", 34, DATA),
                       label("The one claim every later section is derived from.", 26, TEXT)).arrange(DOWN, buff=0.3).shift(UP * 0.5)
        for line in spine:
            self.play(FadeIn(line, shift=UP * 0.15))
        col = VGroup(*[label(f"{i + 1}   {x}", 21, MUTED) for i, x in enumerate(MOVES)]).arrange(DOWN, aligned_edge=LEFT, buff=0.14).next_to(spine, DOWN, buff=0.55)
        self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.15) for x in col], lag_ratio=0.12))
        self.finish("""Who the talk is for and what they will be able to do afterwards. The spine sentence, said once, slowly. Then the
        map: the moves in order, one line each, so the audience knows where they are for the next forty minutes.""")
