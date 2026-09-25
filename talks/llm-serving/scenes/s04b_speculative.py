"""Move 3, knob four: speculative decoding. One picture: the text as a row of tokens at the top, the target model as a
wide box under it, and under the box the row where a pass puts its predictions, one under every position it read. The
newest token always sits at the same place (the write head) and older text slides left under a mask, so every pass
happens in the same five lanes.

Clicks: a pass predicts the next token at every position it reads (prefill, the prompt); decode reads one position per
pass, so one token per read of the weights; a draft guesses four tokens; one target pass over all of them; each
prediction flies to the slot it predicts, a matching guess is kept and the first miss takes the target's own token;
three more rounds at speed; where guesses come from; then what it gains as the batch grows, measured, and the schedule
that removes the loss. Drawn with greedy decoding (a guess is kept when it equals the target's pick); the note gives the
sampling rule, which keeps the target's distribution the same way."""
from lib.palette import *
from objects import *

PITCH, SIDE = 0.72, 0.62
ROW_Y, PRED_Y = 2.0, -1.0
L0 = -1.2                                   # the write head: the newest token's slot
BOX_C, BOX_W, BOX_H = [-2.1, 0.3, 0], 8.6, 1.5
DRAFT_C = [4.1, 2.0, 0]
PROMPT_WORDS = ["The", "cat", "sat", "on", "the"]

TITLE_SPEC = ("Knob four: speculative decoding, several tokens per pass", "3  four knobs: weights, experts, cache, drafts")


def lane(j: int) -> float:
    return L0 + PITCH * j


def tok(word: str, kind: str) -> VGroup:
    """One token: prompt and output solid, a draft's guess and a prediction outlined in their colours."""
    if kind in ("prompt", "output"):
        c = PROMPT if kind == "prompt" else OUTPUT
        sq = Square(SIDE, fill_color=c, fill_opacity=SOLID, stroke_width=0)
        t = label(word, 15, ink_on(c))
    else:
        c = DRAFT if kind == "draft" else OUTPUT
        sq = Square(SIDE, fill_color=c, fill_opacity=0.18, stroke_color=c, stroke_width=sw(0.8))
        t = label(word, 15, TEXT)
    if t.width > SIDE - 0.06:
        t.scale_to_fit_width(SIDE - 0.06)
    return VGroup(sq, t.move_to(sq))


def start_speculative(scene, add: bool = True) -> dict:
    """The still the scene opens on: the prompt at the write head, the target model, two counters, two gauges."""
    row = VGroup(*[tok(w, "prompt").move_to([lane(i - 4), ROW_Y, 0]) for i, w in enumerate(PROMPT_WORDS)])
    target = box(BOX_W, BOX_H, "", WEIGHTS).move_to(BOX_C)
    tl = label("target model: every pass reads all its weights", 18, WEIGHTS).move_to(target[0].get_corner(UL) + RIGHT * 0.2 + DOWN * 0.22, aligned_edge=UL)
    passes = Counter("passes of the target, this answer", 0, "", WEIGHTS, size=30).move_to([-6.4, -2.05, 0], aligned_edge=LEFT)
    written = Counter("tokens written, this answer", 0, "", OUTPUT, size=30).move_to([-2.6, -2.05, 0], aligned_edge=LEFT)
    bus, comp = Gauge("bus", OUTPUT, 1.2).move_to([5.7, 1.65, 0]), Gauge("compute", PROMPT, 1.2).move_to([6.45, 1.65, 0])
    mask = Rectangle(width=1.45, height=0.9, fill_color=BG, fill_opacity=1, stroke_width=0).move_to([-6.6, ROW_Y, 0]).set_z_index(5)
    cap = pin(scene, label("One pass reads all the weights: how many tokens can it write?", 22, color=CAPTION, width=12.8, thread=True), buff=0.3)
    parts = dict(row=row, target=target, tl=tl, passes=passes, written=written, bus=bus, comp=comp, mask=mask, cap=cap)
    parts["shown"] = [row, target, tl, passes, written, bus, comp, mask, cap]
    if add:
        scene.add(*parts["shown"])
    return parts


class Speculative(TalkSlide):
    def construct(self):
        t = title_still(self, *TITLE_SPEC)
        p = start_speculative(self)
        row, target, passes, written, bus, comp, cap = p["row"], p["target"], p["passes"], p["written"], p["bus"], p["comp"], p["cap"]
        row = list(row)
        count = dict(passes=0, written=0)

        def lit(xs):
            """The arithmetic of one pass at each position it reads: a light column inside the target box."""
            return VGroup(*[Rectangle(width=SIDE, height=0.85, fill_color=HI, fill_opacity=0.28, stroke_width=0).move_to([x, BOX_C[1] - 0.18, 0]) for x in xs])

        def target_pass(xs, words, rt):
            """One pass of the target over the positions at xs: the weights are read once (the box lights), each position
            does its arithmetic, and a prediction comes out under each. Returns the predictions."""
            cols = lit(xs)
            count["passes"] += 1
            self.play(FadeIn(cols), target[0].animate.set_fill(WEIGHTS, 0.42), bus.set(0.88), comp.set(0.06 + 0.07 * len(xs)), passes.to(count["passes"]), run_time=rt)
            preds = VGroup(*[tok(w, "pred").move_to([x, PRED_Y, 0]) for x, w in zip(xs, words)])
            self.play(LaggedStart(*[FadeIn(q, shift=DOWN * 0.25) for q in preds], lag_ratio=0.15), run_time=rt)
            self.play(FadeOut(cols), target[0].animate.set_fill(WEIGHTS, FILL), run_time=rt * 0.6)
            return preds

        def write(pred, j, word, rt):
            """A prediction flies to the slot it predicts and becomes the next token of the text."""
            pred.set_z_index(6)
            self.play(pred.animate.move_to([lane(j), ROW_Y, 0]), run_time=rt)
            out = tok(word, "output").move_to(pred)
            self.remove(pred); self.add(out)
            count["written"] += 1
            self.play(written.to(count["written"]), run_time=rt * 0.3)
            return out

        mask = p["mask"]

        def slide(k, rt):
            """The text slides left by k slots so the newest token is at the write head again. The mask takes part in the
            play (a still mobject is drawn under every moving one whatever its z-index), and what went under it leaves."""
            self.play(*[m.animate.shift(LEFT * PITCH * k) for m in row], mask.animate.shift(ORIGIN), run_time=rt)
            for m in [m for m in row if m.get_x() < mask.get_right()[0]]:
                row.remove(m); self.remove(m)
            self.wait(0.2)   # a step that ends on a slide ends on a settled row

        # --- 1. a pass predicts the next token at every position it reads: the prompt, in one pass
        cap = swap_caption(self, cap, "One pass predicts the next token at every position it reads")
        xs = [m.get_x() for m in row]
        preds = target_pass(xs, ["cat", "sat", "on", "the", "mat"], 0.8)
        self.play(*[q.animate.set_opacity(0.35) for q in preds[:4]], run_time=0.5)
        row.append(write(preds[4], 1, "mat", 0.8))
        self.play(FadeOut(VGroup(*preds[:4])), run_time=0.4)
        slide(1, 0.6)
        self.next_slide("""One fact from move one carries this whole knob: a pass predicts the next token at every
        position it reads, not only at the last. Prefill is that: one pass over five positions, and under each position the
        token the model would write after it. After 'The' it predicts 'cat', after 'cat' 'sat', and so on; those four only
        repeat the prompt, and the engine throws them away. The fifth is new, 'mat', and it becomes the first token of the
        answer. The text then slides left so that the newest token always sits in the same place.""")

        # --- 2. decode: one position per pass, one token per read of the weights
        cap = swap_caption(self, cap, "Decode: one position per pass, one token per read of the weights")
        for word, rt in ((".", 0.7), ("It", 0.25)):
            preds = target_pass([lane(0)], [word], rt)
            row.append(write(preds[0], 1, word, rt))
            slide(1, rt * 0.8)
        self.next_slide("""Decode. Each pass now has one new position to compute, the newest token, and it writes one token. The earlier
        positions are not computed again; their keys and values are in the cache. And every pass still reads all the weights:
        the bus gauge is full, the compute gauge nearly empty. This is the latency ceiling from move two, bandwidth over bytes
        per token, and batching cannot raise it for one request: batching fills the idle arithmetic with other requests'
        tokens. The way past it for one request would be to compute several of its own positions per pass. Those positions do
        not exist yet, because each token depends on the one before it.""")

        # --- 3. a draft guesses the next four tokens, one after another
        cap = swap_caption(self, cap, "A small draft guesses the next four tokens, one after another")
        draft = box(2.3, 0.7, "draft: a small model", DRAFT, size=17).move_to(DRAFT_C)
        self.play(FadeIn(draft), run_time=0.6)

        def guess(words, rt):
            gs = []
            for j, w in enumerate(words, start=1):
                g = tok(w, "draft").move_to(draft[0].get_left() + LEFT * (SIDE / 2 + 0.05))
                self.play(draft[0].animate.set_fill(DRAFT, 0.4), bus.set(0.12), comp.set(0.04), FadeIn(g), run_time=rt * 0.5)
                self.play(g.animate.move_to([lane(j), ROW_Y, 0]), draft[0].animate.set_fill(DRAFT, FILL), run_time=rt)
                gs.append(g)
            return gs

        gs = guess(["slept", "in", "the", "sun"], 0.5)
        self.next_slide("""So guess them. A draft is a small model, often one to four layers riding on the target's own features, and it
        guesses the next four tokens. It guesses them one after another, like any model decodes, but each of its passes reads
        a small fraction of the bytes a target pass reads, so four guesses cost a fraction of one target pass. The guesses are one
        continuation, 'slept in the sun', not four alternatives. They are only guesses; nothing is written yet.""")

        # --- 4. one pass of the target over the newest token and the four guesses
        cap = swap_caption(self, cap, "One pass of the target checks all four: one read of the weights")
        preds = target_pass([lane(j) for j in range(5)], ["slept", "in", "the", "warm", "."], 0.8)
        self.wait(0.3)
        self.next_slide("""Now one pass of the target over five positions: the newest real token and the four guesses. It is the prefill
        trick again. Under each position is what the target would write after it: after 'It', 'slept'; after 'slept', 'in';
        after 'in', 'the'; after 'the', 'warm'. Attention only looks backwards, so each prediction is exactly the one the target
        would have made if it had written the text up to there itself. The pass read the weights once, the bus gauge is where
        it was, and the compute gauge rose: five positions of arithmetic instead of one, on units that were idle.""")

        # --- 5. each prediction flies to the slot it predicts; the first miss takes the target's token
        cap = swap_caption(self, cap, "Kept while the guesses match; the first miss takes the target's own token")

        def check(gs, preds, words, rt):
            """Walk the positions in order: a prediction that equals the guess in its slot keeps the guess as text; at the
            first miss the prediction replaces the guess and everything after it is discarded. All guesses matched: the
            last prediction is a bonus token after them. Returns the number of tokens written."""
            n = 0
            for j, g in enumerate(gs):
                q = preds[j]; q.set_z_index(6)
                self.play(q.animate.move_to(g), run_time=rt)
                if g[1].text == q[1].text:
                    out = tok(words[j], "output").move_to(g)
                    self.play(FadeOut(q), ReplacementTransform(g, out), run_time=rt * 0.6)
                    row.append(out); n += 1
                else:
                    self.play(g[0].animate.set_stroke(HOT).set_fill(HOT, 0.3), run_time=rt * 0.5)
                    out = tok(q[1].text, "output").move_to(g)
                    rest = VGroup(*gs[j + 1:], *preds[j + 1:])
                    self.play(FadeOut(g, shift=UP * 0.3), rest.animate.set_opacity(0.2), run_time=rt * 0.6)
                    self.remove(q); self.add(out)
                    self.play(FadeOut(rest), run_time=rt * 0.5)
                    row.append(out); n += 1
                    break
            else:
                row.append(write(preds[len(gs)], len(gs) + 1, preds[len(gs)][1].text, rt))
                count["written"] -= 1; n += 1
            count["written"] += n
            self.play(written.to(count["written"]), comp.set(0.06), run_time=rt * 0.5)
            return n

        n = check(gs, preds, ["slept", "in", "the"], 0.7)
        slide(n, 0.7)
        self.next_slide("""The check, in order. The prediction after 'It' is 'slept', and the guess in that slot is 'slept': kept. 'in':
        kept. 'the': kept. The prediction after 'the' is 'warm', the guess was 'sun': the first miss. The target's own 'warm'
        takes the slot, and everything after it is thrown away, the last prediction too, because it was computed after a
        wrong guess. Four tokens from one pass of the target where decode wrote one. And every token kept is the target's own
        prediction, so the text is exactly what the target alone would have written; only the speed changed. With sampling
        instead of greedy picks the rule is a coin: a guess is kept with probability of the target's over the draft's for that
        token, and a rejected slot is filled from the difference of the two, which leaves the output distribution exactly the
        target's (Leviathan and Chen, 2023). Kept tokens' keys and values stay in the cache; nothing is computed twice.""")

        # --- 6. three more rounds at speed: one to five tokens per pass
        cap = swap_caption(self, cap, "At speed: one to five tokens per pass, and the same text")
        for words, predicted in ((["sun", "until", "the", "dog"], ["sun", "until", "the", "dog", "came"]),
                                 (["back", "to", "the", "house"], ["home", "and", "barked", ".", "It"]),
                                 (["and", "barked", ".", "It"], ["and", "barked", ".", "The", "cat"])):
            gs = guess(words, 0.14)
            preds = target_pass([lane(j) for j in range(5)], predicted, 0.18)
            n = check(gs, preds, words, 0.18)
            slide(n, 0.25)
        self.next_slide("""Three more rounds at speed. All four guesses right: five tokens, the fifth a bonus, the target's prediction after
        the last guess. The first guess wrong: one token, the same as plain decode, and the draft's work wasted. Three right:
        four tokens. A pass writes at least one token and at most one more than was drafted. What matters is the average, and
        the engine logs it as the mean acceptance length, counted with the target's own token: 3.1 tokens per pass for Gemma 4
        12B with its four-guess drafter, 2.2 for an EAGLE-3 draft of three on the 30B model of this talk. Seventeen tokens in
        seven passes here.""")

        # --- 7. where the guesses come from
        cap = swap_caption(self, cap, "Where the guesses come from decides how many are kept, and what they cost")
        kinds = VGroup(block("n-gram · copies a match from the text so far", DRAFT, w=4.3, h=0.46, size=17),
                       block("EAGLE-3 · a small model trained on the target", DRAFT, w=4.3, h=0.46, size=17),
                       block("MTP · draft layers shipped with the model", DRAFT, w=4.3, h=0.46, size=17)).arrange(DOWN, buff=0.12)
        kinds.move_to([2.4, 1.3, 0], aligned_edge=UL)
        self.play(FadeOut(bus), FadeOut(comp), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(k, shift=DOWN * 0.1) for k in kinds], lag_ratio=0.3), run_time=1.2)
        self.next_slide("""Every method draws the same check; they differ in where the guesses come from. N-gram, or prompt lookup, copies
        what followed the last few tokens where they appeared earlier in the text: free, and right only when the answer quotes
        the prompt, as in summaries, code edits and extraction. On open-ended answers under load it measured 58 percent slower
        here: almost nothing was accepted, the verification was paid anyway, and turning it on switched off the engine's
        asynchronous scheduling. A draft model is a small separate network with
        the same vocabulary; EAGLE-3 is one trained on the target's own internal features, which is what makes it accurate,
        and a publisher ships it next to the model. Multi-token prediction, MTP, is draft layers built with the model: DeepSeek
        V3 and Qwen3-Next have them inside the checkpoint, and each Gemma 4 size has a four-layer drafter that reads the
        target's own cache instead of keeping one. Around these sit variants that verify a tree of guesses in one pass, draft
        from the model's own early layers, or draft a whole block at once. The better the guesses and the cheaper they are,
        the more each pass writes.""")

        # --- 8. what it gains as the batch grows, measured: the verification needs the compute the batch needs too
        cap = swap_caption(self, cap, "Measured: the gain shrinks as the batch fills the compute")
        x_at = dict(zip([1, 8, 16, 32, 64], [-4.6, -3.1, -1.6, -0.1, 1.4]))
        s, y0 = 0.0228, -1.36
        yv = lambda v: y0 + s * v
        zero = DashedLine([-5.2, y0, 0], [1.8, y0, 0], color=DIM, stroke_width=sw(0.6), dash_length=0.08)
        yt = VGroup(*[label(t_, 15, DIM).move_to([-5.35, yv(v), 0], aligned_edge=RIGHT) for t_, v in (("0", 0), ("+50%", 50), ("+100%", 100))])
        grid_ = VGroup(*[DashedLine([-5.2, yv(v), 0], [1.8, yv(v), 0], color=DIM, stroke_width=sw(0.3), dash_length=0.05, stroke_opacity=0.5) for v in (50, 100)])
        ticks = VGroup(*[label(str(k), 15, DIM).move_to([x, -2.3, 0]) for k, x in x_at.items()])
        xname = label("requests in flight, one engine", 15, DIM).next_to(ticks, RIGHT, buff=0.4)
        yname = label("gain in requests/s from the draft, against the same engine without one", 15, DIM).move_to([-5.2, 1.45, 0], aligned_edge=LEFT)
        passes.stop(); written.stop()
        self.play(FadeOut(kinds), FadeOut(VGroup(target, p["tl"])), FadeOut(passes), FadeOut(written), run_time=0.6)
        self.play(Create(zero), FadeIn(yt), FadeIn(grid_), FadeIn(ticks), FadeIn(xname), FadeIn(yname), run_time=0.6)

        def series(points, color, name, dashed=False, rt=0.35):
            dots = VGroup(); segs = VGroup()
            prev = None
            for k, v in points:
                d = Dot([x_at[k], yv(v), 0], radius=0.06, color=HOT if v < 0 else color)
                if prev is not None:
                    seg = (DashedLine if dashed else Line)(prev.get_center(), d.get_center(), color=color, stroke_width=sw(0.8))
                    self.play(Create(seg), FadeIn(d), run_time=rt)
                    segs.add(seg)
                else:
                    self.play(FadeIn(d), run_time=rt)
                dots.add(d); prev = d
            nl = label(name, 16, color).next_to(dots[-1], RIGHT, buff=0.15)
            self.play(FadeIn(nl), run_time=0.3)
            return VGroup(dots, segs, nl)

        own = series([(1, 107), (8, 88), (16, 79), (32, 54), (64, 32)], DRAFT, "dense 12B, its own drafter, 4 guesses")
        self.next_slide("""Now the cost, and it is the compute the verification takes. A dense 12B in fp8 with its publisher's four-layer
        drafter, against the same engine without it, unique 1,000-token prompts: one request in flight, twice the requests per
        second, 176 against 86 tokens per second; eight in flight, plus 88 percent; then 79, 54 and 32 percent at 64. The gain
        falls as the batch grows because a batch already uses the arithmetic that was idle for one request, so the extra
        positions stop being free. It never went negative on this model: its prefill wall is far above what 64 users ask of it,
        and a drafter that shares the target's cache is cheap. The 26B mixture of experts with its drafter kept plus 51 percent
        at 64.""")

        fixed = series([(8, 44), (16, 47), (32, 8), (64, -27)], MUTED, "120B MoE, EAGLE-3, always 3 guesses")
        self.next_slide("""A different model and draft: the 120B mixture of experts with its publisher's EAGLE-3 draft, always three guesses,
        measured on eight engines and read per engine.
        Plus 44 and 47 percent at 8 and 16 in flight per engine, plus 8 at 32, and minus 27 percent at 64: a loss. With many
        unique prompts in flight, prefill needs the compute, and three guesses per request per step, many of them rejected,
        take it away. Speculation trades arithmetic for fewer passes, and that is only a good trade while arithmetic is spare.""")

        sched = series([(8, 23), (16, 27), (32, 17), (64, -6)], TEXT, "same, 3 then 1 then 0 as the batch grows", dashed=True)
        self.next_slide("""So draft less as the batch grows. The engine takes a schedule of draft lengths by the number of running requests;
        here three guesses up to 16, one up to 32, none above. The same model on one engine: plus 23, 27 and 17 percent
        where it drafts, and minus 6 at 64, inside the noise, where the fixed length lost 27. One configuration then holds across the day. Two practical
        points. The draft is specific to its target: change the model and the draft must change with it. And the first time
        the engine meets a new draft length at a new batch size it compiles for about thirty seconds, so warm every level
        you will serve before taking traffic. Where decode is the wall, this is the knob to turn on first.""")

        # --- hand-over: the text, the target and the chart give way to the model that does not fit one GPU
        from s05_parallelism import start_parallelism, TITLE_PAR
        nxt = start_parallelism(self, add=False)
        leaving = [*row, draft, zero, yt, grid_, ticks, xname, yname, own, fixed, sched, mask, cap]
        t = handover(self, t, *TITLE_PAR, leaving=leaving, arriving=nxt["shown"])
        self.finish("""The picture hands over. 236 GB of weights and no GPU that holds them: divide the model, and pay at the seams. Some models do not fit one card. A 235B mixture of experts in fp8 is 236 GB of weights; the largest single GPU we can rent holds 96. So the model has to be divided over several GPUs, and how it is divided shows up as time.""")
