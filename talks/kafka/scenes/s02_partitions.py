"""Move 2, partitions. Three brokers side by side from the start; only the first is used until the load forces the
split. Then the producer hashes keys to partitions, a consumer group takes one partition each, one member leaves,
and the group's committed offsets turn out to be a log too.

  Final frame: producer at top, three brokers each with a partition, gauge for broker 1, consumer group of three
  below with pointers, the __consumer_offsets log at the bottom.
  Clicks: 1 everything to one partition, broker 1 saturates  2 split by key hash; order per partition  3 consumer
  group, one partition per member  4 a member leaves, its partition is reassigned  5 committed offsets are a log.
"""
from lib.palette import *
from objects import *
import random

XS = [-4.35, 0.0, 4.35]
BY, CY = 0.75, -2.15
KEY_PARTITION = {KEY_A: 0, KEY_B: 1, KEY_C: 2}


class Partitions(TalkSlide):
    def construct(self):
        t = title(self, "One log cannot take the load: partitions", "2  partitions")
        prod = producer("producer").move_to([0.0, 2.55, 0])
        brokers = VGroup(*[broker(f"broker {i + 1}", 4.0, 2.1).move_to([x, BY, 0]) for i, x in enumerate(XS)])
        logs = [Log(x - 1.75, BY - 0.2, capacity=7, name=f"partition {i}") for i, x in enumerate(XS)]
        load = Gauge("write\nload", FAIL, 1.8).move_to([-6.75, BY, 0])
        self.play(FadeIn(prod), FadeIn(brokers[0]), FadeIn(logs[0]), FadeIn(load), *[FadeIn(b.copy().set_opacity(0.25)) for b in brokers[1:]], run_time=0.6)
        ghosts = [m for m in self.mobjects if isinstance(m, VGroup) and m not in (prod, brokers[0], logs[0], load, t)]
        rnd = random.Random(2)
        seq = [rnd.choice(KEYS) for _ in range(4)]
        for k, c in enumerate(seq):
            logs[0].append(self, c, source=prod, rt=0.2, extra=[load.set(0.25 + 0.24 * k)])
        l1 = label("one partition: one broker's disk, one ordering", 17, LOGC).move_to([-6.3, -1.0, 0], aligned_edge=LEFT)
        self.play(FadeIn(l1), run_time=0.4)
        self.next_slide("""One partition means one file on one broker, and one ordering. Every record of the topic lands on the same disk
        and goes out through the same network card, and the write load gauge of that broker climbs with the traffic while
        the two brokers beside it sit idle. The topic's throughput is capped by one machine. The fix is the second word of
        the spine: split the log.""")
        # --- split by key
        self.remove(*ghosts)
        hashl = label("partition = hash(key) mod 3", 17, TEXT).next_to(prod, RIGHT, buff=0.5)
        self.play(FadeIn(brokers[1]), FadeIn(brokers[2]), FadeIn(logs[1]), FadeIn(logs[2]), FadeIn(hashl), load.set(0.35), run_time=0.6)
        for c in [KEY_B, KEY_C, KEY_A, KEY_C, KEY_B, KEY_A, KEY_B, KEY_C, KEY_A]:
            p = KEY_PARTITION[c]
            logs[p].append(self, c, source=prod, rt=0.22)
        l2 = label("one key, one partition, one order; no order across partitions", 17, LOGC).move_to(l1, aligned_edge=LEFT)
        self.play(FadeOut(l1), FadeIn(l2), run_time=0.4)
        self.next_slide("""Three partitions on three brokers. The producer hashes each record's key and takes the remainder by the number
        of partitions, so alice's records always go to partition zero, bob's to one, carol's to two; with no key, the
        producer fills one partition's batch and then moves to another. Each partition is still an append-only log with its
        own offsets, so every record of one key is in order, and Kafka promises nothing about order between partitions.
        That is the trade: the topic's load now spreads across three disks, and ordering is per key, not per topic. Choose
        the key so that the things that must stay ordered share it.""")
        # --- a consumer group
        cons = [consumer(f"consumer {i + 1}").move_to([x, CY, 0]) for i, x in enumerate(XS)]
        grp = SurroundingRectangle(VGroup(*cons), color=READER, buff=0.25, corner_radius=0.1, stroke_width=1.5)
        gl = label("consumer group: one partition per member", 16, READER).next_to(grp, UP, buff=0.08).align_to(grp, LEFT)
        ptrs = [Pointer(f"c{i + 1}").place(logs[i], 0) for i in range(3)]
        self.play(FadeIn(VGroup(*cons)), Create(grp), FadeIn(gl), *[FadeIn(p) for p in ptrs], run_time=0.6)
        for step in range(3):
            for i in range(3):
                if step < len(logs[i].cells):
                    read_flash(self, logs[i].cells[step], ptrs[i], cons[i], rt=0.15)
            self.play(*[ptrs[i].to(logs[i], min(step + 1, len(logs[i].cells))) for i in range(3)], run_time=0.2)
        self.play(FadeOut(l2), run_time=0.3)
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
                    read_flash(self, logs[i].cells[step], ptrs[i], cons[min(i, 1)], rt=0.15)
            self.play(*[ptrs[i].to(logs[i], min(step + 1, len(logs[i].cells))) for i in range(3)], run_time=0.2)
        l3 = label("rebalance: a leaving member's partition moves to another (KIP-848: one at a time)", 17, READER).move_to([-6.3, -1.0, 0], aligned_edge=LEFT)
        self.play(FadeIn(l3), run_time=0.4)
        self.next_slide("""Consumer three crashes. Its partition cannot stay unread, so the group rebalances: partition two is assigned to
        consumer two, which now reads two partitions from their committed offsets. In the classic protocol every member
        stopped, rejoined and received a new assignment computed by one of the clients; a single slow member could stall
        the whole group. The protocol that became generally available in Kafka 4.0, KIP-848, has the broker's group
        coordinator assign partitions and moves them one at a time, so the members that keep their partitions never pause.
        It is enabled per group with group.protocol=consumer and becomes the default in 5.0.""")
        # --- committed offsets are a log too
        self.play(FadeOut(l3), run_time=0.3)
        olog = Log(-2.9, -3.4, capacity=12, name="__consumer_offsets: committed positions, a compacted topic of 50 partitions")
        self.play(FadeIn(olog), run_time=0.5)
        for i, src in enumerate([cons[0], cons[1], cons[1], cons[0]]):
            d = Dot(color=READER, radius=0.09).move_to(src.get_bottom())
            self.add(d)
            self.play(d.animate.move_to(olog.slot(i)), run_time=0.3)
            self.remove(d)
            olog.put(READER); self.add(olog.cells[-1], olog.offs[-1])
        self.finish("""Where does a group's position live between restarts? In Kafka itself. Each consumer commits its offset, by default
        automatically every five seconds, and the commit is a record appended to an internal topic, __consumer_offsets,
        fifty partitions, keyed by group and partition and compacted so only the latest position per key survives. A
        consumer that restarts reads its last committed offset from there and continues. So the readers' state is kept the
        same way as the data: as a log. The next problem is the machine under the log.""")
