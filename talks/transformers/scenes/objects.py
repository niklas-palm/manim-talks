"""This talk's vocabulary on top of the shared library.

Colours, each with one meaning for the whole deck:
  TOKEN  (blue)    a token's vector, the thing that flows down the stack (the "residual stream")
  QUERY  (yellow)  what a token is looking for
  KEY    (teal)    how a token answers other tokens' queries
  VALUE  (green)   what a token hands over when its key matches
  WEIGHTS(violet)  the learned matrices (Wq, Wk, Wv, feed-forward, the vocabulary matrix)
  ATTN   (orange)  attention weights and the update a layer computes; also the position vector added at the start
  MASK   (red)     a blocked connection (the causal mask)

Vocabulary of shapes: a token is a square; a vector is a column of shaded cells (8 drawn for 512); a matrix is a
grid; a multiplication is one row of the matrix lighting up against the vector, its products collapsing into one
output cell, then the sweep of the remaining rows. A read over many things is a fan of lines. A distribution is a row
of bars. Cells are 0.14 to 0.25 units unless a picture is a deliberate miniature (the layer stack).
"""
from lib.palette import *

TOKEN, QUERY, KEY, VALUE, WEIGHTS, ATTN, MASK = BLUE, YELLOW, TEAL, GREEN, VIOLET, ORANGE, RED
set_thread({"token": TOKEN, "tokens": TOKEN, "query": QUERY, "queries": QUERY, "key": KEY, "keys": KEY,
            "value": VALUE, "values": VALUE, "attention": ATTN, "weights": WEIGHTS, "weight": WEIGHTS})

WORDS = ["The", "cat", "sat", "on", "the", "mat"]
XS = [-5.0 + 1.9 * i for i in range(6)]   # the six token columns, used by every scene that shows the sentence
ROW_Y = 1.75                              # the persistent row of token vectors sits here
D = 8                                     # cells drawn per vector; the real model has 512 (a named simplification)


def softmax(scores) -> list:
    import math
    m = max(scores)
    ex = [math.exp(s - m) for s in scores]
    tot = sum(ex)
    return [e / tot for e in ex]


def layer_glyph(w: float = 4.2, h: float = 0.74) -> VGroup:
    """One layer as a miniature of the pictures already shown: a vector goes in, becomes query/key/value, the fan reads
    the row, the feed-forward grid, a vector comes out. Repeated down the stack so the audience sees "the same again".
    A deliberate miniature: its cells are below the usual minimum because the full-size version was just shown."""
    box_ = RoundedRectangle(corner_radius=0.1, width=w, height=h, stroke_color=WEIGHTS, stroke_width=2, fill_color=WEIGHTS, fill_opacity=0.08)
    vin = column(4, TOKEN, 0.1)
    tri = VGroup(column(3, QUERY, 0.08), column(3, KEY, 0.08), column(3, VALUE, 0.08)).arrange(RIGHT, buff=0.03)
    fan = VGroup(*[Line(ORIGIN, RIGHT * 0.45 + UP * (0.16 - 0.08 * i), color=MUTED, stroke_width=1.2) for i in range(5)])
    att = column(3, ATTN, 0.08)
    ff = grid(4, 6, WEIGHTS, cell=0.08)
    vout = column(4, TOKEN, 0.1)
    inner = VGroup(vin, tri, fan, att, ff, vout).arrange(RIGHT, buff=0.22).move_to(box_)
    return VGroup(box_, inner)
