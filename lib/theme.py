"""The look, in one place: a theme is the only thing that decides colour, type, corner and stroke.

`lib/palette.py` reads a theme at import and derives every constant the helpers use, so a deck's drawing code names
meanings ("the model is accent three") and never a hue. Changing the theme changes every talk in the repository and
nothing else. See AGENTS.md for the styles that ship and how to choose one; docs/library.md for the tokens.

Resolution order, first hit wins:
    THEME=<name>            environment variable, for one render
    talks/<talk>/.theme     one line, that talk's style; bin/render.sh exports it
    .theme                  one line at the repository root, the project's style
    studio-dark             the dark house style, the fallback

A theme file is `themes/<name>.json`; keys it leaves out are taken from `themes/studio-dark.json`, so a variant can be
five lines. Every value is either a hex colour, a number, a font family name or a Pygments style name.

Why the numbers are in the theme and not in the scenes: a style is not only its palette. Square corners and thick
strokes read as brutalist, soft corners and low contrast as japandi, thin lines and pale ink as Scandinavian. The
helpers take their corner radius, stroke width and fill opacity from here and scale the rest proportionally.
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEME_DIR = os.path.join(REPO, "themes")
DEFAULT = "studio-dark"   # the dark house style: every other theme inherits the keys it does not set

# Colour roles. A theme must give each one a value; a variant inherits the ones it omits.
ROLES = ["bg", "text", "muted", "dim", "caption", "hi", "panel"]
# Accent slots. a1..a6 are the talk's vocabulary; alert is "wrong, hot, refused" and is never a second meaning.
# A theme keeps each slot's character so that decks read the same across themes: a1 cool, a2 warm, a3 deep, a4 fresh,
# a5 growth, a6 spice, alert wrong.
ACCENTS = ["a1", "a2", "a3", "a4", "a5", "a6", "alert"]
NUMBERS = ["radius", "stroke", "fill", "solid"]

_warned = set()


def _warn(msg: str):
    if msg not in _warned:
        _warned.add(msg)
        print(f"theme: {msg}", file=sys.stderr)


# ------------------------------------------------------------------------------------------------ colour maths
# Enough of CIE to answer two questions: can the audience see this against the background (contrast ratio), and can
# they tell these two accents apart (perceptual distance). Both are used by bin/themes.py check and by the PowerPoint
# extractor, which lifts a corporate accent until it passes.

def rgb(c: str) -> tuple:
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


def hex_of(t) -> str:
    return "#" + "".join(f"{max(0, min(255, round(v * 255))):02X}" for v in t)


def _lin(v: float) -> float:
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminance(c: str) -> float:
    r, g, b = (_lin(v) for v in rgb(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    """WCAG contrast ratio, 1 to 21. Body text wants 7, small text and shapes 4.5, a graphical object 3."""
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _lab(c: str) -> tuple:
    r, g, b = (_lin(v) for v in rgb(c))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def distance(a: str, b: str) -> float:
    """Perceptual distance in Lab (CIE76). Two accents below about 22 are read as the same colour on a projector."""
    la, lb = _lab(a), _lab(b)
    return sum((x - y) ** 2 for x, y in zip(la, lb)) ** 0.5


def blend(a: str, b: str, t: float) -> str:
    """t of the way from a to b."""
    return hex_of(tuple(x + (y - x) * t for x, y in zip(rgb(a), rgb(b))))


def lift(c: str, bg: str, ratio: float = 3.0, steps: int = 60) -> str:
    """Move a colour away from the background until it has at least `ratio` contrast against it, keeping its hue: what
    makes a real corporate palette usable on a stage. Returns the colour unchanged if it already passes."""
    if contrast(c, bg) >= ratio:
        return c
    target = "#FFFFFF" if luminance(bg) < 0.5 else "#000000"
    best = c
    for i in range(1, steps + 1):
        best = blend(c, target, i / steps)
        if contrast(best, bg) >= ratio:
            break
    return best


# ------------------------------------------------------------------------------------------------ loading

def names() -> list:
    """Every theme that ships, plus anything under themes/local (extracted from a PowerPoint file, never committed)."""
    out = sorted(f[:-5] for f in os.listdir(THEME_DIR) if f.endswith(".json"))
    local = os.path.join(THEME_DIR, "local")
    if os.path.isdir(local):
        out += sorted("local/" + f[:-5] for f in os.listdir(local) if f.endswith(".json"))
    return out


def path_of(name: str) -> str:
    return os.path.join(THEME_DIR, f"{name}.json")


def active_name() -> str:
    """The theme this render uses. THEME wins; then the repository's .theme; then the dark house style."""
    env = os.environ.get("THEME", "").strip()
    if env:
        return env
    f = os.path.join(REPO, ".theme")
    if os.path.exists(f):
        with open(f) as fh:
            n = fh.read().strip()
        if n:
            return n
    return DEFAULT


def fonts_available() -> set:
    """The installed families, asked of Pango. Only a check calls this: asking during a render initialises Pango's font
    map before Manim does and shifts glyph positions by a fraction of a pixel, which changes every frame in the deck."""
    try:
        import manimpango
        return set(manimpango.list_fonts())
    except Exception:                                  # no Pango (a doc build, a bare checkout): trust the theme
        return set()


def pick_font(candidates, kind: str, probe: bool = False) -> str:
    """The first installed family, so a theme written on one machine still renders on another. Pango substitutes
    silently when a family is missing, which is how a deck ends up in a font nobody chose. A render never probes
    (see fonts_available); bin/themes.py check does, and says which family is missing."""
    if not probe:
        return candidates[0]
    have = fonts_available()
    if not have:
        return candidates[0]
    for c in candidates:
        if c in have:
            return c
    _warn(f"none of the {kind} fonts {candidates} is installed; Pango will substitute")
    return candidates[0]


def load(name: str = None, probe_fonts: bool = False) -> dict:
    """The theme as a flat dict: the seven roles, the seven accents, the four numbers, the fonts, the code style,
    plus `name`, `mode` and `description`. Unknown keys are kept, missing ones inherited from the default."""
    name = name or active_name()
    with open(path_of(DEFAULT)) as f:
        t = json.load(f)
    if name != DEFAULT:
        p = path_of(name)
        if not os.path.exists(p):
            raise SystemExit(f"theme: no such theme '{name}'. Available: {', '.join(names())} "
                             f"(see AGENTS.md, 'Choosing the look')")
        with open(p) as f:
            over = json.load(f)
        accents = dict(t["accents"]); accents.update(over.pop("accents", {}))
        t.update(over); t["accents"] = accents
    t["name"] = name
    t["font"] = pick_font([t["font"]] + t.get("font_fallbacks", []), "body", probe_fonts)
    t["code_font"] = pick_font([t["code_font"]] + t.get("code_font_fallbacks", []), "code", probe_fonts)
    return t


def validate(t: dict) -> list:
    """What makes a theme unusable on a stage, as a list of sentences. Empty means the theme is fit to present."""
    bad = []
    for k in ROLES + NUMBERS + ["font", "code_font", "code_style", "mode", "description"]:
        if k not in t:
            bad.append(f"missing key '{k}'")
    for k in ACCENTS:
        if k not in t.get("accents", {}):
            bad.append(f"missing accent '{k}'")
    if bad:
        return bad
    bg = t["bg"]
    if t["mode"] not in ("dark", "light"):
        bad.append(f"mode is '{t['mode']}', not dark or light")
    if (luminance(bg) < 0.5) != (t["mode"] == "dark"):
        bad.append(f"mode says {t['mode']} but the background {bg} is not")
    for role, need in (("text", 7.0), ("caption", 4.5), ("muted", 4.5), ("hi", 3.0)):
        r = contrast(t[role], bg)
        if r < need:
            bad.append(f"{role} {t[role]} has {r:.1f}:1 against the background, needs {need}:1")
    acc = t["accents"]
    for k in ACCENTS:
        r = contrast(acc[k], bg)
        if r < 3.0:
            bad.append(f"accent {k} {acc[k]} has {r:.1f}:1 against the background, needs 3:1")
    keys = ACCENTS
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            d = distance(acc[a], acc[b])
            if d < 22:
                bad.append(f"accents {a} {acc[a]} and {b} {acc[b]} are {d:.0f} apart, needs 22: they read as one colour")
    return bad
