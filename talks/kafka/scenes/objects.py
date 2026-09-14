"""Kafka's vocabulary on top of the shared library.

  KEY_A / KEY_B / KEY_C (blue, yellow, orange)   records, coloured by their key, from producer to disk to consumer
  LOGC (violet)      the log and everything structural: partitions, segments, brokers
  READER (teal)      consumers and the offsets they own
  SYNC (green)       replicated and committed: in-sync replicas, the high-water mark
  FAIL (red)         a lagging replica, a dead broker, a refused write
"""
from lib.palette import *

KEY_A, KEY_B, KEY_C = BLUE, YELLOW, ORANGE
LOGC, READER, SYNC, FAIL = VIOLET, TEAL, GREEN, RED
KEYS = [KEY_A, KEY_B, KEY_C]
set_thread({"log": LOGC, "logs": LOGC, "partition": LOGC, "partitions": LOGC, "segment": LOGC, "segments": LOGC,
            "offset": READER, "offsets": READER, "consumer": READER, "consumers": READER,
            "committed": SYNC, "in-sync": SYNC, "leader": SYNC})

SIDE, GAP = 0.42, 0.07          # a record cell and the gap between cells; every Log() in this talk is built with these
PITCH = SIDE + GAP


def producer(name: str = "producer", w: float = 1.9) -> VGroup:
    return node(name, TEXT, w=w, h=0.7, size=20)


def consumer(name: str, w: float = 2.1) -> VGroup:
    return node(name, READER, w=w, h=0.7, size=20)


def broker(name: str, w: float, h: float, color: str = LOGC) -> VGroup:
    return box(w, h, name, color, size=18)


def claim(scene, old, text: str, color: str = LOGC):
    """The one line a step claims, in the caption band, left-aligned to the margin: at most eight words, size 17. Every
    scene uses this one slot, so the eye knows where to look; the sentence behind it is in the note."""
    t = label(text, 17, color).move_to([-MARGIN, CAPTION_Y, 0], aligned_edge=LEFT)
    if old is None:
        scene.play(FadeIn(t), run_time=0.4)
    else:
        scene.play(FadeOut(old), FadeIn(t), run_time=0.4)
    return t


def config(text: str, size: float = 15) -> VGroup:
    """A broker or client setting as a small highlighted code block (ini syntax), never as plain text."""
    return code(text, "ini", size)


class Isr(VGroup):
    """The in-sync set as a row of numbered markers with a name, attached to the leader's box: a marker is green when
    that broker is in sync, red when it has fallen out, dim when it is gone. set(scene, in_sync, out) animates."""

    def __init__(self, n: int = 3, **kw):
        super().__init__(**kw)
        self.marks = VGroup(*[VGroup(Square(0.3, fill_color=SYNC, fill_opacity=0.9, stroke_width=0), label(str(i + 1), 14, BG)) for i in range(n)]).arrange(RIGHT, buff=0.06)
        self.name = label("in-sync", 15, SYNC).next_to(self.marks, DOWN, buff=0.05).align_to(self.marks, RIGHT)   # under the marks: the HWM label rides at the marks' height
        self.add(self.name, self.marks)

    def set(self, in_sync, out=(), gone=()):
        anims = []
        for i, m in enumerate(self.marks):
            colour = SYNC if i + 1 in in_sync else FAIL if i + 1 in out else DIM
            anims += [m[0].animate.set_fill(colour, 0.9 if i + 1 not in gone else 0.35), m[1].animate.set_color(BG if i + 1 not in gone else MUTED)]
        return anims


def claim_still(text: str, color: str = LOGC) -> Text:
    """The claim line without animation, for rebuilding a previous scene's last frame."""
    return label(text, 17, color).move_to([-MARGIN, CAPTION_Y, 0], aligned_edge=LEFT)


# ------------------------------------------------------------------------------------------------ the deck's stages
# Every scene after the first opens on the previous scene's last frame, rebuilt statically from these builders, and then
# transforms it. A builder returns a dict of named parts at their final positions; the scene that owns the picture uses
# the same builder for its own start, so the two frames cannot drift apart.

# move 1, the log
LOG_CELL, LOG_Y, ROW_C = 0.55, 1.55, -1.3
LOG_SEQ = [KEY_A, KEY_B, KEY_A, KEY_C, KEY_B, KEY_A, KEY_C, KEY_A]   # the eight records the log holds at the end of move 1
NAMES = {KEY_A: "alice", KEY_B: "bob", KEY_C: "carol"}


def legend() -> VGroup:
    return VGroup(*[VGroup(Square(0.22, fill_color=c, fill_opacity=0.9, stroke_width=0), label(f"key {NAMES[c]}", 15, MUTED)).arrange(RIGHT, buff=GAP_TIGHT)
                    for c in KEYS]).arrange(RIGHT, buff=GAP)


def log_stage() -> dict:
    """Move 1's picture before anything is written: producer, one broker spanning the band, an empty partition."""
    prod = producer().move_to([-5.45, LOG_Y, 0])
    brk = broker("broker", 10.6, 3.0).move_to([1.1, 1.1, 0])
    brk[1].align_to(brk[0].get_left() + RIGHT * 0.25, LEFT)
    log = Log(-3.6, LOG_Y, capacity=12, name="topic payments, one partition", cell=LOG_CELL, gap=GAP)
    leg = legend().move_to([6.15, 2.35, 0], aligned_edge=RIGHT)
    ar = Arrow(prod.get_right() + RIGHT * 0.1, [brk[0].get_left()[0] - 0.1, LOG_Y, 0], buff=0, color=MUTED, stroke_width=2.2, tip_length=0.18)
    al = label("append", 14, MUTED).next_to(ar, UP, buff=0.05)
    return {"prod": prod, "brk": brk, "log": log, "leg": leg, "ar": ar, "al": al}


def log_end() -> dict:
    """Move 1's last frame: eight records, two consumers with their pointers, the position counter, the reset setting."""
    d = log_stage()
    for c in LOG_SEQ:
        d["log"].put(c)
    d["c1"] = consumer("consumer 1").move_to([-3.2, ROW_C, 0])
    d["c2"] = consumer("consumer 2").move_to([0.0, ROW_C, 0])
    d["p1"] = Pointer("consumer 1", READER).place(d["log"], 3, dy=0.95)
    d["p2"] = Pointer("consumer 2", READER).place(d["log"], 2, dy=1.45)
    d["pos"] = Counter("consumer 1: offset of the next record", 3, "", READER, size=26).move_to([3.2, ROW_C, 0], aligned_edge=LEFT)
    d["reset"] = config("auto.offset.reset = latest", 15).move_to([MARGIN, ROW_C - 0.95, 0], aligned_edge=RIGHT)
    d["claim"] = claim_still("replay: move the offset back", READER)
    return d


# move 2, partitions
P_XS, P_BY, P_CY = [-4.0, 0.0, 4.0], 1.0, -1.3
KEY_PARTITION = {KEY_A: 0, KEY_B: 1, KEY_C: 2}
import random as _random
P_FIRST = [_random.Random(2).choice(KEYS) for _ in range(4)]          # the four records written before the split (same seed as the scene)
P_FILL = [P_FIRST + [KEY_A] * 3, [KEY_B] * 3, [KEY_C] * 3]           # what the three partitions hold at the end of move 2


def partitions_stage() -> dict:
    prod = producer("producer").move_to([0.0, 2.45, 0])
    brokers = VGroup(*[broker(f"broker {i + 1}", 3.8, 2.1).move_to([x, P_BY, 0]) for i, x in enumerate(P_XS)])
    logs = [Log(x - 1.75, P_BY - 0.2, capacity=7, name=f"partition {i}", gap=GAP) for i, x in enumerate(P_XS)]
    load = Gauge("write\nload", FAIL, 1.8).move_to([-6.55, P_BY, 0])
    return {"prod": prod, "brokers": brokers, "logs": logs, "load": load}


def partitions_end() -> dict:
    """Move 2's last frame: three partitions filled, two consumers left in the group, three pointers, the offsets log."""
    d = partitions_stage()
    for log, fill in zip(d["logs"], P_FILL):
        for c in fill:
            log.put(c)
    d["load"].fill.become(Rectangle(width=0.30, height=d["load"].h * 0.35, fill_color=FAIL, fill_opacity=0.9, stroke_width=0).move_to(d["load"].frame.get_bottom() + UP * 0.03, aligned_edge=DOWN))
    d["hashc"] = code("partition = hash(key) % 3", "python", 16).next_to(d["prod"], RIGHT, buff=GAP_WIDE)
    cons = [consumer(f"consumer {i + 1}").move_to([x, P_CY, 0]) for i, x in enumerate(P_XS)]
    d["cons"] = cons
    d["grp"] = SurroundingRectangle(VGroup(*cons), color=READER, buff=GAP, corner_radius=0.1, stroke_width=1.5)
    d["gl"] = label("consumer group: one partition per member", 16, READER).next_to(d["grp"], UP, buff=GAP_TIGHT).align_to(d["grp"], LEFT)
    d["ptrs"] = [Pointer(n, READER).place(d["logs"][i], min(6, len(d["logs"][i].cells))) for i, n in enumerate(("c1", "c2", "c2"))]   # six read rounds happened
    olog = Log(-2.9, -2.5, capacity=12, name="__consumer_offsets: committed positions, a compacted topic", gap=GAP)
    for _ in range(4):
        olog.put(READER)
    d["olog"] = olog
    d["claim"] = claim_still("the readers' positions are a log too", READER)
    return d


# move 3, replication
R_YS, R_BW, R_X0, R_CAP, R_CELL, R_XR = [1.7, 0.0, -1.7], 6.6, -3.05, 8, 0.5, 3.3
R_SEQ = [KEY_A, KEY_B, KEY_C, KEY_A, KEY_A, KEY_B, KEY_A, KEY_C]   # the eight records every replica holds at the end of move 3


def replication_stage(names=("broker 1: leader", "broker 2: follower", "broker 3: follower")) -> dict:
    boxes = VGroup(*[box(R_BW, 1.55, n, LOGC, size=17, name_align="left").move_to([0.0, y, 0]) for y, n in zip(R_YS, names)])
    logs = [Log(R_X0, y - 0.2, capacity=R_CAP, cell=R_CELL, gap=GAP) for y in R_YS]
    prod = producer().move_to([-5.45, R_YS[0], 0])
    cons = consumer("consumer", w=1.9).move_to([5.45, R_YS[0], 0])
    return {"boxes": boxes, "logs": logs, "prod": prod, "cons": cons}


def hwm_marker() -> VGroup:
    hwm = VGroup(Line(UP * 0.38, DOWN * 0.38, color=SYNC, stroke_width=3), label("HWM", 15, SYNC))
    hwm[1].next_to(hwm[0], UP, buff=0.04)
    return hwm


def hwm_pos(log: Log, i: int):
    return [log.slot(i)[0] - log.pitch / 2, log.y + 0.17, 0]


def replication_end() -> dict:
    """Move 3's last frame: broker 2 leads, all three copies hold the same eight records and are in sync."""
    d = replication_stage(("broker 1: follower", "broker 2: leader", "broker 3: follower"))
    d["boxes"][1][1].set_color(SYNC)
    for log in d["logs"]:
        for c in R_SEQ:
            log.put(c)
    d["isr"] = Isr(3).move_to([d["boxes"][1][0].get_right()[0] - 0.25, d["boxes"][1][0].get_top()[1] - 0.42, 0], aligned_edge=RIGHT)
    d["hwm"] = hwm_marker().move_to(hwm_pos(d["logs"][1], 8))
    d["ptr"] = Pointer("consumer", READER).place(d["logs"][1], 3, dy=0.55)
    d["a_in"] = arrow(d["prod"], d["boxes"][1], "acks=all", MUTED)
    d["a_out"] = arrow(d["boxes"][1], d["cons"], "fetch", MUTED)
    d["claim"] = claim_still("back as a follower: fetch, catch up, rejoin", LOGC)
    return d


# move 4, retention and compaction
S_Y, S_XS, S_CY, S_XR = 1.45, [-4.3, 0.0, 4.3], -1.75, 3.2
S_NAMES = ("00000000000000000000.log", "00000000000000000008.log", "00000000000000000016.log")
S_SEQ = R_SEQ + [KEY_B, KEY_C, KEY_A, KEY_B, KEY_A, KEY_C, KEY_B, KEY_A, KEY_C, KEY_B, KEY_A, KEY_B, KEY_C]   # segment 0 is the leader's log of move 3
C_SEQ = [KEY_A, KEY_B, KEY_C, KEY_A, KEY_B, KEY_A, KEY_C, KEY_B]


def retention_stage() -> dict:
    segs = VGroup(*[broker(n, 4.1, 1.7).move_to([x, S_Y, 0]) for n, x in zip(S_NAMES, S_XS)])
    logs = [Log(x - 1.85, S_Y - 0.22, capacity=8, base=b, cell=0.38, gap=GAP) for x, b in zip(S_XS, (0, 8, 16))]
    for i, l in enumerate(logs):
        for k in range(8 if i < 2 else 5):
            l.put(S_SEQ[i * 8 + k])
    pl = label("one partition on disk: segment files", 17, LOGC).next_to(segs, UP, buff=GAP_TIGHT).align_to(segs, LEFT)
    active = label("active segment: appends go here", 15, LOGC).next_to(segs[2], DOWN, buff=GAP_TIGHT).align_to(segs[2], LEFT)
    return {"segs": segs, "logs": logs, "pl": pl, "active": active}


def retention_end() -> dict:
    """Move 4's last frame: segment 0 deleted, the slow consumer reset to offset 8, the compacted topic below."""
    d = retention_stage()
    d["ptr"] = Pointer("consumer, slow", READER).place(d["logs"][1], 0, dy=0.95)
    clog = Log(-4.6, S_CY, capacity=12, name="topic account-balances: the latest state per key", gap=GAP)
    for c in C_SEQ:
        clog.put(c)
    keep = {}
    for i, c in enumerate(clog.cells):
        keep[c.get_fill_color().to_hex()] = i
    survivors = sorted(keep.values())
    for i in range(len(C_SEQ)):   # after compaction only the latest per key is drawn; after the tombstone, bob is gone too
        if i not in survivors or C_SEQ[i] == KEY_B:
            clog.cells[i].set_opacity(0); clog.offs[i].set_opacity(0)
    d["clog"] = clog
    d["headl"] = label("latest record per key; offsets keep gaps", 15, LOGC).next_to(clog.rail, DOWN, buff=0.45).align_to(clog.rail, LEFT)
    d["compc"] = config("cleanup.policy\n= compact", 15).move_to([S_XR, S_CY, 0], aligned_edge=LEFT)
    d["delc"] = config("delete.retention.ms\n= 86400000", 15).next_to(d["compc"], DOWN, buff=GAP).align_to(d["compc"], LEFT)
    d["dr"] = Counter("tombstone age", 24, "h", MUTED, size=24).move_to([S_XR, S_CY + 1.05, 0], aligned_edge=LEFT)
    d["claim"] = claim_still("a tombstone deletes the key, then is removed itself", KEY_B)
    return d
