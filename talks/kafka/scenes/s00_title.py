"""Opening: the title, the spine in one sentence, the map of moves. One step."""
from lib.palette import *
from objects import *

MOVES = ["the log", "partitions", "replication", "retention and compaction", "the controller"]


class Opening(TalkSlide):
    def construct(self):
        t = label("Kafka: a log you can replay", 56, TEXT).shift(UP * 1.0)
        s = label("what a topic is, and why ordering, parallelism, replay and durability follow from it", 26, MUTED).next_to(t, DOWN, buff=0.35)
        self.play(Write(t), run_time=1.0)
        self.play(FadeIn(s, shift=UP * 0.15))
        self.play(FadeOut(s), t.animate.to_edge(UP, buff=0.4).scale(0.65))
        spine = VGroup(label("A topic is an append-only log, split into partitions.", 34, LOGC),
                       label("Readers keep one integer each: an offset into it.", 34, READER),
                       label("Everything else is a consequence of those two facts.", 26, TEXT)).arrange(DOWN, buff=0.3).shift(UP * 0.5)
        for line in spine:
            self.play(FadeIn(line, shift=UP * 0.15))
        col = VGroup(*[label(f"{i + 1}   {x}", 21, MUTED) for i, x in enumerate(MOVES)]).arrange(DOWN, aligned_edge=LEFT, buff=0.14).next_to(spine, DOWN, buff=0.55)
        self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.15) for x in col], lag_ratio=0.12))
        self.finish("""This talk is for engineers who have produced to or consumed from Kafka and never seen the machinery. One
        sentence carries it: a topic is an append-only log split into partitions, and every reader keeps one integer, an
        offset into that log. Ordering, parallelism, replay and durability are all consequences of those two facts, and
        each move shows one of them: the log itself, then partitions, then replication, then what happens when disks fill,
        then who decides. Sources are the Apache Kafka design documentation, current for release 4.3.""")
