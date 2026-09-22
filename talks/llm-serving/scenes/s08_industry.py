"""Move 7: where the industry is. The two-phase pipeline from move 1, redrawn, with each live front placed on the part
of it that it attacks. Then the spine, then the close."""
from lib.palette import *
from objects import *


TITLE_IND = ("Where this is going", "7  where the industry is")
TITLE_CLOSE = ("Five things to take home", "close")


def two_phases() -> VGroup:
    """The prefill box, the decode box with its loop, and the arrow between: the picture every engine shares."""
    pre = box(3.0, 1.3, "prefill", PROMPT, size=24).shift(LEFT * 2.8 + UP * 1.2)
    dec = box(3.0, 1.3, "decode", OUTPUT, size=24).shift(RIGHT * 2.8 + UP * 1.2)
    arrow = Arrow(pre[0].get_right(), dec[0].get_left(), buff=0.05, color=DIM)
    loop = CurvedArrow(dec[0].get_center() + RIGHT * 0.6, dec[0].get_center() + LEFT * 0.6, angle=-TAU / 3, color=OUTPUT, stroke_width=sw(0.8), tip_length=0.15)   # the loop inside its box, under the name
    return VGroup(pre, dec, arrow, loop)


def start_industry(scene, add: bool = True) -> dict:
    grp = two_phases()
    pre, dec, arrow, loop = grp
    cap = pin(scene, label("Every engine is a batching scheduler over these two phases", 22, color=CAPTION, width=12.8, thread=True), buff=0.3)
    parts = dict(pre=pre, dec=dec, arrow=arrow, loop=loop, cap=cap); parts["shown"] = [pre, dec, arrow, loop, cap]
    if add:
        scene.add(*parts["shown"])
    return parts


def start_close(scene, add: bool = True) -> dict:
    """The still Close opens on: the two phases as Industry left them (pushed apart), small, at the top."""
    grp = two_phases()
    pre, dec, arrow, loop = grp
    pre.shift(LEFT * 0.4); dec.shift(RIGHT * 0.4); arrow.put_start_and_end_on(pre[0].get_right() + LEFT * 0.4, dec[0].get_left() + RIGHT * 0.4)
    loop.shift(RIGHT * 0.4)
    grp.scale(0.6).move_to([0, 2.0, 0])
    parts = dict(phases=grp); parts["shown"] = [grp]
    if add:
        scene.add(*parts["shown"])
    return parts


class Industry(TalkSlide):
    def construct(self):
        t = title_still(self, *TITLE_IND)
        p = start_industry(self)
        pre, dec, arrow, loop, cap = p["pre"], p["dec"], p["arrow"], p["loop"], p["cap"]
        def front(name, what, color, pos):
            g = VGroup(label(name, 20, color), label(what, 15, TEXT, width=4.2)).arrange(DOWN, aligned_edge=LEFT, buff=0.04).move_to(pos, aligned_edge=LEFT)
            self.play(FadeIn(g, shift=UP * 0.12), run_time=0.5)
            return g
        f1 = front("disaggregated serving", "prefill and decode on separate pools, each sized and tuned for its own gauge", PROMPT, LEFT * 4.7 + DOWN * 0.15)
        self.play(pre.animate.shift(LEFT * 0.4), dec.animate.shift(RIGHT * 0.4), loop.animate.shift(RIGHT * 0.4), arrow.animate.put_start_and_end_on(pre[0].get_right() + LEFT * 0.4, dec[0].get_left() + RIGHT * 0.4), run_time=0.6)
        self.next_slide("""Disaggregated serving pulls the two phases onto different pools of GPUs: prefill on hardware and settings chosen
        for compute, decode on hardware and settings chosen for bandwidth, with the KV cache handed across between them. It is
        the logical end of the two-gauge picture, and the orchestration layers built for large fleets, NVIDIA Dynamo and llm-d
        among them, are organised around it. Be precise about what it buys: the engine projects say it does not raise throughput
        per GPU by itself; it lets time-to-first-token and time-per-token be tuned independently and stops a long prefill from
        stalling everyone's decode. For a homogeneous single-GPU fleet at moderate prompt lengths the transfer costs more than
        it saves, which is why our stack does not do it.""")
        f2 = front("caches with an address", "routers that know which engine holds which blocks; tiers where evicted blocks live on", PROMPT, LEFT * 4.7 + DOWN * 1.3)
        self.next_slide("""The cache stops being one engine's private memory. Routers that score engines by the blocks they hold and the
        depth of their queue are now standard parts of the fleet layer, the grown-up version of the session cookie from knob
        three, and the vendors report time-to-first-token roughly halved on conversational traffic. Behind them, tiers: the
        engines now ship frameworks that spill evicted blocks to host memory, local disk, object stores and other nodes, and
        pull them back on a hit. Knob three's measurement is the caution to carry into that world: a tier pays only when it is
        sized to the working set that comes back.""")
        f6 = front("sparse attention", "a token reads only a chosen part of the cache, so the read stops growing with context", PROMPT, LEFT * 4.7 + DOWN * 2.45)
        self.next_slide("""The third front on this side attacks the read that grew with every token in move one. Sparse attention lets a
        token score a selected subset of the cached keys instead of all of them, and the newest large models ship with it
        built in; the engines have separate prefill and decode paths for it. If it holds up in quality, the cache read stops
        being the thing that fills the bus at long context, and long conversations get much cheaper to hold.""")
        f3 = front("speculative decoding", "a small draft proposes several tokens, the big model verifies them in one step", OUTPUT, RIGHT * 1.7 + DOWN * 0.15)
        self.next_slide("""Speculative decoding attacks the decode loop directly. A small draft proposes several tokens; the big model checks
        them all in one step, one read of the weights for several tokens, like a batch of one request with itself. The drafts
        have become cheaper and more parallel, several tokens drafted at once rather than one after another. Measured here with
        a separate draft model: 24 to 41 percent more tokens per second, most on a lightly loaded engine and least at the prefill
        knee, where verifying the drafts competes with prefill for the compute. Then a publisher's own drafter, four layers that
        share the target's cache, on a dense 12B: twice the tokens per second for one request, plus 88 percent at eight in flight,
        plus 32 at 64, and no level lost; plus 51 percent at 64 in flight on a 26B mixture of experts. So the condition is not
        light load but a decode-bound fleet, and where decode is the wall this is the first setting to turn on. It has stopped
        being a frontier and become a knob.""")
        f4 = front("4-bit, two ways", "native FP4 arithmetic on Blackwell, or weights unpacked to bf16: pick by the wall you are at", OUTPUT, RIGHT * 1.7 + DOWN * 1.3)
        f5 = front("reasoning effort", "tokens per answer becomes the capacity setting: 1.7 to 3.8 times", OUTPUT, RIGHT * 1.7 + DOWN * 2.45)
        self.next_slide("""Two more on the decode side. Four-bit weights are two different products. A weight-only kernel unpacks int4 to bf16 and multiplies at the bf16 rate: half the bytes again, so one request decoded 48 to 58 percent faster than in fp8, and prefill fell back to the bf16 rate, half of fp8's. Blackwell GPUs also compute in four-bit floating point natively, with a scale per block of sixteen values, so NVFP4 keeps fp8's arithmetic rate and cuts the bytes: another 25 percent here on one dense model, and nothing over fp8 on a mixture of experts with narrow experts. So pick a 4-bit checkpoint by the wall you are at and by the kernel the startup log names, not by the bit count; what the two cost in answers was the same, the half point to two from move five, calibrated build or not. And reasoning models turn the number of tokens per answer into a knob, effort, which changes capacity by 1.7 to 3.8 times, more than any flag on the engine. Back to the spine: a model reads your prompt once and then writes one token at a time, and every item on this slide is an attack on one of those two costs.""")
        # --- hand-over: the fronts fade, the two phases shrink to the top, and the close begins on them
        grp = VGroup(pre, dec, arrow, loop)
        t = retitle(self, t, *TITLE_CLOSE, extra=[FadeOut(VGroup(f1, f2, f6, f3, f4, f5, cap)), grp.animate.scale(0.6).move_to([0, 2.0, 0])], run_time=1.2)
        self.finish("""The picture hands over. The fronts fade and the two phases shrink to the top: five things to take home, each a measurement rather than an opinion.""")


class Close(TalkSlide):
    def construct(self):
        t = title_still(self, *TITLE_CLOSE)
        start_close(self)
        lines = ["Measure one engine before sizing anything.",
                 "fp8 weights and fp8 cache: no measured cost, twice the work per GPU.",
                 "Smallest degree that fits, then replicas; NVLink below the knee excepted.",
                 "Route conversations home; a cache tier pays only if it outsizes the churn.",
                 "Score your own task, against your own baseline, knowing the noise."]
        col = VGroup(*[label(s, 28, TEXT) for s in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.35).shift(DOWN * 0.35)
        for l in col:
            self.play(FadeIn(l, shift=UP * 0.12), run_time=0.5)
        self.next_slide("""Five things to take home, each of them a measurement rather than an opinion.""")
        foot = label("Every number in this talk is in the repository, with its conditions", 20, DIM).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(foot))
        self.finish("""Every number in this talk is in the repository, with the conditions it was measured under. The repository has the stack, the measurements as data, and the tuning document that explains each one.
        Nothing here needs to be believed; all of it can be re-run.""")
