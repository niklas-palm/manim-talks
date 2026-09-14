"""This talk's vocabulary on top of the shared library: the five meanings its colours carry, the nouns that are
coloured wherever they appear, and the one drawing every scene shares, the GPU.

  PROMPT (blue)   tokens that came in       WEIGHTS (violet)  the model's parameters
  OUTPUT (yellow) tokens the model wrote    CACHE (teal)      the KV cache, working memory per request
  HOT (red)       saturated or wrong
"""
from lib.palette import *

PROMPT, OUTPUT, WEIGHTS, CACHE, HOT = BLUE, YELLOW, VIOLET, TEAL, RED
set_thread({"prefill": PROMPT, "decode": OUTPUT, "weights": WEIGHTS, "weight": WEIGHTS, "cache": CACHE, "caching": CACHE})


class GPU(VGroup):
    """The one drawing of a GPU used everywhere: memory bar (weights, cache), compute grid, two gauges."""

    def __init__(self, name: str = "one GPU", w: float = 5.2, mem_gb: float = 96, weights_gb: float = 57, **kw):
        super().__init__(**kw)
        self.outer = RoundedRectangle(corner_radius=0.18, width=w, height=3.6, stroke_color=WEIGHTS, stroke_width=2.5, fill_color=WEIGHTS, fill_opacity=0.06)
        self.title = label(name, 22, WEIGHTS).next_to(self.outer.get_top(), DOWN, buff=0.15)
        bar_w = w - 1.9
        self.mem_gb, self.bar_w = mem_gb, bar_w
        self.mem = Rectangle(width=bar_w, height=0.55, stroke_color=DIM, stroke_width=2, fill_opacity=0).move_to(self.outer.get_center() + UP * 0.55 + LEFT * 0.7)
        self.weights = Rectangle(width=bar_w * weights_gb / mem_gb, height=0.51, fill_color=WEIGHTS, fill_opacity=0.85, stroke_width=0).align_to(self.mem, LEFT).set_y(self.mem.get_y())
        self.cache = Rectangle(width=0.01, height=0.51, fill_color=CACHE, fill_opacity=0.85, stroke_width=0).next_to(self.weights, RIGHT, buff=0).set_y(self.mem.get_y())
        self.mem_label = label(f"memory {mem_gb:g} GB", 15, DIM).next_to(self.mem, UP, buff=0.08).align_to(self.mem, LEFT)
        side = (bar_w - 15 * 0.05) / 16
        self.cores = VGroup(*[Square(side, fill_color=DIM, fill_opacity=0.9, stroke_width=0) for _ in range(32)]).arrange_in_grid(rows=2, cols=16, buff=0.05)
        self.cores.next_to(self.mem, DOWN, buff=0.45).align_to(self.mem, LEFT)
        self.cores_label = label("compute", 15, DIM).next_to(self.cores, DOWN, buff=0.08).align_to(self.cores, LEFT)
        self.bandwidth = Gauge("bus", OUTPUT).move_to(self.outer.get_right() + LEFT * 1.15 + DOWN * 0.25)
        self.compute = Gauge("compute", PROMPT).move_to(self.outer.get_right() + LEFT * 0.5 + DOWN * 0.25)
        self.add(self.outer, self.title, self.mem, self.weights, self.cache, self.mem_label, self.cores, self.cores_label, self.bandwidth, self.compute)

    def set_weights(self, gb: float):
        return self.weights.animate.stretch_to_fit_width(self.bar_w * gb / self.mem_gb).align_to(self.mem, LEFT)

    def set_cache(self, gb: float, color: str = CACHE):
        w = max(0.01, self.bar_w * gb / self.mem_gb)
        target = Rectangle(width=w, height=0.51, fill_color=color, fill_opacity=0.85, stroke_width=0).next_to(self.weights, RIGHT, buff=0).set_y(self.mem.get_y())
        return self.cache.animate.become(target)

    def flash_weights(self, scene, color: str = OUTPUT, run_time: float = 0.35):
        """One decode step: the weights are read once."""
        scene.play(self.weights.animate.set_fill(color, 1.0), run_time=run_time * 0.5)
        scene.play(self.weights.animate.set_fill(WEIGHTS, 0.85), run_time=run_time * 0.5)

    def light_cores(self, fraction: float, color: str = PROMPT):
        n = int(round(32 * fraction))
        return [c.animate.set_fill(color if i < n else DIM, 0.9) for i, c in enumerate(self.cores)]


# ------------------------------------------------------------------------------------------------ hand-overs
# Every scene after the first opens on the previous scene's last frame. The previous scene ends by retitling and
# transforming its picture into this scene's still start; this scene rebuilds that start statically. Both use the same
# start_<scene>() function, so the two frames are pixel-identical (bin/seams.py checks).

def gauge_at(g: Gauge, level: float):
    """Set a gauge without animating it (Gauge.set returns an animation)."""
    level = max(0.006, min(1.0, level))
    target = Rectangle(width=0.30, height=g.h * level, fill_color=HOT if level > 0.9 else g.color, fill_opacity=0.9, stroke_width=0)
    target.move_to(g.frame.get_bottom() + UP * 0.03, aligned_edge=DOWN)
    g.fill.become(target)
    return g


def cache_at(gpu: GPU, gb: float, color: str = CACHE):
    """Set a GPU's cache segment without animating it."""
    w = max(0.01, gpu.bar_w * gb / gpu.mem_gb)
    gpu.cache.become(Rectangle(width=w, height=0.51, fill_color=color, fill_opacity=0.85, stroke_width=0).next_to(gpu.weights, RIGHT, buff=0).set_y(gpu.mem.get_y()))
    return gpu


def caption_still(scene, s: str, size: float = 22, color: str = TEXT) -> Text:
    """The footnote caption as a still: what caption() draws, added without its fade-in."""
    t = pin(scene, label(s, size, color=CAPTION if color == TEXT else color, width=12.8, thread=(color == TEXT)), buff=0.3)
    scene.add(t)
    return t


def handover(scene, old_title, new_title: str, kicker: str, leaving, arriving, run_time: float = 1.2):
    """The last play of a scene: the title changes to the next scene's, what this scene drew fades out, and the next
    scene's still start fades in, all in one motion. `arriving` are the next scene's start objects, not yet added."""
    return retitle(scene, old_title, new_title, kicker, extra=[FadeOut(VGroup(*leaving)), FadeIn(VGroup(*arriving))], run_time=run_time)
