"""Move 5, the controller. Three controllers on the top row hold the cluster's metadata in a log of their own,
replicated by Raft (dashed lines); brokers on the bottom row fetch it (dashed lines). An event, a broker fenced, is
appended and propagates. Closing: Kafka's own state is a log.

  Final frame: three controller boxes (y 2.1), the metadata log across the middle (y 0.2), dashed replicate and fetch
  relations, three brokers (y -1.7), the event label on the log, the claim in the caption band.
  Clicks: 1 the quorum and its log  2 an event travels: appended, replicated, fetched  3 KRaft only since 4.0.
"""
from lib.palette import *
from objects import *

CX = [-4.3, 0.0, 4.3]
LY, CELL = 0.2, 0.52


class Controller(TalkSlide):
    def construct(self):
        t = title(self, "Who decides: the controller quorum", "5  the controller")
        ctrls = VGroup(*[broker(n, 3.9, 1.0, SYNC if i == 0 else LOGC).move_to([x, 2.1, 0]) for i, (n, x) in enumerate(zip(("controller 1: active", "controller 2: standby", "controller 3: standby"), CX))])
        mlog = Log(-3.6, LY, capacity=12, name="__cluster_metadata: the cluster's state", cell=CELL, gap=GAP)
        for c in (LOGC, LOGC, SYNC, LOGC, LOGC, LOGC):
            mlog.put(c)
        brks = VGroup(*[broker(f"broker {i + 1}", 3.9, 1.0).move_to([x, -1.7, 0]) for i, x in enumerate(CX)])
        raft = VGroup(*[dashed(c, mlog.rail, "Raft" if i == 1 else "", SYNC) for i, c in enumerate(ctrls)])
        fetch = VGroup(*[dashed(mlog.rail, b, "fetch" if i == 1 else "", MUTED) for i, b in enumerate(brks)])
        self.play(FadeIn(ctrls), FadeIn(mlog), FadeIn(brks), run_time=0.7)
        self.play(Create(raft), Create(fetch), run_time=0.6)
        cl = claim(self, None, "3 or 5 controllers, one active; brokers fetch the log", LOGC)
        self.next_slide("""Every decision so far, which broker leads a partition, which replicas are in sync, where a topic's partitions
        live, is metadata, and something has to hold it and agree on it. Since Kafka 4.0 that is a quorum of controllers,
        three or five machines, running the Raft protocol over a log of their own, the __cluster_metadata topic. One
        controller is active and appends the changes; the others replicate the log and can take over in seconds. Every
        broker fetches that log from the active controller and keeps a local copy, so it learns cluster state the way a
        consumer learns anything: by reading a log from an offset.""")
        # --- an event travels
        ev = label("broker 3 fenced", 16, FAIL).next_to(mlog.rail, UP, buff=GAP_TIGHT).align_to(mlog.rail, RIGHT)
        self.play(brks[2][0].animate.set_stroke(FAIL), brks[2][1].animate.set_color(FAIL), FadeIn(ev), run_time=0.5)
        cell = mlog.append(self, FAIL, source=ctrls[0], rt=0.4)
        for k in (1, 2):
            c = cell.copy(); self.add(c)
            self.play(c.animate.move_to(ctrls[k][0].get_center()).scale(0.6), run_time=0.3)
            self.play(FadeOut(c), Flash(ctrls[k][0], color=SYNC, flash_radius=1.6, num_lines=8), run_time=0.25)
        for k in (0, 1):
            c = cell.copy(); self.add(c)
            self.play(c.animate.move_to(brks[k][0].get_center()).scale(0.6), run_time=0.3)
            self.play(FadeOut(c), Flash(brks[k][0], color=LOGC, flash_radius=1.6, num_lines=8), run_time=0.25)
        cl = claim(self, cl, "a change is a record: appended, replicated, fetched", SYNC)
        self.next_slide("""Broker three stops sending heartbeats and the active controller fences it: that decision is one record appended
        to the metadata log, replicated to the other controllers, and committed once a majority has it. Brokers one and
        two fetch the record, learn that broker three is out, and that the partitions it led now have a new leader from
        their in-sync sets, the failover of the replication move seen from above. Because it is a log, every broker sees
        the same changes in the same order and can catch up from where it left off, which is what let Kafka drop its
        dependency on ZooKeeper and scale to millions of partitions.""")
        # --- KRaft only
        self.play(mlog.rail.animate.set_stroke(SYNC, width=2), run_time=0.6)
        cl = claim(self, cl, "Kafka 4.0: KRaft only. Kafka's own state is a log", TEXT)
        self.finish("""Kafka 4.0, released in March 2025, runs only this way; the ZooKeeper mode that held the metadata for fifteen
        years was removed, and the last release that could bridge from it is 3.9. So the talk ends where it started. A
        topic is an append-only log split into partitions, and readers keep an offset into it. Consumers read it that way,
        followers replicate it that way, the group's positions are stored that way, and the cluster's own state is held
        that way. When something in Kafka looks complicated, find the log and the offset underneath it, and it usually
        stops being complicated.""")
