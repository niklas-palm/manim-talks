"""Move 5: what quantisation costs in answers, from the mechanism to the measurement. First the mechanism: a weight is a
number; fewer bits means fewer levels it can take; every weight moves a little; every score moves a little; where two
choices were close the pick flips, where one was sure nothing happens. Then the measurement: a grid of one hundred scored
items shows flip rates, first for two identical deployments (the noise floor), then for each precision against bf16.
Green dots got better, red got worse, grey did not change."""
from lib.palette import *
from objects import *
import random

W_VALUE = 0.7342


def flip(scene, grid, gains: int, losses: int, seed: int, run_time: float = 1.2):
    """Colour `gains` dots green and `losses` red at random positions; returns the chosen indices."""
    rnd = random.Random(seed)
    idx = rnd.sample(range(len(grid)), gains + losses)
    anims = [grid[i].animate.set_color(CACHE) for i in idx[:gains]] + [grid[i].animate.set_color(HOT) for i in idx[gains:]]
    scene.play(LaggedStart(*anims, lag_ratio=0.03), run_time=run_time)
    return idx


def reset(scene, grid, idx):
    scene.play(*[grid[i].animate.set_color(DIM) for i in idx], run_time=0.4)


def levels_row(x0: float, length: float, y: float, n: int, name: str) -> VGroup:
    """The values a weight can take between 0 and 1 at one precision: n tick marks along a line, or a solid band when
    there are too many to draw."""
    line = Line([x0, y, 0], [x0 + length, y, 0], color=DIM, stroke_width=1.5)
    if n > 512:
        ticks = Rectangle(width=length, height=0.16, fill_color=WEIGHTS, fill_opacity=0.55, stroke_width=0).move_to(line)
    else:
        ticks = VGroup(*[Line([x0 + length * i / n, y - 0.08, 0], [x0 + length * i / n, y + 0.08, 0], color=WEIGHTS, stroke_width=1.6 if n <= 16 else 1.0) for i in range(n + 1)])
    lab = label(name, 15, DIM).next_to(line, UP, buff=0.08).align_to(line, LEFT)
    return VGroup(line, ticks, lab)


def bars(heights, x: float, y: float, color: str = OUTPUT, op: float = 0.9, outline: bool = False) -> VGroup:
    g = VGroup()
    for h in heights:
        if outline:
            g.add(Rectangle(width=0.28, height=max(0.03, h), stroke_color=TEXT, stroke_width=1.5, fill_opacity=0))
        else:
            g.add(Rectangle(width=0.28, height=max(0.03, h), fill_color=color, fill_opacity=op, stroke_width=0))
    return g.arrange(RIGHT, buff=0.08, aligned_edge=DOWN).move_to([x, y, 0], aligned_edge=DOWN)


def pick(bs, color: str) -> Triangle:
    top = max(bs, key=lambda b: b.height)
    return Triangle(color=color, fill_color=color, fill_opacity=1, stroke_width=0).scale(0.09).rotate(PI).next_to(top, UP, buff=0.06)


TITLE_ROUNDING = ("What rounding a weight does to an answer", "5  what precision costs in answers")
TITLE_NOISE = ("Before any number: two identical deployments differ", "5  what precision costs in answers")
TITLE_PRECISION = ("What each precision costs, against its own bf16", "5  what precision costs in answers")


def start_rounding(scene, add: bool = True) -> dict:
    mat = VGroup(*[Square(0.3, fill_color=WEIGHTS, fill_opacity=0.6, stroke_width=0) for _ in range(64)]).arrange_in_grid(rows=8, cols=8, buff=0.04).move_to([-4.7, 1.4, 0])
    ml = label("a weight matrix: numbers, stored in 16 bits each", 15, DIM).next_to(mat, DOWN, buff=0.12)
    parts = dict(mat=mat, ml=ml); parts["shown"] = [mat, ml]
    if add:
        scene.add(*parts["shown"])
    return parts


def start_noise(scene, add: bool = True) -> dict:
    grid = dot_grid(100, 20).shift(UP * 0.3)
    gl = label("100 benchmark questions, one dot each, scored right or wrong", 18, DIM).next_to(grid, UP, buff=0.25)
    legend = VGroup(VGroup(Dot(color=CACHE, radius=0.09), label("answer changed from wrong to right", 15, DIM)).arrange(RIGHT, buff=0.12),
                    VGroup(Dot(color=HOT, radius=0.09), label("answer changed from right to wrong", 15, DIM)).arrange(RIGHT, buff=0.12)).arrange(RIGHT, buff=0.6).next_to(grid, DOWN, buff=0.3)
    parts = dict(grid=grid, gl=gl, legend=legend); parts["shown"] = [grid, gl, legend]
    if add:
        scene.add(*parts["shown"])
    return parts


def start_precision(scene, add: bool = True) -> dict:
    grid = dot_grid(100, 20).shift(UP * 0.3)
    gl = label("the same 100 questions; a coloured dot is an answer that changed", 18, DIM).next_to(grid, UP, buff=0.25)
    parts = dict(grid=grid, gl=gl); parts["shown"] = [grid, gl]
    if add:
        scene.add(*parts["shown"])
    return parts


class Rounding(TalkSlide):
    def construct(self):
        t = title_still(self, *TITLE_ROUNDING)
        p = start_rounding(self)
        mat, ml = p["mat"], p["ml"]
        one = mat[3 * 8 + 5]
        x0, length = -2.4, 7.0
        wx = x0 + length * W_VALUE
        self.play(one.animate.set_fill(OUTPUT, 1.0), run_time=0.4)
        val = label(f"one weight: {W_VALUE}", 20, OUTPUT).move_to([wx, 2.75, 0])
        self.play(FadeIn(val))
        self.next_slide("""Move one made the weights smaller and the fleet half the size. Now the question everyone held: what did that do
        to the answers? Start from what a weight is: a number, one of billions, stored in sixteen bits. Take one of them,
        0.7342. Quantisation stores it in fewer bits, and fewer bits means fewer values it is allowed to take.""")
        rows = [(65536, "16-bit: tens of thousands of levels between 0 and 1, more than can be drawn", 2.15, 0.0),
                (128, "8-bit: about 128 levels (drawn evenly; fp8 packs them closer near zero)", 1.3, 0.0002),
                (8, "4-bit: 8 levels", 0.45, 0.0158)]
        cap = caption(self, "Fewer bits, fewer levels: each weight moves to the nearest one")
        levels = VGroup()
        for n, name, y, err in rows:
            row = levels_row(x0, length, y, n, name)
            dot = Dot([wx, y, 0], color=OUTPUT, radius=0.07)
            self.play(FadeIn(row), FadeIn(dot), run_time=0.5)
            snapped = x0 + length * round(W_VALUE * n) / n
            seg = Line([wx, y, 0], [snapped, y, 0], color=HOT, stroke_width=4)
            el = label(f"error {err:.4f}", 16, HOT if err > 0.001 else DIM).move_to([5.9, y, 0])
            self.play(dot.animate.move_to([snapped, y, 0]), Create(seg), FadeIn(el), run_time=0.6)
            levels.add(row, dot, seg, el)
        self.next_slide("""Three precisions, one weight. In sixteen bits the allowed values are so dense, tens of thousands on this stretch, that the weight barely moves. In
        eight bits there are 128 levels on this stretch and it moves by two ten-thousandths. In four bits there are eight
        levels, and it moves by 0.016, two percent of its value. Real formats are smarter than this picture: they fit a scale to
        each small block of weights so the levels cover that block's range, and fp8 spaces its levels unevenly; the picture
        is the same. Fewer bits, coarser levels, larger rounding error per weight.""")
        rnd = random.Random(4)
        self.play(*[c.animate.set_fill(HOT if rnd.random() < 0.5 else CACHE, 0.35 + 0.45 * rnd.random()) for c in mat if c is not one], one.animate.set_fill(HOT, 0.8), run_time=1.0)
        cap = swap_caption(self, cap, "Every weight moves a little; every score moves a little")
        self.next_slide("""Every weight moves a little, up or down; every score the model computes moves a little. Now every weight in the matrix has done the same, each by its own small amount, some up, some down. A layer's
        output is a sum over thousands of these, so the errors partly cancel and partly do not: each output number is a little
        off, and after a hundred layers every score at the bottom, every next-token probability, has moved by a small random
        amount. That is the whole effect. What it does to an answer depends on how close the decision was.""")
        cap = swap_caption(self, cap, "Sure positions hold; close calls flip")
        sure = [0.15, 0.1, 1.5, 0.2, 0.12, 0.25, 0.08, 0.18, 0.1]
        close = [0.15, 0.1, 0.9, 0.2, 0.86, 0.25, 0.08, 0.18, 0.1]
        rnd = random.Random(9)
        wiggle = lambda hs: [max(0.03, h + rnd.uniform(-0.08, 0.08)) for h in hs]
        b1 = bars(sure, -3.6, -2.35)
        b2 = bars(close, 1.8, -2.35)
        l1 = label("a position the model is sure about", 15, DIM).next_to(b1, DOWN, buff=0.1)
        l2 = label("a close call", 15, DIM).next_to(b2, DOWN, buff=0.1)
        p1, p2 = pick(b1, OUTPUT), pick(b2, OUTPUT)
        self.play(FadeOut(val), FadeIn(b1), FadeIn(b2), FadeIn(l1), FadeIn(l2), FadeIn(p1), FadeIn(p2), run_time=0.7)
        q1 = bars(wiggle(sure), -3.6, -2.35, outline=True)
        q2h = wiggle(close); q2h[2], q2h[4] = 0.84, 0.91
        q2 = bars(q2h, 1.8, -2.35, outline=True)
        self.play(Create(q1), Create(q2), run_time=0.8)
        p3, p4 = pick(q1, TEXT), pick(q2, TEXT)
        self.play(FadeIn(p3), FadeIn(p4), run_time=0.4)
        # --- hand-over: one weight's story gives way to a hundred questions
        nxt = start_noise(self, add=False)
        t = handover(self, t, *TITLE_NOISE, leaving=[mat, ml, levels, b1, b2, l1, l2, p1, p2, q1, q2, p3, p4, cap], arriving=nxt["shown"])
        self.finish("""Where the model was sure, nothing changes. Where it was nearly undecided, the choice flips. Two positions in an answer. Left, the model is sure: one token far ahead, the shift moves the bars a little and the pick, the marker, stays. Right, a close call: two tokens nearly tied, the same small shift and the pick flips. So quantisation does not degrade every answer a little. It leaves the sure ones alone and re-decides the close ones, and one re-decided token early in an answer can send the rest of it elsewhere. The cost is a flip rate on the hard items, and it is exactly the kind of thing that must be measured rather than reasoned about. Which sets the terms for the next two scenes. We will score the same items on two deployments and count flips.
        But close calls flip for other reasons too: a different batch, a different summation order in a kernel. So before
        crediting any flip to precision we need to know how many flip when nothing changed at all. Then the picture hands over: 100 questions from a standard benchmark, each dot one question, scored right or wrong. One hundred items from a standard benchmark, each scored pass or fail, on a bf16 deployment. Now deploy the same model with the same settings a second time and score the same hundred items again. Nothing about the weights has changed.""")


class NoiseFloor(TalkSlide):
    def construct(self):
        t = title_still(self, *TITLE_NOISE)
        p = start_noise(self)
        grid, gl, legend = p["grid"], p["gl"], p["legend"]
        cap = caption(self, "The same model, deployed and scored a second time")
        idx = flip(self, grid, 2, 1, seed=1)
        gl2 = label("same model deployed twice: 3 of 100 changed, 2 to right, 1 to wrong", 18, TEXT).next_to(grid, UP, buff=0.25)
        self.play(FadeOut(gl), FadeIn(gl2))
        # --- hand-over: the same grid, cleared, ready to compare precisions
        nxt = start_precision(self, add=False)
        t = retitle(self, t, *TITLE_PRECISION, extra=[*[grid[i].animate.set_color(DIM) for i in idx], FadeOut(VGroup(gl2, cap, legend)), FadeIn(nxt["gl"])], run_time=1.2)
        self.finish("""the same model deployed twice: 3 of 100 answers changed, 2 to right, 1 to wrong. Three of a hundred change anyway. The close calls from the last scene flip on their own: a different batch composition changes a kernel's summation order, a near-tie breaks the other way, and a multi-step task ends somewhere else. How many flip depends on the task, and we measured it: about 3 percent on tool-calling tests, 2 on structured extraction, 12 on coding fixes, 27 on long agent tasks, where one different token early sends the whole trajectory elsewhere. This is the flip rate of nothing. So the rule for reading everything that follows. A difference smaller than the repeat spread is not a result.
        Per-item flips only mean something when gains and losses are unbalanced. And a baseline has to be run twice before
        it can be compared with anything; we did, for exactly this reason. Then the picture hands over: The still picture: the same hundred questions as the last scene, every dot grey, no answer changed yet. Each click from here compares one precision against the same model in bf16.""")


class PrecisionCost(TalkSlide):
    def construct(self):
        t = title_still(self, *TITLE_PRECISION)
        p = start_precision(self)
        grid, gl = p["grid"], p["gl"]
        cap = caption(self, "fp8 against bf16: 4 of 100 change, 2 each way: the noise floor")
        idx = flip(self, grid, 2, 2, seed=2)
        self.next_slide("""fp8 against bf16. Across three model families and several thousand items per task, about 4 percent of items
        change, and the gains equal the losses: on one 32B model, 84 items got better and 84 got worse. That is the noise floor
        from the last scene. It held on the standard question suites, on structured extraction, on tool calling, on coding
        fixes and on agent tasks: every aggregate inside the repeat spread, every flip balanced. Half the bytes per weight,
        the fleet halved, and no cost in answers that we could measure. This is why fp8 is the default and not a trade-off.""")
        reset(self, grid, idx)
        cap = swap_caption(self, cap, "Calibrated 4-bit: 6 to 10 of 100 change, 4 wrong per 3 right")
        idx = flip(self, grid, 3, 4, seed=3)
        self.next_slide("""Calibrated 4-bit: 6 to 10 of 100 change, 4 to wrong for every 3 to right. Four-bit weights are the first precision with a consistent cost, and it is the coarse levels from the rounding
        picture showing up. Six to ten percent of items change and the losses outnumber the gains about four to three: plus 123
        and minus 163 for one format, plus 114 and minus 167 for another, on the same model. In aggregates that is half a point
        to two points on the standard suite, 3 to 5 percent worse perplexity, about a point on tool calling. Small, real, and
        the same for every 4-bit format we tried. The format does not matter; the number of levels does.""")
        reset(self, grid, idx)
        cap = swap_caption(self, cap, "One community 4-bit build: 18 of 100 change, 3 wrong per 1 right", 22, HOT)
        idx = flip(self, grid, 4, 14, seed=4)
        # --- hand-over: from what one engine answers to how many engines you need
        from s07_fleet import start_fleet, TITLE_FLEET
        nxt = start_fleet(self, add=False)
        t = handover(self, t, *TITLE_FLEET, leaving=[grid, gl, cap], arriving=nxt["shown"])
        self.finish("""One community 4-bit build: 18 of 100 change, 3 to wrong for every 1 to right. One more, because it changes what you have to do. A 4-bit format has a scale per block of weights, fitted on a sample of text, and where the sample does not resemble the traffic the rounding errors land on the wrong weights. One community build of a coding model scored within a point of bf16 on extraction and on simple function calls, so on a chat leaderboard it looked fine. On multi-step tool use it lost 27 points of the ability to decline a tool call it should not make, and it resolved seven coding tasks where bf16 resolved 22. Eighteen percent of items flipped, three losses per gain. The same format from a publisher who calibrated it cost one point. The format is not the risk; the build is, and only a measurement on the task you will run tells them apart. Three habits, then. Score the checkpoint you will deploy, under the settings you will serve it with. Compare
        it with your own bf16 run, not with a published number. And score the task your traffic is, not a proxy: the broken
        build passed every proxy and failed the real work. Then the picture hands over: A fleet starts from one engine's measured rate, at your latency budget and prompt shape. Everything before this was one engine, and a fleet is built from one number about it: how many requests per second one engine sustains inside your latency budget, at your prompt shape. That number is the operating point on the batching curve from move two, and nothing about it can be looked up; it moves with the model, the prompt length and the budget. In the companion measurements it is about 16 requests per second, 16,000 input tokens per second, for 1,000-token prompts inside an 8-second p95. Take that as the worked example, not as a constant.""")
