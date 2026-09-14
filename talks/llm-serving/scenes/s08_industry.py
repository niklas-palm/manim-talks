"""Move 7: where the industry is. The two-phase pipeline from move 1, redrawn, with each live front placed on the part
of it that it attacks. Then the spine, then the close."""
from lib.palette import *
from objects import *


class Industry(TalkSlide):
    def construct(self):
        t = title(self, "Where this is going", "7  where the industry is")
        pre = box(3.0, 1.1, "prefill", PROMPT, size=24).shift(LEFT * 3.6 + UP * 1.2)
        dec = box(3.0, 1.1, "decode", OUTPUT, size=24).shift(RIGHT * 0.2 + UP * 1.2)
        arrow = Arrow(pre[0].get_right(), dec[0].get_left(), buff=0.05, color=DIM)
        loop = CurvedArrow(dec[0].get_bottom() + RIGHT * 0.6, dec[0].get_bottom() + LEFT * 0.6, angle=-TAU / 3, color=OUTPUT, stroke_width=2, tip_length=0.15)
        self.play(FadeIn(pre), FadeIn(dec), Create(arrow), Create(loop))
        cap = caption(self, "Every engine is a batching scheduler over these two phases")
        self.next_slide("""vLLM, SGLang, TensorRT-LLM: different code, the same shape. A prefill phase, a decode loop, a scheduler that
        decides which requests share each step. The frontier is not a new shape; it is a list of attacks on the two costs we
        started with. Here are the five that matter this year, placed on the part of the pipeline they attack.""")
        def front(name, what, color, pos):
            g = VGroup(label(name, 20, color), label(what, 15, TEXT, width=3.6)).arrange(DOWN, aligned_edge=LEFT, buff=0.04).move_to(pos, aligned_edge=LEFT)
            self.play(FadeIn(g, shift=UP * 0.12), run_time=0.5)
            return g
        f1 = front("disaggregated serving", "prefill and decode on separate pools, each sized and tuned for its own gauge", PROMPT, LEFT * 5.1 + DOWN * 0.15)
        self.play(pre.animate.shift(LEFT * 0.4), dec.animate.shift(RIGHT * 0.4), arrow.animate.put_start_and_end_on(pre[0].get_right() + LEFT * 0.4, dec[0].get_left() + RIGHT * 0.4), run_time=0.6)
        self.next_slide("""Disaggregated serving pulls the two phases onto different pools of GPUs: prefill on hardware and settings chosen
        for compute, decode on hardware and settings chosen for bandwidth, with the KV cache handed across between them. It is
        the logical end of the two-gauge picture, and the orchestration layers built for large fleets, NVIDIA Dynamo and llm-d
        among them, are organised around it. Be precise about what it buys: the engine projects say it does not raise throughput
        per GPU by itself; it lets time-to-first-token and time-per-token be tuned independently and stops a long prefill from
        stalling everyone's decode. For a homogeneous single-GPU fleet at moderate prompt lengths the transfer costs more than
        it saves, which is why the companion stack does not do it.""")
        f2 = front("caches with an address", "routers that know which engine holds which blocks; tiers where evicted blocks live on", PROMPT, LEFT * 5.1 + DOWN * 1.3)
        self.next_slide("""The cache stops being one engine's private memory. Routers that score engines by the blocks they hold and the
        depth of their queue are now standard parts of the fleet layer, the grown-up version of the session cookie from knob
        three, and the vendors report time-to-first-token roughly halved on conversational traffic. Behind them, tiers: the
        engines now ship frameworks that spill evicted blocks to host memory, local disk, object stores and other nodes, and
        pull them back on a hit. Knob three's measurement is the caution to carry into that world: a tier pays only when it is
        sized to the working set that comes back.""")
        f6 = front("sparse attention", "a token reads only a chosen part of the cache, so the read stops growing with context", PROMPT, LEFT * 5.1 + DOWN * 2.45)
        self.next_slide("""The third front on this side attacks the read that grew with every token in move one. Sparse attention lets a
        token score a selected subset of the cached keys instead of all of them, and the newest large models ship with it
        built in; the engines have separate prefill and decode paths for it. If it holds up in quality, the cache read stops
        being the thing that fills the bus at long context, and long conversations get much cheaper to hold.""")
        f3 = front("speculative decoding", "a small draft proposes several tokens, the big model verifies them in one step", OUTPUT, RIGHT * 1.7 + DOWN * 0.15)
        self.next_slide("""Speculative decoding attacks the decode loop directly. A small draft proposes several tokens; the big model checks
        them all in one step, one read of the weights for several tokens, like a batch of one request with itself. The drafts
        have become cheaper and more parallel, several tokens drafted at once rather than one after another. Measured here: 24
        to 41 percent more tokens per second on a lightly loaded engine, fading to nothing under heavy load, because a full
        batch already uses the read; the engine documentation says the same, high gain at low load, medium at best when busy.""")
        f4 = front("4-bit as arithmetic", "Blackwell computes in NVFP4 natively; 4-bit stops being a decompression trick", OUTPUT, RIGHT * 1.7 + DOWN * 1.3)
        f5 = front("reasoning effort", "tokens per answer becomes the capacity setting: 1.7 to 3.5 times", OUTPUT, RIGHT * 1.7 + DOWN * 2.45)
        self.finish("""Two more on the decode side. Blackwell GPUs compute in four-bit floating point natively, with a scale per block of
        sixteen values, so NVFP4 weights stop being something the kernel decompresses and become something it multiplies:
        another 25 percent here, and the vendor's own numbers put the accuracy cost within a point of fp8 when the build is
        calibrated, which is exactly the caveat move five ended on. And reasoning models turn the number of tokens per answer
        into a knob, effort, which changes capacity by 1.7 to 3.5 times, more than any flag on the engine. Back to the spine:
        a model reads your prompt once and then writes one token at a time, and every item on this slide is an attack on one
        of those two costs.""")


class Close(TalkSlide):
    def construct(self):
        lines = ["Measure one engine before sizing anything.",
                 "fp8 weights and fp8 cache: no measured cost, twice the work per GPU.",
                 "Smallest degree that fits, then replicas.",
                 "Route conversations home; a cache tier pays only if it outsizes the churn.",
                 "Score your own task, against your own baseline, knowing the noise."]
        col = VGroup(*[label(s, 28, TEXT) for s in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.35).shift(UP * 0.3)
        for l in col:
            self.play(FadeIn(l, shift=UP * 0.12), run_time=0.5)
        self.next_slide("""Five things to take home, each of them a measurement rather than an opinion.""")
        foot = label("Every number in this talk is in the repository, with its conditions", 20, DIM).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(foot))
        self.finish("""Every number in this talk is in the repository, with the conditions it was measured under. The repository has the stack, the measurements as data, and the tuning document that explains each one.
        Nothing here needs to be believed; all of it can be re-run.""")
