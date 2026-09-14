"""Move 5: from the last vector to the next word, and the loop. Opens on the stack of layers with the small vector
under it; the stack goes and the vector grows into the one we read the next word from. The row across the top is the
sentence itself: its last token, "mat", is what we are about to predict, so it leaves the row first and comes back as
the sampled word. The vocabulary matrix, the scores, the distribution as tall bars, the sampled word rejoining the
row, the loop.
"""
from lib.palette import *
from objects import *
import random

Y = PIPE_Y


class Predict(TalkSlide):
    def construct(self):
        # --- move 4's last frame, rebuilt
        t = title_still(self, "Then the token thinks on its own", "4  the token thinks alone, many times")
        row, vecs = token_row(0.16)
        stack, nl = layer_stack()
        tiny = tiny_token(stack)
        self.add(row, stack, nl, tiny)
        # --- the boundary: the stack goes, the small vector grows into the one we read from; "mat" leaves the row (we predict it)
        vec = vector(30, TOKEN, cell=0.24).move_to([COLS[2], Y, 0])
        vll = label('final vector\nof the last token', 17, TOKEN).next_to(vec, UP, buff=GAP)
        t = retitle(self, t, "From the last vector to the next word", "5  one token at a time",
                    extra=[FadeOut(stack), FadeOut(nl), ReplacementTransform(tiny, vec), FadeIn(vll), FadeOut(row[5])], run_time=0.9)
        self.next_slide("""The stack is done and one vector falls out of it. Look at the row: "mat" has stepped out, because that is the
        word the model has not seen yet; the sentence it has is "The cat sat on the", and the last position, "the", has been
        shaped by the entire sentence and carries everything the model knows about what should come next. We only need this
        one vector: whatever the last token has become is the model's summary of "what word follows".""")
        # --- vocabulary matrix -> a score per vocab entry, by the same sweep
        vocab = grid(12, 8, WEIGHTS, cell=0.2).move_to([COLS[1], Y, 0])
        vocl = label("vocabulary matrix\n50,257 rows, one per token", 17, WEIGHTS).next_to(vocab, UP, buff=GAP)
        scores = column(12, TEXT, 0.2, op=0.0).move_to([-1.6, Y, 0])
        scl = label("a score for every\npossible next token", 17, TEXT).next_to(scores, RIGHT, buff=GAP)
        dest = vec.copy().move_to([-5.6, Y, 0])
        self.play(vec.animate.move_to(dest), vll.animate.next_to(dest, UP, buff=GAP), run_time=0.6)   # the label keeps its GAP above the moved vector
        self.play(FadeIn(vocab), FadeIn(vocl), FadeIn(scores), FadeIn(scl))
        sweep(self, vec, TOKEN, [(vocab, scores, TEXT)], rt=0.1)
        rnd = random.Random(5)
        self.play(*[c.animate.set_fill(TEXT, 0.25 + 0.6 * rnd.random()) for c in scores], run_time=0.4)
        self.next_slide("""Turning a vector into a word uses the same trick as the very first step, run backwards. A matrix with one row per
        vocabulary entry multiplies the vector, the same sweep as in every layer, giving one score per possible next token:
        50,257 numbers. In fact this is usually the same table used for the embeddings at the start, shared. A high score means
        the model thinks that token is a likely continuation.""")
        # --- softmax to a distribution: tall bars, one per token
        rnd = random.Random(5)
        hs = [rnd.uniform(0.1, 0.5) for _ in range(12)]
        hs[7] = 2.3
        dist = Bars(hs, width=0.36, gap=0.1, color=ATTN).move_to([3.9, ROWS[4], 0], aligned_edge=DOWN)   # right of the scores and their label, 0.5 from the frame edge
        dl = label("softmax: a probability per token, summing to 1", 18, ATTN).next_to(dist, UP, buff=GAP_WIDE)
        self.play(FadeOut(VGroup(vocab, vocl)), TransformFromCopy(scores, dist), FadeIn(dl), run_time=1.0)
        self.next_slide("""Softmax again turns the scores into probabilities that sum to one: the model's guess at the next word, spread over
        every token it knows. Most get almost nothing; a few are plausible. The engine then samples from this distribution.
        Take the highest and the output is predictable; sample with some randomness and it is more varied. That choice is
        the "temperature" setting people tune.""")
        top = dist[7]
        picked = VGroup(Square(0.8, fill_color=ATTN, fill_opacity=SOLID, stroke_width=0), label("mat", 24, ink_on(ATTN)))
        picked[1].move_to(picked[0])
        picked.next_to(top, UP, buff=0.2)
        self.play(FadeOut(dl), Indicate(top, color=ATTN, scale_factor=1.1), FadeIn(picked, shift=UP * 0.2), run_time=0.8)
        self.next_slide("""One token is drawn, "mat". That is the model's entire output for one pass through the whole stack: a single next
        token. Everything we have built, the embeddings, dozens of layers of attention and feed-forward, hundreds of billions
        of multiplications, produces exactly one word.""")
        # --- append: the sampled word takes its place in the row, and the whole model runs again
        back = VGroup(vector(25, ATTN, cell=0.16).move_to([XS[5], ROW_Y, 0]), label("mat", 18, ATTN))
        back[1].next_to(back[0], UP, buff=GAP_TIGHT)
        self.play(FadeOut(VGroup(vec, vll, scores, scl)), picked.animate.scale(0.3).move_to(back[0].get_center()), run_time=0.7)
        self.play(FadeOut(picked), FadeIn(back), run_time=0.4)
        loop = CurvedArrow(back[0].get_bottom() + DOWN * 0.25, vecs[0].get_bottom() + DOWN * 0.25, color=MUTED, stroke_width=sw(1.4), angle=-PI / 4)
        loopl = label("append, then run the whole model again", 20, MUTED).next_to(loop, DOWN, buff=GAP_TIGHT)
        self.play(Create(loop), FadeIn(loopl), run_time=0.9)
        self.next_slide("""Then the sampled word is appended: "mat" takes its place at the end of the row, in the colour of something the
        model wrote, and the entire model runs again, now with one more token, to produce the word after that. And again, and
        again. This is why a language model streams its answer one word at a time, and why a long answer costs many full
        passes through the stack. Everything you have seen happens for every single token you have ever watched one of these
        models type.""")
        tvi = VGroup(label("training: all positions at once", 22, MUTED), label("inference: one new token at a time", 22, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=GAP).move_to([COLS[0], ROWS[3] - 0.2, 0], aligned_edge=LEFT)   # below the loop's label
        self.play(FadeIn(tvi), run_time=0.6)
        self.finish("""One last thing, to place what you have seen. This whole machine is inference: the weights are fixed and it writes
        one token at a time. Training is the same arithmetic run in bulk, predicting the next token at every position of a
        huge corpus and nudging all those matrices, the embedding table, the query, key and value matrices, the feed-forward
        weights, until the predictions are good. That is a transformer: turn words into vectors, let every token gather from
        every other in parallel and then think alone, stack that many times, and read the next word off the end.""")
