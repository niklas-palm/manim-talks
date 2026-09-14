"""Move 3 finished: two things attention needs. Opens on the weighted sum's last frame under the token row; the bars,
the query and the new vector give way to the grid of who-attends-to-whom, whose last row is what we just computed;
the mask blanks the grid's upper triangle; then three heads side by side, their outputs concatenated and projected
back to the token's size. The token row stays across the top throughout.
"""
from lib.palette import *
from objects import *

N = 6


class MaskAndHeads(TalkSlide):
    def construct(self):
        # --- move 3's last frame, rebuilt
        t = title_still(self, "Every token reads every other", "3  attention")
        row, vecs = token_row(0.16)
        tri = triples(vecs)
        bars, wlabels, bl = softmax_bars()
        qbig, qbl, out, outl = attention_result()
        self.add(row, tri, bars, wlabels, bl, qbig, qbl, out, outl)
        # --- the attention grid under the row: rows are the querying token, columns the attended token
        cell = 0.45   # 6 cells and the label above fit between the token row and the content bottom
        gridg = VGroup(*[Square(cell, fill_color=ATTN, fill_opacity=0.5, stroke_color=BG, stroke_width=2) for _ in range(N * N)]).arrange_in_grid(rows=N, cols=N, buff=0.02)
        gridg.move_to([0.2, -0.9, 0])   # top at 0.5; the label above clears the token row
        rowl = VGroup(*[label(w, 17, TOKEN).next_to(gridg[i * N], LEFT, buff=GAP) for i, w in enumerate(WORDS)])
        for lab in rowl:
            lab.align_to(rowl[0], RIGHT)
        rk = label("querying token", 17, TOKEN).rotate(PI / 2).next_to(rowl, LEFT, buff=GAP)
        ck = label("attended token, through its key", 17, KEY).next_to(gridg, UP, buff=GAP_TIGHT)
        # the bars become the grid's last row: the weights of "mat" over every token
        lastrow = VGroup(*[gridg[N * (N - 1) + j] for j in range(N)])
        upper = VGroup(*[gridg[i] for i in range(N * (N - 1))])
        t = retitle(self, t, "Don't read the future; use many views", "3  attention",
                    extra=[FadeOut(tri), FadeOut(wlabels), FadeOut(bl), FadeOut(qbig), FadeOut(qbl), FadeOut(out), FadeOut(outl),
                           *[ReplacementTransform(b, c) for b, c in zip(bars, lastrow)], FadeIn(upper),
                           FadeIn(rowl), FadeIn(rk), FadeIn(ck)], run_time=1.0)
        self.remove(upper, *lastrow); self.add(gridg)   # one group for the grid from here on, so it can be faded as one
        self.next_slide("""The bars we just computed fold into the bottom row of a grid: the row is the token doing the looking, the column is
        the token being looked at, and every cell is one attention weight. "mat" attending to all six is the row we built;
        the other five rows are the same computation for the other tokens, all done at once. Filled in full, this is every
        token attending to every token, the parallel read drawn as a grid. For a model that understands a whole sentence at
        once, that is what you want.""")
        # --- the causal mask
        self.play(*[c.animate.set_fill(ATTN, 0.95) for c in lastrow], run_time=0.6)
        self.play(*[c.animate.set_fill(ATTN, 0.5) for c in lastrow], run_time=0.6)
        blocked = VGroup(*[gridg[i * N + j] for i in range(N) for j in range(N) if j > i])
        self.play(*[c.animate.set_fill(MASK, 0.75) for c in blocked], run_time=0.8)
        self.play(*[c.animate.set_fill(BG, 1.0) for c in blocked], run_time=0.6)
        ml = label("causal mask:\nonly itself and\nearlier tokens", 20, MASK).next_to(gridg, RIGHT, buff=GAP_WIDE).align_to(gridg, UP)
        self.play(FadeIn(ml))
        self.next_slide("""But a language model is trained to predict the next word, so it must not see the answer. When it is deciding what
        comes after "sat", it cannot be allowed to look at "on the mat", or predicting would be copying. The causal mask
        blocks the upper triangle: each token attends only to itself and the tokens before it. This one change is the whole
        difference between a model that reads and a model that writes, and it is why this lower-triangle shape shows up
        everywhere in this field.""")
        # --- multi-head: the same read three times, side by side
        heads = head_tiles()
        self.play(FadeOut(VGroup(gridg, rowl, rk, ck, ml)), LaggedStart(*[FadeIn(h, shift=UP * 0.1) for h in heads], lag_ratio=0.12), run_time=1.0)
        self.next_slide("""One point of view is not enough. A single query, key and value can track one kind of relationship, say the
        subject of a verb. So attention runs several times in parallel, each with its own three matrices: the heads. The
        original transformer used eight, drawn here as three. Each head does the whole read we just built and produces its
        own short output vector for the token, capturing a different relationship.""")
        # --- concatenate and project back to the token's size
        joined, jl, proj, pl, result, rl = projection_parts()
        outs = [h[2][2] for h in heads]
        copies = [o.copy() for o in outs]
        self.play(LaggedStart(*[c.animate.scale(0.16 / 0.24).move_to(VGroup(*joined[i * 3:(i + 1) * 3]).get_center()) for i, c in enumerate(copies)], lag_ratio=0.1), FadeIn(jl), run_time=1.0)
        self.add(joined); self.remove(*copies)
        self.play(FadeIn(proj), FadeIn(pl))
        sweep(self, joined, ATTN, [(proj, result, TOKEN)], cols=9, rt=0.1)
        self.play(FadeIn(rl), run_time=0.4)
        self.finish("""The heads' outputs are stitched into one long vector and passed through one more learned matrix that mixes them
        and brings the length back to the token's size, the same sweep as before. That single vector, the shape the token's
        vector had going in, is the output of the whole attention block: the token, updated with what it gathered from the
        sentence through several different lenses at once. That is attention, start to finish. Now the other half of a layer,
        where each token is worked on by itself.""")
