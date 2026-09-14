"""Move 3 finished: two things attention needs. A language model must not read the future, so a mask blocks each
token from attending to later ones; and one set of query/key/value is one point of view, so several run in parallel
and their outputs are joined. One picture: the grid of who-attends-to-whom, large; the mask blanking its upper
triangle; then three heads side by side, their outputs concatenated and projected back to the token's size.
"""
from lib.palette import *
from objects import *

N = 6


class MaskAndHeads(TalkSlide):
    def construct(self):
        t = title(self, "Don't read the future; use many views", "3  attention")
        # --- the attention grid: rows are the querying token, columns the attended token
        cell = 0.62
        gridg = VGroup(*[Square(cell, fill_color=ATTN, fill_opacity=0.5, stroke_color=BG, stroke_width=2) for _ in range(N * N)]).arrange_in_grid(rows=N, cols=N, buff=0.02)
        gridg.move_to([-1.6, -0.3, 0])
        rowl = VGroup(*[label(w, 17, TOKEN).next_to(gridg[i * N], LEFT, buff=0.25) for i, w in enumerate(WORDS)])
        coll = VGroup(*[label(w, 17, KEY).next_to(gridg[i], UP, buff=0.18) for i, w in enumerate(WORDS)])
        rk = label("querying token", 17, TOKEN).rotate(PI / 2).next_to(rowl, LEFT, buff=0.3)
        ck = label("attended token, through its key", 17, KEY).next_to(coll, UP, buff=0.2)
        self.play(FadeIn(gridg), FadeIn(rowl), FadeIn(coll), FadeIn(rk), FadeIn(ck))
        self.play(*[gridg[N * (N - 1) + j].animate.set_fill(ATTN, 0.95) for j in range(N)], run_time=0.5)
        self.play(*[gridg[N * (N - 1) + j].animate.set_fill(ATTN, 0.5) for j in range(N)], run_time=0.5)
        self.next_slide("""Every cell here is one attention weight: the row is the token doing the looking, the column is the token being
        looked at. The last scene filled one row, "mat" attending to all six; it flashes here. Filled in full, this is every
        token attending to every token, the parallel read drawn as a grid. For a model that understands a whole sentence at
        once, that is what you want.""")
        # --- the causal mask
        blocked = VGroup(*[gridg[i * N + j] for i in range(N) for j in range(N) if j > i])
        self.play(*[c.animate.set_fill(MASK, 0.75) for c in blocked], run_time=0.8)
        self.play(*[c.animate.set_fill(BG, 1.0) for c in blocked], run_time=0.6)
        ml = label("causal mask: only itself and earlier tokens", 17, MASK).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(ml))
        self.next_slide("""But a language model is trained to predict the next word, so it must not see the answer. When it is deciding what
        comes after "sat", it cannot be allowed to look at "on the mat", or predicting would be copying. The causal mask
        blocks the upper triangle: each token attends only to itself and the tokens before it. This one change is the whole
        difference between a model that reads and a model that writes, and it is why this lower-triangle shape shows up
        everywhere in this field.""")
        # --- multi-head: the same read three times, side by side
        self.play(FadeOut(VGroup(gridg, rowl, coll, rk, ck, ml)), run_time=0.5)
        heads = VGroup()
        for hh in range(3):
            tile = VGroup(RoundedRectangle(corner_radius=0.12, width=3.6, height=2.1, stroke_color=ATTN, stroke_width=2, fill_color=ATTN, fill_opacity=0.07),
                          label(f"head {hh + 1}: its own Wq, Wk, Wv", 16, ATTN))
            tile[1].next_to(tile[0].get_top(), DOWN, buff=0.14)
            trio = VGroup(column(3, QUERY, 0.18), column(3, KEY, 0.18), column(3, VALUE, 0.18)).arrange(RIGHT, buff=0.1)
            ar = Arrow(ORIGIN, RIGHT * 0.9, buff=0, color=MUTED, stroke_width=2.5, tip_length=0.18)
            outc = column(3, ATTN, 0.2)
            inner = VGroup(trio, ar, outc).arrange(RIGHT, buff=0.3).move_to(tile[0]).shift(DOWN * 0.2)
            tile.add(inner)
            heads.add(tile)
        heads.arrange(RIGHT, buff=0.5).move_to([0, 1.0, 0])
        self.play(LaggedStart(*[FadeIn(h, shift=UP * 0.1) for h in heads], lag_ratio=0.12), run_time=1.0)
        self.next_slide("""And one point of view is not enough. A single query, key and value can track one kind of relationship, say the
        subject of a verb. So attention runs several times in parallel, each with its own three matrices: the heads. The
        original transformer used eight, drawn here as three. Each head does the whole read we just built and produces its
        own short output vector for the token, capturing a different relationship.""")
        # --- concatenate and project back to the token's size
        joined = column(9, ATTN, 0.2).move_to([-2.6, -1.5, 0])
        jl = label("concatenate\nthe three outputs", 16, ATTN).next_to(joined, LEFT, buff=0.35)
        outs = [h[2][2] for h in heads]
        copies = [o.copy() for o in outs]
        self.play(LaggedStart(*[c.animate.move_to(VGroup(*joined[i * 3:(i + 1) * 3]).get_center()) for i, c in enumerate(copies)], lag_ratio=0.1), FadeIn(jl), run_time=1.0)
        self.add(joined); self.remove(*copies)
        proj = grid(8, 9, WEIGHTS, cell=0.2).next_to(joined, RIGHT, buff=0.7)
        pl = label("one more matrix, Wo", 16, WEIGHTS).next_to(proj, UP, buff=0.14)
        result = column(8, TOKEN, 0.2).next_to(proj, RIGHT, buff=0.6)
        rl = label('attention output for "mat":\nthe token\'s size again', 16, TOKEN).next_to(result, RIGHT, buff=0.3)
        self.play(FadeIn(proj), FadeIn(pl))
        sweep(self, joined, ATTN, [(proj, result, TOKEN)], cols=9, rt=0.1)
        self.play(FadeIn(rl), run_time=0.4)
        self.finish("""The heads' outputs are stitched into one long vector and passed through one more learned matrix that mixes them
        and brings the length back to the token's size, the same sweep as before. That single vector, the shape the token's
        vector had going in, is the output of the whole attention block: the token, updated with what it gathered from the
        sentence through several different lenses at once. That is attention, start to finish. Now the other half of a layer,
        where each token is worked on by itself.""")
