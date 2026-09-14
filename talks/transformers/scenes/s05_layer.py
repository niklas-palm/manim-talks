"""Move 4: after gathering from its neighbours, each token is transformed on its own, and the whole layer repeats.
The feed-forward network expands the vector, applies a nonlinearity, contracts it; a residual connection adds that
update to the input rather than replacing it; and the layer (attention then feed-forward) is stacked N times. One
picture: a token vector expands and contracts, the update is added back, then the stack on the right runs it through
every layer.
"""
from lib.palette import *
from objects import *


class Layer(TalkSlide):
    def construct(self):
        t = title(self, "Then the token thinks on its own", "4  the token thinks alone, many times")
        vec = vector(30, TOKEN, cell=0.16).move_to([-5.6, 0.4, 0])
        vl = label('vector for "mat"\nafter attention', 14, TOKEN).next_to(vec, UP, buff=0.2)
        self.play(FadeIn(vec), FadeIn(vl))
        self.next_slide("""Attention let every token gather from the others. The second half of a layer does the opposite: it works on each
        token entirely by itself, the same small network applied to every position independently. Its job is to take what the
        token just gathered and compute something new from it.""")
        # --- expand, nonlinearity, contract
        wide = vector(31, WEIGHTS, cell=0.1, n=24).move_to([-2.6, 0.4, 0])
        el = label("expand: 512 to 2048\n(drawn 8 to 24)", 14, WEIGHTS).next_to(wide, UP, buff=0.2)
        w1 = grid(24, 8, WEIGHTS, cell=0.055).move_to([-4.1, 0.4, 0])
        self.play(FadeIn(w1), run_time=0.4)
        self.play(TransformFromCopy(vec, wide), FadeIn(el), run_time=0.9)
        self.next_slide("""First it expands. A matrix multiplies the vector up to four times its length, 512 to 2048 in the original paper,
        drawn here eight to twenty-four. This gives the network room: many more numbers, each a different learned combination
        of the token's features, room to represent things the compact vector could not.""")
        import random
        rnd = random.Random(3)
        killed = [i for i in range(24) if rnd.random() < 0.45]
        rl = label("nonlinearity (ReLU): negatives set to zero", 14, WEIGHTS).next_to(wide, DOWN, buff=0.35)
        self.play(*[wide[i].animate.set_fill(DIM, 0.15) for i in killed], FadeIn(rl), run_time=0.8)
        self.next_slide("""Then a nonlinearity, ReLU in the paper: every negative number is set to zero. This is small but it is the point of
        the whole block. Without it, stacking layers would collapse into one big matrix and the model could only draw
        straight lines. The nonlinearity is what lets the network build up complicated functions, layer on layer.""")
        out = vector(32, ATTN, cell=0.16).move_to([0.6, 0.4, 0])
        w2 = grid(8, 24, WEIGHTS, cell=0.055).move_to([-1.0, 0.4, 0])
        cl = label("contract back to 512\n(the update)", 14, ATTN).next_to(out, UP, buff=0.2)
        self.play(FadeIn(w2), run_time=0.3)
        self.play(TransformFromCopy(wide, out), FadeIn(cl), FadeOut(rl), run_time=0.9)
        self.next_slide("""A second matrix contracts it back to the original length. So the feed-forward block is expand, throw away the
        negatives, contract. Out comes a vector the same size as the token's, an update the network computed from this token
        alone. The vast majority of a model's weights live in these two matrices, repeated in every layer.""")
        # --- residual connection
        self.play(FadeOut(VGroup(w1, w2, wide, el, cl)), run_time=0.4)
        keep = vec.copy()
        plus = label("+", 40, TEXT).move_to([-1.6, 0.4, 0])
        result = vector(30, TOKEN, cell=0.16).move_to([1.6, 0.4, 0])
        arc = CurvedArrow(vec.get_bottom(), plus.get_bottom() + DOWN * 0.1, color=TOKEN, stroke_width=3, angle=-TAU / 6)
        rl2 = label("residual: the layer adds an update, it does not replace the vector", 15, TOKEN).to_edge(DOWN, buff=0.6)
        self.play(Create(arc), FadeIn(plus), FadeIn(rl2), out.animate.move_to([-0.4, 0.4, 0]), run_time=0.8)
        self.play(FadeIn(result, shift=RIGHT * 0.2), run_time=0.6)
        self.next_slide("""Now the piece that makes deep stacks trainable at all. The update is not the new vector; it is added to the vector
        that came in. The token's own representation flows straight through, and each block only nudges it. This residual
        connection, one around attention and one around the feed-forward, is why gradients survive a hundred layers and why a
        layer can safely learn to do almost nothing when that is best. The paper also normalises after each add; that keeps
        the numbers in range and does not change the shape of the story.""")
        # --- repeat N times
        self.play(FadeOut(VGroup(vec, vl, out, plus, arc, rl2, keep)), result.animate.move_to([-5.6, 2.0, 0]).scale(0.6), run_time=0.7)
        stack = VGroup(*[RoundedRectangle(corner_radius=0.1, width=3.2, height=0.62, stroke_color=WEIGHTS, stroke_width=2, fill_color=WEIGHTS, fill_opacity=0.1) for _ in range(6)])
        stack.arrange(DOWN, buff=0.22).move_to([-1.5, -0.4, 0])
        sll = VGroup(*[label("attention  +  feed-forward", 15, MUTED).move_to(b) for b in stack])
        nl = label("one layer, stacked N times\nN = 6 in the paper, 30 to 100 in today's LLMs", 15, WEIGHTS).next_to(stack, RIGHT, buff=0.6)
        self.play(LaggedStart(*[FadeIn(VGroup(b, s), shift=LEFT * 0.1) for b, s in zip(stack, sll)], lag_ratio=0.1), FadeIn(nl), run_time=1.2)
        tok = result
        for b in stack:
            self.play(tok.animate.next_to(b, LEFT, buff=0.3), run_time=0.18)
            self.play(b[0].animate.set_fill(ATTN, 0.4) if False else b.animate.set_fill(WEIGHTS, 0.3), run_time=0.12)
            self.play(b.animate.set_fill(WEIGHTS, 0.1), run_time=0.1)
        self.play(tok.animate.next_to(stack, DOWN, buff=0.3), run_time=0.3)
        self.finish("""And that is the whole layer: gather from the sentence with attention, then transform each token alone with the
        feed-forward, both wrapped in residual adds. Stack it. Six layers in the original paper, thirty to a hundred in a
        modern language model, every layer with its own weights, each refining the vectors a little more. The vector that
        falls out of the bottom has been shaped by the whole sentence, many times over. One thing left: turning that vector
        into the next word.""")
