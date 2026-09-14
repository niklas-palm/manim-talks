"""Move 3: three knobs that change how many bytes a decode step reads and how many requests fit. Each scene keeps a
bytes-per-step counter on screen, because bytes per step is the quantity that decides decode speed."""
from lib.palette import *
from objects import *


TITLE_Q = ("Knob one: quantisation, fewer bytes per weight", "3  three knobs: weights, experts, cache")
TITLE_MOE = ("Knob two: dense versus mixture of experts", "3  three knobs: weights, experts, cache")
TITLE_PREFIX = ("Knob three: reusing the KV cache, across turns and across engines", "3  three knobs: weights, experts, cache")


def start_quantisation(scene, add: bool = True) -> dict:
    """The still Quantisation opens on, and that Batching hands over to: the 96 GB card with the bf16 weights in it."""
    tt = label(TITLE_Q[0], 38, thread=True).to_edge(UP, buff=0.5)   # the title's geometry, to hang the strip under it
    strip = label("this talk's model: 30B mixture of experts, 3B active, 96 GB card", 16, MUTED).next_to(tt, DOWN, buff=0.12)
    gpu = GPU("one GPU, 96 GB", w=5.0, weights_gb=57).scale(0.92).shift(LEFT * 3.2 + DOWN * 0.3)
    cache_at(gpu, 30); gauge_at(gpu.bandwidth, 0.95)
    bytes_ = Counter("weights: 30B parameters, read per decode step", 57, "GB", WEIGHTS).move_to([0.0, 1.3, 0], aligned_edge=LEFT)
    bl = label("bf16: 2 bytes per weight", 15, MUTED).next_to(bytes_, DOWN, buff=0.1).align_to(bytes_, LEFT)
    fit = Counter("tokens of context in the cache, all requests", 330000, "", CACHE).move_to([0.0, 0.0, 0], aligned_edge=LEFT)
    fl = label("about 40 conversations of 8k tokens (96 KB of cache per token)", 15, MUTED).next_to(fit, DOWN, buff=0.1).align_to(fit, LEFT)
    rate = Counter("prompt tokens prefilled per second, measured", 7900, "", PROMPT).move_to([0.0, -1.3, 0], aligned_edge=LEFT)
    rl = label("one GPU, inside an eight-second latency budget", 15, MUTED).next_to(rate, DOWN, buff=0.1).align_to(rate, LEFT)
    parts = dict(strip=strip, gpu=gpu, bytes_=bytes_, bl=bl, fit=fit, fl=fl, rate=rate, rl=rl)
    parts["shown"] = list(parts.values())
    if add:
        scene.add(*parts["shown"])
    return parts


def start_moe(scene, add: bool = True) -> dict:
    """The still MixtureOfExperts opens on: the dense stack, its label and its bytes counter."""
    dense = VGroup(*[Rectangle(width=3.4, height=0.42, fill_color=WEIGHTS, fill_opacity=0.7, stroke_width=0) for _ in range(6)]).arrange(DOWN, buff=0.14).shift(LEFT * 3.2 + DOWN * 0.1)
    dl = label("dense, 32B parameters: every weight read for every token", 16, TEXT, width=4.4).next_to(dense, DOWN, buff=0.4)
    bytes_d = Counter("bytes read per token", 32, "GB", WEIGHTS).next_to(dense, UP, buff=0.35).align_to(dense, LEFT)
    parts = dict(dense=dense, dl=dl, bytes_d=bytes_d)
    parts["shown"] = list(parts.values())
    if add:
        scene.add(*parts["shown"])
    return parts


def start_prefix(scene, add: bool = True) -> dict:
    """The still PrefixCache opens on: the first turn of a conversation and the prefill counter."""
    l1 = label("turn 1: question, answer", 18, DIM).move_to([-6.4, 1.9, 0], aligned_edge=LEFT)
    turn1 = VGroup(tokens(6, PROMPT, side=0.5, gap=0.1), tokens(3, OUTPUT, side=0.5, gap=0.1)).arrange(RIGHT, buff=0.1).next_to(l1, RIGHT, buff=GAP_WIDE)
    prefill = Counter("tokens prefilled", 9, "", PROMPT).move_to([3.2, 1.9, 0], aligned_edge=LEFT)
    parts = dict(l1=l1, turn1=turn1, prefill=prefill)
    parts["shown"] = list(parts.values())
    if add:
        scene.add(*parts["shown"])
    return parts


class Quantisation(TalkSlide):
    def construct(self):
        t = title_still(self, *TITLE_Q)
        p = start_quantisation(self)
        strip, gpu, bytes_, bl, fit, fl, rate, rl = p["strip"], p["gpu"], p["bytes_"], p["bl"], p["fit"], p["fl"], p["rate"], p["rl"]
        bl2 = label("fp8: 1 byte per weight", 15, MUTED).move_to(bl, aligned_edge=LEFT)
        fl2 = label("about 80 conversations of 8k tokens (still 96 KB per token)", 15, MUTED).move_to(fl, aligned_edge=LEFT)
        self.play(gpu.set_weights(29), bytes_.to(29), FadeOut(bl), FadeIn(bl2), run_time=1.5)
        self.play(gpu.set_cache(60), fit.to(630000), FadeOut(fl), FadeIn(fl2), run_time=1.5)
        self.play(rate.to(16200), run_time=1.2)
        self.next_slide("""Store each weight in one byte instead of two. Every decode step now reads 29 GB instead of 57, so the
        bandwidth-bound loop runs nearly twice as fast, and the cache has about 58 GB instead of 30, so twice as many tokens
        of context fit, about 630,000. Both gauges of the talk move at once. Measured: 16,200 input tokens per second per GPU,
        twice the work per GPU, which is half the fleet for the same traffic. One config line.""")
        fl3 = label("about 160 conversations of 8k tokens (48 KB per token in fp8)", 15, MUTED).move_to(fl, aligned_edge=LEFT)
        kl = label("the cache has its own precision, set separately", 15, CACHE).next_to(gpu, DOWN, buff=0.12)
        self.play(gpu.cache.animate.set_fill(CACHE, 1.0), gpu.set_cache(60), fit.to(1270000), FadeOut(fl2), FadeIn(fl3), FadeIn(kl), run_time=1.5)
        self.next_slide("""The KV cache is a second, independent decision. Its entries can be stored in fp8 as well, which halves the bytes per cached token, 48 kilobytes instead of 96 for this model, so the same 58 GB holds about 1.27 million tokens; that last figure is what the engine reported at start on this card, the other two follow from the same arithmetic. On this GPU's attention kernels the fp8 cache also measured 12 percent faster decode. The two knobs are set separately and the right answer for one does not follow from the other: on H100s the same cache setting measured slower, because the kernels differ. The obvious question is what all this did to the answers. It gets its own move, five, because the answer has a mechanism worth seeing and a measurement worth trusting. The short version: fp8 costs nothing we could measure on any task; 4-bit costs a little, always. Hold the question until then.""")
        # --- hand-over: the weights bar grows into a stack of layers, the next knob's picture
        nxt = start_moe(self, add=False)
        wcopy = gpu.weights.copy()
        t = retitle(self, t, *TITLE_MOE, extra=[FadeOut(VGroup(strip, gpu, bytes_, bl2, fit, fl3, rate, rl, kl)), ReplacementTransform(wcopy, nxt["dense"]),
                                              FadeIn(nxt["dl"]), FadeIn(nxt["bytes_d"])], run_time=1.4)
        self.finish("""The picture hands over. The still picture: a dense model as a stack of six layers, each layer one solid block of weights, and a counter for the bytes a token reads on its way down: 32 GB, all of it. Nothing moves yet; the next click sends one token through.""")


class MixtureOfExperts(TalkSlide):
    def construct(self):
        t = title_still(self, *TITLE_MOE)
        p = start_moe(self)
        dense, dl, bytes_d = p["dense"], p["dl"], p["bytes_d"]
        tok = Square(0.42, fill_color=OUTPUT, fill_opacity=0.9, stroke_width=0).next_to(dense, UP, buff=0.08)
        self.play(FadeIn(tok, shift=DOWN * 0.2))
        for layer in dense:   # slowly: this is the first time a token passes a layer in this scene
            self.play(layer.animate.set_fill(OUTPUT, 1.0), tok.animate.move_to(layer.get_center()), run_time=0.35)
            self.play(layer.animate.set_fill(WEIGHTS, 0.7), run_time=0.15)
        self.play(tok.animate.next_to(dense, DOWN, buff=0.08), run_time=0.2)
        self.play(FadeOut(tok), run_time=0.15)
        self.next_slide("""A dense model reads all of itself for every token: the token passes down through every layer and every layer
        is read in full. A 32B model in fp8 is 32 GB per token, per decode step, whatever the token is about.""")
        layers = VGroup()
        for _ in range(6):
            layers.add(VGroup(*[Rectangle(width=0.37, height=0.42, fill_color=WEIGHTS, fill_opacity=0.35, stroke_width=0) for _ in range(8)]).arrange(RIGHT, buff=0.06))
        layers.arrange(DOWN, buff=0.14).shift(RIGHT * 3.2 + DOWN * 0.1)
        ml = label("mixture of experts, 30B: 128 experts per layer, 8 chosen (drawn 8, 2 chosen)", 15, TEXT, width=5.6).next_to(layers, DOWN, buff=0.4)
        bytes_m = Counter("bytes read per token", 3, "GB", CACHE).next_to(layers, UP, buff=0.35).align_to(layers, LEFT)
        used = Counter("experts read, this layer", 2, "of 8", CACHE, size=22).next_to(bytes_m, RIGHT, buff=GAP_WIDE).align_to(bytes_m, DOWN)
        self.play(FadeIn(layers), FadeIn(ml), FadeIn(bytes_m), FadeIn(used))
        import random
        random.seed(3)
        for _ in range(3):
            tok = Square(0.42, fill_color=OUTPUT, fill_opacity=0.9, stroke_width=0).next_to(layers, UP, buff=0.08)
            self.play(FadeIn(tok, shift=DOWN * 0.2), run_time=0.12)
            for row in layers:
                picks = random.sample(range(8), 2)
                self.play(*[row[j].animate.set_fill(OUTPUT, 1.0) for j in picks], tok.animate.move_to(row.get_center()), run_time=0.14)
                self.play(*[row[j].animate.set_fill(WEIGHTS, 0.35) for j in picks], run_time=0.07)
            self.play(tok.animate.next_to(layers, DOWN, buff=0.08), run_time=0.15)
            self.play(FadeOut(tok), run_time=0.1)
        self.next_slide("""mixture of experts, 30B parameters: each layer holds 128 experts, a router picks 8, so 3B are read (drawn as 8 experts with 2 chosen). A mixture of experts splits each layer's big feed-forward matrices into several smaller ones, the experts,
        and a router sends each token to a few of them; drawn here as eight experts with two chosen, where the real 30B model has 128
        per layer and routes eight. The token still passes down through every layer, but in each layer only
        two of eight experts light up. The 30B model has 3B active parameters: a token touches 3 GB of weights, not 30. Since
        decode is bound by bytes read, that is a tenfold cut in the thing that costs. A 30B mixture of experts decodes like a
        3B model and answers like a 30B one.""")
        key = label("a tenth of the bytes per token: ten times the decode ceiling", 17, MUTED).to_edge(DOWN, buff=0.55)
        self.play(FadeIn(key), run_time=0.5)
        self.next_slide("""same layers, same depth; a tenth of the bytes per token, so ten times the decode ceiling. So the two knobs so far both attack bytes per token: quantisation shrinks every weight, a mixture of experts
        reads fewer of them. Same depth, same stack of layers, a tenth of the bytes, ten times the decode ceiling from the last
        scene. That is why this talk's model is one. Now the catch.""")
        key2 = label("the catch: eight tokens pick seven of eight experts", 17, MUTED).move_to(key)
        self.play(FadeOut(key), FadeIn(key2), run_time=0.5)
        toks = VGroup(*[Square(0.37, fill_color=OUTPUT, fill_opacity=0.9, stroke_width=0) for _ in range(8)]).arrange(RIGHT, buff=0.06).next_to(layers, UP, buff=0.08)
        self.play(FadeIn(toks, shift=DOWN * 0.2), run_time=0.3)
        for row in layers:
            picks = random.sample(range(8), 7)
            self.play(*[row[j].animate.set_fill(OUTPUT, 1.0) for j in picks], toks.animate.move_to(row.get_center()), used.to(7), run_time=0.22)
        self.play(bytes_m.to(11), toks.animate.next_to(layers, DOWN, buff=0.08), run_time=0.6)
        self.play(FadeOut(toks), run_time=0.2)
        self.next_slide("""the catch: a batch of eight tokens picks seven of eight experts; under load most of the model is read anyway. The catch is the batch. Remember, the engine decodes many requests in one step. Eight tokens each pick their own two experts, and together they pick most of them: seven of eight per layer here, and the counter shows it. The step now reads eleven of the thirty gigabytes in the drawing, not three. On the real model, with 128 experts and eight chosen per token, a batch of 128 touches nearly all of them, and we measured it on the memory bus: at one request the memory controller is busy 39 percent of the time and the step reads about the active 3 GB; at 128 in flight it is busy 77 percent of the time and the step reads essentially all 29 GB. The mixture-of-experts advantage is large at low concurrency and shrinks as the batch grows. Size a fleet on the loaded number, never the batch-of-one number. Two knobs so far, both about bytes per step. The third is about not reading at all.""")
        # --- hand-over: the two stacks give way to a conversation's tokens, the third knob's picture
        nxt = start_prefix(self, add=False)
        t = handover(self, t, *TITLE_PREFIX, leaving=[dense, dl, bytes_d, layers, ml, bytes_m, used, key2], arriving=nxt["shown"])
        self.finish("""The picture hands over. The still picture: the first turn of a conversation, six prompt tokens in blue and three answer tokens in yellow, and a counter of tokens prefilled, nine. Where the attention state of those nine tokens went is the next click.""")


class PrefixCache(TalkSlide):
    def construct(self):
        t = title_still(self, *TITLE_PREFIX)
        p = start_prefix(self)
        l1, turn1, prefill = p["l1"], p["turn1"], p["prefill"]
        blocks = VGroup(*[RoundedRectangle(corner_radius=0.06, width=0.9, height=0.5, fill_color=CACHE, fill_opacity=0.85, stroke_width=0) for _ in range(3)]).arrange(RIGHT, buff=0.08).move_to([turn1.get_left()[0], -1.3, 0], aligned_edge=LEFT)
        bl = label("KV cache blocks, one engine", 16, CACHE).next_to(blocks, DOWN, buff=0.12)
        self.play(TransformFromCopy(turn1, blocks), FadeIn(bl), run_time=0.9)
        self.next_slide("""The first turn of a conversation: six prompt tokens, three answer tokens. Prefill read nine tokens and left
        their attention state in the cache, stored in fixed-size blocks and tagged by the tokens they hold.""")
        turn2 = VGroup(tokens(6, PROMPT, side=0.5, gap=0.1), tokens(3, OUTPUT, side=0.5, gap=0.1), tokens(4, PROMPT, side=0.5, gap=0.1)).arrange(RIGHT, buff=0.1).next_to(turn1, DOWN, buff=0.55).align_to(turn1, LEFT)
        l2 = label("turn 2: everything so far, plus the follow-up", 18, DIM).next_to(turn2, DOWN, buff=0.2).align_to(turn2, LEFT)
        self.play(FadeIn(turn2), FadeIn(l2))
        self.next_slide("""Turn two arrives carrying turn one inside it: the chat client resends the whole conversation plus the new
        question. Without help, prefill reads all thirteen tokens again. Nine of them the engine has already seen.""")
        pl = label("prefix caching: matching blocks reused, only new tokens prefilled", 16, CACHE).next_to(blocks, RIGHT, buff=0.6)
        match = SurroundingRectangle(VGroup(turn2[0], turn2[1]), color=CACHE, buff=0.06)
        arrows = VGroup(*[Line(match.get_bottom() + LEFT * 0.9 + RIGHT * 0.9 * i, b.get_top(), color=CACHE, stroke_width=1.5) for i, b in enumerate(blocks)])
        self.play(Create(match), Create(arrows), FadeIn(pl))
        self.play(prefill.to(4), Indicate(turn2[2], color=PROMPT))
        self.next_slide("""prefix caching: blocks whose tokens match are reused; only the new tokens are prefilled. Prefix caching hashes the incoming tokens block by block and matches them against blocks already in the
        cache. Nine tokens match, so prefill computes four. On a long conversation, a shared system prompt or a document that
        many users ask about, this removes most of the prefill work. It is on by default and costs about one percent when
        nothing matches. Measured with every prompt cached: plus 46 percent on short prompts, 2.7 times on 4,000-token ones.""")
        # routing
        self.play(FadeOut(match), FadeOut(arrows), FadeOut(pl), FadeOut(turn1), FadeOut(l1), FadeOut(turn2), FadeOut(l2), FadeOut(blocks), FadeOut(bl), FadeOut(prefill))
        q = label("many engines, each with its own cache: which one gets the next turn?", 17, TEXT).move_to([0, 2.4, 0])
        self.play(FadeIn(q), run_time=0.5)
        engines = VGroup(*[box(1.15, 1.6, f"{i+1}", WEIGHTS, size=18) for i in range(8)]).arrange(RIGHT, buff=0.22).shift(DOWN * 0.6)
        caches = VGroup(*[Rectangle(width=0.8, height=0.22, stroke_color=DIM, stroke_width=1.5, fill_opacity=0).move_to(e[0].get_bottom() + UP * 0.3) for e in engines])
        lb = box(2.8, 0.7, "load balancer", DIM, size=20).shift(UP * 1.4)
        hits = Counter("cache hit rate", 0, "%", CACHE).move_to([3.2, 1.4, 0], aligned_edge=LEFT)
        self.play(FadeIn(engines), FadeIn(caches), FadeIn(lb), FadeIn(hits))
        home = 2
        caches[home].set_fill(CACHE, 0.9)
        self.next_slide("""at scale: many engines, each with its own cache. Which engine gets the next turn?. Now the fleet. Eight engines, each with its own cache: the blocks of a conversation live in the engine that
        served its first turn, engine three here. The load balancer's job is to spread requests evenly. Those two facts collide.""")
        import random
        random.seed(11)
        rr = label("round robin: the next turn lands anywhere", 15, HOT).next_to(lb, DOWN, buff=0.1)
        self.play(FadeIn(rr), run_time=0.4)
        rate = 0
        for k, target in enumerate([5, 0, 7, home, 4, 1]):
            dot = Dot(color=PROMPT, radius=0.09).move_to(lb[0].get_bottom())
            self.play(dot.animate.move_to(caches[target].get_center()), run_time=0.35)
            hit = target == home
            rate = 21 if k >= 3 else rate + (21 if hit else 0)
            self.play(Flash(engines[target][0], color=CACHE if hit else HOT, flash_radius=0.6, num_lines=8), FadeOut(dot), hits.to(rate), run_time=0.3)
        self.next_slide("""Round robin sends each turn to the next engine in line, so a conversation's second turn finds its blocks
        about one time in eight, and the fraction falls as the fleet grows. Measured on eight engines with six-turn
        conversations: 21 percent of turns hit their cache. Most of the prefill work that caching should have saved was done
        again, on the wrong engine.""")
        st = label("a session cookie steers each conversation home: +14% throughput", 15, CACHE).move_to(rr)
        self.play(FadeOut(rr), FadeIn(st), run_time=0.4)
        for _ in range(4):
            dot = Dot(color=PROMPT, radius=0.09).move_to(lb[0].get_bottom())
            self.play(dot.animate.move_to(caches[home].get_center()), run_time=0.3)
            self.play(Flash(engines[home][0], color=CACHE, flash_radius=0.6, num_lines=8), FadeOut(dot), hits.to(75), run_time=0.3)
        self.next_slide("""The fix is not in the engine. A load balancer cookie pins each client's conversation to the engine that holds
        its blocks. Same engines, same cache, same model: 75 percent of turns hit, and the fleet served 14 percent more requests
        per second at lower latency. The lesson generalises: prefix caching is a routing decision. The engine can only reuse
        what it is sent.""")
        # tiers: a bigger, slower home for evicted blocks, per engine and then shared
        self.play(FadeOut(st), FadeOut(q), run_time=0.3)
        q2 = label("blocks are evicted before a conversation ends: give them a bigger home", 17, TEXT).move_to([0, 2.4, 0])
        host = VGroup(*[Rectangle(width=1.0, height=0.22, stroke_color=DIM, stroke_width=1.5, fill_opacity=0).move_to(e[0].get_bottom() + DOWN * 0.25) for e in engines])
        store = Rectangle(width=engines.width, height=0.3, stroke_color=DIM, stroke_width=1.5, fill_opacity=0).move_to([engines.get_x(), -2.2, 0])
        tiers = VGroup(*[label(s_, 13, DIM).move_to([engines.get_left()[0] - GAP, y_, 0], aligned_edge=RIGHT) for s_, y_ in (("GPU cache\nper engine", caches[0].get_y()), ("host RAM\nper engine", host[0].get_y()), ("shared store\nover the network", store.get_y()))])
        ex = label("shared store (LMCache, Mooncake, Dynamo KVBM): shared documents, agent context between tools", 13, MUTED).next_to(store, DOWN, buff=0.08).align_to(store, LEFT)
        self.play(FadeIn(q2), FadeIn(host), FadeIn(store), FadeIn(tiers), FadeIn(ex), run_time=0.6)
        random.seed(12)
        spills = {}
        for e in (home, 1, 4):   # three engines fill up and spill blocks to their own host RAM
            self.play(caches[e].animate.set_fill(HOT, 0.9), run_time=0.25)
            sp = VGroup(*[Rectangle(width=0.16, height=0.12, fill_color=CACHE, fill_opacity=0.9, stroke_width=0).move_to(caches[e]) for _ in range(3)])
            self.play(sp.animate.arrange(RIGHT, buff=0.05).move_to(host[e]), caches[e].animate.set_fill(CACHE, 0.9), run_time=0.5)
            spills[e] = sp
        dot = Dot(color=PROMPT, radius=0.09).move_to(lb[0].get_bottom())   # a turn comes home: its block comes back from host RAM
        self.play(dot.animate.move_to(caches[home].get_center()), run_time=0.3)
        self.play(spills[home][0].animate.move_to(caches[home]), Flash(engines[home][0], color=CACHE, flash_radius=0.6, num_lines=8), FadeOut(dot), run_time=0.4)
        self.remove(spills[home][0])
        copies = VGroup(*[spills[e][1].copy() for e in (home, 1, 4)])   # the shared store: copies any engine can read
        self.play(*[c.animate.move_to([engines[e].get_x() + 0.2 * i - 0.2, store.get_y(), 0]) for i, (c, e) in enumerate(zip(copies, (home, 1, 4)))], run_time=0.6)
        far = 6
        dot = Dot(color=PROMPT, radius=0.09).move_to(lb[0].get_bottom())   # a turn lands on a far engine and still finds its blocks
        self.play(dot.animate.move_to(caches[far].get_center()), run_time=0.3)
        self.play(copies[0].animate.move_to(caches[far]), Flash(engines[far][0], color=CACHE, flash_radius=0.6, num_lines=8), FadeOut(dot), run_time=0.5)
        self.play(caches[far].animate.set_fill(CACHE, 0.9), FadeOut(copies[0]), run_time=0.3)
        self.next_slide("""a shared store (LMCache, Mooncake, Dynamo KVBM): a long document many users ask about, an agent's context between tool calls. The other way out attacks a different limit: the cache is small and blocks are evicted long before a
        conversation is over, so even the home engine forgets. Three engines fill up here and spill blocks; a turn that comes
        home gets its block back from host RAM, and a turn that lands on a far engine can still find a copy in a store every
        engine can read. What lives in such a store: a long document many users ask about, a system prompt shared by a
        product, an agent's context while it waits on a tool. The projects that build them are LMCache, Mooncake and NVIDIA's
        Dynamo KVBM, all speaking the engine's connector interface. The engine's blocks are content-addressed, tagged by the hash
        of the tokens they hold, and a connector can copy a block out when it is evicted and look for it there on a miss. The
        cheap tier is the host's own RAM, copied over PCIe; the tier behind that is a shared store on the network, which any
        engine can read. We measured the first on this stack, and the result is the lesson. A 32 GB host tier behind a 58 GB
        GPU cache, with conversations whose working set was 1.4 times the cache: the tier absorbed 590 GB of evicted blocks in
        four minutes and served zero hits, because every block was overwritten before its conversation came back; throughput
        and latency within 1.5 percent of having no tier. Shrink the GPU cache so that the tier is nine times larger than it,
        and 79 percent of prompt tokens come back from host memory. The mechanism works; the ratio decides. A tier smaller
        than the churn is pure cost, and a tier is one engine's own: a turn routed to another engine cannot see it. So the knob
        has two parts. Routing decides whether a request reaches the blocks it could reuse; a second tier decides whether
        they still exist, and only when it is sized to the working set that will come back. Read the hit counters the engine
        publishes before paying for either. One caveat for the operators in the room: the cookie pins a client, not a user.
        Behind an API gateway that holds one cookie jar, stickiness would pin the whole gateway to one engine. Turn it on only
        when clients keep a cookie per end-user conversation, or have the gateway replay it per session; or use a router that
        looks at the prefix itself, which move seven comes back to.""")
        # --- hand-over: the fleet of engines gives way to the model that does not fit one GPU
        from s05_parallelism import start_parallelism, TITLE_PAR
        nxt = start_parallelism(self, add=False)
        spills[home].remove(spills[home][0])
        leaving = [q2, lb, hits, engines, caches, host, store, tiers, ex, *spills.values(), copies[1], copies[2]]
        t = handover(self, t, *TITLE_PAR, leaving=leaving, arriving=nxt["shown"])
        self.finish("""The picture hands over. 236 GB of weights and no GPU that holds them: divide the model, and pay at the seams. Some models do not fit one card. A 235B mixture of experts in fp8 is 236 GB of weights; the largest single GPU we can rent holds 96. So the model has to be divided over several GPUs, and how it is divided shows up as time.""")
