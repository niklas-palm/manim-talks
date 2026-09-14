"""Move 3 finished: two things attention needs. A language model must not read the future, so a mask blocks each
token from attending to later ones; and one set of query/key/value is one point of view, so several run in parallel
and their outputs are joined. One picture: a grid of who-attends-to-whom, then the mask; then the attention block
shrunk to a tile, three tiles side by side, concatenated and projected.
"""
from lib.palette import *
from objects import *

WORDS = ["The", "cat", "sat", "on", "the", "mat"]
N = 6


class MaskAndHeads(TalkSlide):
    def construct(self):
        t = title(self, "Don't read the future; use many views", "3  attention")
        # --- the attention grid: rows query, columns key
        cell = 0.5
        gridg = VGroup(*[Square(cell, fill_color=ATTN, fill_opacity=0.5, stroke_color=BG, stroke_width=2) for _ in range(N * N)]).arrange_in_grid(rows=N, cols=N, buff=0.02)
        gridg.move_to([-1.2, -0.2, 0])
        rowl = VGroup(*[label(w, 14, TOKEN).next_to(gridg[i * N], LEFT, buff=0.2) for i, w in enumerate(WORDS)])
        coll = VGroup(*[label(w, 14, KEY).next_to(gridg[i], UP, buff=0.15).rotate(PI / 6) for i, w in enumerate(WORDS)])
        rk = label("querying token", 14, TOKEN).next_to(gridg, LEFT, buff=1.2).rotate(PI / 2)
        ck = label("attended token (its key)", 14, KEY).next_to(coll, UP, buff=0.2)
        self.play(FadeIn(gridg), FadeIn(rowl), FadeIn(coll), FadeIn(rk), FadeIn(ck))
        self.next_slide("""Every cell here is one attention weight: the row is the token doing the looking, the column is the token being
        looked at. The last scene filled one row, "mat" attending to all six. Filled in full, this is every token attending
        to every token, the parallel read drawn as a grid. For a model that understands a whole sentence at once, that is
        what you want.""")
        # --- the causal mask
        blocked = VGroup()
        for i in range(N):
            for j in range(N):
                if j > i:
                    blocked.add(gridg[i * N + j])
        self.play(*[c.animate.set_fill(MASK, 0.7) for c in blocked], run_time=0.8)
        self.play(*[c.animate.set_fill(BG, 1.0) for c in blocked], run_time=0.6)
        ml = label("a language model predicts the next word: token i may attend only to tokens 1..i", 15, MASK).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(ml))
        self.next_slide("""But a language model is trained to predict the next word, so it must not see the answer. When it is deciding what
        comes after "sat", it cannot be allowed to look at "on the mat", or predicting would be copying. The causal mask
        blocks the upper triangle: each token attends only to itself and the tokens before it. This one change is the whole
        difference between a model that reads and a model that writes, and it is why the lower-triangle shape shows up
        everywhere in this field.""")
        # --- multi-head
        self.play(FadeOut(VGroup(gridg, rowl, coll, rk, ck, ml)), run_time=0.5)
        heads = VGroup()
        cols = [QUERY, KEY, VALUE]
        for hh in range(3):
            tile = VGroup(RoundedRectangle(corner_radius=0.1, width=2.2, height=1.5, stroke_color=ATTN, stroke_width=2, fill_color=ATTN, fill_opacity=0.08),
                          label(f"head {hh + 1}", 15, ATTN))
            tile[1].next_to(tile[0].get_top(), DOWN, buff=0.12)
            inner = VGroup(column(3, QUERY, 0.07), column(3, KEY, 0.07), column(3, VALUE, 0.07)).arrange(RIGHT, buff=0.08).move_to(tile[0]).shift(DOWN * 0.15)
            tile.add(inner)
            heads.add(tile)
        heads.arrange(RIGHT, buff=0.4).move_to([0, 0.8, 0])
        self.play(LaggedStart(*[FadeIn(h, shift=UP * 0.1) for h in heads], lag_ratio=0.12), run_time=1.0)
        outs = VGroup(*[column(3, ATTN, 0.12).next_to(h, DOWN, buff=0.5) for h in heads])
        self.play(LaggedStart(*[FadeIn(o, shift=DOWN * 0.1) for o in outs], lag_ratio=0.1), run_time=0.6)
        self.next_slide("""And one point of view is not enough. A single query, key and value can track one kind of relationship, say the
        subject of a verb. So attention runs several times in parallel, each with its own three matrices: the heads. The
        original transformer used eight, drawn here as three. Each head does the whole read we just built and produces its
        own short output vector for the token, capturing a different relationship.""")
        # --- concatenate and project
        joined = column(9, ATTN, 0.12).move_to([0, -1.9, 0])
        jl = label("concatenate the heads", 15, ATTN).next_to(joined, LEFT, buff=0.3)
        self.play(*[o.animate.move_to(joined.get_center() + DOWN * 0) for o in outs], run_time=0.01)
        self.play(LaggedStart(*[Transform(outs[i], VGroup(*joined[i * 3:(i + 1) * 3])) for i in range(3)], lag_ratio=0.1), FadeIn(jl), run_time=1.0)
        self.add(joined)
        proj = grid(8, 9, WEIGHTS, cell=0.1).next_to(joined, RIGHT, buff=0.6)
        pl = label("projection Wo", 15, WEIGHTS).next_to(proj, UP, buff=0.12)
        result = column(8, TOKEN, 0.12).next_to(proj, RIGHT, buff=0.4)
        self.play(FadeIn(proj), FadeIn(pl))
        self.play(FadeIn(result, shift=RIGHT * 0.2), run_time=0.6)
        self.finish("""The heads' outputs are stitched into one long vector and passed through one more learned matrix that mixes them
        and brings the length back to the token's size. That single vector, the same shape as the token's vector went in, is
        the output of the whole attention block: the token, updated with what it gathered from the sentence through several
        different lenses at once. That is attention, start to finish. Now the other half of a layer, where each token is
        worked on by itself.""")
