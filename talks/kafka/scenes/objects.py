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
