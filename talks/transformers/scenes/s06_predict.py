"""Move 5: from the last vector to the next word, and the loop. The final vector of the last position is multiplied
by a matrix with one row per vocabulary entry, giving a score for every possible next token; softmax makes a
probability distribution; one token is sampled, appended to the sentence, and the whole model runs again. One
picture: the sentence, the last vector, the vocabulary matrix, the distribution, the sampled word joining, the loop.
"""
from lib.palette import *
from objects import *


class Predict(TalkSlide):
    def construct(self):
        t = title(self, "From the last vector to the next word", "5  one token at a time")
        sentence = label("The cat sat on the", 32, TOKEN).move_to([-2.2, 2.5, 0])
        self.play(FadeIn(sentence))
        vec = vector(30, TOKEN, cell=0.16).move_to([-5.4, 0.2, 0])
        vll = label('final vector of\nthe last token', 14, TOKEN).next_to(vec, UP, buff=0.2)
        self.play(FadeIn(vec), FadeIn(vll))
        self.next_slide("""After the whole stack, the last position, here the vector for "the", has been shaped by the entire sentence and
        carries everything the model knows about what should come next. We only need this one vector: whatever the last token
        has become is the model's summary of "what word follows".""")
        # --- vocabulary matrix -> a score per vocab entry
        vocab = grid(14, 8, WEIGHTS, cell=0.1).move_to([-3.2, 0.0, 0])
        vocl = label("vocabulary matrix\none row per token, 50,257 rows", 14, WEIGHTS).next_to(vocab, UP, buff=0.18)
        self.play(FadeIn(vocab), FadeIn(vocl))
        scores = column(14, MUTED, 0.12).move_to([-1.2, 0.0, 0])
        for c in scores:
            c.set_fill(MUTED, 0.3 + 0.6 * __import__("random").Random(int(c.get_y() * 97)).random())
        scl = label("a score for every\npossible next token", 14, MUTED).next_to(scores, UP, buff=0.18)
        self.play(TransformFromCopy(vocab, scores), FadeIn(scl), run_time=0.9)
        self.next_slide("""Turning a vector into a word uses the same trick as the very first step, run backwards. A matrix with one row per
        vocabulary entry multiplies the vector, giving one score per possible next token: 50,257 numbers. In fact this is
        usually the same table used for the embeddings at the start, shared. A high score means the model thinks that token
        is a likely continuation.""")
        # --- softmax to a distribution, sample
        import random
        rnd = random.Random(5)
        hs = [rnd.uniform(0.05, 0.3) for _ in range(14)]
        hs[8] = 1.4
        dist = Bars(hs, width=0.3, gap=0.08, color=OUTPUT).move_to([2.6, -1.1, 0], aligned_edge=DOWN)
        dl = label("softmax: a probability over the whole vocabulary", 15, OUTPUT).next_to(dist, UP, buff=0.25)
        self.play(FadeOut(VGroup(vocab, vocl)), TransformFromCopy(scores, dist), FadeIn(dl), run_time=1.0)
        self.next_slide("""Softmax again turns the scores into probabilities that sum to one: the model's guess at the next word, spread over
        every token it knows. Most get almost nothing; a few are plausible. The engine then samples from this distribution.
        Take the highest and the output is predictable; sample with some randomness and it is more varied. That choice is
        the "temperature" setting people tune.""")
        top = dist[8]
        picked = VGroup(Square(0.6, fill_color=OUTPUT, fill_opacity=0.9, stroke_width=0), label("mat", 20, "#0f1116"))
        picked[1].move_to(picked[0])
        picked.next_to(top, UP, buff=0.2)
        self.play(Indicate(top, color=OUTPUT, scale_factor=1.15), FadeIn(picked, shift=UP * 0.2), run_time=0.8)
        self.next_slide("""One token is drawn, "mat". That is the model's entire output for one pass through the whole stack: a single next
        token. Everything we have built, the embeddings, dozens of layers of attention and feed-forward, hundreds of billions
        of multiplications, produces exactly one word.""")
        # --- append and loop
        newword = label(" mat", 32, OUTPUT).next_to(sentence, RIGHT, buff=0.12)
        self.play(FadeOut(VGroup(vec, vll, scores, scl, dist, dl)),
                  picked.animate.scale(0.5).move_to(newword.get_center()), run_time=0.7)
        self.play(FadeOut(picked), FadeIn(newword), run_time=0.4)
        loop = CurvedArrow(sentence.get_right() + RIGHT * 1.6 + UP * 0.1, sentence.get_left() + DOWN * 1.2, color=MUTED, stroke_width=3, angle=TAU / 3)
        loopl = label("append the word, run the whole model again for the next one", 16, MUTED).move_to([0, -1.4, 0])
        self.play(Create(loop), FadeIn(loopl), run_time=0.9)
        self.next_slide("""Then the sampled word is appended to the sentence and the entire model runs again, now with one more token, to
        produce the word after that. And again, and again. This is why a language model streams its answer one word at a
        time, and why a long answer costs many full passes through the stack. Everything you have seen happens for every
        single token you have ever watched one of these models type.""")
        tvi = label("training: predict every next token in a huge corpus at once, and adjust the weights\ninference: the same math, one new token at a time", 16, MUTED).move_to([0, 1.0, 0])
        self.play(FadeOut(loop), FadeOut(loopl), FadeIn(tvi), run_time=0.6)
        self.finish("""One last thing, to place what you have seen. This whole machine is inference: the weights are fixed and it writes
        one token at a time. Training is the same arithmetic run in bulk, predicting the next token at every position of a
        huge corpus and nudging all those matrices, the embedding table, the query, key and value matrices, the feed-forward
        weights, until the predictions are good. That is a transformer: turn words into vectors, let every token gather from
        every other in parallel and then think alone, stack that many times, and read the next word off the end.""")
