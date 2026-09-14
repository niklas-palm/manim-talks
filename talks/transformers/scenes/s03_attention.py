"""Move 3, the heart: self-attention. Opens on move 2's last frame; the six vectors rise to become the token row that
stays across the top for the rest of the deck, and the sentence and squares go. Below the row, large: three learned
matrices turn one token's vector into a query, a key and a value; every token gets its triple; the last token's
query is scored against every key (the fan); softmax turns the scores into weights (bars); and the values, each
scaled by its weight, land in the token's new vector (the weighted sum, drawn).
"""
from lib.palette import *
from objects import *

FOCUS = 5   # the token we follow: "mat", the last


class Attention(TalkSlide):
    def construct(self):
        # --- move 2's last frame, rebuilt
        t = title_still(self, "From words to vectors", "2  words become vectors")
        sentence = sentence_label()
        toks = big_tokens(1.0)
        old = embed_vectors(solid=True)
        pl = position_label()
        self.add(sentence, toks, old, pl)
        # --- the boundary: the vectors rise into the row that carries the rest of the talk; the text has done its job
        row, vecs = token_row(0.16)
        t = retitle(self, t, "Every token reads every other", "3  attention",
                    extra=[FadeOut(sentence), FadeOut(toks), FadeOut(pl), *[ReplacementTransform(o, v) for o, v in zip(old, vecs)],
                           *[FadeIn(g[1]) for g in row]], run_time=0.9)
        self.next_slide("""The six vectors rise to the top and stay there for the rest of the talk; the text has done its job. Each carries
        what its token is and where it sits. A word's meaning depends on its neighbours: "bank" near "river" is not "bank"
        near "money". Attention is how each token pulls in what it needs from the others. It starts by giving every token
        three different views of itself.""")
        # --- three matrices turn one token's vector into q, k, v, drawn large
        WY = -1.45   # the work band is centred here, under the token row and its triples
        src = vector(25, TOKEN, cell=0.32).move_to([-4.8, WY, 0])
        W = VGroup(grid(3, 8, cell=0.3), grid(3, 8, cell=0.3), grid(3, 8, cell=0.3)).arrange(DOWN, buff=GAP).move_to([-1.0, WY, 0])
        wl = VGroup(*[label(s, 22, WEIGHTS).next_to(m, LEFT, buff=GAP) for s, m in zip(("Wq", "Wk", "Wv"), W)])
        q = column(3, QUERY, 0.3, op=0.0).move_to([2.5, W[0].get_y(), 0])
        k = column(3, KEY, 0.3, op=0.0).move_to([2.5, W[1].get_y(), 0])
        v = column(3, VALUE, 0.3, op=0.0).move_to([2.5, W[2].get_y(), 0])
        ql = VGroup(*[label(s, 22, c).move_to([4.5, col.get_y(), 0], aligned_edge=LEFT) for s, col, c in zip(("query", "key", "value"), (q, k, v), (QUERY, KEY, VALUE))])
        self.play(TransformFromCopy(vecs[FOCUS], src), run_time=0.7)
        self.play(FadeIn(W), FadeIn(wl), FadeIn(q), FadeIn(k), FadeIn(v))
        dot_product(self, src, TOKEN, W[0], 0, q[0], QUERY, beat=0.3)   # the first time, slow enough to follow each pair
        self.next_slide("""Take the last token, "mat", and bring its vector down. Three matrices, learned in training, and here is the
        arithmetic once, slowly. One output number is one row of a matrix times the vector: each number in the row multiplies
        the number beside it in the token's vector, and the products are summed into one cell. This is the operation every
        layer is built from, done here for the first cell of the query.""")
        sweep(self, src, TOKEN, [(W[0], q, QUERY), (W[1], k, KEY), (W[2], v, VALUE)], rt=0.18)
        self.play(FadeIn(ql))
        self.next_slide("""Now every row of all three matrices. The token's vector becomes three short vectors, 64 numbers each in the
        paper, drawn as three. Their names describe the roles they will play. The query is what this token is looking for.
        The key is how it advertises itself to others' queries. The value is what it will hand over when its key is a good
        match. Just learned numbers; the names come from how they are used next.""")
        # --- every token gets its own triple, under its vector
        tri = triples(vecs)
        work = VGroup(W, wl, src, q, k, v, ql)
        self.play(work.animate.set_opacity(0.3), run_time=0.5)   # the matrices stay, faded: the band does not go empty
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.1) for g in tri], lag_ratio=0.06), run_time=0.9)
        self.next_slide("""The same three matrices run on every token, all at once, giving each its own query, key and value. That "all at
        once" is the parallel step from move one. Now the read: we follow one token's query, the last, "mat", and let it
        gather from the rest.""")
        # --- the chosen query, large at the right, scored against every key: the fan
        self.play(FadeOut(work), run_time=0.4)
        qbig_t, qbl, out_t, outl = attention_result()
        qbig = tri[FOCUS][0].copy()
        self.play(qbig.animate.scale(0.28 / 0.2).move_to(QBIG_POS), run_time=0.6)
        self.remove(qbig); self.add(qbig_t)   # the exact object move 3's second scene rebuilds
        self.play(FadeIn(qbl), run_time=0.3)
        keys = [tri[j][1] for j in range(6)]
        lines = VGroup(*[Line(qbig_t.get_corner(UL) + DOWN * 0.05, kc.get_bottom(), color=MUTED, stroke_width=1.8, stroke_opacity=0.65) for kc in keys])   # to the query's top corner, so the fan stays above the scores
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.08), run_time=1.0)
        slabels = VGroup(*[label(f"{s:.1f}", 20, TEXT).move_to([XS[j], ROWS[2] - 0.55, 0]) for j, s in enumerate(SCORES)])   # below the lowest line of the fan
        self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.05) for s in slabels], lag_ratio=0.06), run_time=0.8)
        sl = label('score: query of "mat" times each key', 18, MUTED).move_to([0, ROWS[3] - 0.2, 0])
        self.play(FadeIn(sl))
        self.next_slide("""The query of "mat" is compared with the key of every token, by the same multiply-and-sum, one score per token.
        A big score means that token's key matches what "mat" is looking for. In the original paper the score is divided by
        the square root of the key length before the next step, so the numbers do not blow up as vectors get longer. Six
        scores, one per token, and they can be any size.""")
        # --- softmax: the scores become weights, drawn as bars under the tokens
        self.play(FadeOut(sl), FadeOut(lines), run_time=0.3)
        weights = softmax(SCORES)
        bars, wlabels, bl = softmax_bars()
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.06), FadeOut(slabels), FadeIn(bl), run_time=1.0)
        self.play(FadeIn(wlabels), run_time=0.4)
        self.next_slide("""Raw scores are not yet a mixture. Softmax turns them into weights between zero and one that add up to one: the
        exponential of each score over the sum of them all. The biggest score gets most of the weight, the rest little.
        These are the attention weights: "mat" pays this much attention to each token, and this row of bars is exactly what
        people mean by an attention pattern.""")
        # --- the weighted sum: each value, scaled by its weight, lands in the new vector
        out = column(3, ATTN, 0.28, op=0.0).move_to(OUT_POS)
        self.play(FadeIn(outl), run_time=0.3)
        cum = 0.0
        for j in range(6):
            vc = tri[j][2].copy()
            cum += weights[j]
            self.play(bars[j].animate.set_fill(ATTN, 1.0), run_time=0.15)
            self.play(vc.animate.scale((0.28 / 0.2) * (0.35 + 1.4 * weights[j])).move_to(out.get_center()).set_opacity(0.35 + 0.65 * weights[j]), run_time=0.4)
            self.play(FadeOut(vc), *[c.animate.set_fill(ATTN, min(0.95, cum)) for c in out], bars[j].animate.set_fill(ATTN, 0.45 + 0.5 * (weights[j] == max(weights))), run_time=0.25)
        self.play(Flash(out, color=ATTN, flash_radius=0.6, num_lines=10), run_time=0.5)
        self.remove(out); self.add(out_t)   # the exact object the next scene rebuilds
        self.finish("""Last step of the read, and watch the new vector fill. Take every token's value, scale it by that token's weight,
        and add them up: a big weight brings most of that token's value, a small weight almost none. Six landings, and the
        sum is a new vector for "mat", built from the whole sentence, weighted by relevance. Every token does this for its own
        query at the same time, so one attention step rewrites all six vectors in parallel. Two things still to add: a
        language model must not peek ahead, and one view of the sentence is not enough.""")
