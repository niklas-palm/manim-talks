"""Move 5: from the last vector to the next word, and the loop. The final vector of the last position is multiplied
by a matrix with one row per vocabulary entry, giving a score for every possible next token; softmax makes a
probability distribution; one token is sampled, appended to the sentence, and the whole model runs again. One
picture: the sentence, the last vector, the vocabulary matrix, the scores, the distribution as tall bars, the sampled
word joining the sentence, the loop.
"""
from lib.palette import *
from objects import *
import random


class Predict(TalkSlide):
    def construct(self):
        t = title(self, "From the last vector to the next word", "5  one token at a time")
        sentence = label("The cat sat on the", 34, TOKEN).move_to([-2.0, 2.45, 0])
        self.play(FadeIn(sentence))
        vec = vector(30, TOKEN, cell=0.2).move_to([-6.0, -0.2, 0])
        vll = label('final vector\nof the last token', 16, TOKEN).next_to(vec, UP, buff=0.2)
        self.play(FadeIn(vec), FadeIn(vll))
        self.next_slide("""After the whole stack, the last position, here the vector for "the", has been shaped by the entire sentence and
        carries everything the model knows about what should come next. We only need this one vector: whatever the last token
        has become is the model's summary of "what word follows".""")
        # --- vocabulary matrix -> a score per vocab entry, by the same sweep
        vocab = grid(12, 8, WEIGHTS, cell=0.2).move_to([-4.1, -0.2, 0])
        vocl = label("vocabulary matrix\n50,257 rows, one per token", 16, WEIGHTS).next_to(vocab, UP, buff=0.2)
        scores = column(12, TEXT, 0.2, op=0.0).move_to([-1.3, -0.2, 0])
        scl = label("a score for every\npossible next token", 16, TEXT).next_to(scores, RIGHT, buff=0.3)
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
        dist = Bars(hs, width=0.5, gap=0.1, color=ATTN).move_to([2.9, -2.2, 0], aligned_edge=DOWN)
        dl = label("softmax: a probability per token, summing to 1", 17, ATTN).move_to([2.9, 0.75, 0])
        self.play(FadeOut(VGroup(vocab, vocl)), TransformFromCopy(scores, dist), FadeIn(dl), run_time=1.0)
        self.next_slide("""Softmax again turns the scores into probabilities that sum to one: the model's guess at the next word, spread over
        every token it knows. Most get almost nothing; a few are plausible. The engine then samples from this distribution.
        Take the highest and the output is predictable; sample with some randomness and it is more varied. That choice is
        the "temperature" setting people tune.""")
        top = dist[7]
        picked = VGroup(Square(0.8, fill_color=ATTN, fill_opacity=0.9, stroke_width=0), label("mat", 24, "#0f1116"))
        picked[1].move_to(picked[0])
        picked.next_to(top, UP, buff=0.2)
        self.play(FadeOut(dl), Indicate(top, color=ATTN, scale_factor=1.1), FadeIn(picked, shift=UP * 0.2), run_time=0.8)
        self.next_slide("""One token is drawn, "mat". That is the model's entire output for one pass through the whole stack: a single next
        token. Everything we have built, the embeddings, dozens of layers of attention and feed-forward, hundreds of billions
        of multiplications, produces exactly one word.""")
        # --- append and loop
        newword = label(" mat", 34, ATTN).next_to(sentence, RIGHT, buff=0.12)
        self.play(FadeOut(VGroup(vec, vll, scores, scl, dist)), picked.animate.scale(0.5).move_to(newword.get_center()), run_time=0.7)
        self.play(FadeOut(picked), FadeIn(newword), run_time=0.4)
        loop = CurvedArrow(newword.get_right() + RIGHT * 0.2 + DOWN * 0.15, sentence.get_left() + LEFT * 0.2 + DOWN * 0.15, color=MUTED, stroke_width=3.5, angle=-PI / 3)
        loopl = label("append, then run the whole model again", 18, MUTED).move_to([-1.9, 0.9, 0])
        self.play(Create(loop), FadeIn(loopl), run_time=0.9)
        self.next_slide("""Then the sampled word is appended to the sentence and the entire model runs again, now with one more token, to
        produce the word after that. And again, and again. This is why a language model streams its answer one word at a
        time, and why a long answer costs many full passes through the stack. Everything you have seen happens for every
        single token you have ever watched one of these models type.""")
        tvi = VGroup(label("training: all positions at once", 18, MUTED), label("inference: one new token at a time", 18, MUTED)).arrange(DOWN, buff=0.2).move_to([0, -0.9, 0])
        self.play(FadeIn(tvi), run_time=0.6)
        self.finish("""One last thing, to place what you have seen. This whole machine is inference: the weights are fixed and it writes
        one token at a time. Training is the same arithmetic run in bulk, predicting the next token at every position of a
        huge corpus and nudging all those matrices, the embedding table, the query, key and value matrices, the feed-forward
        weights, until the predictions are good. That is a transformer: turn words into vectors, let every token gather from
        every other in parallel and then think alone, stack that many times, and read the next word off the end.""")
