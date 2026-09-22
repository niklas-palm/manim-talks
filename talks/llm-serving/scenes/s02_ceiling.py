"""Move 1b: the two words the rest of the talk uses, latency and throughput, and the ceiling anyone can compute for
the first from two spec-sheet numbers. One picture: the GPU on the left, named; the model on the right, named; the
division between them; the measured number under it. Each click changes one thing, slowly. No caption: the numbers
carry their own names, and the two definitions stay on screen once they appear."""
from lib.palette import *
from objects import *

XR = 0.0   # left edge of the right-hand column, on the centre grid line


TITLE_CEILING = ("GPU latency and throughput", "1  two jobs, two costs")


def start_ceiling(scene, add: bool = True) -> dict:
    """The still this scene opens on, and that Mechanics hands over to: the card named, the model named, both gauges
    of the argument. Built identically on both sides of the seam."""
    gpu = GPU("one GPU", w=4.6, weights_gb=32).scale(0.85).shift(LEFT * 3.2 + UP * 0.2)
    gauge_at(gpu.bandwidth, 0.97)
    card = label("RTX PRO 6000 Blackwell Server Edition (g7e): 96 GB GDDR7", 14, MUTED, width=3.6).next_to(gpu, DOWN, buff=0.15)
    bw = Counter("memory bandwidth", 1.6, "TB/s", OUTPUT, decimals=2).move_to([3.2, 1.3, 0], aligned_edge=LEFT)
    mk = label("model", 13, MUTED).move_to([XR, 2.35, 0], aligned_edge=LEFT)
    mname = label("dense, 32B parameters, fp8: one byte per weight", 17, TEXT).move_to([XR, 2.0, 0], aligned_edge=LEFT)
    by = Counter("bytes read per token", 32, "GB", WEIGHTS).move_to([XR, 1.3, 0], aligned_edge=LEFT)
    parts = dict(gpu=gpu, card=card, bw=bw, mk=mk, mname=mname, by=by)
    parts["shown"] = list(parts.values())
    if add:
        scene.add(*parts["shown"])
    return parts


class DecodeCeiling(TalkSlide):
    def construct(self):
        # --- the last frame of Mechanics is this still; nothing animates until the first click
        t = title_still(self, *TITLE_CEILING)
        p = start_ceiling(self)
        gpu, card, bw, mk, mname, by = p["gpu"], p["card"], p["bw"], p["mk"], p["mname"], p["by"]
        # --- the division
        bar = Line(LEFT * 1.2, RIGHT * 1.2, color=TEXT).move_to([1.2, 0.0, 0])   # from the column line; the '=' after it stays clear of the result's digits
        num = label("1.6 TB/s", 24, OUTPUT).next_to(bar, UP, buff=0.1)
        den = label("32 GB per token", 24, WEIGHTS).next_to(bar, DOWN, buff=0.1)
        eq = label("=", 30, TEXT).next_to(bar, RIGHT, buff=0.3)
        res = Counter("fastest one request can decode", 50, "tokens/s", TEXT).move_to([3.2, 0.0, 0], aligned_edge=LEFT)
        lat = Counter("between two of its tokens", 20, "ms", TEXT, size=22, decimals=1).move_to([3.2, -1.3, 0], aligned_edge=LEFT)
        self.play(Create(bar), FadeIn(num), FadeIn(den), run_time=0.6)
        self.play(FadeIn(eq), FadeIn(res), FadeIn(lat), run_time=0.8)
        self.next_slide("""RTX PRO 6000 Blackwell Server Edition, 96 GB GDDR7: the GPU in a g7e instance. Two words for the rest of the talk. Latency is how fast one request gets its tokens; throughput is how many tokens
        the whole GPU produces per second for everyone. Start with latency, because it has a ceiling anyone can compute
        before renting anything, from two numbers. The card: this is the RTX PRO 6000 Blackwell Server Edition, the GPU inside
        a g7e instance, 96 GB of GDDR7, and its spec sheet says it moves 1.6 terabytes per second; the 1.8 often quoted is the
        workstation card. The model: a dense 32B in fp8 reads every weight for every token, 32 GB. Divide, and no request on
        this card can decode faster than 50 tokens per second, 20 milliseconds between tokens, whatever the software does. Do
        this division for any model you are considering; it is the per-user speed limit in ten seconds.""")
        # --- this talk's model
        mname2 = label("mixture of experts, 30B parameters, 3B active, fp8", 17, TEXT).move_to(mname, aligned_edge=LEFT)
        den2 = label("3 GB per token", 24, WEIGHTS).move_to(den)
        self.play(FadeOut(mname), FadeIn(mname2), FadeOut(den), FadeIn(den2), gpu.set_weights(29), run_time=1.0)
        self.play(by.to(3), res.to(530), lat.to(1.9), run_time=2.0)
        self.next_slide("""The model this talk measures is built differently: 30B weights in total, but only about 3B of them are read for
        any one token. How it manages that is knob two, later; for now take the number. 3 GB per token against the same 1.6
        terabytes per second gives about 530 tokens per second for one request, under two milliseconds between tokens. Ten
        times the dense ceiling, from the same card, because the token reads a tenth of the bytes.""")
        # --- measured, and the two words on screen
        meas = Counter("measured, one request alone", 175, "tokens/s", HOT).move_to([XR, -1.3, 0], aligned_edge=LEFT)
        mlat = label("5.7 ms between tokens; a third of the ceiling", 15, MUTED).next_to(meas, DOWN, buff=0.1).align_to(meas, LEFT)
        d1 = label("latency: the time between one request's tokens. Here 5.7 ms.", 18, MUTED).move_to([-6.4, -2.6, 0], aligned_edge=LEFT)
        d2 = label("throughput: tokens per second from the whole GPU. Here 175.", 18, MUTED).move_to([-6.4, -2.95, 0], aligned_edge=LEFT)
        self.play(FadeIn(meas), FadeIn(mlat), gpu.bandwidth.set(0.39), run_time=1.0)
        self.play(FadeIn(d1), FadeIn(d2), run_time=0.6)
        self.next_slide("""throughput: tokens per second from the whole GPU. Here 175: with one request, the two are the same number. Measured alone, the same request decodes at about 175 tokens per second, 5.7 milliseconds between tokens, a third
        of its ceiling. The gap is overhead per step: a few hundred kernel launches, the scheduler, the expert router, none of
        which is bandwidth. Watch the gauge: we measured the memory controller busy 39 percent of the time with one request
        in flight; the rest of the time the bus is idle. Now the two words, written down. Latency: 5.7 milliseconds between
        this request's tokens. Throughput: 175 tokens per second from the whole GPU, and with one request that is the same
        number, because one request is all there is. Hold on to the idle bus.""")
        # --- the other card
        card2 = label("H100 SXM, 80 GB HBM3: the GPU in a p5 instance", 14, MUTED, width=3.9).move_to(card, aligned_edge=UP)
        num2 = label("3.35 TB/s", 24, OUTPUT).move_to(num)
        mem2 = label("memory 80 GB", 15, DIM).move_to(gpu.mem_label, aligned_edge=LEFT)
        dense2 = label("the dense 32B on the H100: 105 tokens/s", 15, MUTED).move_to([XR, -1.95, 0], aligned_edge=LEFT)
        meas2 = label("measured, eight in flight: 67 tokens/s each here, 102 on the H100", 15, MUTED).next_to(dense2, DOWN, buff=0.1).align_to(dense2, LEFT)
        self.play(FadeOut(card), FadeIn(card2), FadeOut(num), FadeIn(num2), Transform(gpu.mem_label, mem2), gpu.set_weights(29 * 96 / 80),
                  FadeOut(meas), FadeOut(mlat), gpu.bandwidth.set(0.97), run_time=1.0)
        self.play(bw.to(3.35), res.to(1120), lat.to(0.9), run_time=2.0)
        self.play(FadeIn(dense2), FadeIn(meas2), run_time=0.6)
        self.next_slide("""The same division on a different card, because the card is half the answer. The H100 in a p5 instance moves 3.35 terabytes per second, twice this card's 1.6, so both ceilings double: 105 tokens per second for the dense 32B, about 1,120 for this model, under a millisecond between tokens. That is what hardware buys, and it is the only thing that raises this line; no engine setting does. Then the measurement, the other half. At eight requests in flight this model decoded at 67 tokens per second per request here and 102 on the H100; the dense 27B in fp8 went from 35 to 54. Half again on both, not twice: part of every step is overhead that bandwidth does not shrink, and the faster the bus, the larger that part's share. How large depends on the kernel the engine picks for the model, and that showed when a fourth family was measured on the same two cards: twice the bandwidth bought 26 percent on this model, 20 to 58 percent on a dense 31B, and nothing on a mixture of experts whose wide attention heads forced both cards onto the same slow kernel. The card sets the ceiling; the kernel decides how close a model gets, and the engine's startup log names the kernel it chose. So: the card sets the latency ceiling. Throughput is a different question, and one request answers it badly, with the bus idle most of the time. The engine's knob between the two words is the batch, and that is the next step.""")
        # --- hand-over: the ceiling gives way to the timeline of steps; the title changes with it
        from s03_batching import start_batching, TITLE_BATCHING
        nxt = start_batching(self, add=False)
        t = handover(self, t, *TITLE_BATCHING, leaving=[gpu, card2, bw, mk, mname2, by, bar, num2, den2, eq, res, lat, dense2, meas2, d1, d2], arriving=nxt["shown"])
        self.finish("""The picture becomes a timeline: a time axis, one decode step after another from left to right; a row for the weights read and a row for one request; two counters, weights read per step and tokens produced per step, both at one. Nothing moves yet.""")
