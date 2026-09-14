"""Move 5, the controller. Three controllers on the top row hold the cluster's metadata in a log of their own,
replicated by Raft (dashed lines); brokers on the bottom row fetch it (dashed lines). An event, a broker fenced, is
appended and propagates. Closing: Kafka's own state is a log.

  Final frame: three controller boxes (y 2.1), the metadata log across the middle (y 0.2) spanning all three columns,
  vertical dashed Raft and fetch relations in each column, three brokers (y -1.7), the event label beside broker 3's
  relation, the claim in the caption band.
  Clicks: 1 the quorum and its log  2 an event travels: appended, replicated, fetched  3 KRaft only since 4.0.
"""
from lib.palette import *
from objects import *

CX = [-4.0, 0.0, 4.0]          # controllers and brokers share these columns; the relations run straight down them
LY, CELL = 0.2, 0.52


class Controller(TalkSlide):
    def construct(self):
        # --- the last frame of move 4, rebuilt; then the compacted topic becomes the cluster's own metadata log
        d = retention_end()
        t = title_still(self, "Disks fill: retention and compaction", "4  retention and compaction")
        self.add(d["segs"][1], d["segs"][2], d["logs"][1], d["logs"][2], d["ptr"], d["pl"], d["active"], d["cprod"], d["clog"], d["headl"], d["compc"], d["delc"], d["dr"], d["claim"])
        ctrls = VGroup(*[broker(n, 3.6, 1.0, SYNC if i == 0 else LOGC).move_to([x, 2.1, 0]) for i, (n, x) in enumerate(zip(("controller 1: active", "controller 2: standby", "controller 3: standby"), CX))])
        mlog = Log(-4.35, LY, capacity=14, name="__cluster_metadata: the cluster's state", cell=CELL, gap=GAP)   # spans the three columns
        mlog.name.set_x(2.0)   # between the middle and right relations, so no line crosses it
        for c in (LOGC, LOGC, SYNC, LOGC, LOGC, LOGC):
            mlog.put(c)
        brks = VGroup(*[broker(f"broker {i + 1}", 3.6, 1.0).move_to([x, -1.7, 0]) for i, x in enumerate(CX)])
        # standing relations run straight down each column: controller to log (Raft), log to broker (fetch); never skewed
        def vdash(x, y0, y1, color):
            return DashedLine([x, y0, 0], [x, y1, 0], color=color, stroke_width=1.6, dash_length=0.1, stroke_opacity=0.7)
        raft = VGroup(*[vdash(x, ctrls[i][0].get_bottom()[1] - 0.08, mlog.rail.get_top()[1] + 0.08, SYNC) for i, x in enumerate(CX)])
        raft.add(label("Raft", 13, SYNC).next_to(raft[1], RIGHT, buff=GAP_TIGHT))
        fetch = VGroup(*[vdash(x, mlog.rail.get_bottom()[1] - 0.08, brks[i][0].get_top()[1] + 0.08, MUTED) for i, x in enumerate(CX)])
        fetch.add(label("fetch", 13, MUTED).next_to(fetch[1], RIGHT, buff=GAP_TIGHT))
        gone = VGroup(d["segs"][1], d["segs"][2], d["logs"][1], d["logs"][2], d["ptr"], d["pl"], d["active"], d["cprod"], d["headl"], d["compc"], d["delc"], d["dr"], d["claim"])
        t = retitle(self, t, "Who decides: the controller quorum", "5  the controller",
                    extra=[FadeOut(gone), ReplacementTransform(d["clog"], mlog), FadeIn(ctrls), FadeIn(brks)], run_time=1.0)
        self.play(Create(raft), Create(fetch), run_time=0.6)
        cl = claim(self, None, "3 or 5 controllers, one active; brokers fetch the log", LOGC)
        self.next_slide("""The compacted topic of the last move slides up and becomes something else: the cluster's own metadata log,
        kept exactly the same way. Every decision so far, which broker leads a partition, which replicas are in sync, where a topic's partitions
        live, is metadata, and something has to hold it and agree on it. Since Kafka 4.0 that is a quorum of controllers,
        three or five machines, running the Raft protocol over a log of their own, the __cluster_metadata topic. One
        controller is active and appends the changes; the others replicate the log and can take over in seconds. Every
        broker fetches that log from the active controller and keeps a local copy, so it learns cluster state the way a
        consumer learns anything: by reading a log from an offset.""")
        # --- an event travels
        ev = label("broker 3 fenced", 16, FAIL).move_to([CX[2] - 0.15, -0.72, 0], aligned_edge=RIGHT)   # beside broker 3's own relation, between log and broker
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
