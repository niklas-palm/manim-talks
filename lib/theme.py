"""The look, in one place: a theme is the only thing that decides colour, type, corner and stroke.

`lib/palette.py` reads a theme at import and derives every constant the helpers use, so a deck's drawing code names
meanings ("the model is accent three") and never a hue. Changing the theme changes every talk in the repository and
nothing else. See AGENTS.md for the styles that ship and how to choose one; docs/library.md for the tokens.

Resolution order, first hit wins:
    THEME=<name>            environment variable, for one render
    <talk>/.theme           one line, that talk's style; every tool that knows the talk resolves it (active_name)
    .theme                  one line at the repository root, the project's style
    dark                    the fallback

There are two styles and a way in: `dark`, `bright`, and whatever `bin/themes.py from-pptx` makes of a PowerPoint
template (under `themes/local`, never committed). Two is the point: a deck is judged on whether the picture teaches,
and a gallery of styles is a way of not deciding.

A theme file is `themes/<name>.json`; keys it leaves out are taken from `themes/dark.json`, so a variant can be
five lines. Every value is either a hex colour, a number, a font family name or a Pygments style name.

Why the numbers are in the theme and not in the scenes: a style is not only its palette. The bright style is not the
dark one with the colours swapped; it has thinner lines, smaller corners and fainter fills, because a pale ground shows
weight differently. The helpers take their corner radius, stroke width and fill opacity from here and scale the rest
proportionally, so those three numbers reach every drawing.
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEME_DIR = os.path.join(REPO, "themes")
DEFAULT = "dark"   # the fallback; "bright" and any imported theme inherit the keys they do not set

# Colour roles. A theme must give each one a value; a variant inherits the ones it omits.
ROLES = ["bg", "text", "muted", "dim", "caption", "hi", "panel"]
# Accent slots. a1..a6 are the talk's vocabulary; alert is "wrong, hot, refused" and is never a second meaning.
# A theme keeps each slot's character so that decks read the same across themes: a1 cool, a2 warm, a3 deep, a4 fresh,
# a5 growth, a6 spice, alert wrong.
ACCENTS = ["a1", "a2", "a3", "a4", "a5", "a6", "alert"]
NUMBERS = ["radius", "stroke", "fill", "solid"]   # the feel: a corner, a line weight, a container fill, a solid mark

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
    makes a real corporate palette usable on a stage. Returns the colour unchanged if it already passes, and the
    extreme it was heading for when the ratio cannot be reached at all (a mid grey ground caps every colour); the
    caller learns that from validate(), which is where an unusable theme is refused.

    The direction is whichever of black and white has more contrast to give against this background. That crossover is
    at a relative luminance of about 0.18, not at 0.5: a light grey ground wants dark ink."""
    if contrast(c, bg) >= ratio:
        return c
    target = "#000000" if contrast("#000000", bg) > contrast("#FFFFFF", bg) else "#FFFFFF"
    best = c
    for i in range(1, steps + 1):
        best = blend(c, target, i / steps)
        if contrast(best, bg) >= ratio:
            break
    return best


# ------------------------------------------------------------------------------------------------ loading

def is_dark(bg: str) -> bool:
    """Whether a background wants light ink. White text against it beats black text against it: the WCAG crossover,
    around luminance 0.18, rather than the midpoint, which would call a light grey dark."""
    return contrast("#FFFFFF", bg) > contrast("#000000", bg)


def names() -> list:
    """Every theme that ships, plus anything under themes/local (extracted from a PowerPoint file, never committed)."""
    out = sorted(f[:-5] for f in os.listdir(THEME_DIR) if f.endswith(".json"))
    local = os.path.join(THEME_DIR, "local")
    if os.path.isdir(local):
        out += sorted("local/" + f[:-5] for f in os.listdir(local) if f.endswith(".json"))
    return out


def path_of(name: str) -> str:
    return os.path.join(THEME_DIR, f"{name}.json")


def _named_in(folder: str) -> str:
    """The theme named by a `.theme` file in `folder`, or "" if there is none. Whitespace only counts as none."""
    f = os.path.join(REPO, folder, ".theme")
    if os.path.exists(f):
        with open(f) as fh:
            return fh.read().strip()
    return ""


def active_name(root: str = None) -> str:
    """The theme a talk presents in, in one place and in the documented order: THEME, then the talk's own .theme, then
    the repository's, then dark. `root` is the talk folder (`talks/x` or `out/x`); every tool that knows which talk it
    is working on passes it, so a deck cannot be built in one style and rendered in another."""
    env = os.environ.get("THEME", "").strip()
    if env:
        return env
    return (_named_in(root) if root else "") or _named_in("") or DEFAULT


def fonts_available():
    """The installed families, asked of Pango, or None when Pango cannot be asked (a tool run under an interpreter
    without it). Only the checkers call this: a render uses what the theme declares, so that what is checked is what
    will be drawn. None and the empty set are different answers, and a checker must not read the first as the second."""
    try:
        import manimpango
        return set(manimpango.list_fonts())
    except Exception:
        return None


def _read(path: str) -> dict:
    """A theme file as a dict, or a message naming the file. A half-written theme is a normal thing to have on disk
    while editing one; a traceback with no file name in it is not a normal thing to read."""
    try:
        with open(path) as f:
            t = json.load(f)
    except json.JSONDecodeError as e:
        raise SystemExit(f"theme: {path} is not valid JSON: {e}")
    if not isinstance(t, dict):
        raise SystemExit(f"theme: {path} must be a JSON object, not {type(t).__name__}")
    return t


def sheet_bg(t: dict) -> str:
    """The padding between frames on a contact sheet: a shade off the deck's own ground, so a bright deck's sheets are
    not framed in black. bin/shots.py, bin/seams.py, bin/review.sh and bin/themes.py all tile frames."""
    return blend(t["bg"], t["text"], 0.10)


def missing_fonts(t: dict):
    """The families this theme asks for that are not installed, or None when that cannot be determined here. Pango
    substitutes a missing family silently, which is how a deck ends up in a font nobody chose, so the checkers report
    it rather than the render guessing. Run them under the project's interpreter, or the answer is None."""
    have = fonts_available()
    if have is None:
        return None
    return [t[k] for k in ("font", "code_font") if t[k] not in have]


def load(name: str = None) -> dict:
    """The theme as a flat dict: the seven roles, the seven accents, the four numbers, the fonts, the code style,
    plus `name`, `mode` and `description`. Unknown keys are kept, missing ones inherited from the default."""
    name = name or active_name()
    t = _read(path_of(DEFAULT))
    if name != DEFAULT:
        p = path_of(name)
        if not os.path.exists(p):
            raise SystemExit(f"theme: no such theme '{name}'. Available: {', '.join(names())} "
                             f"(see AGENTS.md, 'Choosing the look')")
        over = _read(p)
        accents = dict(t["accents"]); accents.update(over.pop("accents", {}))
        t.update(over); t["accents"] = accents
    t["name"] = name
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
    for k in ROLES + list(t["accents"]):
        v = t["accents"].get(k, t.get(k))
        if not (isinstance(v, str) and re.fullmatch(r"#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})", v)):
            bad.append(f"{k} is {v!r}, not a hex colour like #1A2B3C")
    for k in NUMBERS:
        if not isinstance(t[k], (int, float)) or isinstance(t[k], bool) or not 0 <= t[k] <= 12:
            bad.append(f"{k} is {t[k]!r}, not a number between 0 and 12")
    if bad:
        return bad                                     # the colour maths below would only raise on these
    bg = t["bg"]
    if t["mode"] not in ("dark", "light"):
        bad.append(f"mode is '{t['mode']}', not dark or light")
    elif is_dark(bg) != (t["mode"] == "dark"):
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
