"""Move 3, replication. One partition, three brokers stacked: leader on top, two followers that fetch from it like
consumers. A producer on the left waits for acknowledgement, a consumer on the right reads only what is committed.

  Final frame: three broker rows with copies of the log, the in-sync set label, the high-water mark on the leader,
  producer and consumer arrows pointing at whichever broker leads.
  Clicks: 1 every record is copied to the followers before the producer is told it is committed; consumers see only
  committed records  2 a follower falls behind and leaves the in-sync set  3 too few in sync: the write is refused
  4 the leader dies; a follower from the in-sync set takes over, nothing committed is lost  5 the old leader returns.
"""
from lib.palette import *
from objects import *

YS = [1.5, 0.25, -1.0]
X0, CAP = -2.35, 11


class Replication(TalkSlide):
    def construct(self):
        t = title(self, "A broker dies: replication", "3  replication")
        names = ["broker 1: leader", "broker 2: follower", "broker 3: follower"]
        boxes = VGroup(*[broker(n, 5.6, 1.15).move_to([0.0, y, 0]) for n, y in zip(names, YS)])
        logs = [Log(X0, y - 0.1, capacity=CAP) for y in YS]
        prod = producer().move_to([-5.5, YS[0], 0])
        cons = consumer("consumer").move_to([5.45, YS[0], 0])
        isr = label("in-sync replicas: 1  2  3", 15, SYNC).move_to([3.0, YS[1], 0], aligned_edge=LEFT)
        self.play(FadeIn(boxes), *[FadeIn(l) for l in logs], FadeIn(prod), FadeIn(cons), FadeIn(isr), run_time=0.6)
        a_in = arrow(prod, boxes[0], "acks=all", MUTED)
        a_out = arrow(boxes[0], cons, "fetch", MUTED)
        self.play(Create(a_in[0]), FadeIn(a_in[1]), Create(a_out[0]), FadeIn(a_out[1]), run_time=0.4)
        hwm = VGroup(Line(UP * 0.3, DOWN * 0.3, color=SYNC, stroke_width=3), label("high-water mark", 11, SYNC))
        hwm[1].next_to(hwm[0], UP, buff=0.04)
        hwm.move_to([logs[0].slot(0)[0] - PITCH / 2, logs[0].y + 0.15, 0])
        self.play(FadeIn(hwm), run_time=0.3)
        ptr = Pointer("consumer").place(logs[0], 0)
        self.add(ptr)

        def hwm_to(i):
            return hwm.animate.move_to([logs[0].slot(i)[0] - PITCH / 2, logs[0].y + 0.15, 0])

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
                self.play(d.animate.move_to(prod.get_right()), hwm_to(len(logs[0].cells)), run_time=rt)
                self.play(FadeOut(d), Flash(prod, color=SYNC, flash_radius=0.9, num_lines=8), run_time=0.25)
            return cell

        for c in (KEY_A, KEY_B, KEY_C):
            replicate(c)
        for i in range(3):
            read_flash(self, logs[0].cells[i], ptr, cons, rt=0.18)
            self.play(ptr.to(logs[0], i + 1), run_time=0.15)
        l1 = label("a record is committed when every in-sync replica has it; only then is the producer told, and only committed records are handed to consumers", 14, SYNC, width=12.6).move_to([-5.9, -2.05, 0], aligned_edge=LEFT)
        self.play(FadeIn(l1), run_time=0.4)
        self.next_slide("""One partition, three copies. The broker that leads takes the writes; the two followers fetch from the leader
        exactly as a consumer would and append the same records at the same offsets. With acks=all, the default since
        Kafka 3.0, the producer is not told that a record is written until every replica in the in-sync set has it. The
        green marker is the high-water mark: the last offset all in-sync replicas hold. Consumers are only ever given records
        below it, so a record a consumer has seen can never disappear in a failover. Three replicas is the common
        production setting: f plus one copies survive f broker failures without losing a committed record.""")
        # --- a follower falls behind
        lag = Counter("broker 3 behind the leader for", 0, "s", FAIL, size=22).move_to([3.0, YS[2] + 0.15, 0], aligned_edge=LEFT)
        self.play(FadeIn(lag), run_time=0.3)
        for k, c in enumerate((KEY_A, KEY_A)):
            replicate(c, followers=(1,), ack=False)
            self.play(lag.to(15 * (k + 1)), run_time=0.4)
        isr2 = label("in-sync replicas: 1  2", 15, SYNC).move_to(isr, aligned_edge=LEFT)
        self.play(FadeOut(isr), FadeIn(isr2), boxes[2][1].animate.set_color(FAIL), boxes[2][0].animate.set_stroke(FAIL), run_time=0.5)
        self.play(hwm_to(len(logs[0].cells)), run_time=0.4)
        l2 = label("a follower that has not caught up for replica.lag.time.max.ms (30,000 ms) leaves the in-sync set; the leader stops waiting for it", 14, FAIL, width=12.6).move_to(l1, aligned_edge=LEFT)
        self.play(FadeOut(l1), FadeIn(l2), run_time=0.4)
        self.next_slide("""Broker three falls behind: a slow disk, a network partition, a garbage-collection pause. The leader keeps track of
        how long each follower has been behind, and after replica.lag.time.max.ms, thirty seconds by default, it drops the
        follower from the in-sync set. That set is written into the cluster metadata, so everyone agrees on it. From now on
        a record is committed once brokers one and two have it: the high-water mark moves again, and the producer gets its
        acknowledgements back. Durability shrank from three copies to two, quietly, which is why the in-sync replica count
        is the number to alarm on.""")
        # --- not enough replicas
        lag2 = Counter("broker 2 behind the leader for", 0, "s", FAIL, size=22).move_to([3.0, YS[1] - 0.35, 0], aligned_edge=LEFT)
        self.play(FadeIn(lag2), run_time=0.3)
        cell = logs[0].append(self, KEY_B, source=prod, rt=0.25)
        self.play(lag2.to(30), boxes[1][1].animate.set_color(FAIL), boxes[1][0].animate.set_stroke(FAIL), run_time=0.6)
        isr3 = label("in-sync replicas: 1", 15, SYNC).move_to(isr, aligned_edge=LEFT)
        self.play(FadeOut(isr2), FadeIn(isr3), run_time=0.3)
        refused = label("NotEnoughReplicas", 14, FAIL).next_to(prod, DOWN, buff=0.12)
        cell2 = Square(SIDE, fill_color=KEY_C, fill_opacity=0.9, stroke_width=0).move_to(prod.get_center())
        self.add(cell2)
        self.play(cell2.animate.move_to(logs[0].slot(len(logs[0].cells))), run_time=0.25)
        self.play(cell2.animate.set_fill(FAIL).move_to(prod.get_center()), FadeIn(refused), run_time=0.35)
        self.play(FadeOut(cell2), run_time=0.2)
        l3 = label("min.insync.replicas = 2 with acks=all: with one replica in sync the leader refuses the write rather than store it on one disk", 14, FAIL, width=12.6).move_to(l1, aligned_edge=LEFT)
        self.play(FadeOut(l2), FadeIn(l3), run_time=0.4)
        self.next_slide("""Then broker two falls behind too, and the in-sync set is the leader alone. A record could still be appended to
        the leader's log, but it would be committed on one disk, and acknowledged as safe. min.insync.replicas is the
        floor that prevents this: set to two, the leader refuses acks=all writes while fewer than two replicas are in sync,
        and the producer sees NotEnoughReplicas and retries instead of being lied to. The default is one; production
        clusters with three replicas set it to two. Availability for writes is traded for the promise that nothing
        acknowledged lives on a single machine.""")
        # --- catch up, then the leader dies
        self.play(FadeOut(refused), run_time=0.2)
        for f in (1, 2):
            while len(logs[f].cells) < len(logs[0].cells):
                i = len(logs[f].cells)
                c = logs[0].cells[i].copy(); self.add(c)
                self.play(c.animate.move_to(logs[f].slot(i)), run_time=0.12)
                self.remove(c); logs[f].put(logs[0].cells[i].get_fill_color()); self.add(logs[f].cells[-1], logs[f].offs[-1])
        isr4 = label("in-sync replicas: 1  2  3", 15, SYNC).move_to(isr, aligned_edge=LEFT)
        self.play(FadeOut(isr3), FadeIn(isr4), FadeOut(lag), FadeOut(lag2), boxes[1][1].animate.set_color(LOGC), boxes[1][0].animate.set_stroke(LOGC),
                  boxes[2][1].animate.set_color(LOGC), boxes[2][0].animate.set_stroke(LOGC), hwm_to(len(logs[0].cells)), run_time=0.6)
        self.play(boxes[0][0].animate.set_stroke(FAIL).set_fill(FAIL, 0.12), boxes[0][1].animate.set_color(FAIL), logs[0].animate.set_opacity(0.3), FadeOut(hwm), FadeOut(ptr), run_time=0.6)
        newname = label("broker 2: leader", 16, SYNC).move_to(boxes[1][1])
        a_in2 = arrow(prod, boxes[1], "acks=all", MUTED)
        a_out2 = arrow(boxes[1], cons, "fetch", MUTED)
        hwm2 = hwm.copy().set_opacity(1).move_to([logs[1].slot(len(logs[1].cells))[0] - PITCH / 2, logs[1].y + 0.15, 0])
        self.play(FadeOut(boxes[1][1]), FadeIn(newname), Transform(a_in, a_in2), Transform(a_out, a_out2), FadeIn(hwm2), run_time=0.8)
        isr5 = label("in-sync replicas: 2  3", 15, SYNC).move_to(isr, aligned_edge=LEFT)
        self.play(FadeOut(isr4), FadeIn(isr5), run_time=0.3)
        ptr2 = Pointer("consumer").place(logs[1], 3)
        self.add(ptr2)
        for c in (KEY_A, KEY_C):
            cell = logs[1].append(self, c, source=prod, rt=0.25)
            cp = cell.copy(); self.add(cp)
            self.play(cp.animate.move_to(logs[2].slot(len(logs[2].cells))), run_time=0.25)
            self.remove(cp); logs[2].put(c); self.add(logs[2].cells[-1], logs[2].offs[-1])
            self.play(hwm2.animate.move_to([logs[1].slot(len(logs[1].cells))[0] - PITCH / 2, logs[1].y + 0.15, 0]), run_time=0.2)
        l4 = label("the leader dies: the controller picks a new leader from the in-sync set, so no committed record is lost; unclean.leader.election.enable = false keeps out-of-sync replicas out", 14, SYNC, width=12.6).move_to(l1, aligned_edge=LEFT)
        self.play(FadeOut(l3), FadeIn(l4), run_time=0.4)
        self.next_slide("""The followers catch up, all three are in sync again, and then broker one dies. Its log is gone from the picture.
        The controller, which we meet in the last move, picks a new leader from the in-sync set, broker two here, and tells
        producers and consumers, who reconnect to it. Because every committed record was on every in-sync replica, the new
        leader has all of them: the high-water mark is exactly where it was, the consumer continues from the same offset,
        and the producer's next records go to broker two and are copied to broker three. A replica that was out of sync
        may not become leader while unclean.leader.election.enable is false, the default; turning it on trades the loss of
        the records that replica missed for availability when the whole in-sync set is gone.""")
        # --- the old leader returns as a follower
        self.play(boxes[0][0].animate.set_stroke(LOGC).set_fill(LOGC, 0.10), FadeOut(boxes[0][1]), run_time=0.4)
        oldname = label("broker 1: follower", 16, LOGC).move_to(boxes[0][1])
        self.play(FadeIn(oldname), logs[0].animate.set_opacity(1.0), run_time=0.4)
        while len(logs[0].cells) < len(logs[1].cells):
            i = len(logs[0].cells)
            c = logs[1].cells[i].copy(); self.add(c)
            self.play(c.animate.move_to(logs[0].slot(i)), run_time=0.15)
            self.remove(c); logs[0].put(logs[1].cells[i].get_fill_color()); self.add(logs[0].cells[-1], logs[0].offs[-1])
        isr6 = label("in-sync replicas: 2  3  1", 15, SYNC).move_to(isr, aligned_edge=LEFT)
        self.play(FadeOut(isr5), FadeIn(isr6), run_time=0.3)
        self.finish("""Broker one comes back. It is not the leader any more; it rejoins as a follower, fetches what it missed from
        broker two, and once it has caught up it is back in the in-sync set. Leadership is per partition, so on a real
        cluster every broker leads some partitions and follows others, and the controller spreads leaders evenly so that
        no single machine takes all the writes. Three copies, one in-sync set, one high-water mark: that is the whole of
        Kafka's durability story, and the next move is about the disks those copies sit on.""")
