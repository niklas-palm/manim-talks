"""Move 4: after gathering from its neighbours, each token is transformed on its own, and the whole layer repeats.
Opens on the attention output for "mat" from the previous frame; that vector is what the feed-forward works on. It
expands the vector, zeroes the negatives, contracts it; the residual connection adds that update to the input, cell
by cell, rather than replacing it; and the layer is stacked, drawn as the same layer picture repeated smaller with the
token travelling down. The token row stays across the top.
"""
from lib.palette import *
from objects import *
import random

Y = PIPE_Y


class Layer(TalkSlide):
    def construct(self):
        # --- the previous frame, rebuilt
        t = title_still(self, "Don't read the future; use many views", "3  attention")
        row, vecs = token_row(0.16)
        heads = head_tiles()
        joined, jl, proj, pl, result, rl = projection_parts(filled=True)
        self.add(row, heads, joined, jl, proj, pl, result, rl)
        # --- the boundary: the heads and the projection go; the attention output for "mat" becomes the vector we work on
        vec = vector(30, TOKEN, cell=0.24).move_to([COLS[2], Y, 0])
        vl = label('"mat" after attention', 18, TOKEN).next_to(vec, UP, buff=GAP)
        t = retitle(self, t, "Then the token thinks on its own", "4  the token thinks alone, many times",
                    extra=[FadeOut(heads), FadeOut(joined), FadeOut(jl), FadeOut(proj), FadeOut(pl), FadeOut(rl), ReplacementTransform(result, vec), FadeIn(vl)], run_time=0.9)
        self.next_slide("""Attention let every token gather from the others; its output for "mat" comes to the centre. The second half of a
        layer does the opposite: it works on each token entirely by itself, the same small network applied to every position
        independently. Its job is to take what the token just gathered and compute something new from it.""")
        # --- expand
        w1 = grid(16, 8, WEIGHTS, cell=0.14).move_to([COLS[1], Y, 0])
        wide = vector(31, WEIGHTS, cell=0.14, n=16).move_to([-1.5, Y, 0])
        el = label("expand 512 to 2048\n(drawn 8 to 16)", 17, WEIGHTS).next_to(wide, UP, buff=GAP)
        self.play(VGroup(vec, vl).animate.move_to([-5.2, Y, 0]).align_to(vec, DOWN), run_time=0.6)
        vl.next_to(vec, UP, buff=GAP)
        self.play(FadeIn(w1), run_time=0.4)
        self.play(TransformFromCopy(vec, wide), FadeIn(el), run_time=0.9)
        self.next_slide("""First it expands. A matrix multiplies the vector up to four times its length, 512 to 2048 in the original paper,
        drawn here eight to sixteen. This gives the network room: many more numbers, each a different learned combination of
        the token's features, room to represent things the compact vector could not.""")
        # --- nonlinearity
        rnd = random.Random(3)
        killed = [i for i in range(16) if rnd.random() < 0.45]
        rl2 = label("ReLU: every negative\nnumber becomes zero", 17, WEIGHTS).next_to(wide, DOWN, buff=GAP)
        self.play(*[wide[i].animate.set_fill(DIM, 0.15) for i in killed], FadeIn(rl2), run_time=0.8)
        self.next_slide("""Then a nonlinearity, ReLU in the paper: every negative number is set to zero, the cells that went dark. This is
        small but it is the point of the whole block. Without it, stacking layers would collapse into one big matrix and the
        model could only draw straight lines. The nonlinearity is what lets the network build up complicated functions,
        layer on layer.""")
        # --- contract
        w2 = grid(8, 16, WEIGHTS, cell=0.14).move_to([1.3, Y, 0])
        out = vector(32, ATTN, cell=0.24).move_to([4.4, Y, 0])
        cl = label("contract back to 512:\nthe update", 17, ATTN).next_to(out, UP, buff=GAP)
        self.play(FadeIn(w2), run_time=0.3)
        self.play(TransformFromCopy(wide, out), FadeIn(cl), FadeOut(rl2), run_time=0.9)
        self.next_slide("""A second matrix contracts it back to the original length. So the feed-forward block is expand, throw away the
        negatives, contract. Out comes a vector the same size as the token's, an update the network computed from this token
        alone. The vast majority of a model's weights live in these two matrices, repeated in every layer.""")
        # --- residual: the update is added to the input, cell by cell
        self.play(FadeOut(VGroup(w1, w2, wide, el, cl, vl)), run_time=0.4)
        big_in = vector(30, TOKEN, cell=0.3).move_to([COLS[1], Y, 0])
        plus = label("+", 48, TEXT).move_to([-1.6, Y, 0])
        upd = vector(32, ATTN, cell=0.3).move_to([COLS[2], Y, 0])
        eq = label("=", 48, TEXT).move_to([1.6, Y, 0])
        res = vector(30, TOKEN, cell=0.3).move_to([COLS[3], Y, 0])
        li = label("the token\nas it came in", 18, TOKEN).next_to(big_in, UP, buff=GAP)
        lu = label("the update", 18, ATTN).next_to(upd, UP, buff=GAP)
        lr = label("the token\ngoing out", 18, TOKEN).next_to(res, UP, buff=GAP)
        self.play(ReplacementTransform(vec, big_in), ReplacementTransform(out, upd), FadeIn(plus), FadeIn(li), FadeIn(lu), run_time=0.8)
        self.play(FadeIn(eq), TransformFromCopy(big_in, res), FadeIn(lr), run_time=0.6)
        rl3 = label("residual: the input plus its update", 18, TOKEN).next_to(upd, DOWN, buff=GAP_WIDE)
        self.play(FadeIn(rl3), run_time=0.3)
        rnd = random.Random(8)
        for i in range(D):
            piece = upd[i].copy()
            new_op = min(1.0, max(0.25, res[i].get_fill_opacity() + rnd.uniform(-0.3, 0.3)))
            self.play(piece.animate.move_to(res[i]), run_time=0.35 if i < 3 else 0.15)   # first landings slow, the rest at speed
            self.play(FadeOut(piece), res[i].animate.set_fill(TOKEN, new_op), Flash(res[i], color=ATTN, flash_radius=0.28, num_lines=6), run_time=0.22)
        self.next_slide("""Now the piece that makes deep stacks trainable at all. The update is not the new vector; it is added to the vector
        that came in, number by number, and each cell of the token shifts a little. The token's own representation flows
        straight through, and each block only nudges it. This residual connection, one around attention and one around the
        feed-forward, is why gradients survive a hundred layers and why a layer can safely learn to do almost nothing when
        that is best. The paper also normalises after each add; that keeps the numbers in range and does not change the shape
        of the story.""")
        # --- the layer, repeated: the same picture smaller, stacked, the token travelling down
        stack, nl = layer_stack()
        tiny = tiny_token(stack)
        start = vector(30, TOKEN, cell=0.12).next_to(stack[0], LEFT, buff=GAP)
        self.play(FadeOut(VGroup(big_in, plus, upd, eq, li, lu, lr, rl3)), ReplacementTransform(res, start), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(b, shift=LEFT * 0.1) for b in stack], lag_ratio=0.1), FadeIn(nl), run_time=1.2)
        for b in stack:
            self.play(start.animate.next_to(b, LEFT, buff=GAP), run_time=0.2)
            self.play(b[0].animate.set_fill(WEIGHTS, 0.3), run_time=0.12)
            self.play(b[0].animate.set_fill(WEIGHTS, 0.08), run_time=0.1)
        self.play(ReplacementTransform(start, tiny), run_time=0.3)
        self.finish("""And that is the whole layer: gather from the sentence with attention, then transform each token alone with the
        feed-forward, both wrapped in residual adds. Here it is again, smaller, five times: a vector goes in, becomes a
        query, a key and a value, reads the row, passes the feed-forward grid, comes out the same shape. Six layers in the
        original paper, thirty to a hundred in a modern language model, every layer with its own weights, each refining the
        vectors a little more. The vector that falls out of the bottom has been shaped by the whole sentence, many times over.
        One thing left: turning that vector into the next word.""")
