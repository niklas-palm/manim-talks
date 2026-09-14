"""Move 3, the heart: self-attention. Each token's vector is turned into a query, a key and a value by three learned
matrices; a token's query is scored against every key, the scores become weights that sum to one, and the weighted
sum of the values is the token's new vector. Then the causal mask (a token sees only itself and earlier ones), then
several heads in parallel. One picture: six token vectors along the top, the three matrices below, the q/k/v triples
under each token, and the read-and-mix for one chosen token drawn large in the lower half.
"""
from lib.palette import *
from objects import *

WORDS = ["The", "cat", "sat", "on", "the", "mat"]
XS = [-5.4 + 2.0 * i for i in range(6)]
FOCUS = 5   # the token we follow: "mat", the last


class Attention(TalkSlide):
    def construct(self):
        t = title(self, "Every token reads every other", "3  attention")
        # --- the six token vectors along the top
        toks, vecs = VGroup(), []
        for k, (w, x) in enumerate(zip(WORDS, XS)):
            v = vector(20 + k, TOKEN, cell=0.09).move_to([x, 2.5, 0])
            lab = label(w, 16, TOKEN).next_to(v, UP, buff=0.1)
            toks.add(VGroup(v, lab)); vecs.append(v)
        self.play(LaggedStart(*[FadeIn(g, shift=DOWN * 0.1) for g in toks], lag_ratio=0.06), run_time=0.9)
        self.next_slide("""Here are the six token vectors from the last move, each carrying what its token is and where it sits. A word's
        meaning depends on its neighbours: "bank" near "river" is not "bank" near "money". Attention is how each token pulls
        in what it needs from the others. It starts by giving every token three different views of itself.""")
        # --- three matrices turn the first token's vector into q, k, v
        W = VGroup(grid(3, 8), grid(3, 8), grid(3, 8)).arrange(DOWN, buff=0.35).move_to([-3.3, -0.6, 0])
        wl = VGroup(*[label(s, 16, WEIGHTS).next_to(m, LEFT, buff=0.15) for s, m in zip(("Wq", "Wk", "Wv"), W)])
        src = vecs[FOCUS].copy().scale(1.6).move_to([-5.0, -0.6, 0])
        q = column(3, QUERY, 0.14, op=0.0).next_to(W[0], RIGHT, buff=0.3)
        k = column(3, KEY, 0.14, op=0.0).next_to(W[1], RIGHT, buff=0.3)
        v = column(3, VALUE, 0.14, op=0.0).next_to(W[2], RIGHT, buff=0.3)
        ql = VGroup(*[label(s, 16, c).next_to(col, RIGHT, buff=0.12) for s, col, c in zip(("query", "key", "value"), (q, k, v), (QUERY, KEY, VALUE))])
        self.play(FadeIn(W), FadeIn(wl), FadeIn(src), FadeIn(q), FadeIn(k), FadeIn(v))
        dot_product(self, src, TOKEN, W[0], 0, q[0], QUERY)
        self.next_slide("""Three matrices, learned in training, and here is the arithmetic once, slowly. One output number is one row of a
        matrix times the vector: each number in the row multiplies the number beside it in the token's vector, and the
        products are summed into one cell. This is the operation every layer is built from, done here for the first cell of
        the query.""")
        sweep(self, src, TOKEN, [(W[0], q, QUERY), (W[1], k, KEY), (W[2], v, VALUE)], rt=0.16)
        self.play(FadeIn(ql))
        self.next_slide("""Now every row of all three matrices. The token's vector becomes three short vectors. Their names describe the
        roles they will play. The query is what this token is looking for. The key is how it advertises itself to others'
        queries. The value is what it will hand over when its key is a good match. Just learned numbers; the names come from
        how they are used next.""")
        # --- every token gets its q,k,v triple
        triexamples = VGroup()
        for kk in range(6):
            tri = VGroup(column(3, QUERY, 0.06), column(3, KEY, 0.06), column(3, VALUE, 0.06)).arrange(RIGHT, buff=0.04).next_to(vecs[kk], DOWN, buff=0.2)
            triexamples.add(tri)
        self.play(FadeOut(VGroup(W, wl, src, q, k, v, ql)),
                  LaggedStart(*[FadeIn(tri, shift=UP * 0.1) for tri in triexamples], lag_ratio=0.06), run_time=1.0)
        self.next_slide("""The same three matrices run on every token, all at once, giving each its own query, key and value. That "all at
        once" is the parallel step from move one. Now the read: we follow one token's query, the last, "mat", and let it
        gather from the rest.""")
        # --- the chosen query scored against every key (the fan), one dot product slow
        qf = triexamples[FOCUS][0]
        self.play(qf.animate.set_fill(QUERY, 1.0), Indicate(triexamples[FOCUS][0], color=QUERY), run_time=0.6)
        keys = [triexamples[j][1] for j in range(6)]
        lines = VGroup(*[Line(qf.get_bottom(), kc.get_top(), color=MUTED, stroke_width=1.6, stroke_opacity=0.6) for kc in keys])
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.08), run_time=1.0)
        scores = [1.2, 0.4, 2.1, 0.2, 0.9, 2.6]   # illustrative match strengths
        slabels = VGroup(*[label(f"{s:.1f}", 14, MUTED).next_to(keys[j], DOWN, buff=0.12) for j, s in enumerate(scores)])
        self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.05) for s in slabels], lag_ratio=0.06), run_time=0.8)
        sl = label('each score is query "mat" against one key: how much this token matters to "mat"', 15, MUTED).to_edge(DOWN, buff=0.55)
        self.play(FadeIn(sl))
        self.next_slide("""The query of "mat" is compared with the key of every token, by the same multiply-and-sum, one score per token.
        A big score means that token's key matches what "mat" is looking for. In the original paper the score is divided by
        the square root of the key length before the next step, so the numbers do not blow up as vectors get longer. Six
        scores, one per token, and they can be any size.""")
        # --- softmax to weights
        self.play(FadeOut(sl), FadeOut(lines), run_time=0.3)
        bars, weights = softmax_bars(scores, x=0.0, y=-2.2, colour=ATTN)
        for j, (b, kc) in enumerate(zip(bars, keys)):
            b.next_to(keys[j], DOWN, buff=0.35).align_to(bars, DOWN)
        bl = label("softmax: scores become weights that sum to 1", 15, ATTN).next_to(bars, DOWN, buff=0.2)
        bl.to_edge(DOWN, buff=0.55)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.06), FadeOut(slabels), FadeIn(bl), run_time=1.0)
        self.next_slide("""Raw scores are not yet a mixture. Softmax turns them into weights between zero and one that add up to one: the
        exponential of each score over the sum of them all. The biggest score gets most of the weight, the rest little.
        These are the attention weights, "mat" pays this much attention to each token, and this bar chart is exactly the
        number people mean by an attention pattern.""")
        # --- weighted sum of values into the new vector
        out = column(8, ATTN, 0.12, op=0.0).move_to([4.6, -0.9, 0])
        outl = label('new vector for "mat"', 15, ATTN).next_to(out, UP, buff=0.15)
        self.play(FadeIn(outl))
        for j in range(6):
            vc = triexamples[j][2].copy()
            self.play(vc.animate.scale(0.4 + weights[j] * 2.2).move_to(out.get_center()).set_opacity(0.3 + 0.6 * weights[j]), run_time=0.3)
            self.play(FadeOut(vc), run_time=0.08)
        self.play(*[c.animate.set_fill(ATTN, 0.9) for c in out], run_time=0.5)
        self.finish("""Last step of the read. Take every token's value, scale it by that token's weight, and add them up. Tokens "mat"
        attends to strongly contribute most of their value; ignored tokens contribute almost nothing. The sum is a new vector
        for "mat", built from the whole sentence, weighted by relevance. Every token does this for its own query at the same
        time, so one attention step rewrites all six vectors in parallel. Two things still to add: a language model must not
        peek ahead, and one view of the sentence is not enough.""")
