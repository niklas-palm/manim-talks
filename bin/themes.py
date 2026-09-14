#!/usr/bin/env python3
"""The styles a deck can be presented in: list them, check one is fit to present, see them side by side, or take one
from a PowerPoint file.

    bin/themes.py list                            every theme with its mode and one line about it
    bin/themes.py check [name ...]                contrast, accent distance and installed fonts; the default is all
    bin/themes.py preview [talk] [Scene]          the same frame in every theme -> media/themes/<talk>-<Scene>.png
    bin/themes.py from-pptx <file.pptx> <name>    a company's theme -> themes/local/<name>.json, never committed

A theme is chosen with THEME=<name> for one render, a `.theme` file in a talk folder for that talk, or `.theme` at the
repository root for the project. AGENTS.md, "Choosing the look", is the guide an agent reads.
"""
import glob
import json
import os
import re
import subprocess
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import theme as T
from lib.talks import dir_of

REPO = T.REPO
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"


def cmd_list():
    print(f"{'theme':22s} {'mode':6s} description")
    for n in T.names():
        t = T.load(n)
        print(f"{n:22s} {t['mode']:6s} {t['description']}")
    print(f"\nactive: {T.active_name()}   (THEME=<name>, a talk's .theme, or .theme at the repository root)")


def cmd_check(which):
    ok = True
    for n in which or T.names():
        t = T.load(n, probe_fonts=True)
        bad = T.validate(t)
        have = T.fonts_available()
        for kind, fam in (("body", t["font"]), ("code", t["code_font"])):
            if have and fam not in have:
                bad.append(f"the {kind} font '{fam}' is not installed; Pango will substitute one")
        print(f"{n:22s} {'ok' if not bad else 'FAIL'}")
        for b in bad:
            print("   -", b)
        ok = ok and not bad
    return 0 if ok else 1


def cmd_preview(talk: str, scene: str):
    """One frame of a real deck in every theme, tiled. The frame is rendered with manim -s (the last frame only), so a
    sheet of ten themes takes about a minute. Look at it before choosing; a palette that reads on a screen can lose a
    colour on a projector."""
    root = dir_of(talk)
    src = next((f for f in sorted(glob.glob(f"{root}/scenes/s*.py"))
                if re.search(rf"^class {scene}\(", open(f).read(), re.M)), None)
    if not src:
        sys.exit(f"no scene {scene} in {root}/scenes")
    from PIL import Image, ImageDraw, ImageFont
    shots = []
    for n in T.names():
        out = f"/tmp/theme-preview/{n.replace('/', '-')}"
        env = dict(os.environ, THEME=n, PYTHONPATH=f".:{root}/scenes")
        subprocess.run([".venv/bin/manim", "-ql", "-s", "--media_dir", out, src, scene],
                       env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
        png = sorted(glob.glob(f"{out}/images/*/*.png"))
        if png:
            shots.append((n, png[-1]))
            print(f"  {n}")
    if not shots:
        sys.exit("nothing rendered")
    cols = 2
    w, h = Image.open(shots[0][1]).size
    tw, th = w // 2, h // 2
    band = 26
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + band)), (24, 24, 26))
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
    except Exception:
        font = ImageFont.load_default()
    d = ImageDraw.Draw(sheet)
    for i, (n, p) in enumerate(shots):
        x, y = (i % cols) * tw, (i // cols) * (th + band)
        sheet.paste(Image.open(p).convert("RGB").resize((tw, th)), (x, y + band))
        cap = f"{n}   {T.load(n)['description']}"
        while font.getlength(cap) > tw - 16 and len(cap) > 12:      # one line per tile, cut to fit: no label crosses into its neighbour
            cap = cap[:-2] + "\u2026"
        d.text((x + 8, y + 5), cap, fill=(232, 232, 232), font=font)
    os.makedirs(f"{REPO}/media/themes", exist_ok=True)
    dst = f"{REPO}/media/themes/{talk}-{scene}.png"
    sheet.save(dst)
    print(f"-> {dst}")


# ------------------------------------------------------------------------------------------------ from a PowerPoint file

def _colour(el):
    """A DrawingML colour element's hex, whichever of the two forms it uses."""
    for tag, attr in ((f"{A}srgbClr", "val"), (f"{A}sysClr", "lastClr")):
        c = el.find(tag) if el is not None else None
        if c is not None and c.get(attr):
            return "#" + c.get(attr)
    return None


def _scheme(zf) -> dict:
    """The colour and font scheme of the first theme part: dk1, lt1, dk2, lt2, accent1..6, and the two typefaces."""
    import xml.etree.ElementTree as ET
    name = next(n for n in zf.namelist() if re.match(r"ppt/theme/theme\d+\.xml$", n))
    root = ET.fromstring(zf.read(name))
    cs = root.find(f".//{A}clrScheme")
    cols = {}
    for child in cs:
        key = child.tag.split("}")[1]
        cols[key] = _colour(child)
    fs = root.find(f".//{A}fontScheme")
    fonts = {}
    for which in ("majorFont", "minorFont"):
        latin = fs.find(f"{A}{which}/{A}latin")
        fonts[which] = latin.get("typeface") if latin is not None else None
    return cols, fonts


def _master_bg(zf, cols) -> tuple:
    """The slide master's background colour, and whether it is a picture or gradient we cannot import."""
    import xml.etree.ElementTree as ET
    names = [n for n in zf.namelist() if re.match(r"ppt/slideMasters/slideMaster\d+\.xml$", n)]
    if not names:
        return None, ""
    root = ET.fromstring(zf.read(sorted(names)[0]))
    cmap = root.find(f"{P}clrMap")
    mapping = dict(cmap.attrib) if cmap is not None else {}

    def resolve(scheme_name):
        target = mapping.get(scheme_name, scheme_name)
        return cols.get({"dk1": "dk1", "lt1": "lt1", "dk2": "dk2", "lt2": "lt2"}.get(target, target))
    bg = root.find(f".//{P}bg")
    if bg is None:
        return None, ""
    if bg.find(f".//{A}blipFill") is not None:
        return None, "the master background is a picture; only its colours are imported"
    if bg.find(f".//{A}gradFill") is not None:
        stop = bg.find(f".//{A}gradFill//{A}gs/{A}srgbClr")
        return ("#" + stop.get("val") if stop is not None else None), "the master background is a gradient; its first stop is used"
    solid = bg.find(f".//{A}solidFill")
    if solid is not None:
        c = _colour(solid)
        if c:
            return c, ""
        sc = solid.find(f"{A}schemeClr")
        if sc is not None:
            return resolve(sc.get("val")), ""
    ref = bg.find(f"{P}bgRef/{A}schemeClr")
    if ref is not None:
        return resolve(ref.get("val")), ""
    return None, ""


def cmd_from_pptx(path: str, name: str):
    """A company's PowerPoint theme as a theme file: its background, its two typefaces and its six accents, each lifted
    away from the background until it can be seen from the back row, then spread until no two read as one colour.

    What is not imported, on purpose: logos, picture backgrounds, slide layouts. A talk here is a picture that unfolds,
    not a slide with a brand frame; the colours and the type are what carry a house style into it. The result goes to
    themes/local, which git ignores: a company's palette is theirs, not this repository's."""
    with zipfile.ZipFile(path) as zf:
        cols, fonts = _scheme(zf)
        bg, note = _master_bg(zf, cols)
    bg = bg or cols.get("lt1") or "#FFFFFF"
    dark = T.luminance(bg) < 0.5
    ink = "#FFFFFF" if dark else "#000000"
    for cand in (cols.get("dk1") if not dark else cols.get("lt1"), ink):
        if cand and T.contrast(cand, bg) >= 7:
            ink = cand
            break
    acc = [cols.get(f"accent{i}") or ink for i in range(1, 7)]
    slots = _assign(acc, bg, dark)
    t = {
        "mode": "dark" if dark else "light",
        "description": f"Imported from {os.path.basename(path)}: its background, type and accents. Not committed.",
        "font": fonts.get("minorFont") or "Helvetica",
        "font_fallbacks": ["Helvetica", "Arial", "DejaVu Sans"],
        "code_font": "Menlo",
        "code_font_fallbacks": ["Monaco", "DejaVu Sans Mono"],
        "code_style": "monokai" if dark else "xcode",
        "bg": bg,
        "text": ink,
        "muted": T.blend(bg, ink, 0.62),
        "dim": T.blend(bg, ink, 0.30),
        "caption": T.blend(bg, ink, 0.80),
        "hi": T.blend(bg, ink, 0.96),
        "panel": T.blend(bg, ink, 0.06),
        "accents": slots,
    }
    os.makedirs(f"{T.THEME_DIR}/local", exist_ok=True)
    dst = f"{T.THEME_DIR}/local/{name}.json"
    with open(dst, "w") as f:
        json.dump(t, f, indent=2)
        f.write("\n")
    loaded = T.load(f"local/{name}")
    bad = T.validate(loaded)
    print(f"-> {dst}   THEME=local/{name} bin/render.sh <talk> ql")
    if note:
        print(f"   note: {note}")
    print(f"   {'fit to present' if not bad else 'still not fit to present:'}")
    for b in bad:
        print("   -", b)
    print("   themes/local is ignored by git: a company's palette does not belong in this repository.")


# What each slot means, as the hue the house style uses for it: cool, warm, deep, fresh, growth, spice. An imported
# palette is matched to these rather than taken in the template's own order, so a deck that calls its model "the deep
# accent" still looks like itself in a company's colours.
SLOT_HUES = {"a1": 191, "a2": 41, "a3": 260, "a4": 174, "a5": 111, "a6": 15}


def _hue(c: str) -> float:
    import colorsys
    r, g, b = T.rgb(c)
    return colorsys.rgb_to_hls(r, g, b)[0] * 360


def _assign(acc: list, bg: str, dark: bool) -> dict:
    """Six imported accents onto the six slots, by the closest match of hue to what each slot means, then an alert red
    of their own character, then everything lifted off the background and pushed apart."""
    import colorsys
    import itertools

    def gap(a, b):
        d = abs(a - b) % 360
        return min(d, 360 - d)
    keys = list(SLOT_HUES)
    best = min(itertools.permutations(range(6)),
               key=lambda perm: sum(gap(_hue(acc[perm[i]]), SLOT_HUES[keys[i]]) for i in range(6)))
    slots = {keys[i]: acc[best[i]] for i in range(6)}
    # "Wrong" is a red the palette could have had: the hue of alarm, the saturation and lightness of these accents.
    hls = [colorsys.rgb_to_hls(*T.rgb(c)) for c in acc]
    sat = sorted(h[2] for h in hls)[len(hls) // 2]
    lit = sorted(h[1] for h in hls)[len(hls) // 2]
    alert = T.hex_of(colorsys.hls_to_rgb(2 / 360, min(0.72, max(0.3, lit)), max(0.55, sat)))
    out = {"alert": T.lift(alert, bg, 3.2)}            # first, so spreading moves the other slots and "wrong" stays red
    out.update({k: T.lift(v, bg, 3.2) for k, v in slots.items()})
    return _spread(out, bg)


def _spread(slots: dict, bg: str, need: float = 22.0) -> dict:
    """Push accents apart until no two read as one colour, keeping each as close to the original as possible. Corporate
    palettes are often three blues and two greys; without this, two meanings in a deck would look the same."""
    import colorsys
    keys = list(slots)
    for _ in range(4):
        worst = None
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                d = T.distance(slots[a], slots[b])
                if d < need and (worst is None or d < worst[0]):
                    worst = (d, a, b)
        if not worst:
            break
        _, a, b = worst
        for slot in (b, a):                                   # move the later slot first; a1 keeps its hue if it can
            r, g, bl = T.rgb(slots[slot])
            h, l, s = colorsys.rgb_to_hls(r, g, bl)
            for dh in (0.04, -0.04, 0.08, -0.08, 0.12, -0.12, 0.16, -0.16, 0.2, -0.2):
                for dl in (0, 0.08, -0.08, 0.16, -0.16):
                    c = T.hex_of(colorsys.hls_to_rgb((h + dh) % 1.0, min(0.95, max(0.05, l + dl)), min(1.0, s * 1.15)))
                    if T.contrast(c, bg) < 3.2:
                        continue
                    if min(T.distance(c, slots[k]) for k in keys if k != slot) >= need:
                        slots[slot] = c
                        break
                else:
                    continue
                break
            if T.distance(slots[a], slots[b]) >= need:
                break
    return slots


if __name__ == "__main__":
    args = sys.argv[1:] or ["list"]
    what, rest = args[0], args[1:]
    os.chdir(REPO)
    if what == "list":
        cmd_list()
    elif what == "check":
        sys.exit(cmd_check(rest))
    elif what == "preview":
        cmd_preview(rest[0] if rest else "agents", rest[1] if len(rest) > 1 else "TheApi")
    elif what == "from-pptx":
        if len(rest) < 2:
            sys.exit("usage: bin/themes.py from-pptx <file.pptx> <name>")
        cmd_from_pptx(rest[0], rest[1])
    else:
        sys.exit(__doc__)
