"""Move 4, retention and compaction. A partition on disk: segment files named by their first offset. Time passes and
whole segments are deleted; a consumer that pointed into one is reset. Below, a keyed topic is compacted: the latest
record per key survives, a tombstone deletes a key.

  Final frame: three segment boxes (the first gone), a consumer pointer, a compacted log below with a tombstone.
  Clicks: 1 segments  2 retention deletes the oldest segment whole; the stale offset is reset  3 compaction keeps
  the latest record per key  4 a tombstone deletes a key, and is itself removed later.
"""
from lib.palette import *
from objects import *

SY = 1.45
SEGX = [-4.55, 0.0, 4.55]
SEQ = [KEY_A, KEY_B, KEY_C, KEY_A, KEY_B, KEY_A, KEY_C, KEY_B, KEY_A, KEY_C, KEY_B, KEY_A]


class Retention(TalkSlide):
    def construct(self):
        t = title(self, "Disks fill: retention and compaction", "4  retention and compaction")
        segs = VGroup(*[broker(n, 4.4, 1.7).move_to([x, SY, 0]) for n, x in zip(("00000000000000000000.log", "00000000000000000008.log", "00000000000000000016.log"), SEGX)])
        logs = [Log(x - 2.0, SY - 0.22, capacity=8, base=b, gap=GAP) for x, b in zip(SEGX, (0, 8, 16))]
        for i, l in enumerate(logs):
            for k in range(8 if i < 2 else 5):
                l.put(SEQ[(i * 8 + k) % len(SEQ)])
        pl = label("one partition on disk", 17, LOGC).move_to([-6.7, 2.5, 0], aligned_edge=LEFT)
        active = label("active segment: appends go here", 15, LOGC).next_to(segs[2], DOWN, buff=0.1)
        self.play(FadeIn(segs), *[FadeIn(l) for l in logs], FadeIn(pl), FadeIn(active), run_time=0.7)
        ptr = Pointer("consumer, slow", READER).place(logs[0], 3, dy=0.95)
        self.play(FadeIn(ptr), run_time=0.3)
        l1 = label("segment files named by first offset; a new one at 1 GiB or 168 h", 17, LOGC).move_to([-6.7, -0.5, 0], aligned_edge=LEFT)
        self.play(FadeIn(l1), run_time=0.4)
        self.next_slide("""Zoom in on one partition's directory. The log is not one file but a sequence of segment files, each named by the
        offset of the first record it holds, so finding offset twelve is a binary search over file names and then an index
        lookup inside one file. A segment rolls when it reaches log.segment.bytes, one gibibyte by default, or after
        log.roll.hours, a week. Only the last segment, the active one, is ever appended to; the others are immutable, which
        is what makes the next two mechanisms cheap: deleting a segment is unlinking a file.""")
        # --- retention deletes whole segments
        age = Counter("age of the oldest segment", 0, "h", MUTED, size=24).move_to([-6.7, -1.3, 0], aligned_edge=LEFT)
        self.play(FadeIn(age), run_time=0.3)
        self.play(age.to(168), run_time=1.5)
        self.play(segs[0][0].animate.set_stroke(FAIL), run_time=0.3)
        self.play(FadeOut(segs[0]), FadeOut(logs[0]), run_time=0.6)
        self.play(ptr.to(logs[1], 0, dy=0.95), run_time=0.6)
        l2 = label("retention: whole segments deleted after 168 h; a stale offset is reset", 17, FAIL).move_to(l1, aligned_edge=LEFT)
        self.play(FadeOut(l1), FadeIn(l2), run_time=0.4)
        self.next_slide("""Retention is the default cleanup policy: keep records for log.retention.hours, one hundred and sixty-eight by
        default, or until the partition exceeds log.retention.bytes, and delete by removing the oldest segment whole. It is
        time or size, per topic, whichever comes first, and it happens whether or not anyone has read the records: reading
        never deletes and deleting never asks. A consumer that was slow enough to still point into the deleted segment has
        an offset that no longer exists; it is reset by auto.offset.reset, to the oldest remaining record with earliest or
        to the end with latest, and either way it has lost data. Lag against retention is the other number to alarm on.""")
        # --- compaction keeps the latest record per key
        clog = Log(-2.9, -1.95, capacity=12, name="topic account-balances, cleanup.policy=compact: a record is the key's latest state", gap=GAP)
        for c in [KEY_A, KEY_B, KEY_C, KEY_A, KEY_B, KEY_A, KEY_C, KEY_B]:
            clog.put(c)
        self.play(FadeOut(age), FadeIn(clog), run_time=0.6)
        keep = {}
        for i, c in enumerate(clog.cells):
            keep[c.get_fill_color().to_hex()] = i
        stale = [i for i in range(len(clog.cells)) if i not in keep.values()]
        self.play(*[clog.cells[i].animate.set_fill(opacity=0.15) for i in stale], run_time=0.6)
        self.play(*[FadeOut(clog.cells[i]) for i in stale], *[FadeOut(clog.offs[i]) for i in stale], run_time=0.5)
        headl = label("tail: the latest record per key; offsets keep their gaps", 15, LOGC).move_to([clog.slot(0)[0] - SIDE / 2, clog.y - 0.78, 0], aligned_edge=LEFT)
        self.play(FadeIn(headl), run_time=0.3)
        l3 = label("compaction: the newest record per key survives", 17, LOGC).move_to(l1, aligned_edge=LEFT)
        self.play(FadeOut(l2), FadeIn(l3), run_time=0.4)
        self.next_slide("""The other cleanup policy is for topics where a record means the current state of its key: an account balance,
        a user's profile, a committed offset. Compaction keeps, for every key, at least the most recent record, and a
        background cleaner rewrites the older segments to drop the rest. Offsets are never renumbered, so the compacted
        tail has gaps, and a consumer that reads from the beginning still gets a complete, if abbreviated, history: the
        latest value of every key. This is how a topic becomes a table you can rebuild from, and it is exactly how
        __consumer_offsets and Kafka's own metadata log are kept small.""")
        # --- a tombstone
        tomb = Square(SIDE, fill_opacity=0, stroke_color=KEY_B, stroke_width=2.5).move_to([clog.slot(len(clog.cells))[0], clog.y + 1.05, 0])
        cross = VGroup(Line(UL * 0.11, DR * 0.11, color=KEY_B, stroke_width=2), Line(UR * 0.11, DL * 0.11, color=KEY_B, stroke_width=2)).move_to(tomb)
        tl = label("tombstone: key bob, value null", 15, KEY_B).next_to(tomb, RIGHT, buff=0.12)
        self.play(FadeIn(tomb), FadeIn(cross), FadeIn(tl), run_time=0.4)
        n = len(clog.cells)
        self.play(VGroup(tomb, cross).animate.move_to(clog.slot(n)), FadeOut(tl), run_time=0.5)
        off = label(str(clog.base + n), 14, MUTED).move_to([clog.slot(n)[0], clog.y - SIDE / 2 - 0.22, 0]); self.play(FadeIn(off), run_time=0.15)
        bob = [i for i in range(n) if clog.cells[i].get_fill_color().to_hex() == KEY_B.upper() or clog.cells[i].get_fill_color().to_hex() == KEY_B]
        self.play(*[FadeOut(clog.cells[i]) for i in bob], *[FadeOut(clog.offs[i]) for i in bob], run_time=0.5)
        dr = Counter("tombstone age", 0, "h", MUTED, size=24).move_to([3.8, -3.1, 0], aligned_edge=LEFT)
        self.play(FadeIn(dr), run_time=0.2)
        self.play(dr.to(24), run_time=1.0)
        self.play(FadeOut(tomb), FadeOut(cross), FadeOut(off), run_time=0.4)
        l4 = label("tombstone: a null value deletes the key; removed itself after 24 h", 17, KEY_B).move_to(l1, aligned_edge=LEFT)
        self.play(FadeOut(l3), FadeIn(l4), run_time=0.4)
        self.finish("""How do you delete a key from a log that only appends? You append a tombstone: the key with a null value. The
        cleaner treats it as the key's latest state and drops every earlier record for that key, and after
        delete.retention.ms, a day by default, drops the tombstone too, so a consumer that started in that window saw the
        deletion and a later one sees nothing at all. Same log, same offsets, same readers; the only thing that changed is
        which old records the cleaner is allowed to forget. One question remains: who decides which broker leads a
        partition, which replicas are in sync, and where a partition lives at all.""")
