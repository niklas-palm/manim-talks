"""Move 1 as one continuous picture. A sentence at the top, its tokens beneath, the tokens' vectors under them, a stack
of layers on the left, the KV cache as a rack on the right (one column per token, one row per layer), the two gauges at
the edge, and the answer appearing in the sentence as it is sampled. Nothing is replaced: the camera zooms into a layer,
the layer opens up to show its parts, the camera zooms out, and the same objects then carry prefill, decode and the loop.
The camera goes in a second time during decode, to show the same weights being read for one column of work.

Vocabulary: a token is a square; a vector is a thin column of shaded cells; a weight matrix is a grid; a multiplication
is one row of the matrix lighting up against the vector, the products collapsing into one output cell, then the sweep
of the remaining rows. The sweep is the point: one output vector, the whole matrix read from memory. A read of the
cache is a fan of lines from the query to every stored key."""
from lib.palette import *
from objects import *
import random

WORDS = ["The", "cat", "sat", "on", "the"]
IDS = ["791", "8415", "7731", "389", "279"]
ROWS = (2, 9, 6, 11, 4)            # the embedding-table row each token selects
ANSWER = ["mat", ".", "It", "slept", "."]
L, TOK = 4, 10                     # layers drawn, token columns in the cache rack
ZOOM = 0.4
BRIGHT = "#A9F5EE"                 # a cache cell while it is being read


def small(s: str, color: str = TEXT) -> Text:
    """Text for the zoomed view: rendered large, scaled down, so Pango lays it out properly."""
    return label(s, 20, color).scale(0.3)


def cache_cell(slot: Mobject) -> Rectangle:
    return Rectangle(width=0.22, height=0.36, fill_color=CACHE, fill_opacity=0.9, stroke_width=0).move_to(slot)


def vector(seed: int, color: str = PROMPT, cell: float = 0.065) -> VGroup:
    """A token's vector: eight cells whose shades stand for different numbers, so two vectors look different."""
    rnd = random.Random(seed)
    return VGroup(*[Square(cell, fill_color=color, fill_opacity=0.3 + 0.7 * rnd.random(), stroke_width=0) for _ in range(8)]).arrange(DOWN, buff=0.012)


def shades(v: VGroup) -> list:
    return [c.get_fill_opacity() for c in v]


def restore(v: VGroup, ops: list, color: str):
    return [c.animate.set_fill(color, o) for c, o in zip(v, ops)]


def dot_product(scene, vec, vcolor, mat, i, out, color, cols: int = 8):
    """One output number, slowly: the vector's cells and the matrix row's cells light up in pairs, the eight products
    collapse into the output cell."""
    ops = shades(vec)
    row = [mat[i * cols + j] for j in range(cols)]
    for j in range(cols):
        scene.play(vec[j].animate.set_fill(OUTPUT, 1.0), row[j].animate.set_fill(OUTPUT, 1.0), run_time=0.09)
    prods = VGroup(*[Square(0.06, fill_color=OUTPUT, fill_opacity=1.0, stroke_width=0).move_to(c) for c in row])
    scene.add(prods)
    scene.play(*[p.animate.move_to(out) for p in prods], run_time=0.5)
    scene.play(FadeOut(prods), out.animate.set_fill(color, 0.95), *restore(vec, ops, vcolor), *[m.animate.set_fill(WEIGHTS, 0.6) for m in row], run_time=0.3)


def sweep(scene, vec, vcolor, jobs, cols: int = 8, rt: float = 0.14):
    """Multiply, at speed: for each output cell its row of the matrix lights up with the vector and the cell fills.
    jobs = [(matrix, out, colour)]; every matrix in the list is swept at the same time, one row per beat."""
    ops = shades(vec)
    for i in range(len(jobs[0][1])):
        rows = [[mat[i * cols + j] for j in range(cols)] for mat, _, _ in jobs]
        on = [c.animate.set_fill(OUTPUT, 1.0) for c in vec]
        for row, (_, out, color) in zip(rows, jobs):
            on += [m.animate.set_fill(OUTPUT, 1.0) for m in row] + [out[i].animate.set_fill(color, 0.95)]
        scene.play(*on, run_time=rt)
        # The dim-again builders are made only now: .animate generates a mobject's target when the builder is created, and a
        # second builder on the same cell would overwrite the first one's target, so the highlight would animate to violet.
        off = [m.animate.set_fill(WEIGHTS, 0.6) for row in rows for m in row]
        scene.play(*off, *restore(vec, ops, vcolor), run_time=rt * 0.4)


def single_parts(y: float):
    """The open layer for one token: three projections and their outputs, the attention vector, the feed-forward matrix
    and the output vector, at the single-column layout."""
    W = VGroup(*[grid(3, 8) for _ in range(3)])
    for m, dy in zip(W, (0.42, 0.0, -0.42)):
        m.move_to([-3.35, y + dy, 0])
    wl = VGroup(*[small(s_, WEIGHTS).next_to(m, LEFT, buff=0.06) for s_, m in zip(("Wq", "Wk", "Wv"), W)])
    q, k, v = column(3, TEXT, op=0.0), column(3, CACHE, op=0.0), column(3, CACHE, op=0.0)
    for c, m in zip((q, k, v), W):
        c.next_to(m, RIGHT, buff=0.12)
    att = column(8, PROMPT, op=0.0).move_to([-2.4, y, 0])
    ff = grid(8, 8).move_to([-1.75, y, 0])
    eq = small("=").move_to([-1.2, y, 0])
    outv = column(8, PROMPT, op=0.0).move_to([-1.0, y, 0])
    return W, wl, q, k, v, att, ff, eq, outv


def attend_one(scene, q, cells, att, color, rt: float = 0.5):
    """One query scored against every stored key, the values unfolding into the new vector. Returns the visible vector."""
    lines = VGroup(*[Line(q.get_right(), c.get_left(), color=TEXT, stroke_width=1.4, stroke_opacity=0.7) for c in cells])
    scene.play(Create(lines), LaggedStart(*[c.animate.set_fill(BRIGHT, 1.0) for c in cells], lag_ratio=0.1), run_time=rt)
    back = VGroup(*[Square(0.12, fill_color=CACHE, fill_opacity=0.9, stroke_width=0).move_to(c) for c in cells])
    scene.remove(att)
    att = column(8, color).move_to(att)
    scene.play(*[c.animate.set_fill(CACHE, 0.9) for c in cells], ReplacementTransform(back, att), FadeOut(lines), run_time=rt)
    return att


def replay_layer(scene, y: float, vec, keys: list, own_slot, rt: float = 0.07, color: str = PROMPT):
    """A whole layer at speed for one token: three projections, the key and value stored, the query read over the cache
    row, the feed-forward sweep. Returns (everything drawn, the output vector, the new cache cell)."""
    W, wl, q, k, v, att, ff, eq, outv = single_parts(y)
    scene.play(FadeIn(W), FadeIn(wl), FadeIn(q), FadeIn(k), FadeIn(v), run_time=0.3)
    sweep(scene, vec, color, [(W[0], q, TEXT), (W[1], k, CACHE), (W[2], v, CACHE)], rt=rt)
    cell = store_kv(scene, VGroup(k), VGroup(v), [own_slot], rt=0.4)[0]
    att = attend_one(scene, q, [*keys, cell], att, color, rt=0.4)
    scene.play(FadeIn(ff), FadeIn(eq), FadeIn(outv), run_time=0.25)
    sweep(scene, att, color, [(ff, outv, color)], rt=rt)
    return VGroup(W, wl, q, k, v, att, ff, outv, eq), outv, cell

ZP = 0.42                          # the prefill zoom is a little wider: five columns of work need the room
XW, XATT, XFF, XEQ, XOUT = -3.2, -1.9, -1.15, -0.72, -0.45


def block_of(n: int, color: str, rows: int = 8, cell: float = 0.07, op: float = 0.9) -> VGroup:
    """n vectors side by side: a block of tokens going through a layer together, or the layer's outputs for them."""
    return VGroup(*[column(rows, color, cell, op=op) for _ in range(n)]).arrange(RIGHT, buff=0.02)


def layer_parts(y: float, n: int):
    """The open layer for a block of n tokens: three projections and their outputs, the attention block, the feed-forward
    matrix and the output block, all at the block layout."""
    W = VGroup(*[grid(3, 8, cell=0.07) for _ in range(3)])
    for m, dy in zip(W, (0.38, 0.0, -0.38)):
        m.move_to([XW, y + dy, 0])
    wl = VGroup(*[small(s_, WEIGHTS).next_to(m, LEFT, buff=0.06) for s_, m in zip(("Wq", "Wk", "Wv"), W)])
    q, k, v = block_of(n, TEXT, 3, op=0.0), block_of(n, CACHE, 3, op=0.0), block_of(n, CACHE, 3, op=0.0)
    for c, m in zip((q, k, v), W):
        c.next_to(m, RIGHT, buff=0.1)
    att = block_of(n, PROMPT, op=0.0).move_to([XATT, y, 0])
    ff = grid(8, 8, cell=0.07).move_to([XFF, y, 0])
    eq = small("=").move_to([XEQ, y, 0])
    outv = block_of(n, PROMPT, op=0.0).move_to([XOUT, y, 0])
    return W, wl, q, k, v, att, ff, eq, outv


def dot_product_block(scene, vecs, vcolor, mat, i, outs, color, cols: int = 8):
    """One row of the matrix, read once, against every vector in the block, slowly: the row stays lit while each column
    takes its turn, and one output number lands in each column. The read is paid once; the arithmetic happens n times."""
    row = [mat[i * cols + j] for j in range(cols)]
    scene.play(*[m.animate.set_fill(OUTPUT, 1.0) for m in row], run_time=0.4)
    for c, v in enumerate(vecs):
        ops = shades(v)
        scene.play(*[cell.animate.set_fill(OUTPUT, 1.0) for cell in v], run_time=0.18)
        prods = VGroup(*[Square(0.05, fill_color=OUTPUT, fill_opacity=1.0, stroke_width=0).move_to(m) for m in row])
        scene.add(prods)
        scene.play(*[p_.animate.move_to(outs[c][i]) for p_ in prods], run_time=0.35)
        scene.play(FadeOut(prods), outs[c][i].animate.set_fill(color, 0.95), *restore(v, ops, vcolor), run_time=0.18)
    scene.play(*[m.animate.set_fill(WEIGHTS, 0.6) for m in row], run_time=0.2)


def sweep_block(scene, vecs, vcolor, jobs, cols: int = 8, rt: float = 0.14):
    """Every row at speed, for a block: a row lights once and one cell fills in each of the block's output columns.
    jobs = [(matrix, outs, colour)] with outs a block; all matrices in the list sweep together."""
    ops = [shades(v) for v in vecs]
    for i in range(len(jobs[0][1][0])):
        rows = [[mat[i * cols + j] for j in range(cols)] for mat, _, _ in jobs]
        on = [c.animate.set_fill(OUTPUT, 1.0) for v in vecs for c in v]
        for row, (_, outs, color) in zip(rows, jobs):
            on += [m.animate.set_fill(OUTPUT, 1.0) for m in row] + [o[i].animate.set_fill(color, 0.95) for o in outs]
        scene.play(*on, run_time=rt)
        off = [m.animate.set_fill(WEIGHTS, 0.6) for row in rows for m in row]   # built after the on-play; see sweep
        scene.play(*off, *[a for v, o in zip(vecs, ops) for a in restore(v, o, vcolor)], run_time=rt * 0.4)


def store_kv(scene, k, v, slots, rt: float = 0.9):
    """Each token's key and value fly into its own column of the layer's cache row."""
    cells = [cache_cell(sl) for sl in slots]
    ks, vs = [k[c].copy() for c in range(len(slots))], [v[c].copy() for c in range(len(slots))]
    scene.play(*[kc.animate.move_to(cell.get_center() + UP * 0.09).scale(0.75) for kc, cell in zip(ks, cells)],
               *[vc.animate.move_to(cell.get_center() + DOWN * 0.09).scale(0.75) for vc, cell in zip(vs, cells)], run_time=rt)   # the key on top, the value below: one cell
    scene.play(*[FadeIn(c_) for c_ in cells], *[FadeOut(m) for m in ks + vs], run_time=0.3)
    return cells


def attend_block(scene, q, cells, att, color, rt: float = 0.6):
    """Each token's query scored against its own key and the keys before it (the causal fan), the values unfolding into
    the attention block. Returns the visible block."""
    lines = VGroup(*[Line(q[c].get_right(), cells[j].get_left(), color=TEXT, stroke_width=1.2, stroke_opacity=0.6) for c in range(len(q)) for j in range(c + 1)])
    scene.play(Create(lines, lag_ratio=0.02), run_time=rt)
    scene.play(LaggedStart(*[c_.animate.set_fill(BRIGHT, 1.0) for c_ in cells], lag_ratio=0.15), run_time=rt * 0.8)
    back = VGroup(*[Square(0.12, fill_color=CACHE, fill_opacity=0.9, stroke_width=0).move_to(c_) for c_ in cells])
    scene.remove(att)
    att = block_of(len(q), color).move_to(att)
    scene.play(*[c_.animate.set_fill(CACHE, 0.9) for c_ in cells], ReplacementTransform(back, att), FadeOut(lines), run_time=rt * 1.4)
    return att


def replay_layer_block(scene, y: float, block, slots, rt: float = 0.07):
    """A whole layer at speed for the block, the second layer: project, store five keys and values, attend, feed-forward.
    Returns (everything drawn, the output block, the cache cells)."""
    W, wl, q, k, v, att, ff, eq, outv = layer_parts(y, len(block))
    scene.play(FadeIn(W), FadeIn(wl), FadeIn(q), FadeIn(k), FadeIn(v), run_time=0.3)
    sweep_block(scene, list(block), PROMPT, [(W[0], q, TEXT), (W[1], k, CACHE), (W[2], v, CACHE)], rt=rt)
    cells = store_kv(scene, k, v, slots, rt=0.4)
    att = attend_block(scene, q, cells, att, PROMPT, rt=0.3)
    scene.play(FadeIn(ff), FadeIn(eq), FadeIn(outv), run_time=0.25)
    sweep_block(scene, list(att), PROMPT, [(ff, outv, PROMPT)], rt=rt)
    return VGroup(W, wl, q, k, v, att, ff, outv, eq), outv, cells


class Mechanics(TalkSlide):
    def construct(self):
        frame = self.camera.frame
        t = title(self, "How a model answers, from text to text", "1  two jobs, two costs")
        # --- the sentence and its tokens
        sentence = label("The cat sat on the", 34, PROMPT).move_to([-6.4, 2.8, 0], aligned_edge=LEFT)
        self.play(Write(sentence), run_time=1.0)
        self.next_slide("""This talk is for engineers who will host a model, or buy hosting, and want to know what they are paying for.
        No product, no vendor; one stack we built to measure things, and the numbers it produced. One sentence carries the
        whole talk: a model reads your prompt once, then writes one token at a time, and every hosting decision is about which
        of those two you are paying for. Seven moves: two jobs and their costs, why the engine batches, three knobs, more than
        one GPU, what precision costs in answers, the fleet, and where the industry is. Start from actual text: a prompt someone typed. Five words. We follow them through the machine and out the
        other side, on one picture that only grows. Everything later in the talk is a consequence of what happens on this
        picture, so it is worth twenty minutes.""")
        toks = VGroup(*[VGroup(Square(0.5, fill_color=PROMPT, fill_opacity=0.9, stroke_width=0), label(w, 13, "#0f1116")) for w in WORDS]).arrange(RIGHT, buff=0.1).move_to([-6.4, 2.25, 0], aligned_edge=LEFT)
        ids = VGroup(*[label(i, 13, DIM).next_to(k, DOWN, buff=0.05) for i, k in zip(IDS, toks)])
        self.play(ReplacementTransform(sentence.copy(), toks), run_time=0.8)   # a copy is morphed, so toks itself is not padded with empty submobjects
        self.play(FadeIn(ids))
        cap = caption(self, "Tokenisation: text becomes integers from a fixed vocabulary")
        self.next_slide("""Tokenisation. The text is cut into tokens, whole words here and pieces of words in general, and each becomes an
        integer from a vocabulary of thirty to two hundred thousand entries. The model never sees letters, only these integers.
        The two 'the's differ, capitalised and not: two entries.""")
        # --- embedding: each integer selects a row of a table and becomes a vector
        table = VGroup(*[Square(0.13, fill_color=WEIGHTS, fill_opacity=0.5, stroke_width=0) for _ in range(14 * 8)]).arrange_in_grid(rows=14, cols=8, buff=0.02).move_to([3.4, 1.4, 0])
        tl = label("embedding table: one row per vocabulary entry, a few thousand numbers each", 13, WEIGHTS).next_to(table, UP, buff=0.12)
        self.play(FadeIn(table), FadeIn(tl))
        cap = swap_caption(self, cap, "Embedding: each integer selects a row; the token becomes a vector")
        vectors = VGroup()
        for i, row_i in enumerate(ROWS):
            row = VGroup(*[table[row_i * 8 + c] for c in range(8)])
            line = Line(ids[i].get_right(), row.get_left(), color=PROMPT, stroke_width=1.2, stroke_opacity=0.6)
            v = vector(row_i).next_to(toks[i], DOWN, buff=0.1)
            self.play(Create(line), *[c.animate.set_fill(PROMPT, 0.9) for c in row], run_time=0.25)
            self.play(ReplacementTransform(row.copy(), v), FadeOut(line), FadeOut(ids[i]), *[c.animate.set_fill(WEIGHTS, 0.5) for c in row], run_time=0.4)
            vectors.add(v)
        self.next_slide("""Embedding: each integer selects a row of a table; the token is now a vector of numbers. Then the lookup. The model holds a table with one row per vocabulary entry, a few thousand numbers in each row,
        learned like every other weight. Each integer selects its row, and that row is the token from now on: a vector, a
        column of numbers, drawn as eight shaded cells. Five tokens, five vectors, and the two 'the's are different rows. This
        is the only step where the integer matters; everything after this is arithmetic on these columns.""")
        # --- the stage: layers, cache rack, gauges, counters
        layers = VGroup(*[box(3.6, 0.5, "", WEIGHTS, fill=0.12) for _ in range(L)]).arrange(DOWN, buff=0.26).move_to([-2.6, -0.15, 0])
        ll = VGroup(*[label(f"layer {i + 1}", 12, WEIGHTS).next_to(b, LEFT, buff=0.12) for i, b in enumerate(layers)])
        more = label("of 32 to 96", 12, DIM).next_to(layers[-1], LEFT, buff=0.12).shift(DOWN * 0.4)
        rack = VGroup()
        for r in range(L):
            row = VGroup(*[Rectangle(width=0.26, height=0.4, stroke_color=DIM, stroke_width=1, fill_opacity=0) for _ in range(TOK)]).arrange(RIGHT, buff=0.05).move_to([0.9, layers[r].get_y(), 0], aligned_edge=LEFT)
            rack.add(row)
        rl = label("KV cache: one column per token, one row per layer", 13, CACHE).next_to(rack, UP, buff=0.12).align_to(rack, LEFT)
        bus, comp = Gauge("bus", OUTPUT, 1.5), Gauge("compute", PROMPT, 1.5)
        gauges = VGroup(bus, comp).arrange(RIGHT, buff=0.35).move_to([-6.0, -0.5, 0])
        reads = Counter("full reads of the model", 0, "", WEIGHTS, size=22).move_to([3.2, -2.7, 0], aligned_edge=LEFT)
        produced = Counter("tokens produced", 0, "", OUTPUT, size=22).move_to([5.3, -2.7, 0], aligned_edge=LEFT)
        self.play(FadeOut(cap), FadeOut(table), FadeOut(tl), FadeIn(layers), FadeIn(ll), FadeIn(more), FadeIn(rack), FadeIn(rl), FadeIn(gauges), FadeIn(reads), FadeIn(produced))
        self.next_slide("""The stage; everything from here on happens on it. The five vectors wait at the top. Left, the model: a stack of
        layers, four drawn of thirty to a hundred, each a set of weight matrices sitting in GPU memory. Right, the KV cache,
        empty: one column per token, one row per layer. At the edge, the two gauges the talk is about: how busy the memory bus
        is, moving bytes from memory into the chip, and how busy the arithmetic units are. Two counters at the bottom keep
        score.""")
        # --- the five vectors line up as a block; zoom into layer 1 with them; the layer opens up
        y0 = layers[0].get_y()
        block = vectors
        cap = caption(self, "Inside one layer: the five vectors arrive as a block", 22)
        ctx = VGroup(t, sentence, toks, rl, gauges, reads, produced, more, ll)   # captions never go in: a faded-out caption would come back with the group
        others = VGroup(*layers[2:], *rack[2:])
        self.play(frame.animate.scale(ZP).move_to([-1.5, y0 - 0.15, 0]), FadeOut(ctx), FadeOut(others), FadeOut(layers[1]), FadeOut(rack[1]), rack[0].animate.shift(LEFT * 1.0),
                  layers[0][0].animate.stretch_to_fit_height(1.3).stretch_to_fit_width(4.2).shift(RIGHT * 0.3),
                  block.animate.scale(0.07 / 0.065).arrange(RIGHT, buff=0.02).move_to([-4.05, y0, 0]), run_time=1.6)
        self.next_slide("""Inside one layer: the five vectors arrive together as a block, and the layer opens up. This is prefill, and we go inside it. The five vectors line up as a block, side by side, and go into layer one
        together. Zoom in and let the layer open up. The block arrives at the left. Everything the layer does, it does to this
        block: the same arithmetic on each of the five columns. Watch what that means for the weights.""")
        W, wl, q, k, v, att, ff, eq, outv = layer_parts(y0, 5)
        ql = VGroup(*[small(s_, col).next_to(c, RIGHT, buff=0.05) for s_, c, col in zip("qkv", (q, k, v), (TEXT, CACHE, CACHE))])
        self.play(FadeIn(W), FadeIn(wl), FadeIn(q), FadeIn(k), FadeIn(v), run_time=0.6)
        cap = swap_caption(self, cap, "One row, read once, multiplies all five vectors", 22)
        dot_product_block(self, list(block), PROMPT, W[0], 0, q, TEXT)
        self.next_slide("""One row of the matrix, read once, multiplies all five vectors: five output numbers for one read. Three weight matrices sit in the layer, and here is the arithmetic, once, slowly. One output number is one row of
        the matrix against one vector: each number in the row multiplies the number beside it in the vector, the eight
        products are summed, and the sum is one cell of the output. Now the point of the block. The row came in from memory
        once, and it stays lit while all five vectors take their turn against it: five multiplications, five output numbers,
        one read. In a real model the row and the vector are four thousand long, not eight, and the block is every token of
        the prompt. Everything a layer does is this operation, repeated.""")
        cap = swap_caption(self, cap, "Every row in turn: three matrices, read once, give five queries, keys, values", 22)
        sweep_block(self, list(block), PROMPT, [(W[0], q, TEXT), (W[1], k, CACHE), (W[2], v, CACHE)], rt=0.22)
        self.play(FadeIn(ql), run_time=0.3)
        self.next_slide("""Every row in turn: three matrices read once each give a query, a key and a value for all five tokens. Now every row, at speed, for all three matrices. Each row lights once and fills one cell in each of the five
        output columns. Filling the outputs touched every cell of all three matrices: to use a weight it has to come in from
        memory, so producing these outputs meant reading the matrices in full, once, for five columns of work. The outputs
        have names. The query is what a token is looking for in the tokens before it. The key is how it will answer other
        tokens' queries. The value is what it hands over when its key matches. Learned numbers, nothing more; the names
        describe the roles they end up playing.""")
        cap = swap_caption(self, cap, "Keys and values stored: this layer's row, one column per token", 22)
        cells1 = store_kv(self, k, v, [rack[0][i] for i in range(5)])
        self.next_slide("""The keys and values are stored: this layer's row, one column per token. That is the KV cache. The keys and the values are stored in the cache, in this layer's row, one column per token, and they stay for the
        life of the request. That is the whole content of the KV cache: for every token, in every layer, its key and its
        value. Later tokens need them, and recomputing them would mean re-running every earlier token through every layer.
        Storing them is what makes the cache; reading them is what will make the cache expensive.""")
        al = small("attention", PROMPT).next_to(att, UP, buff=0.06)
        cap = swap_caption(self, cap, "Attention: each query scored against the keys before it; weighted values summed", 22)
        att = attend_block(self, q, cells1, att, PROMPT)
        self.play(FadeIn(al), run_time=0.3)
        self.next_slide("""Attention: each query is scored against the keys up to its own; the weighted values form five new vectors. Now the queries do their work. Each token's query is compared with the keys of the tokens up to and including
        itself, one score per pair, and the values are added up weighted by those scores. The result is a new vector for
        each token that carries what it needed from its context. Two things to hold on to. This is the only place tokens
        influence each other. And every query reads the cache row: every key, every value, for every token before it. Five
        cells here; sixty thousand at a long context.""")
        fl = small("feed-forward", WEIGHTS).next_to(ff, UP, buff=0.06)
        self.play(FadeIn(ff), FadeIn(fl), FadeIn(eq), FadeIn(outv), run_time=0.5)
        cap = swap_caption(self, cap, "Feed-forward, most of the weights, read once for five columns", 22)
        sweep_block(self, list(att), PROMPT, [(ff, outv, PROMPT)], rt=0.14)
        # --- the output block drops into layer two, which does the same thing at speed: no new click, the picture repeating once
        y1 = layers[1].get_y()
        nxt = outv.copy()
        layers[1][0].stretch_to_fit_height(1.2).stretch_to_fit_width(4.2).shift(RIGHT * 0.3 + DOWN * 0.12)   # not on screen yet, so its open shape is set directly; opens downward, clear of layer one
        y1 -= 0.12
        rack[1].shift(LEFT * 1.0)
        layer1 = VGroup(W, wl, q, k, v, ql, att, al, ff, fl, outv, eq)
        self.play(frame.animate.move_to([-1.5, y0 - 0.55, 0]), FadeOut(layer1), FadeOut(block), layers[0][0].animate.stretch_to_fit_height(0.5),
                  FadeIn(layers[1]), FadeIn(rack[1]), nxt.animate.move_to([-4.05, y1, 0]), run_time=1.4)
        layer2, out2, cells2 = replay_layer_block(self, y1, nxt, [rack[1][i] for i in range(5)])
        nxt2 = out2.copy()
        self.play(nxt2.animate.move_to([XOUT, y1 - 1.1, 0]).set_opacity(0.0), run_time=0.8)
        self.remove(nxt2)
        self.next_slide("""Feed-forward, most of the weights, read once for five columns of work. Then layer two, the same, at speed. Then the big multiplication. The feed-forward part holds most of the layer's weights, in a real model tens of
        millions of numbers per layer, and it is the same arithmetic: one row per output number, read once, used for all
        five columns, and the highlight has touched every cell by the time the output block is full. That is prefill's
        shape: the weights come in once, and every byte that arrives does five columns of arithmetic, so the arithmetic
        units are the busy ones and the bus has slack. The output block is five vectors of the same shape as the input, and
        it drops into layer two, which has its own three matrices, its own cache row and its own feed-forward, and does
        exactly the same thing at speed: project, store five keys and values, attend, feed-forward, hand on. Thirty to a
        hundred times. So one layer, one block: read all the weights once, write one cache cell per token.""")
        self.play(FadeOut(layer2), FadeOut(nxt), FadeOut(cap), run_time=0.4)   # clear the open layer first, so the camera pulls back on a clean box
        block.scale(0.065 / 0.07).move_to([layers[0].get_x(), y1 + 0.12, 0])   # inside layer two, where the zoom left it
        self.play(frame.animate.scale(1 / ZP).move_to(ORIGIN), FadeIn(others), VGroup(rack[0], *cells1).animate.shift(RIGHT * 1.0), VGroup(rack[1], *cells2).animate.shift(RIGHT * 1.0),
                  layers[0][0].animate.stretch_to_fit_width(3.6).shift(LEFT * 0.3), layers[1][0].animate.stretch_to_fit_height(0.5).stretch_to_fit_width(3.6).shift(LEFT * 0.3 + UP * 0.12),
                  FadeIn(block), FadeIn(ctx), run_time=1.6)
        # --- prefill continues: the block goes down the rest of the stack at the speed it really happens
        filled = [list(cells1), list(cells2), [], []]
        cap = caption(self, "Prefill continues: every layer reads its weights once, five columns of work")
        ratio = label("each layer: weights read once, used for 5 columns", 12, DIM, width=2.4).move_to([-5.55, -2.3, 0])
        self.play(comp.set(0.95), bus.set(0.45), FadeIn(ratio), run_time=0.5)
        for r in range(2, L):
            self.play(block.animate.move_to(layers[r][0].get_center()), layers[r][0].animate.set_fill(PROMPT, 0.5), run_time=0.35)
            cells = VGroup(*[cache_cell(rack[r][i]) for i in range(5)])
            filled[r] += list(cells)
            self.play(layers[r][0].animate.set_fill(WEIGHTS, 0.12), FadeIn(cells), run_time=0.25)
        self.play(reads.to(1), run_time=0.5)
        self.next_slide("""Prefill, the rest of the stack: each layer reads its weights once, for five columns of work. Back out. Two layers done, two rows of the cache filled, and the block continues down the rest of the stack at
        the speed it really happens: in each layer the matrices come in from memory once and are used five times, one column
        of arithmetic per token, so the compute gauge is the busy one and the bus is not; the small label under the gauges
        keeps that ratio. Each layer writes five keys and values into its cache row. The counter says what it cost: one read
        of the model for the whole prompt. A longer prompt costs more arithmetic, not more reads.""")
        base = layers[-1].get_bottom() + DOWN * 0.95
        def bars(heights):
            g = VGroup(*[Rectangle(width=0.16, height=max(0.04, h), fill_color=OUTPUT, fill_opacity=0.35 + 0.6 * (h == max(heights)), stroke_width=0) for h in heights])
            g.arrange(RIGHT, buff=0.05, aligned_edge=DOWN).move_to(base, aligned_edge=DOWN).shift(LEFT * 0.6)
            return g
        rnd = random.Random(7)
        def dist():
            hs = [rnd.uniform(0.04, 0.22) for _ in range(9)]; hs[rnd.randrange(9)] = 0.62; return hs
        cap = swap_caption(self, cap, "The last vector becomes a probability over the vocabulary; one token sampled")
        logits = bars(dist())
        lgl = label("probability of each next token; the tallest is sampled", 13, DIM).next_to(logits, DOWN, buff=0.06)
        self.play(block.animate.move_to(logits.get_center() + UP * 0.6).set_opacity(0.0), FadeIn(logits), FadeIn(lgl), run_time=0.6)
        self.remove(block)
        top = max(logits, key=lambda b: b.height)
        newtok = VGroup(Square(0.5, fill_color=OUTPUT, fill_opacity=0.9, stroke_width=0), label(ANSWER[0], 13, "#0f1116")).next_to(top, UP, buff=0.12)
        self.play(FadeIn(newtok, shift=UP * 0.2), produced.to(1), run_time=0.5)
        words = VGroup(label(" " + ANSWER[0], 34, OUTPUT).next_to(sentence, RIGHT, buff=0.12))
        self.play(newtok.animate.move_to([-6.4 + 0.25 + 0.6 * len(toks), 2.25, 0]), FadeIn(words[-1]), run_time=0.8)
        toks.add(newtok)
        self.next_slide("""The last position's output becomes a probability over the vocabulary; one token is sampled. At the bottom, the last position's vector is multiplied by one more matrix, one row per vocabulary entry, which
        gives a score for every token the model knows. Normalise, and it is a probability distribution; draw from it, and
        the answer has its first token, 'mat'. It joins the sentence. Prefill has done two things: filled the cache with the
        prompt, and produced one token.""")
        # --- decode loop
        cread = Counter("cache cells read, this token", 0, "", CACHE, size=22).move_to([1.0, -2.7, 0], aligned_edge=LEFT)
        cap = swap_caption(self, cap, "Decode: the sampled token goes back in alone")
        self.play(FadeIn(cread), run_time=0.4)
        for k_, w in enumerate(ANSWER[1:], start=1):
            fast = k_ > 1
            src = toks[-1]
            col_ = vector(40 + k_, OUTPUT).next_to(src, DOWN, buff=0.08)
            self.play(TransformFromCopy(src, col_), cread.to(0), run_time=0.15 if fast else 0.3)
            self.play(col_.animate.next_to(layers[0], UP, buff=0.06), run_time=0.15 if fast else 0.3)
            first_layer = 0
            if k_ == 1:
                # --- second zoom: the same layer, the same stages, for one column of work; two clicks, then layer two at speed
                ratio2 = label("each layer: weights read once, used for 1 column", 12, DIM, width=2.4).move_to(ratio)
                self.play(FadeOut(ratio), FadeIn(ratio2), comp.set(0.12), bus.set(0.97), run_time=0.5)
                ratio = ratio2
                self.next_slide("""Decode: the sampled token goes back in alone, the same lookup, one vector. Decode. The sampled token goes back in, alone: the same lookup, its row of the table, one vector above layer
                one. Watch the gauges swap: the bus is pegged and the compute grid nearly idle. To see why, go back inside the
                layer with this one column.""")
                wide = VGroup(t, sentence, toks, words, rl, gauges, ratio, reads, produced, cread, more, ll, logits, lgl, *sum(filled[2:], []))   # row two's cells stay out: they travel with rack[1], and a FadeIn would drag them back to where the fade started
                row0 = VGroup(rack[0], *filled[0])
                self.play(frame.animate.scale(ZOOM).move_to([-1.8, y0 - 0.15, 0]), FadeOut(wide), FadeOut(cap), FadeOut(others), FadeOut(layers[1]), FadeOut(rack[1]), *[FadeOut(c) for c in filled[1]], row0.animate.shift(LEFT * 1.8),
                          layers[0][0].animate.stretch_to_fit_height(1.3), col_.animate.scale(0.08 / 0.065).move_to([-4.2, y0, 0]), run_time=1.6)
                cap = caption(self, "Decode inside the layer: the same stages for one column", 22)
                wlab = small("weights: read in full again; the same bytes for one column as for five", WEIGHTS).move_to([-2.6, y0 + 0.8, 0])
                clab = small("cache: every key and value read,\none more column each token", CACHE).next_to(rack[0], UP, buff=0.08).align_to(rack[0][1], LEFT)
                W, wl, q, k, v, att, ff, eq, outv = single_parts(y0)
                ql = VGroup(*[small(s_, col).next_to(c, RIGHT, buff=0.05) for s_, c, col in zip("qkv", (q, k, v), (TEXT, CACHE, CACHE))])
                self.play(FadeIn(wlab), FadeIn(clab), FadeIn(W), FadeIn(wl), FadeIn(q), FadeIn(k), FadeIn(v), run_time=0.5)
                sweep(self, col_, OUTPUT, [(W[0], q, TEXT), (W[1], k, CACHE), (W[2], v, CACHE)], rt=0.2)
                self.play(FadeIn(ql), run_time=0.3)
                cell1 = store_kv(self, VGroup(k), VGroup(v), [rack[0][5]])[0]
                filled[0].append(cell1); row0.add(cell1)   # the new cell rides back with its row at the zoom-out
                self.next_slide("""Decode inside the layer: the same stages, for one column. Weights read in full; cache read in full. Inside, decode is prefill for one token; nothing is skipped. The same three matrices, read in full, give this
                token its query, key and value, one column of arithmetic per row instead of five. Its key and value go into the
                cache as the sixth column of this layer's row. The label over the matrices is the point: exactly the bytes prefill
                read, for a fifth of the work.""")
                al = small("attention", OUTPUT).next_to(att, UP, buff=0.06)
                att = attend_one(self, q, filled[0], att, OUTPUT)
                self.play(FadeIn(al), run_time=0.3)
                fl = small("feed-forward", WEIGHTS).next_to(ff, UP, buff=0.06)
                self.play(FadeIn(ff), FadeIn(fl), FadeIn(eq), FadeIn(outv), run_time=0.4)
                sweep(self, att, OUTPUT, [(ff, outv, OUTPUT)], rt=0.14)
                # layer two at speed, then back out with the vector inside layer two
                y1 = layers[1].get_y()
                nxt = outv.copy()
                layers[1][0].stretch_to_fit_height(1.2).shift(DOWN * 0.12)
                y1 -= 0.12
                row1 = VGroup(rack[1], *filled[1]).shift(LEFT * 1.8)
                layer1 = VGroup(W, wl, q, k, v, ql, att, al, ff, fl, outv, eq, wlab, clab)
                self.play(frame.animate.move_to([-1.8, y0 - 0.55, 0]), FadeOut(layer1), FadeOut(col_), layers[0][0].animate.stretch_to_fit_height(0.5),
                          FadeIn(layers[1]), FadeIn(row1), nxt.animate.move_to([-4.2, y1, 0]), run_time=1.2)
                layer2, out2, cell2 = replay_layer(self, y1, nxt, list(filled[1]), rack[1][5], rt=0.07, color=OUTPUT)
                filled[1].append(cell2); row1.add(cell2)
                nxt2 = out2.copy()
                self.play(nxt2.animate.move_to([-1.0, y1 - 1.1, 0]).set_opacity(0.0), run_time=0.6)
                self.remove(nxt2)
                self.play(FadeOut(layer2), FadeOut(nxt), FadeOut(cap), run_time=0.4)
                col_.scale(0.065 / 0.08).move_to([layers[0].get_x(), y1 + 0.12, 0])
                self.play(frame.animate.scale(1 / ZOOM).move_to(ORIGIN), FadeIn(others), row0.animate.shift(RIGHT * 1.8), row1.animate.shift(RIGHT * 1.8),
                          layers[1][0].animate.stretch_to_fit_height(0.5).shift(UP * 0.12), FadeIn(col_), FadeIn(wide), run_time=1.6)
                cap = caption(self, "Decode: one token per step, the whole model read every step")
                first_layer = 2
            for r in range(first_layer, L):
                self.play(col_.animate.move_to(layers[r][0].get_center()), layers[r][0].animate.set_fill(OUTPUT, 0.55), run_time=0.12 if fast else 0.25)
                lines = VGroup(*[Line(col_.get_right(), c.get_left(), color=TEXT, stroke_width=1.2, stroke_opacity=0.6) for c in filled[r]])
                self.play(Create(lines), LaggedStart(*[c.animate.set_fill(BRIGHT, 1.0) for c in filled[r]], lag_ratio=0.2), cread.to((r + 1) * len(filled[r])), run_time=0.15 if fast else 0.35)
                newcell = cache_cell(rack[r][len(filled[r])])
                filled[r].append(newcell)
                self.play(FadeOut(lines), *[c.animate.set_fill(CACHE, 0.9) for c in filled[r][:-1]], FadeIn(newcell), layers[r][0].animate.set_fill(WEIGHTS, 0.12), run_time=0.08 if fast else 0.15)
            self.play(col_.animate.move_to(logits.get_center() + UP * 0.6).set_opacity(0.0), run_time=0.3)
            self.remove(col_)
            self.play(Transform(logits, bars(dist())), run_time=0.3)
            top = max(logits, key=lambda b: b.height)
            newtok = VGroup(Square(0.5, fill_color=OUTPUT, fill_opacity=0.9, stroke_width=0), label(w, 13, "#0f1116")).next_to(top, UP, buff=0.12)
            words.add(label((" " + w) if w not in ".," else w, 34, OUTPUT).next_to(words[-1], RIGHT, buff=0.12 if w not in ".," else 0.02))
            self.play(FadeIn(newtok, shift=UP * 0.2), reads.to(k_ + 1), produced.to(k_ + 1), run_time=0.3)
            self.play(newtok.animate.move_to([-6.4 + 0.25 + 0.6 * len(toks), 2.25, 0]), FadeIn(words[-1]), run_time=0.25 if fast else 0.4)
            toks.add(newtok)
            if k_ == 1:
                self.next_slide("""Decode: one token per step; each step reads the whole model plus every cached key and value. Then the query does its work over the whole row, six keys now, and the feed-forward sweeps in full for this one
                column. The output drops into layer two, which does the same at speed: project, store, attend, feed-forward.
                Back out, and the column goes on down the stack: in every layer the matrices are read in full again for one
                column of work, the query fans out over the cache row, the white lines, every stored key and value lights up as
                it is read, and its own key and value go in as a new column. The new counter is the size of that read. At the
                bottom a token is sampled and joins the sentence. One token: one full read of the model plus one full read of
                the cache. A GPU multiplies far faster than its memory delivers numbers: hundreds of operations in the time one
                byte arrives. With five columns per read the arithmetic units had work while the next weights came in; with one
                column they finish at once and wait for the bus. Same bytes, a fifth of the work per byte: that is why decode
                is bound by memory bandwidth, and why the bus gauge is the one that is pegged.""")
        cap = swap_caption(self, cap, "Prefill: one read per prompt. Decode: one read per token")
        self.next_slide("""Prefill: one read for the whole prompt. Decode: one read plus the cache, per token. The loop runs on without a click, and watch the cache counter: each token adds a column, so every later token
        reads one more cell per layer; the read grows with the length of the conversation. The weight read is the same every
        step; the cache read is not. On one request it is small next to the weights. With many requests in flight the weights
        are read once for all of them, while each request's cache is read on its own, and at long contexts it is the cache
        read, not the weights, that fills the bus. The answer arrives one token per loop, which is why it streams word by word. The counters are the summary of the
        talk so far. Prefill: one read of the model for the whole prompt, five columns of work per weight, arithmetic-bound.
        Decode: one read of the model plus a read of a growing cache for every token, one column per weight, bandwidth-bound.
        Same multiplication, opposite bottleneck, and the gauges showed which one at each moment. Everything that follows is
        about those two gauges: what they cost, and how to move them.""")
        # --- hand-over: the stage folds into one GPU drawing, and the title becomes the next move's
        from s02_ceiling import start_ceiling, TITLE_CEILING
        nxt = start_ceiling(self, add=False)
        stage_bits = VGroup(sentence, toks, words, rl, gauges, ratio, reads, produced, cread, more, ll, logits, lgl, layers, rack, *sum(filled, []))
        t = retitle(self, t, *TITLE_CEILING, extra=[FadeOut(cap), stage_bits.animate.scale(0.25).move_to(nxt["gpu"].get_center()).set_opacity(0.0),
                                                  FadeIn(VGroup(*nxt["shown"]))], run_time=1.4)
        self.remove(stage_bits)
        self.finish("""The whole stage then folds into one GPU drawing, because the next question is about the machine. The still picture first. Left, one GPU: the RTX PRO 6000 Blackwell Server Edition, the card in a g7e instance, 96 GB of memory, and its bus gauge pegged because we are about to ask what the bus can do at most. Right, the model, named: a dense 32B in fp8, one byte per weight, so every token reads all 32 GB. Two numbers from two spec sheets, the card's bandwidth and the model's bytes per token. The next click divides one by the other.""")
