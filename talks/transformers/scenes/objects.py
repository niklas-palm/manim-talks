"""This talk's vocabulary on top of the shared library.

Colours, each with one meaning for the whole deck:
  TOKEN  (blue)    a token's vector, the thing that flows down the stack (the "residual stream")
  QUERY  (yellow)  what a token is looking for
  KEY    (teal)    how a token answers other tokens' queries
  VALUE  (green)   what a token hands over when its key matches
  WEIGHTS(violet)  the learned matrices (Wq, Wk, Wv, feed-forward, the vocabulary matrix)
  ATTN   (orange)  the result of attention, and positional information added to a vector
  MASK   (red)     a blocked connection (the causal mask)

Vocabulary of shapes (shared with the reference deck): a token is a square; a vector is a thin column of shaded
cells; a matrix is a grid; a multiplication is one row of the matrix lighting up against the vector, its products
collapsing into one output cell, then the sweep of the remaining rows. A read over many things is a fan of lines.
"""
from lib.palette import *
import random

TOKEN, QUERY, KEY, VALUE, WEIGHTS, ATTN, MASK = BLUE, YELLOW, TEAL, GREEN, VIOLET, ORANGE, RED
set_thread({"token": TOKEN, "tokens": TOKEN, "query": QUERY, "queries": QUERY, "key": KEY, "keys": KEY,
            "value": VALUE, "values": VALUE, "attention": ATTN, "weights": WEIGHTS, "weight": WEIGHTS})

DIM_DRAWN = 8   # cells drawn per vector; the real model has 512 (a named simplification, said in labels)


def vector(seed: int, color: str = TOKEN, cell: float = 0.12, n: int = DIM_DRAWN) -> VGroup:
    """A vector: n cells whose shades stand for different numbers, so two vectors look different."""
    rnd = random.Random(seed)
    return VGroup(*[Square(cell, fill_color=color, fill_opacity=0.3 + 0.7 * rnd.random(), stroke_width=0) for _ in range(n)]).arrange(DOWN, buff=0.02)


def shades(v: VGroup) -> list:
    return [c.get_fill_opacity() for c in v]


def restore(v: VGroup, ops: list, color: str):
    return [c.animate.set_fill(color, o) for c, o in zip(v, ops)]


def dot_product(scene, vec, vcolor, mat, i, out, color, cols: int = DIM_DRAWN):
    """One output number, slowly: the vector's cells and the matrix row's cells light up together, the products
    collapse into the output cell. The first, slow demonstration of the multiplication every layer is made of."""
    ops = shades(vec)
    row = [mat[i * cols + j] for j in range(cols)]
    for j in range(cols):
        scene.play(vec[j].animate.set_fill(color, 1.0), row[j].animate.set_fill(color, 1.0), run_time=0.08)
    prods = VGroup(*[Square(0.09, fill_color=color, fill_opacity=1.0, stroke_width=0).move_to(c) for c in row])
    scene.add(prods)
    scene.play(*[p.animate.move_to(out) for p in prods], run_time=0.5)
    scene.play(FadeOut(prods), out.animate.set_fill(color, 0.95), *restore(vec, ops, vcolor), *[m.animate.set_fill(WEIGHTS, 0.6) for m in row], run_time=0.3)


def sweep(scene, vec, vcolor, jobs, cols: int = DIM_DRAWN, rt: float = 0.14):
    """Every row at speed, for one or more matrices at once: a row lights with the vector, one output cell fills.
    jobs = [(matrix, out, colour)]. The point of the picture: one output vector reads the whole matrix.
    The dim-again builders are made AFTER the on-play; a second .animate on a cell would overwrite the first target."""
    ops = shades(vec)
    for i in range(len(jobs[0][1])):
        rows = [[mat[i * cols + j] for j in range(cols)] for mat, _, _ in jobs]
        on = [c.animate.set_fill(OUTLINE_ON, 1.0) for c in vec]
        for row, (_, out, color) in zip(rows, jobs):
            on += [m.animate.set_fill(color, 1.0) for m in row] + [out[i].animate.set_fill(color, 0.95)]
        scene.play(*on, run_time=rt)
        off = [m.animate.set_fill(WEIGHTS, 0.6) for row in rows for m in row]
        scene.play(*off, *restore(vec, ops, vcolor), run_time=rt * 0.4)


OUTLINE_ON = "#FFFFFF"


def softmax_bars(scores, x: float, y: float, w: float = 0.9, colour: str = ATTN) -> VGroup:
    """Bars whose heights are a softmax over `scores`: the attention weights. Sum to 1, tallest emphasised."""
    import math
    m = max(scores)
    ex = [math.exp(s - m) for s in scores]
    tot = sum(ex)
    weights = [e / tot for e in ex]
    g = VGroup()
    for wt in weights:
        top = max(weights)
        g.add(Rectangle(width=0.22, height=max(0.03, wt * w * len(scores)), fill_color=colour, fill_opacity=0.4 + 0.55 * (wt == top), stroke_width=0))
    g.arrange(RIGHT, buff=0.06, aligned_edge=DOWN).move_to([x, y, 0], aligned_edge=DOWN)
    return g, weights
