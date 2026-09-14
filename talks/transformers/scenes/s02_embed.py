"""Move 2: words become vectors, and the vectors learn their order. Opens on move 1's last frame (the six large tokens,
their connections, the two counters); the connections and counters go, the tokens shrink, the sentence appears above
them, and the picture grows: ids, the table at the left, a vector under each token, the position vectors rising in.
"""
from lib.palette import *
from objects import *

IDS = ["791", "8415", "7731", "389", "279", "2603"]


class Embedding(TalkSlide):
    def construct(self):
        # --- move 1's last frame, rebuilt: nothing moves yet
        t = title_still(self, "The idea: read every token at once", "1  the parallel idea")
        big = big_tokens(1.3)
        edges = all_edges(big)
        steps2, conns = sequential_counters(1, 30)
        for c in (steps2, conns):   # static here: a Counter's updater would redraw its digits through the FadeOut
            c.num.clear_updaters(); c.unit.clear_updaters()
        self.add(big, edges, steps2, conns)
        # --- the boundary: the title changes as the connections go and the tokens settle into their working size
        toks = big_tokens(1.0)
        sentence = sentence_label()
        t = retitle(self, t, "From words to vectors", "2  words become vectors",
                    extra=[FadeOut(edges), FadeOut(steps2), FadeOut(conns), *[Transform(b, s) for b, s in zip(big, toks)], FadeIn(sentence)])
        self.remove(*big); self.add(toks)
        self.next_slide("""The connections come off and the six tokens settle: the same sentence, now with the text it came from above it. A
        neural network does not work on letters; it works on numbers. So the first two jobs are to cut the text into pieces
        and turn each piece into a list of numbers.""")
        # --- ids
        ids = VGroup(*[label(i, 18, MUTED).next_to(g, DOWN, buff=GAP_TIGHT) for i, g in zip(IDS, toks)])
        self.play(LaggedStart(*[FadeIn(i, shift=DOWN * 0.1) for i in ids], lag_ratio=0.08), run_time=0.6)
        bpe = label("byte-pair encoding, vocabulary of 50,257", 18, MUTED).move_to([0, ROWS[2] - 0.4, 0])
        self.play(FadeIn(bpe))
        self.next_slide("""Tokenisation. The text is cut into tokens, whole common words here, and each token is a number, its id, an index
        into a fixed vocabulary. This model's vocabulary is 50,257 entries, built by byte-pair encoding: start from single
        bytes and repeatedly merge the most frequent pair, so common words end up as one token and a rare word splits into a
        few. Two things to notice: both "The" and "the" are tokens, with different ids, and the model has not yet been told
        anything about them beyond a number.""")
        # --- the embedding table: id selects a row -> a vector
        self.play(FadeOut(bpe))
        table = VGroup(*[Rectangle(width=0.8, height=0.2, stroke_color=DIM, stroke_width=sw(0.4), fill_color=WEIGHTS, fill_opacity=SOLID * 0.28) for _ in range(12)]).arrange(DOWN, buff=0.04)
        table.move_to([-6.3, -1.3, 0], aligned_edge=LEFT)
        tl = label("table\n50,257 rows", 15, WEIGHTS).next_to(table, UP, buff=GAP_TIGHT)
        self.play(FadeIn(table), FadeIn(tl))
        vecs = embed_vectors()
        rows = [2, 9, 6, 11, 4, 8]
        for k, (v, r) in enumerate(zip(vecs, rows)):
            sel = table[r].copy().set_fill(TOKEN, 0.9)
            self.play(FadeIn(sel), run_time=0.15)
            self.play(sel.animate.move_to(v.get_center()).scale(0.4), FadeIn(v, scale=0.6), run_time=0.35)
            self.play(FadeOut(sel), run_time=0.1)
        self.play(FadeOut(ids), run_time=0.3)
        vl = label("one vector per token: 512 numbers, drawn 8", 18, TOKEN).move_to([0, ROWS[4] - 0.25, 0])
        self.play(FadeIn(vl))
        self.next_slide("""The lookup. The model holds a table with one row per vocabulary entry, and each row is a list of learned numbers,
        a vector; 512 of them in the original transformer, drawn here as eight. A token's id just picks its row. These
        numbers are learned in training so that tokens used in similar ways get similar vectors, which is where meaning
        starts to live. After this step the sentence is a row of vectors, and everything downstream is arithmetic on them.""")
        # --- the bag has no order
        self.play(FadeOut(table), FadeOut(tl), FadeOut(vl), run_time=0.4)
        self.play(Indicate(vecs[0], color=TOKEN, scale_factor=1.15), Indicate(vecs[4], color=TOKEN, scale_factor=1.15), run_time=1.0)
        same = label('both "the" tokens: same id, same vector', 18, MUTED).move_to([0, ROWS[4] - 0.25, 0])
        order = label("no order: attention sees a set", 18, MASK).next_to(same, DOWN, buff=GAP_TIGHT)
        self.play(FadeIn(same), FadeIn(order))
        self.next_slide("""One problem, and it is the reason for the next step. The attention we are about to build looks at these vectors as
        an unordered set: "the cat sat" and "sat the cat" would come out the same, because nothing in a vector says where it
        sits. But order carries meaning. So before anything else, each vector is given its position.""")
        # --- positional encoding added
        self.play(FadeOut(same), FadeOut(order), run_time=0.3)
        pos = VGroup(*[vector(60 + k, ATTN, cell=0.22).move_to([XS[k] + 0.45, VEC_Y, 0]) for k in range(6)])
        pl = position_label()
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in pos], lag_ratio=0.06), FadeIn(pl), run_time=0.8)
        self.play(LaggedStart(*[p.animate.move_to(v.get_center()) for p, v in zip(pos, vecs)], lag_ratio=0.08), run_time=1.0)
        self.play(*[v.animate.set_fill(TOKEN, 1.0) for v in vecs], FadeOut(pos), run_time=0.5)
        self.finish("""The fix is simple and a little surprising: add a second vector to each token that depends only on its position,
        made from sines and cosines of different frequencies in the original paper. Same word, different place, different
        vector now. From here the vectors carry both what the token is and where it sits, and we never look at the raw text
        again. Now the heart of the machine: letting these vectors read one another.""")
