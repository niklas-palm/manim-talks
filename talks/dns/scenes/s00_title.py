"""Opening: the title, the spine, the map. One step."""
from lib.palette import *
from objects import *

MOVES = ["one list for the whole internet", "delegation: the name is a path", "caching: remember what you were told",
         "the price of remembering", "what keeps it standing"]


class Opening(TalkSlide):
    def construct(self):
        t = label("DNS: how a name becomes an address", 54, TEXT).shift(UP * 1.0)
        s = label("the walk, the pointers, the caches, and what they cost", 28, MUTED).next_to(t, DOWN, buff=0.35)
        self.play(Write(t), run_time=1.0)
        self.play(FadeIn(s, shift=UP * 0.15))
        self.play(FadeOut(s), t.animate.to_edge(UP, buff=0.4).scale(0.65))
        spine = VGroup(label("Every answer is the address, or a pointer to who to ask next,", 32, ZONE),
                       label("and every level remembers what it heard for exactly as long as it was told to.", 32, REMEMBERED),
                       label("The whole system, its speed and its failures, follow from those two rules.", 24, TEXT)).arrange(DOWN, buff=0.3).shift(UP * 0.5)
        spine[0][0:24].set_color(TEXT); spine[0][24:35].set_color(ADDRESS)
        for line in spine:
            self.play(FadeIn(line, shift=UP * 0.15))
        col = VGroup(*[label(f"{i + 1}   {x}", 21, MUTED) for i, x in enumerate(MOVES)]).arrange(DOWN, aligned_edge=LEFT, buff=0.14).next_to(spine, DOWN, buff=0.5)
        self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.15) for x in col], lag_ratio=0.12))
        self.finish("""This talk is for engineers who type names into things all day and have never watched what happens next. Twelve to
        fifteen minutes, one picture that grows. Two rules carry it. Every DNS answer is either the address you asked for
        or a pointer to who to ask next. And every party that hears an answer may remember it for exactly as long as the
        answer said, not longer. Delegation is the first rule at work; caching is the second; every failure mode you have
        met, the change that took a day to propagate, the typo that was slow, the name that resolved differently in two
        offices, is the two rules colliding. Five moves.""")
