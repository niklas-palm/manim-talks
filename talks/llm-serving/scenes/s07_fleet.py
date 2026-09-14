"""Move 6: from one measured engine to a fleet, from first principles. Independent engines add up, so sizing is arithmetic
on one measurement; a new engine has to load the model before it can serve, so adding one takes minutes; the balancer
sees latency but the reasons live inside the engines; agents change the shape of requests. The numbers on screen are
the worked example from the companion repository; the notes say which is which."""
from lib.palette import *
from objects import *


def engine(name: str, color: str = WEIGHTS) -> VGroup:
    return box(1.0, 0.95, name, color, size=17)


class Fleet(TalkSlide):
    def construct(self):
        t = title(self, "From one engine to a fleet", "6  the fleet")
        cap = caption(self, "A fleet starts from one engine's measured rate, at your latency budget and prompt shape")
        gpu = GPU("one engine", w=4.4, weights_gb=29).scale(0.8).shift(LEFT * 3.4 + UP * 0.2)
        self.play(FadeIn(gpu), gpu.set_cache(40), gpu.bandwidth.set(0.92), gpu.compute.set(0.7), *gpu.light_cores(0.7))
        rps = Counter("requests/s one engine sustains inside the latency budget", 16, "", OUTPUT).shift(RIGHT * 2.6 + UP * 1.2)
        self.play(FadeIn(rps))
        self.next_slide("""Everything before this was one engine, and a fleet is built from one number about it: how many requests per
        second one engine sustains inside your latency budget, at your prompt shape. That number is the operating point on the
        batching curve from move two, and nothing about it can be looked up; it moves with the model, the prompt length and the
        budget. In the companion measurements it is about 16 requests per second, 16,000 input tokens per second, for 1,000-token prompts inside an 8-second p95. Take
        that as the worked example, not as a constant.""")
        cap = swap_caption(self, cap, "Sizing is arithmetic: demand over one engine's rate, with headroom, rounded up")
        demand = Counter("demand at peak", 100, "requests/s", TEXT).shift(RIGHT * 2.6 + DOWN * 0.3)
        need = Counter("engines: 100 over (16 times 0.85), rounded up", 8, "", CACHE).shift(RIGHT * 2.6 + DOWN * 1.6)
        self.play(FadeIn(demand))
        self.play(FadeIn(need))
        self.next_slide("""Requests are independent, so engines add up: two engines serve twice what one does, to within a percent or two,
        as long as the balancer spreads the load. That makes sizing arithmetic. Peak demand divided by one engine's rate, with
        some headroom for bursts and for the engine you will lose to a reclaim or a restart, rounded up. In the example: a hundred
        requests per second over sixteen with fifteen percent headroom is eight engines. The exception is multi-turn traffic,
        whose cache hits depend on routing, which knob three covered.""")
        cap = swap_caption(self, cap, "Independent engines behind a balancer: capacity adds up, and a failure costs one engine")
        self.play(FadeOut(gpu), FadeOut(rps), FadeOut(demand), FadeOut(need))
        fleet = VGroup(*[engine(str(i + 1)) for i in range(8)]).arrange(RIGHT, buff=0.18).shift(DOWN * 0.95)
        lb = box(2.8, 0.65, "load balancer", DIM, size=19).shift(UP * 0.8)
        links = VGroup(*[Line(lb[0].get_bottom(), e[0].get_top(), color=DIM, stroke_width=1.5) for e in fleet])
        self.play(FadeIn(lb), LaggedStart(*[FadeIn(e, shift=UP * 0.15) for e in fleet], lag_ratio=0.08), Create(links))
        self.next_slide("""The shape that follows: several independent engines behind a balancer, rather than one large engine over many
        GPUs. Move four gave the throughput reason, replicas over parallelism past the degree where the model fits. There are two
        operational reasons too. A failure or a spot reclaim takes one engine out of eight, not the whole service. And capacity
        comes in engine-sized steps, so the fleet can follow demand more closely. What sits in front of the balancer, TLS, keys,
        rate limits, is ordinary web infrastructure and not this talk's subject.""")
        cap = swap_caption(self, cap, "Adding an engine means loading the model: minutes. Size for the peak, autoscale for the trend")
        clock = VGroup(label("decide", 15, DIM), label("get a machine", 15, DIM), label("load the weights", 15, DIM), label("serving", 15, OUTPUT)).arrange(RIGHT, buff=0.55).shift(UP * 2.3)
        bar = Line(clock.get_left() + DOWN * 0.28, clock.get_right() + DOWN * 0.28, color=DIM)
        prog = Line(bar.get_start(), bar.get_start(), color=OUTPUT, stroke_width=6)
        self.play(FadeIn(clock), Create(bar))
        self.add(prog)
        self.play(prog.animate.put_start_and_end_on(bar.get_start(), bar.get_end()), run_time=2.5)
        new = engine("9", OUTPUT).next_to(fleet, RIGHT, buff=0.18)
        self.play(FadeIn(new), Create(Line(lb[0].get_bottom(), new[0].get_top(), color=DIM, stroke_width=1.5)))
        self.next_slide("""Autoscaling is slower than people expect, for a reason that is not about any one stack. A new engine has to
        notice the load, get a machine with a GPU, pull an image, and load tens of gigabytes of weights before it answers its
        first request; every stage is minutes, not seconds. In the companion stack the whole chain measured eleven minutes from
        alarm to serving, and scale-in is slower still. So the fixed fleet is sized for the peak from the arithmetic above, and
        autoscaling is insurance against a trend that lasts longer than a coffee break, not a way to meet a burst.""")
        self.play(FadeOut(clock), FadeOut(bar), FadeOut(prog))
        cap = swap_caption(self, cap, "The balancer sees latency; the reasons live in the engines: queue, cache, preemptions")
        for e in fleet[:3]:
            e[0].set_fill(HOT, 0.3)
        g1, g2 = Gauge("queue", HOT, 0.8), Gauge("cache", HOT, 0.8)
        gauges = VGroup(g1, g2).arrange(RIGHT, buff=0.35).next_to(fleet, DOWN, buff=0.15)
        self.play(FadeIn(gauges), g1.set(0.95), g2.set(0.98))
        self.next_slide("""When the fleet is slow, the balancer can only tell you that it is: request counts and response times. Why lives
        inside the engines, and every engine publishes it: how many requests are waiting for a place in the batch, how full the
        KV cache is, how many requests were preempted. Read them against the pictures from moves two and three. A queue that is
        never empty is saturation. A cache near full means preemptions next. Any preemption means work done twice. Scrape these
        into whatever dashboard you have; the balancer's numbers alone cannot tell the three apart.""")
        self.play(FadeOut(gauges), *[e[0].animate.set_fill(WEIGHTS, 0.1) for e in fleet[:3]])
        cap = swap_caption(self, cap, "Agents: long requests with tools; the engine parses the calls, the client streams")
        self.finish("""One last shape change, because most new traffic is agents. An agent sends the model a list of tools and expects
        a structured call back, so the engine needs a parser for that model's tool-call format, or the call comes back as plain
        text and the agent stalls without an error. Agent steps carry the whole trajectory, tens of thousands of tokens on a
        busy engine, so they run long, longer than the timeouts most proxies and gateways apply to a request that has not started
        answering. Stream them. None of this changes the machine; it changes what the machine is asked to hold.""")
