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

TOKEN, QUERY, KEY, VALUE, WEIGHTS, ATTN, MASK = A1, A2, A4, A5, A3, A6, ALERT
set_thread({"token": TOKEN, "tokens": TOKEN, "query": QUERY, "queries": QUERY, "key": KEY, "keys": KEY,
            "value": VALUE, "values": VALUE, "attention": ATTN, "weights": WEIGHTS, "weight": WEIGHTS})

WORDS = ["The", "cat", "sat", "on", "the", "mat"]
XS = [-4.75 + 1.9 * i for i in range(6)]  # the six token columns, symmetric about x = 0, used by every scene that shows the sentence
ROW_Y = 1.85                              # the persistent row of token vectors is centred here; its word labels clear the title
D = 8                                     # cells drawn per vector; the real model has 512 (a named simplification)


def token_row(cell: float = 0.16, y: float = ROW_Y) -> tuple:
    """The six token vectors with their words above, across the top of the picture. Returns (group, list of vectors)."""
    g, vecs = VGroup(), []
    for k, (w, x) in enumerate(zip(WORDS, XS)):
        v = vector(20 + k, TOKEN, cell=cell).move_to([x, y, 0])
        lab = label(w, 18, TOKEN).next_to(v, UP, buff=GAP_TIGHT)
        g.add(VGroup(v, lab)); vecs.append(v)
    return g, vecs


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
    box_ = RoundedRectangle(corner_radius=rad(0.67), width=w, height=h, stroke_color=WEIGHTS, stroke_width=sw(0.8), fill_color=WEIGHTS, fill_opacity=FILL * 0.8)
    vin = column(4, TOKEN, 0.1)
    tri = VGroup(column(3, QUERY, 0.08), column(3, KEY, 0.08), column(3, VALUE, 0.08)).arrange(RIGHT, buff=0.03)
    fan = VGroup(*[Line(ORIGIN, RIGHT * 0.45 + UP * (0.16 - 0.08 * i), color=MUTED, stroke_width=sw(0.48)) for i in range(5)])
    att = column(3, ATTN, 0.08)
    ff = grid(4, 6, WEIGHTS, cell=0.08)
    vout = column(4, TOKEN, 0.1)
    inner = VGroup(vin, tri, fan, att, ff, vout).arrange(RIGHT, buff=0.22).move_to(box_)
    return VGroup(box_, inner)


# ------------------------------------------------------------------------------------------------ hand-overs
# Every scene after the first starts on the previous scene's last frame, rebuilt with these. The producing scene uses
# the same builders for the objects that survive to its end, so both frames agree to the pixel.

VEC_Y = -1.0                              # where the embedding vectors sit under their tokens (move 2)
SCORES = [1.2, 0.4, 2.1, 0.2, 0.9, 2.6]   # illustrative match strengths for "mat"; the mechanism is exact, the numbers are chosen
QBIG_POS = [5.4, ROWS[2] - 0.7, 0]        # the chosen query, right of the "mat" bar; its label sits to its right, so the fan to the keys crosses nothing
OUT_POS = [5.4, ROWS[4] + 0.45, 0]
PIPE_Y = -1.25                            # the centre line of the layer and prediction pictures (moves 4 and 5); low enough that two-line labels above the vectors clear the token row


def big_tokens(side: float = 1.3, y: float = ROWS[1]) -> VGroup:
    """The six tokens as squares with their words inside (move 1 at 1.3, move 2 at 1.0)."""
    toks = VGroup(*[VGroup(Square(side, fill_color=TOKEN, fill_opacity=SOLID * 0.94, stroke_width=0), label(w, 28 if side > 1.1 else 22, "#0f1116")) for w in WORDS])
    for g, x in zip(toks, XS):
        g.move_to([x, y, 0]); g[1].move_to(g[0])
    return toks


def all_edges(toks: VGroup) -> VGroup:
    """Every token connected to every other, arcs bowing below the tokens (the n squared picture of move 1)."""
    edges = VGroup()
    for a in range(6):
        for b in range(6):
            if a != b:
                edges.add(ArcBetweenPoints(toks[a][0].get_bottom(), toks[b][0].get_bottom(), angle=PI / 2.2 if a < b else -PI / 2.2,
                                           color=ATTN, stroke_width=sw(0.8), stroke_opacity=0.6))
    return edges


def sequential_counters(steps: int = 1, conns: int = 30) -> tuple:
    a = Counter("sequential steps to read the sentence", steps, "", GREEN, size=30).move_to([COLS[0], ROWS[4], 0], aligned_edge=LEFT)
    b = Counter("connections: every token to every other", conns, "", ATTN, size=30).move_to([COLS[2], ROWS[4], 0], aligned_edge=LEFT)
    return a, b


def sentence_label() -> Text:
    return label("The cat sat on the mat", 34, TOKEN).move_to([0, ROWS[0], 0])


def embed_vectors(solid: bool = False) -> VGroup:
    """One vector under each token (move 2). solid=True is the state after the position vector was added."""
    g = VGroup(*[vector(20 + k, TOKEN, cell=0.22).move_to([XS[k], VEC_Y, 0]) for k in range(6)])
    if solid:
        for v in g:
            v.set_fill(TOKEN, 1.0)
    return g


def position_label() -> Text:
    return label("position vector added, one per slot", 18, ATTN).move_to([0, ROWS[4] - 0.25, 0])


def triples(vecs) -> VGroup:
    """Every token's query, key and value under its vector (move 3)."""
    return VGroup(*[VGroup(column(3, QUERY, 0.2), column(3, KEY, 0.2), column(3, VALUE, 0.2)).arrange(RIGHT, buff=0.05).next_to(vecs[k], DOWN, buff=GAP) for k in range(6)])


def softmax_bars() -> tuple:
    """The attention weights of "mat" as bars under the tokens, with their values and the label. Returns (bars, labels, caption)."""
    weights = softmax(SCORES)
    bars = VGroup(*[Rectangle(width=0.5, height=max(0.05, w * 3.4), fill_color=ATTN, fill_opacity=SOLID * 0.5 + 0.5 * (w == max(weights)), stroke_width=0)
                    .move_to([XS[j], ROWS[4], 0], aligned_edge=DOWN) for j, w in enumerate(weights)])
    wlabels = VGroup(*[label(f"{w:.2f}", 18, ATTN).next_to(b, UP, buff=GAP_TIGHT) for b, w in zip(bars, weights)])
    bl = label("softmax: weights that sum to 1", 18, ATTN).move_to([0, ROWS[4] - 0.35, 0])
    return bars, wlabels, bl


def attention_result() -> tuple:
    """The chosen query and the new vector for "mat", at the right (move 3's last frame). Returns (qbig, qbl, out, outl)."""
    qbig = column(3, QUERY, 0.28).move_to(QBIG_POS)
    qbl = label('query\nof "mat"', 18, QUERY).next_to(qbig, RIGHT, buff=GAP_TIGHT)
    out = column(3, ATTN, 0.28, op=0.95).move_to(OUT_POS)
    outl = label('new vector\nfor "mat"', 18, ATTN).next_to(out, DOWN, buff=GAP_TIGHT).align_to(out, LEFT)   # under it, left-aligned: clear of the "mat" bar and of the frame edge
    return qbig, qbl, out, outl


def head_tiles() -> VGroup:
    """Three attention heads side by side, each with its own query, key, value and output (move 3, second scene)."""
    heads = VGroup()
    for hh in range(3):
        tile = VGroup(RoundedRectangle(corner_radius=rad(0.8), width=3.9, height=1.5, stroke_color=ATTN, stroke_width=sw(0.8), fill_color=ATTN, fill_opacity=FILL * 0.7),
                      label(f"head {hh + 1}: its own Wq, Wk, Wv", 17, ATTN))
        tile[1].next_to(tile[0].get_top(), DOWN, buff=GAP_TIGHT)
        trio = VGroup(column(3, QUERY, 0.22), column(3, KEY, 0.22), column(3, VALUE, 0.22)).arrange(RIGHT, buff=0.1)
        ar = Arrow(ORIGIN, RIGHT * 0.9, buff=0, color=MUTED, stroke_width=sw(), tip_length=0.18)
        outc = column(3, ATTN, 0.24)
        inner = VGroup(trio, ar, outc).arrange(RIGHT, buff=GAP).move_to(tile[0]).shift(DOWN * 0.2)
        tile.add(inner)
        heads.add(tile)
    return heads.arrange(RIGHT, buff=0.4).move_to([0, 0.0, 0])   # top at 0.75: clear of the token row (bottom 1.13)


def projection_parts(filled: bool = False) -> tuple:
    """The concatenated head outputs, the matrix Wo and the attention output for "mat". Returns (joined, jl, proj, pl, result, rl)."""
    y = -1.8   # under the head tiles (bottom -0.75) with a full GAP
    joined = column(9, ATTN, 0.16).move_to([COLS[1], y, 0])
    jl = label("concatenate\nthe three outputs", 17, ATTN).next_to(joined, LEFT, buff=GAP)
    proj = grid(8, 9, WEIGHTS, cell=0.16).move_to([COLS[2], y, 0])
    pl = label("one more matrix, Wo", 17, WEIGHTS).next_to(proj, DOWN, buff=GAP_TIGHT)   # below: above would touch the head tiles
    result = column(8, TOKEN, 0.16, op=0.95 if filled else 0.0).move_to([COLS[3] - 0.6, y, 0])
    rl = label('attention output for "mat":\nthe token\'s size again', 17, TOKEN).next_to(result, RIGHT, buff=GAP)
    return joined, jl, proj, pl, result, rl


def layer_stack() -> tuple:
    """The layer repeated, as miniatures, with the count beside it (move 4's last frame). Returns (stack, label)."""
    stack = VGroup(*[layer_glyph(5.0, 0.58) for _ in range(5)]).arrange(DOWN, buff=0.08).move_to([COLS[2] - 0.6, -0.8, 0])   # top at 0.81, clear of the token row
    nl = label("N layers:\n6 in 2017,\n30 to 100 today", 20, WEIGHTS).move_to([COLS[3], -0.8, 0], aligned_edge=LEFT)
    return stack, nl


def tiny_token(stack: VGroup) -> VGroup:
    """The token after the whole stack, small, under the last layer."""
    return vector(30, TOKEN, cell=0.1).next_to(stack, DOWN, buff=GAP)
