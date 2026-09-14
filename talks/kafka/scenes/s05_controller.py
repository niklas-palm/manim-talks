"""Move 5, the controller. Three controllers hold the cluster's metadata in a log of their own, replicated by Raft;
brokers fetch it. An event (a broker fenced) is appended and propagates. Closing: Kafka's own state is a log.

  Final frame: three controller boxes, the metadata log between them and the brokers, three brokers with the
  event delivered, the closing line.
  Clicks: 1 the quorum and its log  2 an event travels: appended, replicated, fetched  3 KRaft only since 4.0.
"""
from lib.palette import *
from objects import *

CX = [-4.4, 0.0, 4.4]


class Controller(TalkSlide):
    def construct(self):
        t = title(self, "Who decides: the controller quorum", "5  the controller")
        ctrls = VGroup(*[broker(n, 3.9, 1.0, SYNC if i == 0 else LOGC).move_to([x, 2.1, 0]) for i, (n, x) in enumerate(zip(("controller 1: active", "controller 2: standby", "controller 3: standby"), CX))])
        mlog = Log(-2.9, 0.35, capacity=12, name="__cluster_metadata: the cluster's state as a log, replicated by Raft to every controller", gap=GAP)
        for c in (LOGC, LOGC, SYNC, LOGC, LOGC, LOGC):
            mlog.put(c)
        brks = VGroup(*[broker(f"broker {i + 1}", 3.9, 1.0).move_to([x, -1.75, 0]) for i, x in enumerate(CX)])
        self.play(FadeIn(ctrls), FadeIn(mlog), FadeIn(brks), run_time=0.7)
        l1 = label("3 or 5 controllers, one active; brokers fetch the metadata log", 17, LOGC).move_to([-6.7, -3.0, 0], aligned_edge=LEFT)
        self.play(FadeIn(l1), run_time=0.4)
        self.next_slide("""Every decision so far, which broker leads a partition, which replicas are in sync, where a topic's partitions
        live, is metadata, and something has to hold it and agree on it. Since Kafka 4.0 that is a quorum of controllers,
        three or five machines, running the Raft protocol over a log of their own, the __cluster_metadata topic. One
        controller is active and appends the changes; the others replicate the log and can take over in seconds. Every
        broker fetches that log from the active controller and keeps a local copy, so it learns cluster state the way a
        consumer learns anything: by reading a log from an offset.""")
        # --- an event travels
        ev = label("broker 3 fenced: new leader for its partitions", 16, FAIL).move_to([-2.9, 1.25, 0], aligned_edge=LEFT)
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
        l2 = label("a change is a record: appended, replicated, fetched in order", 17, SYNC).move_to(l1, aligned_edge=LEFT)
        self.play(FadeOut(l1), FadeIn(l2), run_time=0.4)
        self.next_slide("""Broker three stops sending heartbeats and the active controller fences it: that decision is one record appended
        to the metadata log, replicated to the other controllers, and committed once a majority has it. Brokers one and
        two fetch the record, learn that broker three is out, and that the partitions it led now have a new leader from
        their in-sync sets, the failover of the replication move seen from above. Because it is a log, every broker sees
        the same changes in the same order and can catch up from where it left off, which is what let Kafka drop its
        dependency on ZooKeeper and scale to millions of partitions.""")
        # --- KRaft only
        l3 = label("Kafka 4.0: KRaft only, ZooKeeper gone. Kafka's own state is a log", 17, TEXT).move_to(l1, aligned_edge=LEFT)
        self.play(FadeOut(l2), FadeIn(l3), run_time=0.5)
        self.play(mlog.rail.animate.set_stroke(SYNC, width=2), run_time=0.6)
        self.finish("""Kafka 4.0, released in March 2025, runs only this way; the ZooKeeper mode that held the metadata for fifteen
        years was removed, and the last release that could bridge from it is 3.9. So the talk ends where it started. A
        topic is an append-only log split into partitions, and readers keep an offset into it. Consumers read it that way,
        followers replicate it that way, the group's positions are stored that way, and the cluster's own state is held
        that way. When something in Kafka looks complicated, find the log and the offset underneath it, and it usually
        stops being complicated.""")
