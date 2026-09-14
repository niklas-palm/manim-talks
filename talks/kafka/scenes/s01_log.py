"""Move 1, the log. One picture: a producer on the left, a broker holding one partition drawn as a row of cells with
their offsets beneath, consumers below with a pointer each under the log.

  Final frame: producer, broker with 8 records, two consumers with pointers at different offsets, position counter.
  Clicks: 1 records append, offsets never change  2 a consumer reads by pulling, its position is one integer
  3 a second consumer with its own offset; records are not deleted by reading  4 replay: the offset moves back.
"""
from lib.palette import *
from objects import *

SEQ = [KEY_A, KEY_B, KEY_A, KEY_C, KEY_B, KEY_A]
NAMES = {KEY_A: "alice", KEY_B: "bob", KEY_C: "carol"}


def legend():
    return VGroup(*[VGroup(Square(0.2, fill_color=c, fill_opacity=0.9, stroke_width=0), label(f"key {NAMES[c]}", 15, MUTED)).arrange(RIGHT, buff=0.08)
                    for c in KEYS]).arrange(RIGHT, buff=0.3)


class TheLog(TalkSlide):
    def construct(self):
        t = title(self, "A topic is an append-only log", "1  the log")
        prod = producer().move_to([-6.1, 0.55, 0])
        brk = broker("broker", 10.2, 3.0).move_to([0.9, 0.55, 0])
        log = Log(-3.85, 0.85, capacity=12, name="topic payments, one partition")
        leg = legend().move_to([4.2, 2.65, 0])
        self.play(FadeIn(prod), FadeIn(brk), FadeIn(log), FadeIn(leg), run_time=0.6)
        ar = arrow(prod, brk, "append", MUTED)
        self.play(Create(ar[0]), FadeIn(ar[1]), run_time=0.4)
        for c in SEQ:
            log.append(self, c, source=prod, rt=0.3)
        l1 = label("append-only: a record takes the next offset and never moves", 17, LOGC).move_to([-6.3, -1.45, 0], aligned_edge=LEFT)
        self.play(FadeIn(l1), run_time=0.4)
        self.next_slide("""Start with one producer, one broker and one topic with a single partition. A record is a key, a value and a
        timestamp; here the colour is the key: alice, bob, carol. Each record the producer sends lands at the end of the
        partition and gets the next offset, a number that counts from zero and never changes for as long as the record
        exists. That is the whole storage model: a file the broker only ever appends to. Nothing is looked up by id,
        nothing is updated in place, and that is why writes are sequential and cheap.""")
        # --- a consumer pulls from its offset
        c1 = consumer("consumer 1").move_to([-3.6, -2.35, 0])
        p1 = Pointer("consumer 1").place(log, 0)
        pos = Counter("consumer 1's position: the offset of the next record", 0, "", READER, size=26).move_to([1.4, -2.45, 0], aligned_edge=LEFT)
        self.play(FadeIn(c1), FadeIn(p1), FadeIn(pos), run_time=0.5)
        for i in range(4):
            read_flash(self, log.cells[i], p1, c1, rt=0.25)
            self.play(p1.to(log, i + 1), pos.to(i + 1), run_time=0.25)
        l2 = label("pull: the consumer owns its offset; the broker keeps no reader state", 17, READER).move_to(l1, aligned_edge=LEFT)
        self.play(FadeOut(l1), FadeIn(l2), run_time=0.4)
        self.next_slide("""A consumer reads by pulling: it asks the broker for records starting at an offset, gets a batch, and moves its own
        pointer forward. Its whole position in the partition is one integer, the offset of the next record it wants. The
        broker does not track who has read what; the consumer owns that number, which is why a slow consumer simply falls
        behind and catches up when it can, and why a fast one can read at the speed of a sequential disk read served from
        the page cache.""")
        # --- a second consumer, independent
        c2 = consumer("consumer 2").move_to([-1.0, -2.35, 0])
        p2 = Pointer("consumer 2").place(log, 0, dy=1.3)
        self.play(FadeIn(c2), FadeIn(p2), run_time=0.4)
        for i in range(2):
            read_flash(self, log.cells[i], p2, c2, rt=0.25)
            self.play(p2.to(log, i + 1, dy=1.3), run_time=0.25)
        for c in (KEY_C, KEY_A):
            log.append(self, c, source=prod, rt=0.3)
        l3 = label("reading deletes nothing; every consumer keeps its own offset", 17, READER).move_to(l1, aligned_edge=LEFT)
        self.play(FadeOut(l2), FadeIn(l3), run_time=0.4)
        self.next_slide("""A second consumer starts from zero with its own pointer. Reading does not remove anything: the records stay,
        the two consumers are at different offsets, and the producer keeps appending behind both of them. Producers and
        consumers never see each other; the log in the middle decouples them completely. This is the difference from a
        queue: a queue hands each message to one reader and forgets it, a log keeps it and lets any number of readers hold
        their own place.""")
        # --- replay
        self.play(p1.to(log, 0), pos.to(0), run_time=0.6)
        for i in range(3):
            read_flash(self, log.cells[i], p1, c1, rt=0.18)
            self.play(p1.to(log, i + 1), pos.to(i + 1), run_time=0.18)
        l4 = label("replay: move the offset back (a new group starts at auto.offset.reset: latest, or earliest)", 17, READER).move_to(l1, aligned_edge=LEFT)
        self.play(FadeOut(l3), FadeIn(l4), run_time=0.4)
        self.finish("""Because the position is one integer the consumer owns, replay is trivial: set the offset back and read the same
        records again, in the same order. A consumer that has no stored position yet starts where auto.offset.reset says,
        latest by default, earliest to read everything the log still holds. Reprocessing after a bug, rebuilding a cache,
        feeding a new system from history: all the same move. Hold on to the picture, because everything that follows is
        this row of cells, with more of them.""")
