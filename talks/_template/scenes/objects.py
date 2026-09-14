"""This talk's vocabulary on top of the shared library. Fill in:
  * the meanings of the accent colours (four to six; one meaning each for the whole deck)
  * the nouns that carry those colours wherever they appear in titles and captions (set_thread)
  * drawings that several scenes share (a machine, a record, a node), so every scene draws them the same way
Every scene file starts with:  from lib.palette import *   and   from objects import *
"""
from lib.palette import *

# Example meanings; rename to the talk's own nouns. Keep the mapping small and never reuse a colour.
CLIENT, SERVER, DATA, STATE, HOTC = BLUE, VIOLET, YELLOW, TEAL, RED
set_thread({"client": CLIENT, "server": SERVER, "record": DATA, "records": DATA, "state": STATE})


def machine(name: str, w: float = 2.4, h: float = 1.4, color: str = SERVER) -> VGroup:
    """A shared drawing: a named box with a slot row inside it. Replace with whatever this talk draws three times."""
    g = box(w, h, name, color)
    slots = VGroup(*[Rectangle(width=0.3, height=0.2, stroke_color=DIM, stroke_width=1.2, fill_opacity=0) for _ in range(5)]).arrange(RIGHT, buff=0.06)
    slots.move_to(g[0].get_bottom() + UP * 0.35)
    g.add(slots)
    return g
