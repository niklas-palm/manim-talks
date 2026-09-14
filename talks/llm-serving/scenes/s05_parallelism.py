"""Move 4: when one GPU is not enough. The teaching object is a step timeline: compute segments shrink as GPUs are
added, the synchronisation segments do not, and two independent engines have no sync at all."""
from lib.palette import *
from objects import *


def gpu_row(n: int, w: float = 1.15, h: float = 1.35, buff: float = 0.22) -> VGroup:
    return VGroup(*[RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=WEIGHTS, stroke_width=2.5, fill_color=WEIGHTS, fill_opacity=0.08) for _ in range(n)]).arrange(RIGHT, buff=buff)


def layer_stack(n: int, width: float, color: str = WEIGHTS, op: float = 0.7, h: float = 0.15, buff: float = 0.06) -> VGroup:
    return VGroup(*[Rectangle(width=width, height=h, fill_color=color, fill_opacity=op, stroke_width=0) for _ in range(n)]).arrange(DOWN, buff=buff)


def timeline(segments, unit: float, y: float, x0: float = -6.4):
    """segments: list of (kind, length): kind 'c' compute (blue) or 's' sync (red). Returns the bars and total width."""
    bars = VGroup(); x = x0
    for kind, length in segments:
        w = unit * length
        bars.add(Rectangle(width=w, height=0.28, fill_color=PROMPT if kind == "c" else HOT, fill_opacity=0.9, stroke_width=0).move_to([x + w / 2, y, 0]))
        x += w + 0.02
    return bars, x - x0


class Parallelism(TalkSlide):
    def construct(self):
        t = title(self, "When the model does not fit one GPU", "4  more than one GPU")
        model = layer_stack(6, 2.6).shift(UP * 2.2 + LEFT * 3.2)
        ml = label("a 235B model: 236 GB of fp8 weights", 18, TEXT).next_to(model, RIGHT, buff=0.35)
        g = gpu_row(4, 2.0, 2.2, buff=0.55).shift(UP * 0.25)   # room between the GPUs for the exchange arrows to be seen
        gl = label("four 80 GB GPUs", 16, DIM).next_to(g, DOWN, buff=0.12)
        cap = caption(self, "No GPU holds 236 GB: divide the model, pay at the seams")
        self.play(FadeIn(model), FadeIn(ml), FadeIn(g), FadeIn(gl))
        self.next_slide("""236 GB of weights and no GPU that holds them: divide the model, and pay at the seams. Some models do not fit one card. A 235B mixture of experts in fp8 is 236 GB of weights; the largest single GPU
        we can rent holds 96. So the model has to be divided over several GPUs, and how it is divided shows up as time.""")
        # TP: slice every matrix; each GPU multiplies its slice, then all of them add their partial results
        cap = swap_caption(self, cap, "Tensor parallelism: whole vector everywhere, a quarter of every matrix each")
        self.play(FadeOut(gl))
        x = column(8, PROMPT, 0.13).move_to([3.9, 2.15, 0])
        xl = label("one token's vector", 14, PROMPT).next_to(x, RIGHT, buff=0.15)
        self.play(FadeIn(x), FadeIn(xl), run_time=0.5)
        slices = VGroup(*[grid(8, 2, cell=0.13).move_to(b.get_center() + RIGHT * 0.05) for b in g])
        self.play(ReplacementTransform(model.copy(), slices), model.animate.set_opacity(0.2), run_time=0.9)
        copies = VGroup(*[column(8, PROMPT, 0.13).next_to(sl, LEFT, buff=0.22) for sl in slices])
        self.play(*[TransformFromCopy(x, c) for c in copies], run_time=0.8)   # the same whole vector arrives on every GPU
        parts = VGroup(*[column(8, OUTPUT, 0.13, op=0.0).next_to(sl, RIGHT, buff=0.22) for sl in slices])
        self.add(parts)
        for i in range(8):   # every GPU sweeps its slice at the same time: a quarter of the arithmetic each
            rows = [[sl[i * 2 + c] for c in range(2)] for sl in slices]
            self.play(*[m.animate.set_fill(OUTPUT, 1.0) for row in rows for m in row], *[c.animate.set_fill(OUTPUT, 1.0) for cp in copies for c in cp],
                      *[parts[j][i].animate.set_fill(OUTPUT, 0.35) for j in range(4)], run_time=0.1)
            self.play(*[m.animate.set_fill(WEIGHTS, 0.6) for row in rows for m in row], *[c.animate.set_fill(PROMPT, 0.9) for cp in copies for c in cp], run_time=0.05)
        pl = label("each GPU now holds a quarter of the answer: partial sums for every output", 14, OUTPUT).next_to(g, DOWN, buff=0.15)
        self.play(FadeIn(pl), run_time=0.4)
        sync = VGroup(*[DoubleArrow(g[i].get_right(), g[i + 1].get_left(), buff=0.04, color=HOT, stroke_width=4, tip_length=0.16) for i in range(3)])
        sl2 = label("all-reduce: partial sums exchanged; every GPU now holds the full output", 14, HOT).move_to(pl)
        self.play(FadeIn(sync), FadeOut(pl), FadeIn(sl2), run_time=0.4)
        travellers = VGroup(*[parts[j].copy().set_opacity(0.6) for j in range(4) for _ in range(3)])
        dests = [parts[k] for j in range(4) for k in range(4) if k != j]
        self.play(*[t.animate.move_to(d) for t, d in zip(travellers, dests)], run_time=0.9)
        self.play(FadeOut(travellers), *[c.animate.set_fill(OUTPUT, 0.95) for pc in parts for c in pc], run_time=0.5)
        tl_y = -1.95
        step1, w1 = timeline([("c", 4.0)], 1.0, tl_y + 0.45)
        l1 = label("one GPU, one layer step (if it fitted)", 15, DIM).next_to(step1, RIGHT, buff=0.2)
        step4, w4 = timeline([("c", 1.0), ("s", 0.6)], 1.0, tl_y)
        l4 = label("TP = 4: a quarter of the arithmetic, then the exchange", 15, DIM).next_to(step4, RIGHT, buff=0.2)
        self.play(FadeIn(step1), FadeIn(l1), FadeIn(step4), FadeIn(l4))
        self.next_slide("""Tensor parallelism: the whole vector to every GPU, a quarter of every matrix each, then exchange. Tensor parallelism is what engines do inside a machine: instead of splitting the stack of layers, split every
        matrix. Each GPU holds a quarter of every weight matrix in every layer, so all four GPUs work on every token at once.
        The same whole vector arrives on every GPU; each multiplies it by its own quarter of the matrix, a quarter of the
        arithmetic in parallel, and what each GPU holds afterwards is a quarter of the answer: partial sums for every output
        number. Then comes the seam. The four have to be added together, so every GPU sends its partial sums to the other three
        and receives theirs, the red arrows, an all-reduce. Only after it does any GPU hold the layer's real output. In a real
        block this exchange comes once per pair of matrices: the first is split so each GPU keeps a slice of the intermediate
        result and needs no exchange, the second turns those slices into partial sums and needs the all-reduce; two per layer.
        Every layer of every token waits on it, and it needs a fast link between the GPUs, which is why this stays inside a
        node. The other way to divide a model, whole layers per GPU with the token walking from one GPU to the next, exists and
        is how a model is spread across machines; it exchanges almost nothing but leaves GPUs idle in turn, and it is not what
        you meet inside a single box. On the timeline: the compute part of a step shrinks to a quarter, the red part is the
        exchange, and it does not shrink when GPUs are added.""")
        step8, w8 = timeline([("c", 0.5), ("s", 0.6)], 1.0, tl_y - 0.45)
        l8 = label("TP = 8: less arithmetic, the same exchange", 15, DIM).next_to(step8, RIGHT, buff=0.2)
        cap = swap_caption(self, cap, "It makes the model fit. It does not make a fitting model faster.")
        self.play(FadeIn(step8), FadeIn(l8))
        self.next_slide("""Go to eight GPUs and the arithmetic halves again while the exchange stays. Past the degree where the
        model fits, each extra GPU buys less compute time and adds another participant to every exchange. This is the third
        wall of the talk, after compute and bandwidth: lockstep. Tensor parallelism is a way to make a model fit, not a way to
        make it fast.""")
        tp_bits = VGroup(slices, copies, parts, x, xl, sync, sl2, step1, l1, step4, l4, step8, l8)
        # EP
        cap = swap_caption(self, cap, "Expert parallelism: whole experts on each GPU, tokens travel to them")
        self.play(FadeOut(tp_bits))
        experts = VGroup(*[VGroup(*[Square(0.4, fill_color=CACHE, fill_opacity=0.75, stroke_width=0) for _ in range(6)]).arrange_in_grid(rows=3, cols=2, buff=0.1).move_to(b) for b in g])
        self.play(FadeIn(experts))
        import random
        random.seed(5)
        for _ in range(3):
            tok = Dot(color=OUTPUT, radius=0.09).move_to(g.get_center() + UP * (g.height / 2 + 0.35))   # from above the row, not above the first GPU
            dest = random.randrange(4)
            self.play(tok.animate.move_to(experts[dest][random.randrange(6)].get_center()), run_time=0.4)
            self.play(FadeOut(tok), run_time=0.12)
        meas = VGroup(label("when it is used", 15, DIM),
                      label("too big for slicing alone: hundreds of experts spread across many GPUs", 16, TEXT),
                      label("and the batch is large enough that every GPU's experts have tokens to serve", 16, TEXT),
                      label("235B on 8 GPUs: 108 to 86 tokens/s each, 7 to 20% fewer requests/s", 16, MUTED),
                      ).arrange(DOWN, aligned_edge=LEFT, buff=0.08).shift(DOWN * 1.6 + LEFT * 0.4)
        self.play(FadeIn(meas))
        self.next_slide("""measured here, 235B on 8 GPUs: per request 108 tokens/s without, 86 with; under load 7 to 20% fewer requests/s. the model is too big for tensor slicing alone: hundreds of experts spread whole across many GPUs. Expert parallelism is the other way to place a mixture of experts: instead of slicing every matrix across the
        GPUs, whole experts are placed on GPUs, and each token travels to the GPUs that hold the experts its router picked.
        That replaces the all-reduce with an all-to-all of tokens. When is that the right layout? When the model is so large
        that slicing alone cannot place it, hundreds of experts across dozens of GPUs, the frontier models of six hundred
        billion parameters and more; and when the batch is large enough that every GPU's experts have tokens to serve on
        every step, otherwise GPUs sit idle waiting for tokens that never come. Our measurement is the small end of that:
        a 235B model on eight GPUs. One request decoded at 108 tokens per second with tensor parallelism and 86 with expert
        parallelism, and under load it served 7 to 20 percent fewer requests per second, because at this size the all-to-all
        costs more than the all-reduce it replaces. One practical reason to turn it on anyway: some fp8 checkpoints refuse a
        tensor split that would cut an expert's 128-wide tiles, and this one would not start at tensor parallel eight without
        it. It is one flag and one restart; measure it rather than assume it.""")
        # replicas
        self.play(FadeOut(experts), FadeOut(meas), FadeOut(model), FadeOut(ml))
        g8 = gpu_row(8, 0.8, 1.15).shift(UP * 0.55)
        self.play(ReplacementTransform(g, g8))
        cap = swap_caption(self, cap, "Eight GPUs: one engine over all of them, or two engines over four each?")
        one = SurroundingRectangle(g8, color=HOT, buff=0.1)
        s_one, _ = timeline([("c", 0.5), ("s", 0.6)] * 3, 0.9, -1.0)
        l_one = label("TP = 8: 13.4 requests/s", 18, HOT).next_to(s_one, RIGHT, buff=0.25)
        self.play(Create(one), FadeIn(s_one), FadeIn(l_one))
        self.next_slide("""Here is the decision that matters on an eight-GPU host. One engine at tensor parallel eight is the obvious
        layout: every GPU works on every request. Its step timeline is compute, sync, compute, sync.""")
        two = VGroup(SurroundingRectangle(VGroup(*g8[:4]), color=OUTPUT, buff=0.1), SurroundingRectangle(VGroup(*g8[4:]), color=OUTPUT, buff=0.1))
        s_two_a, _ = timeline([("c", 1.0), ("s", 0.6)] * 2, 0.9, -1.65)
        s_two_b, _ = timeline([("c", 1.0), ("s", 0.6)] * 2, 0.9, -2.15)
        l_two = label("2 × TP = 4: 22.5 requests/s", 18, OUTPUT).next_to(s_two_a, RIGHT, buff=0.25)
        self.play(ReplacementTransform(one, two), FadeIn(s_two_a), FadeIn(s_two_b), FadeIn(l_two))
        self.finish("""The alternative: two independent engines, each at tensor parallel four, behind the load balancer. Each does more arithmetic per step and synchronises across four GPUs instead of eight, and the two never wait for each other. Same model, same hardware, same load: 22.5 requests per second against 13.4. Sixty-eight percent more work from the same eight GPUs, by dividing them differently. The rule that falls out: use the smallest tensor-parallel degree at which the model fits, and spend the rest of
        the GPUs on more engines. One practical trap: block-quantised fp8 checkpoints refuse degrees that would split an
        expert's 128-wide tiles, so this 235B model would not start at TP=8 without expert parallelism. The engine tells you;
        the docs record which combinations ran.""")
