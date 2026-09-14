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

SIDE, GAP = 0.34, 0.06          # a record cell and the gap between cells
PITCH = SIDE + GAP


class Log(VGroup):
    """A partition: an append-only row of record cells with their offsets beneath, on a rail of `capacity` slots.
    append(scene, colour, source) drops a record into the next slot from `source` (a producer or a leader's cell).
    cells[i] is the record at offset base + i; offs[i] its offset label. The rail is log[0]."""

    def __init__(self, x0: float, y: float, capacity: int = 12, base: int = 0, name: str = "", **kw):
        super().__init__(**kw)
        self.x0, self.y, self.capacity, self.base = x0, y, capacity, base
        self.rail = Rectangle(width=capacity * PITCH + GAP, height=SIDE + 0.14, stroke_color=DIM, stroke_width=1.2, fill_opacity=0)
        self.rail.move_to([x0 + (capacity * PITCH + GAP) / 2, y, 0])
        self.cells, self.offs = VGroup(), VGroup()
        self.add(self.rail, self.cells, self.offs)
        if name:
            self.name = label(name, 13, MUTED).next_to(self.rail, UP, buff=0.06).align_to(self.rail, LEFT)
            self.add(self.name)

    def slot(self, i: int):
        return [self.x0 + GAP + SIDE / 2 + i * PITCH, self.y, 0]

    def record(self, i: int, color: str) -> Square:
        return Square(SIDE, fill_color=color, fill_opacity=0.9, stroke_width=0).move_to(self.slot(i))

    def offset_label(self, i: int) -> Text:
        return label(str(self.base + i), 12, MUTED).move_to([self.slot(i)[0], self.y - SIDE / 2 - 0.2, 0])

    def append(self, scene, color: str, source=None, rt: float = 0.35, extra=()):
        """Animate a record arriving at the next slot; returns the cell."""
        i = len(self.cells)
        cell, off = self.record(i, color), self.offset_label(i)
        if source is not None:
            cell.move_to(source.get_center() if hasattr(source, "get_center") else source)
            scene.add(cell)
            scene.play(cell.animate.move_to(self.slot(i)), *extra, run_time=rt)
            scene.play(FadeIn(off), run_time=0.15)
        else:
            scene.play(FadeIn(cell, shift=DOWN * 0.15), FadeIn(off), *extra, run_time=rt)
        self.cells.add(cell); self.offs.add(off)
        return cell

    def put(self, color: str) -> Square:
        """Place a record without animation (for a picture that starts already filled)."""
        i = len(self.cells)
        cell, off = self.record(i, color), self.offset_label(i)
        self.cells.add(cell); self.offs.add(off)
        return cell

    def below(self, i: int, dy: float = 0.62):
        """A point under offset i, where a consumer's pointer sits."""
        return [self.slot(i)[0], self.y - dy, 0]


class Pointer(VGroup):
    """A consumer's position: a small triangle under the log pointing at the next record to read, with the
    consumer's name beside it. at(log, i) moves it; the offset it holds is one integer, and that is the point."""

    def __init__(self, name: str, color: str = READER, **kw):
        super().__init__(**kw)
        self.tri = Triangle(color=color, fill_color=color, fill_opacity=1.0, stroke_width=0).scale(0.11)
        self.tag = label(name, 12, color).next_to(self.tri, DOWN, buff=0.04)
        self.add(self.tri, self.tag)

    def place(self, log: Log, i: int, dy: float = 0.62):
        self.tri.move_to(log.below(i, dy)); self.tag.next_to(self.tri, DOWN, buff=0.04)
        return self

    def to(self, log: Log, i: int, dy: float = 0.62):
        target = self.copy().place(log, i, dy)
        return Transform(self, target)


def producer(name: str = "producer", w: float = 1.6) -> VGroup:
    return node(name, TEXT, w=w, h=0.55, size=17)


def consumer(name: str, w: float = 1.5) -> VGroup:
    return node(name, READER, w=w, h=0.55, size=17)


def broker(name: str, w: float, h: float, color: str = LOGC) -> VGroup:
    return box(w, h, name, color, size=16)


def read_flash(scene, cell: Square, pointer: Pointer, target: VGroup, rt: float = 0.3):
    """A consumer reads the record under its pointer: the record's copy travels to the consumer, the pointer advances."""
    c = cell.copy()
    scene.play(c.animate.move_to(target.get_center()).scale(0.6), run_time=rt)
    scene.play(FadeOut(c), run_time=0.12)
