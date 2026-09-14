"""Move 1, the log. One picture: a producer on the left column, a broker box spanning the rest of the band holding
one partition as a large row of cells with offsets, the consumers in a row on the grid below, one counter beside
them, and the step's claim in the caption band.

  Final frame: producer (x -5.5), broker (x -4.2 .. 6.4, y 2.6 .. -0.4), log of 8 records, two pointers, two consumer
  boxes on columns -3.2 and 0 at row -1.3, the position counter at column 3.2, the claim at y -3.3.
  Clicks: 1 records append, offsets never change  2 a consumer reads by pulling, its position is one integer
  3 a second consumer with its own offset; records are not deleted by reading  4 replay: the offset moves back.
"""
from lib.palette import *
from objects import *

SEQ = LOG_SEQ[:6]                # the first six records; the last two arrive while the second consumer reads
CELL, ROW_C_ = LOG_CELL, ROW_C


class TheLog(TalkSlide):
    def construct(self):
        t = title(self, "A topic is an append-only log", "1  the log")   # the deck's first frame; every later scene retitles in place
        st = log_stage()
        prod, brk, log, leg, ar, al = st["prod"], st["brk"], st["log"], st["leg"], st["ar"], st["al"]
        self.play(FadeIn(prod), FadeIn(brk), FadeIn(log), FadeIn(leg), run_time=0.6)
        self.play(Create(ar), FadeIn(al), run_time=0.4)
        cl = claim(self, None, "one topic, one partition, nothing written yet", LOGC)
        self.next_slide("""This talk is for engineers who have produced to or consumed from Kafka and never seen the machinery. One
        sentence carries it: a topic is an append-only log split into partitions, and every reader keeps one integer, an
        offset into that log. Ordering, parallelism, replay and durability are consequences of those two facts, and each
        move shows one of them: the log itself, then partitions, then replication, then what happens when disks fill, then
        who decides. The starting picture, nothing moving yet. A producer on the left. A broker, one machine, holding one topic with a
        single partition: the empty rail is where records will land, and the numbers that will appear under them are offsets.
        The legend says what the colours mean: each record is drawn in the colour of its key, alice, bob, carol. Everything
        in this talk happens to this row of cells.""")
        for k, c in enumerate(SEQ):
            log.append(self, c, source=prod, rt=0.55 if k < 2 else 0.3)   # the first two slowly, then at speed
        cl = claim(self, cl, "append-only: the next offset, never moved", LOGC)
        self.next_slide("""Start with one producer, one broker and one topic with a single partition. A record is a key, a value and a
        timestamp; here the colour is the key: alice, bob, carol. Each record the producer sends lands at the end of the
        partition and gets the next offset, a number that counts from zero and never changes for as long as the record
        exists. That is the whole storage model: a file the broker only ever appends to. Nothing is looked up by id,
        nothing is updated in place, and that is why writes are sequential and cheap.""")
        # --- a consumer pulls from its offset
        c1 = consumer("consumer 1").move_to([-3.2, ROW_C, 0])
        p1 = Pointer("consumer 1", READER).place(log, 0, dy=0.95)
        pos = Counter("consumer 1: offset of the next record", 0, "", READER, size=26).move_to([3.2, ROW_C, 0], aligned_edge=LEFT)
        self.play(FadeIn(c1), FadeIn(p1), FadeIn(pos), run_time=0.5)
        for i in range(4):
            rt = 0.5 if i == 0 else 0.25   # the first read slowly: record to consumer, then the pointer moves
            travel(self, log.cells[i], c1, run_time=rt, carry=log.cells[i])
            self.play(p1.to(log, i + 1, dy=0.95), pos.to(i + 1), run_time=rt)
        cl = claim(self, cl, "pull: the consumer owns its offset", READER)
        self.next_slide("""A consumer reads by pulling: it asks the broker for records starting at an offset, gets a batch, and moves its own
        pointer forward. Its whole position in the partition is one integer, the offset of the next record it wants. The
        broker does not track who has read what; the consumer owns that number, which is why a slow consumer simply falls
        behind and catches up when it can, and why a fast one can read at the speed of a sequential disk read served from
        the page cache. The broker keeps no reader state at all.""")
        # --- a second consumer, independent
        c2 = consumer("consumer 2").move_to([0.0, ROW_C, 0])
        p2 = Pointer("consumer 2", READER).place(log, 0, dy=1.45)
        self.play(FadeIn(c2), FadeIn(p2), run_time=0.4)
        for i in range(2):
            travel(self, log.cells[i], c2, run_time=0.25, carry=log.cells[i])
            self.play(p2.to(log, i + 1, dy=1.45), run_time=0.25)
        for c in (KEY_C, KEY_A):
            log.append(self, c, source=prod, rt=0.3)
        cl = claim(self, cl, "reading deletes nothing; every consumer keeps its own offset", READER)
        self.next_slide("""A second consumer starts from zero with its own pointer. Reading does not remove anything: the records stay,
        the two consumers are at different offsets, and the producer keeps appending behind both of them. Producers and
        consumers never see each other; the log in the middle decouples them completely. This is the difference from a
        queue: a queue hands each message to one reader and forgets it, a log keeps it and lets any number of readers hold
        their own place.""")
        # --- replay
        self.play(p1.to(log, 0, dy=0.95), pos.to(0), run_time=0.6)
        for i in range(3):
            travel(self, log.cells[i], c1, run_time=0.18, carry=log.cells[i])
            self.play(p1.to(log, i + 1, dy=0.95), pos.to(i + 1), run_time=0.18)
        reset = config("auto.offset.reset = latest", 15).move_to([MARGIN, ROW_C - 0.95, 0], aligned_edge=RIGHT)
        self.play(FadeIn(reset), run_time=0.4)
        cl = claim(self, cl, "replay: move the offset back", READER)
        self.finish("""Because the position is one integer the consumer owns, replay is trivial: set the offset back and read the same
        records again, in the same order. A consumer that has no stored position yet starts where auto.offset.reset says,
        latest by default, earliest to read everything the log still holds. Reprocessing after a bug, rebuilding a cache,
        feeding a new system from history: all the same move. Hold on to the picture, because everything that follows is
        this row of cells, with more of them.""")
