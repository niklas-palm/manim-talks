"""Move 2: words become vectors, and the vectors learn their order. Text is cut into tokens; each token's id looks up
a row of a learned table, its embedding vector; but a set of vectors has no order, so a position vector is added to
each. One picture that grows: the sentence, the tokens with ids, the table, a vector under each token, then the
position added.
"""
from lib.palette import *
from objects import *

WORDS = ["The", "cat", "sat", "on", "the", "mat"]
IDS = ["791", "8415", "7731", "389", "279", "2603"]
XS = [-5.4 + 2.0 * i for i in range(6)]   # column x for each token


class Embedding(TalkSlide):
    def construct(self):
        t = title(self, "From words to vectors", "2  words become vectors")
        sentence = label("The cat sat on the mat", 30, TOKEN).move_to([0, 2.4, 0])
        self.play(FadeIn(sentence))
        self.next_slide("""We start from text a person typed. A neural network does not work on letters; it works on numbers. So the first
        two jobs are to cut the text into pieces and turn each piece into a list of numbers.""")
        # --- tokens with ids
        toks = VGroup(*[VGroup(Square(0.6, fill_color=TOKEN, fill_opacity=0.85, stroke_width=0), label(w, 17, "#0f1116")) for w in WORDS])
        for g, x in zip(toks, XS):
            g.move_to([x, 1.5, 0]); g[1].move_to(g[0])
        ids = VGroup(*[label(i, 15, MUTED).next_to(g, DOWN, buff=0.12) for i, g in zip(IDS, toks)])
        self.play(LaggedStart(*[TransformFromCopy(sentence, g) for g in toks], lag_ratio=0.08), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(i, shift=DOWN * 0.1) for i in ids], lag_ratio=0.08), run_time=0.6)
        bpe = label("byte-pair encoding: common words are one token, rare ones split into pieces; a fixed vocabulary of 50,257", 15, MUTED).to_edge(DOWN, buff=0.55)
        self.play(FadeIn(bpe))
        self.next_slide("""Tokenisation. The text is cut into tokens, whole common words here, and each token is a number, its id, an index
        into a fixed vocabulary. This model's vocabulary is 50,257 entries, built by byte-pair encoding: start from single
        bytes and repeatedly merge the most frequent pair, so common words end up as one token and a rare word splits into a
        few. Two things to notice: both "The" and "the" are tokens, with different ids, and the model has not yet been told
        anything about them beyond a number.""")
        # --- the embedding table: id selects a row -> a vector
        self.play(FadeOut(bpe))
        table = VGroup(*[Rectangle(width=1.1, height=0.12, stroke_color=DIM, stroke_width=1, fill_color=VIOLET, fill_opacity=0.25) for _ in range(12)]).arrange(DOWN, buff=0.03)
        table.move_to([-5.9, -0.9, 0])
        tl = label("embedding table\n50,257 rows", 14, WEIGHTS).next_to(table, UP, buff=0.12)
        self.play(FadeIn(table), FadeIn(tl))
        vecs = VGroup()
        rows = [2, 9, 6, 11, 4, 8]
        for k, (g, r) in enumerate(zip(toks, rows)):
            v = vector(20 + k, TOKEN, cell=0.1).next_to(g, DOWN, buff=0.7)
            vecs.add(v)
            sel = table[r].copy().set_fill(TOKEN, 0.9)
            self.play(FadeIn(sel), run_time=0.15)
            self.play(sel.animate.move_to(v.get_center()).scale(0.4), FadeIn(v, scale=0.6), run_time=0.35)
            self.play(FadeOut(sel), run_time=0.1)
        self.play(FadeOut(ids), run_time=0.3)
        vl = label("one vector per token: 512 learned numbers (drawn as 8)", 15, TOKEN).to_edge(DOWN, buff=0.55)
        self.play(FadeIn(vl))
        self.next_slide("""The lookup. The model holds a table with one row per vocabulary entry, and each row is a list of learned numbers,
        a vector; 512 of them in the original transformer, drawn here as eight. A token's id just picks its row. These
        numbers are learned in training so that tokens used in similar ways get similar vectors, which is where meaning
        starts to live. After this step the sentence is a row of vectors, and everything downstream is arithmetic on them.""")
        # --- the bag has no order
        self.play(FadeOut(table), FadeOut(tl), FadeOut(vl), run_time=0.4)
        self.play(Indicate(vecs[0], color=TOKEN, scale_factor=1.2), Indicate(vecs[4], color=TOKEN, scale_factor=1.2), run_time=1.0)
        same = label('both "the" tokens: same id, same vector', 15, MUTED).to_edge(DOWN, buff=0.9)
        order = label("attention treats the vectors as a set: reversing the words would give the same answer. Order is missing.", 15, RED).to_edge(DOWN, buff=0.55)
        self.play(FadeIn(same), FadeIn(order))
        self.next_slide("""One problem, and it is the reason for the next step. The attention we are about to build looks at these vectors as
        an unordered set: "the cat sat" and "sat the cat" would come out the same, because nothing in a vector says where it
        sits. But order carries meaning. So before anything else, each vector is given its position.""")
        # --- positional encoding added
        self.play(FadeOut(same), FadeOut(order), run_time=0.3)
        pos = VGroup(*[vector(60 + k, ATTN, cell=0.1).next_to(v, DOWN, buff=0.5) for k, v in enumerate(vecs)])
        pl = label("a position vector, one per slot", 15, ATTN).next_to(pos, DOWN, buff=0.2)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in pos], lag_ratio=0.06), FadeIn(pl), run_time=0.8)
        self.play(LaggedStart(*[p.animate.move_to(v.get_center()) for p, v in zip(pos, vecs)], lag_ratio=0.08), run_time=1.0)
        self.play(*[v.animate.set_fill(TOKEN, 1.0) for v in vecs], FadeOut(pos), run_time=0.5)
        self.finish("""The fix is simple and a little surprising: add a second vector to each token that depends only on its position,
        made from sines and cosines of different frequencies in the original paper. Same word, different place, different
        vector now. From here the vectors carry both what the token is and where it sits, and we never look at the raw text
        again. Now the heart of the machine: letting these vectors read one another.""")
