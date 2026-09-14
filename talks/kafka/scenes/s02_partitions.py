"""Move 2, partitions. Three brokers on the three inner columns from the start; only the first is used until the load
forces the split. Then the producer hashes keys to partitions, a consumer group takes one partition each, one member
leaves, and the group's committed offsets turn out to be a log too.

  Final frame: producer at the top centre with the hash rule as code beside it, a write-load gauge on the left
  margin, three brokers (x -4.0, 0, 4.0; y 1.0) each with a partition, the consumer group row at y -1.3 under the
  brokers, the __consumer_offsets log in the right half at y -2.75, the claim in the caption band.
  Clicks: 1 everything to one partition, broker 1 saturates  2 split by key hash; order per partition  3 consumer
  group, one partition per member  4 a member leaves, its partition is reassigned  5 committed offsets are a log.
"""
from lib.palette import *
from objects import *
import random

XS, BY, CY = P_XS, P_BY, P_CY


class Partitions(TalkSlide):
    def construct(self):
        # --- the last frame of move 1, rebuilt; then the picture rearranges for the split and the title changes with it
        d = log_end()
        t = title_still(self, "A topic is an append-only log", "1  the log")
        self.add(*[d[k] for k in ("prod", "brk", "log", "leg", "ar", "al", "c1", "c2", "p1", "p2", "pos", "reset", "claim")])
        st = partitions_stage()
        prod, brokers, logs, load = st["prod"], st["brokers"], st["logs"], st["load"]
        ghosts = VGroup(*[b_.copy().set_opacity(0.25) for b_ in brokers[1:]])
        gone = VGroup(d["c1"], d["c2"], d["p1"], d["p2"], d["pos"], d["reset"], d["claim"], d["leg"], d["ar"], d["al"], d["log"], d["brk"][1])
        t = retitle(self, t, "One log cannot take the load: partitions", "2  partitions",
                    extra=[FadeOut(gone), Transform(d["brk"][0], brokers[0][0]), FadeIn(brokers[0][1]), Transform(d["prod"], prod),
                           FadeIn(logs[0]), FadeIn(load), FadeIn(ghosts)], run_time=1.0)
        self.remove(d["brk"][0], d["prod"]); self.add(brokers[0][0], prod)
        cl = claim(self, None, "one producer, one broker, one partition", LOGC)
        self.next_slide("""The same picture, rearranged for what comes next: the consumers step aside, the broker shrinks to make room for
        two more, drawn faintly because they exist in the cluster but hold nothing yet, the producer moves to the top, and a
        write-load gauge appears at the left. The partition is empty again so that the load can be watched from zero.""")
        rnd = random.Random(2)
        seq = [rnd.choice(KEYS) for _ in range(4)]
        for k, c in enumerate(seq):
            logs[0].append(self, c, source=prod, rt=0.45 if k == 0 else 0.2, extra=[load.set(0.25 + 0.24 * k)])
        cl = claim(self, cl, "one partition: one disk, one ordering", LOGC)
        self.next_slide("""One partition means one file on one broker, and one ordering. Every record of the topic lands on the same disk
        and goes out through the same network card, and the write load gauge of that broker climbs with the traffic while
        the two brokers beside it sit idle. The topic's throughput is capped by one machine. The fix is the second word of
        the spine: split the log.""")
        # --- split by key
        self.remove(ghosts)
        hashc = code("partition = hash(key) % 3", "python", 16).next_to(prod, RIGHT, buff=GAP_WIDE)
        self.play(FadeIn(brokers[1]), FadeIn(brokers[2]), FadeIn(logs[1]), FadeIn(logs[2]), FadeIn(hashc), load.set(0.35), run_time=0.6)
        for c in [KEY_B, KEY_C, KEY_A, KEY_C, KEY_B, KEY_A, KEY_B, KEY_C, KEY_A]:
            p = KEY_PARTITION[c]
            logs[p].append(self, c, source=prod, rt=0.22)
        cl = claim(self, cl, "one key, one partition, one order", LOGC)
        self.next_slide("""Three partitions on three brokers. The producer hashes each record's key and takes the remainder by the number
        of partitions, so alice's records always go to partition zero, bob's to one, carol's to two; with no key, the
        producer fills one partition's batch and then moves to another. Each partition is still an append-only log with its
        own offsets, so every record of one key is in order, and Kafka promises nothing about order between partitions.
        That is the trade: the topic's load now spreads across three disks, and ordering is per key, not per topic. Choose
        the key so that the things that must stay ordered share it.""")
        # --- a consumer group
        cons = [consumer(f"consumer {i + 1}").move_to([x, CY, 0]) for i, x in enumerate(XS)]
        grp = SurroundingRectangle(VGroup(*cons), color=READER, buff=GAP, corner_radius=rad(0.67), stroke_width=sw(0.6))
        gl = label("consumer group: one partition per member", 16, READER).next_to(grp, DOWN, buff=GAP_TIGHT).align_to(grp, LEFT)   # below: the pointer tags own the space above
        ptrs = [Pointer(f"c{i + 1}", READER).place(logs[i], 0, dy=1.05) for i in range(3)]   # below the broker box, not on its border
        self.play(FadeIn(VGroup(*cons)), Create(grp), FadeIn(gl), *[FadeIn(p) for p in ptrs], run_time=0.6)
        for step in range(3):
            rt = 0.35 if step == 0 else 0.15   # the first round of reads slowly, one partition to one consumer
            for i in range(3):
                if step < len(logs[i].cells):
                    travel(self, logs[i].cells[step], cons[i], run_time=rt, carry=logs[i].cells[step])
            self.play(*[ptrs[i].to(logs[i], min(step + 1, len(logs[i].cells)), dy=1.05) for i in range(3)], run_time=rt)
        cl = claim(self, cl, "a group shares the partitions, one reader each", READER)
        self.next_slide("""Now the readers. A consumer group is a set of consumers that share the work of a topic: each partition is read by
        exactly one member of the group, and each member reads its partitions in order from its own offsets. Three
        partitions, three consumers, three pointers advancing in parallel: the topic's read throughput now scales with the
        partition count, which is why partitions are the unit of parallelism on both sides. A second group, say an
        analytics job, would read the same partitions again with its own pointers.""")
        # --- a member leaves: rebalance
        self.play(cons[2][0].animate.set_stroke(FAIL).set_fill(FAIL, 0.15), cons[2][1].animate.set_color(FAIL), run_time=0.4)
        self.play(FadeOut(cons[2]), FadeOut(ptrs[2].tag), run_time=0.4)
        newtag = label("c2", 15, READER).next_to(ptrs[2].tri, DOWN, buff=0.05)
        self.play(FadeIn(newtag), run_time=0.3)
        ptrs[2].remove(ptrs[2].tag); ptrs[2].add(newtag); ptrs[2].tag = newtag
        for step in range(3, 6):
            for i in range(3):
                if step < len(logs[i].cells):
                    travel(self, logs[i].cells[step], cons[min(i, 1)], run_time=0.15, carry=logs[i].cells[step])
            self.play(*[ptrs[i].to(logs[i], min(step + 1, len(logs[i].cells)), dy=1.05) for i in range(3)], run_time=0.2)
        cl = claim(self, cl, "rebalance: the partition moves to another member", READER)
        self.next_slide("""Consumer three crashes. Its partition cannot stay unread, so the group rebalances: partition two is assigned to
        consumer two, which now reads two partitions from their committed offsets. In the classic protocol every member
        stopped, rejoined and received a new assignment computed by one of the clients; a single slow member could stall
        the whole group. The protocol that became generally available in Kafka 4.0, KIP-848, has the broker's group
        coordinator assign partitions and moves them one at a time, so the members that keep their partitions never pause.
        It is enabled per group with group.protocol=consumer and becomes the default in 5.0.""")
        # --- committed offsets are a log too
        olog = Log(0.6, -2.75, capacity=9, name="__consumer_offsets: the group's committed positions", gap=GAP)   # right half, clear of the group label and the claim
        self.play(FadeOut(cl), FadeIn(olog), run_time=0.5)
        for i, src in enumerate([cons[0], cons[1], cons[1], cons[0]]):
            d = Dot(color=READER, radius=0.09).move_to(src.get_center())   # from the consumer itself, not its edge
            self.add(d)
            self.play(d.animate.move_to(olog.slot(i)), run_time=0.3)
            self.remove(d)
            olog.put(READER); self.add(olog.cells[-1], olog.offs[-1])
        cl = claim(self, None, "the readers' positions are a log too", READER)
        self.finish("""Where does a group's position live between restarts? In Kafka itself. Each consumer commits its offset, by default
        automatically every five seconds, and the commit is a record appended to an internal topic, __consumer_offsets,
        fifty partitions, keyed by group and partition and compacted so only the latest position per key survives. A
        consumer that restarts reads its last committed offset from there and continues. So the readers' state is kept the
        same way as the data: as a log. The next problem is the machine under the log.""")
