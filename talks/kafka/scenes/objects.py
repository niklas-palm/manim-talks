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
