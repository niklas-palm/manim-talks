"""Move 3, replication. One partition, three brokers stacked on the centre columns: leader on top, two followers that
fetch from it like consumers. The producer sits on the left margin column, the consumer on the right; the in-sync set
is a row of markers inside the leader's box; counters and settings live in the two side columns.

  Final frame: three broker rows (x -3.3 .. 3.3; y 1.7, 0, -1.7, filling the band) with copies of the log, in-sync markers in the
  leader's box, the high-water mark on the leader, producer and consumer arrows pointing at whichever broker leads,
  lag counters and the settings as code in the right column, the claim in the caption band.
  Clicks: 1 every record is copied to the followers before the producer is told it is committed; consumers see only
  committed records  2 a follower falls behind and leaves the in-sync set  3 too few in sync: the write is refused
  4 the leader dies; a follower from the in-sync set takes over, nothing committed is lost  5 the old leader returns.
"""
from lib.palette import *
from objects import *

YS, BW, X0, CAP, CELL, XR = R_YS, R_BW, R_X0, R_CAP, R_CELL, R_XR


class Replication(TalkSlide):
    def construct(self):
        # --- the last frame of move 2, rebuilt; then the three brokers stack up as three copies of one partition
        d = partitions_end()
        t = title_still(self, "One log cannot take the load: partitions", "2  partitions")
        self.add(d["prod"], d["hashc"], d["load"], d["brokers"], *d["logs"], d["cons"][0], d["cons"][1], d["grp"], d["gl"], *d["ptrs"], d["olog"], d["claim"])
        st = replication_stage()
        boxes, logs, prod, cons = st["boxes"], st["logs"], st["prod"], st["cons"]
        gone = VGroup(d["hashc"], d["load"], *d["logs"], d["cons"][0], d["cons"][1], d["grp"], d["gl"], *d["ptrs"], d["olog"], d["claim"], *[b_[1] for b_ in d["brokers"]])
        isr = Isr(3)

        def isr_home(b):   # top-right corner inside a broker box
            return isr.move_to([b[0].get_right()[0] - 0.25, b[0].get_top()[1] - 0.42, 0], aligned_edge=RIGHT)

        isr_home(boxes[0])
        t = retitle(self, t, "A broker dies: replication", "3  replication",
                    extra=[FadeOut(gone), *[Transform(d["brokers"][i][0], boxes[i][0]) for i in range(3)], *[FadeIn(boxes[i][1]) for i in range(3)],
                           Transform(d["prod"], prod), *[FadeIn(l) for l in logs], FadeIn(cons), FadeIn(isr)], run_time=1.0)
        self.remove(*[d["brokers"][i][0] for i in range(3)], d["prod"]); self.add(*[boxes[i][0] for i in range(3)], prod)
        a_in = arrow(prod, boxes[0], "acks=all", MUTED)
        a_out = arrow(boxes[0], cons, "fetch", MUTED)
        self.play(Create(a_in[0]), FadeIn(a_in[1]), Create(a_out[0]), FadeIn(a_out[1]), run_time=0.4)
        hwm = VGroup(Line(UP * 0.38, DOWN * 0.38, color=SYNC, stroke_width=3), label("HWM", 15, SYNC))
        hwm[1].next_to(hwm[0], UP, buff=0.04)
        hwm.move_to([logs[0].slot(0)[0] - logs[0].pitch / 2, logs[0].y + 0.17, 0])
        self.play(FadeIn(hwm), run_time=0.3)
        ptr = Pointer("consumer", READER).place(logs[0], 0, dy=0.55)
        self.add(ptr)

        def hwm_pos(log, i):
            return [log.slot(i)[0] - log.pitch / 2, log.y + 0.17, 0]

        def replicate(color, followers=(1, 2), ack=True, rt=0.25):
            """One record: to the leader, copied by the followers that are in sync, then committed and acknowledged."""
            cell = logs[0].append(self, color, source=prod, rt=rt)
            copies = []
            for f in followers:
                c = cell.copy(); self.add(c); copies.append((f, c))
            self.play(*[c.animate.move_to(logs[f].slot(len(logs[f].cells))) for f, c in copies], run_time=rt)
            for f, c in copies:
                self.remove(c); logs[f].put(color); self.add(logs[f].cells[-1], logs[f].offs[-1])
            if ack:
                d = Dot(color=SYNC, radius=0.07).move_to(cell.get_center())
                self.add(d)
                self.play(d.animate.move_to(prod.get_center()), hwm.animate.move_to(hwm_pos(logs[0], len(logs[0].cells))), run_time=rt)   # the acknowledgement lands on the producer itself
                self.play(FadeOut(d), Flash(prod, color=SYNC, flash_radius=0.9, num_lines=8), run_time=0.25)
            return cell

        cl = claim(self, None, "one partition, three copies: a leader and two followers", LOGC)
        self.next_slide("""The three brokers of the last move stack up, and the picture is now one partition on three of them. Broker one leads; brokers two and three are followers
        with empty copies. The producer writes to the leader with acks=all, the consumer fetches from the leader, the
        in-sync markers at the top right say which copies are current, and the green line is the high-water mark, the
        offset up to which everything is committed. Nothing has been written yet.""")
        for k, c in enumerate((KEY_A, KEY_B, KEY_C)):
            replicate(c, rt=(0.55, 0.3, 0.25)[k])   # the first record slowly: append, copy to the followers, acknowledge
        for i in range(3):
            rt = 0.4 if i == 0 else 0.18
            travel(self, logs[0].cells[i], cons, run_time=rt, carry=logs[0].cells[i])
            self.play(ptr.to(logs[0], i + 1, dy=0.55), run_time=rt)
        cl = claim(self, cl, "committed: on every in-sync replica, below the HWM", SYNC)
        self.next_slide("""One partition, three copies. The broker that leads takes the writes; the two followers fetch from the leader
        exactly as a consumer would and append the same records at the same offsets. With acks=all, the default since
        Kafka 3.0, the producer is not told that a record is written until every replica in the in-sync set has it. The
        green marker is the high-water mark: the last offset all in-sync replicas hold. Consumers are only ever given records
        below it, so a record a consumer has seen can never disappear in a failover. Three replicas is the common
        production setting: f plus one copies survive f broker failures without losing a committed record.""")
        # --- a follower falls behind
        lag = Counter("broker 3 behind for", 0, "s", FAIL, size=24).move_to([XR, YS[2] + 0.25, 0], aligned_edge=LEFT)
        lagc = config("replica.lag.time\n.max.ms = 30000", 15).next_to(lag, DOWN, buff=GAP).align_to(lag, LEFT)
        self.play(FadeIn(lag), FadeIn(lagc), run_time=0.3)
        for k, c in enumerate((KEY_A, KEY_A)):
            replicate(c, followers=(1,), ack=False)
            self.play(lag.to(15 * (k + 1)), run_time=0.4)
        self.play(*isr.set({1, 2}, out={3}), boxes[2][1].animate.set_color(FAIL), boxes[2][0].animate.set_stroke(FAIL), run_time=0.5)
        self.play(hwm.animate.move_to(hwm_pos(logs[0], len(logs[0].cells))), run_time=0.4)
        cl = claim(self, cl, "30 s behind: out of the in-sync set", FAIL)
        self.next_slide("""Broker three falls behind: a slow disk, a network partition, a garbage-collection pause. The leader keeps track of
        how long each follower has been behind, and after replica.lag.time.max.ms, thirty seconds by default, it drops the
        follower from the in-sync set. That set is written into the cluster metadata, so everyone agrees on it. From now on
        a record is committed once brokers one and two have it: the high-water mark moves again, and the producer gets its
        acknowledgements back. Durability shrank from three copies to two, quietly, which is why the in-sync replica count
        is the number to alarm on.""")
        # --- not enough replicas
        lag2 = Counter("broker 2 behind for", 0, "s", FAIL, size=24).move_to([XR, YS[1] + 0.25, 0], aligned_edge=LEFT)
        self.play(FadeIn(lag2), run_time=0.3)
        cell = logs[0].append(self, KEY_B, source=prod, rt=0.25)
        self.play(lag2.to(30), *isr.set({1}, out={2, 3}), boxes[1][1].animate.set_color(FAIL), boxes[1][0].animate.set_stroke(FAIL), run_time=0.6)
        minc = config("min.insync.replicas\n= 2", 15).move_to([-3.55, YS[1] + 0.25, 0], aligned_edge=RIGHT)   # clear of the box edge
        refused = label("NotEnoughReplicas", 16, FAIL).next_to(minc, DOWN, buff=GAP_TIGHT).align_to(minc, RIGHT)
        cell2 = Square(CELL, fill_color=KEY_C, fill_opacity=0.9, stroke_width=0).move_to(prod.get_center())
        self.add(cell2)
        self.play(FadeIn(minc), cell2.animate.move_to(logs[0].slot(len(logs[0].cells))), run_time=0.3)
        self.play(cell2.animate.set_fill(FAIL).move_to(prod.get_center()), FadeIn(refused), run_time=0.35)
        self.play(FadeOut(cell2), run_time=0.2)
        cl = claim(self, cl, "too few in sync: the write is refused", FAIL)
        self.next_slide("""Then broker two falls behind too, and the in-sync set is the leader alone. A record could still be appended to
        the leader's log, but it would be committed on one disk, and acknowledged as safe. min.insync.replicas is the
        floor that prevents this: set to two, the leader refuses acks=all writes while fewer than two replicas are in sync,
        and the producer sees NotEnoughReplicas and retries instead of being lied to. The default is one; production
        clusters with three replicas set it to two. Availability for writes is traded for the promise that nothing
        acknowledged lives on a single machine.""")
        # --- catch up, then the leader dies
        self.play(FadeOut(refused), FadeOut(minc), run_time=0.2)
        for f in (1, 2):
            while len(logs[f].cells) < len(logs[0].cells):
                i = len(logs[f].cells)
                c = logs[0].cells[i].copy(); self.add(c)
                self.play(c.animate.move_to(logs[f].slot(i)), run_time=0.12)
                self.remove(c); logs[f].put(logs[0].cells[i].get_fill_color()); self.add(logs[f].cells[-1], logs[f].offs[-1])
        self.play(*isr.set({1, 2, 3}), FadeOut(lag), FadeOut(lagc), FadeOut(lag2), boxes[1][1].animate.set_color(LOGC), boxes[1][0].animate.set_stroke(LOGC),
                  boxes[2][1].animate.set_color(LOGC), boxes[2][0].animate.set_stroke(LOGC), hwm.animate.move_to(hwm_pos(logs[0], len(logs[0].cells))), run_time=0.6)
        self.play(boxes[0][0].animate.set_stroke(FAIL).set_fill(FAIL, 0.12), boxes[0][1].animate.set_color(FAIL), logs[0].cells.animate.set_fill(opacity=0.25), logs[0].offs.animate.set_opacity(0.3),
                  FadeOut(hwm), FadeOut(ptr), FadeOut(a_in), FadeOut(a_out), run_time=0.7)
        self.play(prod.animate.move_to([-5.45, R_YS[1], 0]), cons.animate.move_to([5.45, R_YS[1], 0]), run_time=0.5)   # producer and consumer follow the leader: horizontal arrows, no crossing
        newname = label("broker 2: leader", 17, SYNC).move_to(boxes[1][1], aligned_edge=LEFT)
        a_in2 = arrow(prod, boxes[1], "acks=all", MUTED)
        a_out2 = arrow(boxes[1], cons, "fetch", MUTED)
        hwm2 = hwm.copy().set_opacity(1).move_to(hwm_pos(logs[1], len(logs[1].cells)))
        self.play(FadeOut(boxes[1][1]), FadeIn(newname), Create(a_in2[0]), FadeIn(a_in2[1]), Create(a_out2[0]), FadeIn(a_out2[1]), FadeIn(hwm2),
                  isr.animate.move_to([boxes[1][0].get_right()[0] - 0.25, boxes[1][0].get_top()[1] - 0.42, 0], aligned_edge=RIGHT), run_time=0.8)
        self.play(*isr.set({2, 3}, gone={1}), run_time=0.3)
        ptr2 = Pointer("consumer", READER).place(logs[1], 3, dy=0.55)
        self.add(ptr2)
        for c in (KEY_A, KEY_C):
            cell = logs[1].append(self, c, source=prod, rt=0.25)
            cp = cell.copy(); self.add(cp)
            self.play(cp.animate.move_to(logs[2].slot(len(logs[2].cells))), run_time=0.25)
            self.remove(cp); logs[2].put(c); self.add(logs[2].cells[-1], logs[2].offs[-1])
            self.play(hwm2.animate.move_to(hwm_pos(logs[1], len(logs[1].cells))), run_time=0.2)
        cl = claim(self, cl, "a new leader from the in-sync set; nothing committed is lost", SYNC)
        self.next_slide("""The followers catch up, all three are in sync again, and then broker one dies. Its log is gone from the picture.
        The controller, which we meet in the last move, picks a new leader from the in-sync set, broker two here, and tells
        producers and consumers, who reconnect to it. Because every committed record was on every in-sync replica, the new
        leader has all of them: the high-water mark is exactly where it was, the consumer continues from the same offset,
        and the producer's next records go to broker two and are copied to broker three. A replica that was out of sync
        may not become leader while unclean.leader.election.enable is false, the default; turning it on trades the loss of
        the records that replica missed for availability when the whole in-sync set is gone.""")
        # --- the old leader returns as a follower
        self.play(boxes[0][0].animate.set_stroke(LOGC).set_fill(LOGC, 0.10), FadeOut(boxes[0][1]), run_time=0.4)
        oldname = label("broker 1: follower", 17, LOGC).move_to(boxes[0][1], aligned_edge=LEFT)
        self.play(FadeIn(oldname), logs[0].cells.animate.set_fill(opacity=0.9), logs[0].offs.animate.set_opacity(1.0), run_time=0.4)
        while len(logs[0].cells) < len(logs[1].cells):
            i = len(logs[0].cells)
            c = logs[1].cells[i].copy(); self.add(c)
            self.play(c.animate.move_to(logs[0].slot(i)), run_time=0.15)
            self.remove(c); logs[0].put(logs[1].cells[i].get_fill_color()); self.add(logs[0].cells[-1], logs[0].offs[-1])
        self.play(*isr.set({1, 2, 3}), run_time=0.3)
        cl = claim(self, cl, "back as a follower: fetch, catch up, rejoin", LOGC)
        self.finish("""Broker one comes back. It is not the leader any more; it rejoins as a follower, fetches what it missed from
        broker two, and once it has caught up it is back in the in-sync set. Leadership is per partition, so on a real
        cluster every broker leads some partitions and follows others, and the controller spreads leaders evenly so that
        no single machine takes all the writes. Three copies, one in-sync set, one high-water mark: that is the whole of
        Kafka's durability story, and the next move is about the disks those copies sit on.""")
