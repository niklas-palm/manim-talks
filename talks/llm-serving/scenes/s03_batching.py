"""Move 2: batching. Requests join the decode step one by one; the bandwidth gauge stays where it was, the compute
gauge fills, tokens per second climb, each request slows a little, and the cache fills until something has to go."""
from lib.palette import *
from objects import *

STEPS = [(1, 174, 174, 0.39), (8, 86, 688, 0.65), (32, 56, 1792, 0.76), (64, 48, 3072, 0.77), (128, 41, 5248, 0.77)]   # measured, one engine, 100-token prompts and 500-token answers: in flight, decode tokens/s per request, tokens/s in total, memory controller busy


class Batching(TalkSlide):
    def construct(self):
        t = title(self, "Batching: the knob between latency and throughput", "2  why the engine batches")
        # --- part one: the mechanism, as a timeline of decode steps
        N, X0, W1, W4 = 8, -4.7, 0.92, 1.0                   # steps drawn, first step's x, step width alone and with four
        ROWS = [1.0, 0.55, 0.1, -0.35]
        axis = Arrow([-5.3, 1.95, 0], [4.3, 1.95, 0], color=DIM, stroke_width=2, buff=0, tip_length=0.15)
        al = label("time, one decode step after another", 14, DIM).next_to(axis, UP, buff=0.05).align_to(axis, LEFT)
        wl = label("weights read", 14, WEIGHTS).move_to([-5.5, 1.55, 0], aligned_edge=RIGHT)
        rl = VGroup(*[label(f"request {i + 1}", 14, DIM).move_to([-5.5, y, 0], aligned_edge=RIGHT) for i, y in enumerate(ROWS)])
        reads = Counter("weights read, per step", 1, "", WEIGHTS, size=24).move_to([-6.4, -1.3, 0], aligned_edge=LEFT)
        per_step = Counter("tokens produced, per step", 1, "", OUTPUT, size=24).move_to([-3.2, -1.3, 0], aligned_edge=LEFT)
        steplen = label("step time: the weights read, plus a little arithmetic per request", 14, DIM).move_to([0.0, -1.3, 0], aligned_edge=LEFT)
        self.play(Create(axis), FadeIn(al), FadeIn(wl), FadeIn(rl[0]), FadeIn(reads), FadeIn(per_step))
        cap = caption(self, "One request: every step reads all the weights and produces one token")
        self.next_slide("""The still picture: a time axis, one decode step after another from left to right; a row for the weights read
        and a row for one request; two counters, weights read per step and tokens produced per step, both at one. Nothing
        has happened yet. The next click runs the first steps.""")
        cols = []
        for k in range(N):
            x = X0 + k * W1
            block = Rectangle(width=W1 - 0.1, height=0.32, fill_color=WEIGHTS, fill_opacity=0.75, stroke_width=0).move_to([x, 1.55, 0])
            tok = Square(0.3, fill_color=OUTPUT, fill_opacity=0.9, stroke_width=0).move_to([x, ROWS[0], 0])
            cols.append(VGroup(block, tok))
            slow = k < 2   # the first two steps slowly, then at speed: the audience has seen the beat
            self.play(FadeIn(block, shift=DOWN * 0.1), run_time=0.4 if slow else 0.12)
            self.play(FadeIn(tok, shift=DOWN * 0.1), run_time=0.3 if slow else 0.1)
        self.next_slide("""Here is decode as a timeline. Each violet block is one step: all the weights come in from memory. Each step
        hands the request one token. The step is as long as the weights read, so this request gets a token every eight
        milliseconds or so, and the bus is busy for a fraction of that: the rest is the launches and bookkeeping from the
        last scene. Nothing else is using the GPU.""")
        added = []
        for k in range(N):
            for r in range(1, 4):
                added.append(Square(0.3, fill_color=OUTPUT, fill_opacity=0.9, stroke_width=0).move_to([X0 + k * W1, ROWS[r], 0]))
                cols[k].add(added[-1])
        self.play(FadeIn(rl[1:]), LaggedStart(*[FadeIn(m, shift=DOWN * 0.1) for m in added], lag_ratio=0.02), per_step.to(4), run_time=1.6)
        cap = swap_caption(self, cap, "Four requests: one read of the weights, four tokens per step")
        self.next_slide("""Four requests: the same read of the weights serves all four; four tokens per step. Now three more requests arrive, and the engine puts their tokens into the same steps. Look at what did not
        change: the violet blocks. The weights come in once per step, exactly as before, and that one read now does a
        column of arithmetic for each of the four requests. Tokens per step went from one to four; reads per step stayed at
        one. That is the entire reason an engine batches: the expensive thing, moving the weights, is paid once per step no
        matter how many requests share the step.""")
        cap = swap_caption(self, cap, "The step grows a little: arithmetic and a cache read per request")
        wider = []
        for k, c in enumerate(cols):   # one Transform per column: animating the group and its block separately would fight over the block
            tgt = c.copy()
            tgt[0].stretch_to_fit_width(W4 - 0.1)
            tgt.move_to([X0 + k * W4 + (W4 - W1) / 2, c.get_y(), 0])
            wider.append(Transform(c, tgt))
        self.play(*wider, FadeIn(steplen), run_time=1.0)
        self.next_slide("""The step gets a little longer: each request adds a column of arithmetic and its cache read. The step does get a little longer, and here is the trade in one picture. Each extra request adds one column of
        arithmetic and one read of its own KV cache to the step; the weights read is unchanged. So the time between one
        request's tokens, its latency, creeps up, while the tokens the GPU produces per second, the throughput, climbs almost
        in proportion to the batch. That holds until the added arithmetic or the added cache reads grow to the size of the
        weights read, which is where the curve you are about to see bends.""")
        # --- continuous batching as it runs: a conveyor of steps. The rows are slots, the most requests the engine puts into one
        # step. The newest step enters at the right and time scrolls left at a constant rate, so a longer step is a wider column.
        # A request is one colour from the queue to its slot to its last token; an empty slot is a hollow cell: the weights read
        # was paid, and nothing came out for that row.
        self.play(FadeOut(VGroup(*cols)), FadeOut(steplen), FadeOut(rl), FadeOut(wl), FadeOut(al), FadeOut(axis), FadeOut(reads), FadeOut(per_step), run_time=0.6)
        SLOTS, X_NEW, X_END, W1S = 8, 3.4, -4.9, 0.26
        ys = [1.3 - 0.33 * i for i in range(SLOTS)]
        yw, yq = 1.78, -1.7
        sl = VGroup(*[label(f"slot {i + 1}", 13, DIM).move_to([-5.15, y, 0], aligned_edge=RIGHT) for i, y in enumerate(ys)])
        wr = label("weights read", 13, WEIGHTS).move_to([-5.15, yw, 0], aligned_edge=RIGHT)
        ql = label("waiting", 13, HOT).move_to([-5.15, yq, 0], aligned_edge=RIGHT)
        axis2 = Arrow([-5.0, 2.15, 0], [3.6, 2.15, 0], color=DIM, stroke_width=2, buff=0, tip_length=0.15)
        al2 = label("time: one decode step after another, the newest at the right", 13, DIM).next_to(axis2, UP, buff=0.04).align_to(axis2, LEFT)
        legend = VGroup(label("column: one step, width = its time; colour: one request, outlined at prefill", 12, DIM),
                        label("hollow: an idle slot; 8 slots drawn, the engine's limit is max_num_seqs (256)", 12, DIM)).arrange(DOWN, aligned_edge=LEFT, buff=0.05).move_to([-5.0, -2.4, 0], aligned_edge=LEFT)
        mask = Rectangle(width=2.3, height=4.3, fill_color=config.background_color, fill_opacity=1.0, stroke_width=0).move_to([X_END - 1.15, 0.05, 0]).set_z_index(1)
        for m in (sl, wr, ql):
            m.set_z_index(2)
        busg = Gauge("bus", OUTPUT, 1.6).move_to([5.2, 1.15, 0])
        compg = Gauge("compute", PROMPT, 1.6).move_to([6.0, 1.15, 0])
        nreq_c = Counter("requests sharing the step", 0, "", TEXT, size=22).move_to([4.1, -0.35, 0], aligned_edge=LEFT)
        ms_c = Counter("step time", 0, "ms", WEIGHTS, size=22, decimals=1).move_to([4.1, -1.3, 0], aligned_edge=LEFT)
        tps_c = Counter("tokens per second, all together", 0, "", OUTPUT, size=22).move_to([4.1, -2.25, 0], aligned_edge=LEFT)
        HUES = ["#FFD166", "#F4845F", "#EF476F", "#C77DFF", "#06D6A0", "#8ECAE6", "#FFB703", "#B5E48C", "#F9C74F", "#90BE6D", "#F8961E", "#9BF6FF"]
        # arrivals per step, each number the length of a request in steps (its first step is the prefill). Light load, then more than the slots can take, then quiet.
        arrivals = {0: [7], 4: [9], 9: [6], 14: [8, 10], 15: [9, 7], 16: [11, 8, 9], 17: [9], 18: [10, 8], 19: [7, 9], 20: [8], 21: [10, 9], 22: [8], 23: [9], 25: [8], 27: [7], 30: [9], 32: [8], 34: [8], 36: [9], 37: [8], 38: [9], 39: [10]}

        def per_request(n):   # tokens/s each request gets: measured at 1 and 8 in flight, a straight line between
            return 174 - (174 - 86) * (n - 1) / 7

        slots, waiting, columns, nreq = [None] * SLOTS, [], [], 0
        cap = swap_caption(self, cap, "Requests never arrive together: at light load the GPU mostly waits")
        self.play(FadeIn(sl), FadeIn(wr), FadeIn(ql), FadeIn(axis2), FadeIn(al2), FadeIn(legend), FadeIn(busg), FadeIn(compg), FadeIn(nreq_c), FadeIn(ms_c), FadeIn(tps_c), run_time=0.6)
        self.add(mask)

        def one_step(t):
            nonlocal nreq
            anims, arriving = [], []
            for length in arrivals.get(t, []):
                hue = HUES[nreq % len(HUES)]; nreq += 1
                sq = Square(0.2, fill_color=hue, fill_opacity=0.95, stroke_width=0).move_to([-4.85 + 0.28 * len(waiting), yq, 0])
                waiting.append([hue, length, sq]); arriving.append(FadeIn(sq, shift=UP * 0.1))
            if arriving:
                self.play(*arriving, run_time=0.12)
            admitted = []
            for i in range(SLOTS):   # a free slot takes the next request waiting, at this very step
                if slots[i] is None and waiting:
                    hue, length, sq = waiting.pop(0)
                    slots[i] = [hue, length, True]; admitted.append((i, sq))
            for k, (_, _, sq) in enumerate(waiting):   # the queue closes up
                anims.append(sq.animate.move_to([-4.85 + 0.28 * k, yq, 0]))
            occ = sum(s_ is not None for s_ in slots)
            n = max(occ, 1)
            ms = 1000 / per_request(n)
            w = W1S * ms / (1000 / per_request(1))   # x is time: the column is as wide as the step is long
            xc = X_NEW + w / 2
            col = VGroup(Rectangle(width=w - 0.05, height=0.24, fill_color=WEIGHTS, fill_opacity=0.75, stroke_width=0).move_to([xc, yw, 0]))
            for i, st in enumerate(slots):
                if st is None:
                    col.add(Rectangle(width=w - 0.05, height=0.24, stroke_color=DIM, stroke_width=1, fill_opacity=0).move_to([xc, ys[i], 0]))
                    continue
                hue, remaining, first = st
                col.add(Rectangle(width=w - 0.05, height=0.24, fill_color=hue, fill_opacity=0.95, stroke_color=TEXT if first else hue, stroke_width=1.5 if first else 0).move_to([xc, ys[i], 0]))
                st[1] -= 1; st[2] = False
                if st[1] == 0:
                    slots[i] = None
            self.add(col); columns.append(col)
            for c in columns:
                anims.append(c.animate.shift(LEFT * w))
            for i, sq in admitted:
                anims.append(sq.animate.move_to([xc - w, ys[i], 0]).set_opacity(0))
            self.play(*anims, busg.set(0.39 + 0.26 * (occ - 1) / 7 if occ else 0.05), compg.set(0.12 + 0.43 * (occ - 1) / 7 if occ else 0.03),
                      nreq_c.to(occ), ms_c.to(ms if occ else 0), tps_c.to(occ * per_request(n)), run_time=0.22 * w / W1S, rate_func=linear)
            for i, sq in admitted:
                self.remove(sq)
            for c in [c for c in columns if c.get_right()[0] < X_END]:   # gone behind the mask
                columns.remove(c); self.remove(c)

        for t in range(14):
            one_step(t)
        self.next_slide("""Requests never arrive together. Light load: two or three share each read, the GPU mostly waiting. The timeline assumed four requests that arrived together. They never do: requests come and go on their own
        clocks, so the engine re-forms the batch at every step from whoever is in flight. Watch it run. Eight slots drawn, the
        most requests the engine will put into one step; the real setting is max_num_seqs, 256 in our engine. Time scrolls left; every
        step enters at the right as a column, a violet block for the weights read and one cell per slot. A request is a colour:
        it arrives in the queue at the bottom, takes a free slot, its first cell is its prefill, then one token per step until
        it is done. At light load two or three requests share a step and the rest of the column is hollow: the weights were
        read, and nothing came out for those rows. The bus gauge sits where the single request left it, the compute gauge is
        near the floor, and the tokens per second counter says what that costs. This GPU is mostly waiting.""")
        cap = swap_caption(self, cap, "Heavy load: every slot full, a queue, four times the tokens per second")
        for t in range(14, 41):
            one_step(t)
        self.next_slide("""Heavy load: every slot full, a queue forms, the step a little longer, four times the tokens per second. Then arrivals come faster than requests finish. Slots fill. A request that finishes frees its slot, and the next
        one waiting takes it at the very next step; nobody waits for a batch to drain. That is continuous batching: the batch
        re-formed every step. When all eight slots are taken, arrivals wait in the queue, and that queue is the dashboard's
        saturation signal. Look at what the load did to the machine. The columns are wider: the step is longer, because eight
        columns of arithmetic and eight cache reads ride on each weights read. But it is not eight times longer; it is about
        twice, and that is measured. So eight tokens a step for twice the step: four times the tokens per second, the compute
        gauge up, the bus gauge higher because the cache reads add bytes. When arrivals slow, it runs in reverse: slots empty,
        hollow cells return, the counters fall. The measured curve next is this picture with numbers.""")
        self.play(FadeOut(VGroup(sl, wr, ql, axis2, al2, legend, busg, compg, nreq_c, ms_c, tps_c, mask, *columns, *[sq for _, _, sq in waiting])), run_time=0.8)
        # --- part two: the same GPU, measured
        cap = swap_caption(self, cap, "Measured on this GPU as the batch grows")
        gpu = GPU("one GPU", w=4.8, weights_gb=29).scale(0.9).shift(LEFT * 3.3 + DOWN * 0.3)
        self.play(FadeIn(gpu), gpu.bandwidth.set(0.39), gpu.set_cache(3))
        inflight = Counter("requests in flight", 1, "", TEXT, size=26).move_to([0.0, 1.9, 0], aligned_edge=LEFT)
        each = Counter("tokens/s, each request", 174, "", OUTPUT, size=26).move_to([2.5, 1.9, 0], aligned_edge=LEFT)
        total = Counter("tokens/s, whole GPU", 174, "", CACHE, size=26).move_to([5.0, 1.9, 0], aligned_edge=LEFT)
        clk = label("latency and throughput, both measured while decoding", 12, MUTED).move_to([2.5, 1.3, 0], aligned_edge=LEFT)
        self.play(FadeIn(inflight), FadeIn(each), FadeIn(total), FadeIn(clk))
        self.next_slide("""Now measured, on this GPU: each request's speed and the total, as the batch grows. Now the same thing measured. The GPU from before with one request decoding: the bus busy about forty percent of
        the time, the compute grid nearly idle, and three counters: requests in flight, tokens per second each one gets, and
        tokens per second from the whole GPU. Both are measured while decoding, so with one request they are the same
        number: this is the latency and the throughput from the last scene, side by side. Both count tokens produced; the bus
        gauge is what counts bytes read.""")
        cap = swap_caption(self, cap, "A GPU is a budget you share: throughput up, speed per request down")
        ax = Axes(x_range=[0, 140, 32], y_range=[0, 5200, 1000], x_length=5.0, y_length=2.7,
                  axis_config={"color": DIM, "include_tip": False, "font_size": 14}).move_to([3.6, -1.0, 0])
        xl = label("requests in flight", 14, DIM).next_to(ax.x_axis, DOWN, buff=0.12)
        yl = label("tokens/s", 14, DIM).next_to(ax.y_axis, UP, buff=0.08)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        per_pts, agg_pts = [ax.c2p(1, 174 * 8)], [ax.c2p(1, 174)]     # per-request drawn x8 to share the axis
        per_dot, agg_dot = Dot(per_pts[0], color=OUTPUT, radius=0.05), Dot(agg_pts[0], color=CACHE, radius=0.05)
        self.play(FadeIn(per_dot), FadeIn(agg_dot))
        POINT_NOTES = {
            8: """Eight in flight. Each request slowed from 174 to 86 tokens per second, half; the GPU went from 174 to nearly 700,
            four times. The step grew from 5.7 to 11.6 milliseconds: eight columns of arithmetic and eight cache reads on one
            weights read. That is the trade in numbers: latency doubled, throughput quadrupled.""",
            32: """Thirty-two. Each request at 56 tokens per second, the GPU near 1,800. The memory controller is now busy 76 percent
            of the time, the compute grid filling. Both gauges rising together is the sign that the batch is doing what it should.""",
            64: """Sixty-four. Each request at 48, the GPU past 3,000, and the curve bends: the added arithmetic and the added cache
            reads now weigh about as much as the weights read, so each new request costs the others more than it did.""",
            128: """One hundred and twenty-eight. Each request at 41 tokens per second, the GPU above 5,000. The bus gauge is where it
            was at 32: 77 percent busy is as hard as this kernel stack drives the memory controller. For the record, the wall-clock
            totals we measured were 166 at one in flight and 4,971 at 128; the same picture with prefill and the gaps between
            requests included.""",
        }
        for n, per, agg, busy in STEPS[1:]:
            frac_c = min(0.95, n / 140)
            p2, a2 = ax.c2p(n, per * 8), ax.c2p(n, agg)
            self.play(inflight.to(n), each.to(per), total.to(agg), gpu.bandwidth.set(busy), gpu.compute.set(frac_c),
                      *gpu.light_cores(frac_c, PROMPT), gpu.set_cache(3 + n * 0.45),
                      Create(Line(per_pts[-1], p2, color=OUTPUT, stroke_width=3)), Create(Line(agg_pts[-1], a2, color=CACHE, stroke_width=3)),
                      per_dot.animate.move_to(p2), agg_dot.animate.move_to(a2), run_time=1.4)
            per_pts.append(p2); agg_pts.append(a2)
            gpu.flash_weights(self)
            if n < 128:
                self.next_slide(POINT_NOTES[n])
        pl = label("each request (×8)", 14, OUTPUT).next_to(per_pts[-1], UP, buff=0.12)
        al = label("all together", 14, CACHE).next_to(agg_pts[-1], RIGHT, buff=0.1)
        self.play(FadeIn(pl), FadeIn(al))
        self.next_slide(POINT_NOTES[128])
        # the cache limit
        cap = swap_caption(self, cap, "Memory full: a request is evicted and recomputed later", 26, HOT)
        self.play(gpu.set_cache(3 + 128 * 0.45 + 10), run_time=0.8)
        self.play(gpu.set_cache(gpu.mem_gb - 29 - 0.5, HOT), run_time=0.6)
        self.next_slide("""What stops the batch growing forever is the teal segment. Every request in flight keeps its KV cache in
        memory, and that memory is whatever the weights left over. When it fills, the engine preempts: it evicts a request's
        cache and recomputes it later. That recompute is prefill work done twice, pure waste, and it shows up on a dashboard as
        a latency spike. So the number of requests a GPU can serve is set by the memory left after the weights.""")
        self.play(gpu.set_cache(3 + 128 * 0.45), run_time=0.5)
        cap = swap_caption(self, cap, "Shrink the weights and more requests fit. That is the next knob.")
        self.finish("""Which sets up the first thing anyone does when they host a model: make the weights smaller. Smaller weights
        mean fewer bytes per decode step, so faster tokens, and more memory left for cache, so a bigger batch. Both gauges move
        in the right direction at once.""")
