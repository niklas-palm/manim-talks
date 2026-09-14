"""Move 4, retention and compaction. A partition on disk: segment files named by their first offset, three boxes across
the band. Time passes and the oldest segment is deleted whole; a consumer that pointed into it is reset. Below, a keyed
topic is compacted: the latest record per key survives, a tombstone deletes a key. Counters and settings sit in a right
column; the claim in the caption band.

  Final frame: two segment boxes (the first gone), a consumer pointer, the compacted log at y -1.75 with the
  cleanup.policy setting beside it, the tombstone counter above that, the claim at y -3.3.
  Clicks: 1 segments  2 retention deletes the oldest segment whole; the stale offset is reset  3 compaction keeps
  the latest record per key  4 a tombstone deletes a key, and is itself removed later.
"""
from lib.palette import *
from objects import *

SY, SEGX, CY, XR = S_Y, S_XS, S_CY, S_XR


class Retention(TalkSlide):
    def construct(self):
        # --- the last frame of move 3, rebuilt; then broker 2's log opens into its segment files
        d = replication_end()
        t = title_still(self, "A broker dies: replication", "3  replication")
        self.add(d["prod"], d["cons"], d["boxes"], *d["logs"], d["isr"], d["hwm"], d["ptr"], d["a_in"], d["a_out"], d["claim"])
        st = retention_stage()
        segs, logs, pl, active = st["segs"], st["logs"], st["pl"], st["active"]
        gone = VGroup(d["prod"], d["cons"], d["boxes"][0], d["boxes"][2], d["logs"][0], d["logs"][2], d["isr"], d["hwm"], d["ptr"], d["a_in"], d["a_out"], d["claim"], d["boxes"][1][1])
        t = retitle(self, t, "Disks fill: retention and compaction", "4  retention and compaction",
                    extra=[FadeOut(gone), Transform(d["boxes"][1][0], segs[0][0]), FadeIn(segs[0][1]), ReplacementTransform(d["logs"][1], logs[0]),
                           FadeIn(segs[1]), FadeIn(segs[2]), FadeIn(logs[1]), FadeIn(logs[2]), FadeIn(pl), FadeIn(active)], run_time=1.0)
        self.remove(d["boxes"][1][0]); self.add(segs[0][0])
        ptr = Pointer("consumer, slow", READER).place(logs[0], 3, dy=0.95)
        self.play(FadeIn(ptr), run_time=0.3)
        rollc = config("log.segment.bytes\n= 1 GiB\nlog.roll.hours = 168", 15).move_to([XR, -0.35, 0], aligned_edge=LEFT)
        self.play(FadeIn(rollc), run_time=0.4)
        cl = claim(self, None, "segments: named by first offset, rolled by size or age", LOGC)
        self.next_slide("""Broker two's copy of the partition, opened up: its eight records are the first segment file, and the records that
        arrived since fill two more. Zoom in on one partition's directory. The log is not one file but a sequence of segment files, each named by the
        offset of the first record it holds, so finding offset twelve is a binary search over file names and then an index
        lookup inside one file. A segment rolls when it reaches log.segment.bytes, one gibibyte by default, or after
        log.roll.hours, a week. Only the last segment, the active one, is ever appended to; the others are immutable, which
        is what makes the next two mechanisms cheap: deleting a segment is unlinking a file.""")
        # --- retention deletes whole segments
        age = Counter("age of the oldest segment", 0, "h", MUTED, size=24).move_to([-6.4, -0.55, 0], aligned_edge=LEFT)
        retc = config("log.retention.hours\n= 168", 15).next_to(age, DOWN, buff=GAP).align_to(age, LEFT)
        self.play(FadeIn(age), FadeIn(retc), run_time=0.3)
        self.play(age.to(168), run_time=1.5)
        self.play(segs[0][0].animate.set_stroke(FAIL), run_time=0.3)
        self.play(FadeOut(segs[0]), FadeOut(logs[0]), run_time=0.6)
        self.play(ptr.to(logs[1], 0, dy=0.95), run_time=0.6)
        cl = claim(self, cl, "retention: whole segments deleted; a stale offset is reset", FAIL)
        self.next_slide("""Retention is the default cleanup policy: keep records for log.retention.hours, one hundred and sixty-eight by
        default, or until the partition exceeds log.retention.bytes, and delete by removing the oldest segment whole. It is
        time or size, per topic, whichever comes first, and it happens whether or not anyone has read the records: reading
        never deletes and deleting never asks. A consumer that was slow enough to still point into the deleted segment has
        an offset that no longer exists; it is reset by auto.offset.reset, to the oldest remaining record with earliest or
        to the end with latest, and either way it has lost data. Lag against retention is the other number to alarm on.""")
        # --- compaction keeps the latest record per key
        clog = Log(-4.6, CY, capacity=12, name="topic account-balances: the latest state per key", gap=GAP)
        for c in [KEY_A, KEY_B, KEY_C, KEY_A, KEY_B, KEY_A, KEY_C, KEY_B]:
            clog.put(c)
        compc = config("cleanup.policy\n= compact", 15).move_to([XR, CY, 0], aligned_edge=LEFT)
        self.play(FadeOut(age), FadeOut(retc), FadeOut(rollc), FadeIn(clog), FadeIn(compc), run_time=0.6)
        keep = {}
        for i, c in enumerate(clog.cells):
            keep[c.get_fill_color().to_hex()] = i
        stale = [i for i in range(len(clog.cells)) if i not in keep.values()]
        self.play(*[clog.cells[i].animate.set_fill(opacity=0.15) for i in stale], run_time=0.6)
        self.play(*[FadeOut(clog.cells[i]) for i in stale], *[FadeOut(clog.offs[i]) for i in stale], run_time=0.5)
        headl = label("latest record per key; offsets keep gaps", 15, LOGC).next_to(clog.rail, DOWN, buff=0.45).align_to(clog.rail, LEFT)
        self.play(FadeIn(headl), run_time=0.3)
        cl = claim(self, cl, "compaction: the newest record per key survives", LOGC)
        self.next_slide("""The other cleanup policy is for topics where a record means the current state of its key: an account balance,
        a user's profile, a committed offset. Compaction keeps, for every key, at least the most recent record, and a
        background cleaner rewrites the older segments to drop the rest. Offsets are never renumbered, so the compacted
        tail has gaps, and a consumer that reads from the beginning still gets a complete, if abbreviated, history: the
        latest value of every key. This is how a topic becomes a table you can rebuild from, and it is exactly how
        __consumer_offsets and Kafka's own metadata log are kept small.""")
        # --- a tombstone
        tomb = Square(SIDE, fill_opacity=0, stroke_color=KEY_B, stroke_width=2.5).move_to([clog.slot(len(clog.cells))[0], CY + 1.1, 0])
        cross = VGroup(Line(UL * 0.11, DR * 0.11, color=KEY_B, stroke_width=2), Line(UR * 0.11, DL * 0.11, color=KEY_B, stroke_width=2)).move_to(tomb)
        tl = label("tombstone: key bob, value null", 15, KEY_B).next_to(tomb, RIGHT, buff=GAP_TIGHT)
        self.play(FadeIn(tomb), FadeIn(cross), FadeIn(tl), run_time=0.4)
        n = len(clog.cells)
        self.play(VGroup(tomb, cross).animate.move_to(clog.slot(n)), FadeOut(tl), run_time=0.5)
        off = label(str(clog.base + n), 14, MUTED).move_to([clog.slot(n)[0], clog.y - SIDE / 2 - 0.22, 0]); self.play(FadeIn(off), run_time=0.15)
        bob = [i for i in range(n) if clog.cells[i].get_fill_color().to_hex().upper() == KEY_B.upper()]
        self.play(*[FadeOut(clog.cells[i]) for i in bob], *[FadeOut(clog.offs[i]) for i in bob], run_time=0.5)
        dr = Counter("tombstone age", 0, "h", MUTED, size=24).move_to([XR, CY + 1.05, 0], aligned_edge=LEFT)
        delc = config("delete.retention.ms\n= 86400000", 15).next_to(compc, DOWN, buff=GAP).align_to(compc, LEFT)
        self.play(FadeIn(dr), FadeIn(delc), run_time=0.2)
        self.play(dr.to(24), run_time=1.0)
        self.play(FadeOut(tomb), FadeOut(cross), FadeOut(off), run_time=0.4)
        cl = claim(self, cl, "a tombstone deletes the key, then is removed itself", KEY_B)
        self.finish("""How do you delete a key from a log that only appends? You append a tombstone: the key with a null value. The
        cleaner treats it as the key's latest state and drops every earlier record for that key, and after
        delete.retention.ms, a day by default, drops the tombstone too, so a consumer that started in that window saw the
        deletion and a later one sees nothing at all. Same log, same offsets, same readers; the only thing that changed is
        which old records the cleaner is allowed to forget. One question remains: who decides which broker leads a
        partition, which replicas are in sync, and where a partition lives at all.""")
