#!/usr/bin/env python3
"""The styles a deck can be presented in: list them, check one is fit to present, see them side by side, or take one
from a PowerPoint file.

    .venv/bin/python bin/themes.py list                          every theme with its mode and one line about it
    .venv/bin/python bin/themes.py check [name ...]              contrast, accent distance, installed fonts; all by default
    .venv/bin/python bin/themes.py preview <talk> <Scene>        the same frame in every theme -> media/themes/
    .venv/bin/python bin/themes.py from-pptx <file> <name>       a company's theme -> themes/local/<name>.json

Run them with the project's interpreter: under another one the font check cannot ask Pango and says so instead.

A theme is chosen with THEME=<name> for one render, a `.theme` file in a talk folder for that talk, or `.theme` at the
repository root for the project. AGENTS.md, "Choosing the look", is the guide an agent reads.
"""
import colorsys
import glob
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import theme as _theme
from lib.talks import dir_of, scenes_of

REPO = _theme.REPO
NS_DRAWING = "{http://schemas.openxmlformats.org/drawingml/2006/main}"        # a:  colours and fonts
NS_PRESENT = "{http://schemas.openxmlformats.org/presentationml/2006/main}"   # p:  slides and masters


def cmd_list():
    print(f"{'theme':22s} {'mode':6s} description")
    for n in _theme.names():
        try:                                    # a half-written theme is a normal thing to have while editing one
            t = _theme.load(n)              # and formatting one is as likely to fail as loading it
            print(f"{n:22s} {t['mode']:6s} {t['description']}")
        except (SystemExit, Exception) as e:
            print(f"{n:22s} {'?':6s} {e}")
    print(f"\nactive: {_theme.active_name()}   (THEME=<name>, a talk's .theme, or .theme at the repository root)")


def cmd_check(which):
    ok = True
    for n in which or _theme.names():
        try:                                        # one half-written theme must not hide the verdict on the others
            t = _theme.load(n)
        except (SystemExit, Exception) as e:    # SystemExit is not an Exception; name both, or one theme hides the rest
            print(f"{n:22s} FAIL"); print("   -", e); ok = False; continue
        bad = _theme.validate(t)
        missing = _theme.missing_fonts(t)
        if missing is None:
            print(f"{n:22s} fonts not checked: Pango is not available under {os.path.basename(sys.executable)}; "
                  f"run .venv/bin/python bin/themes.py check")
        bad += [f"the font '{fam}' is not installed; Pango will substitute one nobody chose" for fam in missing or []]
        print(f"{n:22s} {'ok' if not bad else 'FAIL'}")
        for b in bad:
            print("   -", b)
        ok = ok and not bad
    return 0 if ok else 1


def cmd_preview(talk: str, scene: str):
    """One frame of a real deck in every theme, tiled. The frame is rendered with manim -s (the last frame only), so a
    sheet of both styles, and any imported one, takes well under a minute. Look at it before choosing; a palette that reads on a screen can lose a
    colour on a projector."""
    root = dir_of(talk)
    # Asked of the library, so "a scene" means the same thing here as everywhere else, and a name typed by hand is not
    # treated as a regular expression.
    src = next((f"{root}/scenes/{stem}.py" for stem, sc in scenes_of(root) if sc == scene), None)
    if not src:
        sys.exit(f"no scene {scene} in {root}/scenes")
    from PIL import Image, ImageDraw, ImageFont
    work = tempfile.mkdtemp(prefix="theme-preview-")     # a fresh directory: a frame left from another run would be
    shots = []                                           # labelled with this theme, and a fixed /tmp path is not ours
    try:
        for n in _theme.names():
            out = f"{work}/{n.replace('/', '-')}"
            env = dict(os.environ, THEME=n, PYTHONPATH=f".:{root}/scenes")
            r = subprocess.run([".venv/bin/manim", "-ql", "-s", "--media_dir", out, src, scene],
                               env=env, capture_output=True, text=True)
            if r.returncode:
                sys.exit(f"rendering {scene} in {n} failed:\n{((r.stdout or '') + (r.stderr or ''))[-2000:]}")
            png = sorted(glob.glob(f"{out}/images/*/{scene}*.png"))
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
        deck = _theme.of(root)
        sheet = Image.new("RGB", (cols * tw, rows * (th + band)), _theme.sheet_rgb(root))
        ink = _theme.rgb255(deck["text"])          # the labels sit on the padding, so they follow it
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
        except Exception:
            font = ImageFont.load_default()
        d = ImageDraw.Draw(sheet)
        for i, (n, p) in enumerate(shots):
            x, y = (i % cols) * tw, (i // cols) * (th + band)
            sheet.paste(Image.open(p).convert("RGB").resize((tw, th)), (x, y + band))
            cap = f"{n}   {_theme.load(n)['description']}"
            while font.getlength(cap) > tw - 16 and len(cap) > 12:      # one line per tile, cut to fit: no label crosses into its neighbour
                cap = cap[:-2] + "\u2026"
            d.text((x + 8, y + 5), cap, fill=ink, font=font)
        os.makedirs(f"{REPO}/media/themes", exist_ok=True)
        dst = f"{REPO}/media/themes/{talk}-{scene}.png"
        sheet.save(dst)
        print(f"-> {dst}")

    finally:
        shutil.rmtree(work, ignore_errors=True)

# ------------------------------------------------------------------------------------------------ from a PowerPoint file

def _colour(el):
    """A DrawingML colour element's hex, whichever of the two forms it uses."""
    for tag, attr in ((f"{NS_DRAWING}srgbClr", "val"), (f"{NS_DRAWING}sysClr", "lastClr")):
        c = el.find(tag) if el is not None else None
        if c is not None and c.get(attr):
            return "#" + c.get(attr)
    return None


def _scheme(zf) -> tuple:
    """The colour and font scheme of the first theme part: dk1, lt1, dk2, lt2, accent1..6, and the two typefaces."""
    name = next(iter(sorted(n for n in zf.namelist() if re.match(r"ppt/theme/theme\d+\.xml$", n))), None)   # theme1 is the deck's; zip order is not
    if not name:
        sys.exit("that file has no PowerPoint theme part: open it in PowerPoint and save it as .pptx")
    root = ET.fromstring(zf.read(name))
    cs = root.find(f".//{NS_DRAWING}clrScheme")
    if cs is None:
        sys.exit(f"{name} carries no colour scheme: there is nothing to import")
    cols = {}
    for child in cs:
        key = child.tag.split("}")[1]
        cols[key] = _colour(child)
    fs = root.find(f".//{NS_DRAWING}fontScheme")
    if fs is None:
        return cols, {}
    fonts = {}
    for which in ("majorFont", "minorFont"):
        latin = fs.find(f"{NS_DRAWING}{which}/{NS_DRAWING}latin")
        fonts[which] = latin.get("typeface") if latin is not None else None
    return cols, fonts


def _master_bg(zf, cols) -> tuple:
    """The slide master's background colour, and whether it is a picture or gradient we cannot import."""
    names = [n for n in zf.namelist() if re.match(r"ppt/slideMasters/slideMaster\d+\.xml$", n)]
    if not names:
        return None, ""
    root = ET.fromstring(zf.read(sorted(names)[0]))
    cmap = root.find(f"{NS_PRESENT}clrMap")
    mapping = dict(cmap.attrib) if cmap is not None else {}

    def resolve(scheme_name):
        target = mapping.get(scheme_name, scheme_name)
        return cols.get(target)
    bg = root.find(f".//{NS_PRESENT}bg")
    if bg is None:
        return None, ""
    if bg.find(f".//{NS_DRAWING}blipFill") is not None:
        return None, "the master background is a picture; only its colours are imported"
    if bg.find(f".//{NS_DRAWING}gradFill") is not None:
        stop = bg.find(f".//{NS_DRAWING}gradFill//{NS_DRAWING}gs/{NS_DRAWING}srgbClr")
        return ("#" + stop.get("val") if stop is not None else None), "the master background is a gradient; its first stop is used"
    solid = bg.find(f".//{NS_DRAWING}solidFill")
    if solid is not None:
        c = _colour(solid)
        if c:
            return c, ""
        sc = solid.find(f"{NS_DRAWING}schemeClr")
        if sc is not None:
            return resolve(sc.get("val")), ""
    ref = bg.find(f"{NS_PRESENT}bgRef/{NS_DRAWING}schemeClr")
    if ref is not None:
        return resolve(ref.get("val")), ""
    return None, ""


def cmd_from_pptx(path: str, name: str):
    """A company's PowerPoint theme as a theme file: its background, its two typefaces and its six accents, each lifted
    away from the background until it can be seen from the back row, then spread until no two read as one colour.

    What is not imported, on purpose: logos, picture backgrounds, slide layouts. A talk here is a picture that unfolds,
    not a slide with a brand frame; the colours and the type are what carry a house style into it. The result goes to
    themes/local, which git ignores: a company's palette is theirs, not this repository's."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", name):   # the same bound lib/theme.py loads by
        sys.exit(f"not a theme name: {name!r} (letters, digits, dot, dash and underscore, up to 64: it becomes a file "
                 f"name, and a name this repository cannot load again is no use)")
    try:
        zf = zipfile.ZipFile(path)
    except FileNotFoundError:
        sys.exit(f"no such file: {path}")
    except zipfile.BadZipFile:
        sys.exit(f"{path} is not a .pptx (a .pptx is a zip; a .ppt or an alias is not)")
    except (IsADirectoryError, PermissionError) as e:
        sys.exit(f"cannot read {path}: {e}")
    with zf:
        cols, fonts = _scheme(zf)
        bg, note = _master_bg(zf, cols)
    bg = bg or cols.get("lt1") or "#FFFFFF"
    dark = _theme.is_dark(bg)
    ink = "#FFFFFF" if dark else "#000000"
    for cand in (cols.get("dk1") if not dark else cols.get("lt1"), ink):
        if cand and _theme.contrast(cand, bg) >= 7:
            ink = cand
            break
    acc = [cols.get(f"accent{i}") or ink for i in range(1, 7)]
    slots = _assign(acc, bg)
    # A style is not only its palette: a pale ground wants thinner lines and smaller corners. Without these four an
    # imported light theme would inherit the dark style's weights, which is what a white template least wants.
    feel = _theme.load("dark" if dark else "bright")
    t = {
        "mode": "dark" if dark else "light",
        "description": f"Imported from {os.path.basename(path)}: its background, type and accents. Not committed.",
        "font": fonts.get("minorFont") or "Helvetica",
        "code_font": "Menlo",
        "code_style": "monokai" if dark else "xcode",
        "bg": bg,
        "text": ink,
        "muted": _theme.blend(bg, ink, 0.62),
        "dim": _theme.blend(bg, ink, 0.30),
        "caption": _theme.blend(bg, ink, 0.80),
        "hi": _theme.blend(bg, ink, 0.96),
        "panel": _theme.blend(bg, ink, 0.06),
        "accents": slots,
        **{k: feel[k] for k in _theme.NUMBERS},
    }
    os.makedirs(f"{_theme.THEME_DIR}/local", exist_ok=True)
    dst = f"{_theme.THEME_DIR}/local/{name}.json"
    # Validate before replacing anything: the file at dst may be a hand-edited theme, and an import that turns out to be
    # unusable must not be what is left of it. The temporary name is a real theme name so it can be loaded and merged.
    # The temporary name starts with a dot, which theme.names() skips, so a process killed here cannot leave something
    # that looks like a style; and the finally clause means it does not outlive this function either way.
    tmp_name = f".importing{os.getpid()}"
    tmp = f"{_theme.THEME_DIR}/local/{tmp_name}.json"
    try:
        with open(tmp, "w") as f:
            json.dump(t, f, indent=2)
            f.write("\n")
        loaded = _theme.load(f"local/{tmp_name}")
        bad = _theme.validate(loaded)
        if bad:
            print(f"{os.path.basename(path)} does not make a theme that can be presented:")
            for b in bad:
                print("   -", b)
            sys.exit(f"nothing written{'' if not os.path.exists(dst) else f'; {dst} is untouched'}. "
                     f"Fix what is listed above, pick a different template, or write themes/local/{name}.json by hand "
                     f"from themes/bright.json.")
        os.replace(tmp, dst)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    print(f"-> {dst}   THEME=local/{name} bin/render.sh <talk> ql")
    if note:
        print(f"   note: {note}")
    fams = _theme.missing_fonts(loaded)
    if fams is None:
        print(f"   note: fonts not checked: Pango is not available under {os.path.basename(sys.executable)}")
    for fam in fams or []:
        print(f"   note: the font '{fam}' is not installed here; Pango will substitute one")
    print("   fit to present")
    print("   themes/local is ignored by git: a company's palette does not belong in this repository.")


# What each slot means, as the hue the house style uses for it: cool, warm, deep, fresh, growth, spice. An imported
# palette is matched to these rather than taken in the template's own order, so a deck that calls its model "the deep
# accent" still looks like itself in a company's colours.
SLOT_HUES = {"a1": 191, "a2": 41, "a3": 260, "a4": 174, "a5": 111, "a6": 15}
FLOOR = _theme.SEEN + 0.2   # what an imported accent must clear: a little above the bar, so a later nudge stays over it


def _hue(c: str) -> float:
    r, g, b = _theme.rgb(c)
    return colorsys.rgb_to_hls(r, g, b)[0] * 360


def _assign(acc: list, bg: str) -> dict:
    """Six imported accents onto the six slots, by the closest match of hue to what each slot means, then an alert red
    of their own character, then everything lifted off the background and pushed apart."""

    def gap(a, b):
        d = abs(a - b) % 360
        return min(d, 360 - d)
    keys = list(SLOT_HUES)
    best = min(itertools.permutations(range(6)),
               key=lambda perm: sum(gap(_hue(acc[perm[i]]), SLOT_HUES[keys[i]]) for i in range(6)))
    slots = {keys[i]: acc[best[i]] for i in range(6)}
    # "Wrong" is a red the palette could have had: the hue of alarm, the saturation and lightness of these accents.
    hls = [colorsys.rgb_to_hls(*_theme.rgb(c)) for c in acc]
    sat = sorted(h[2] for h in hls)[len(hls) // 2]
    lit = sorted(h[1] for h in hls)[len(hls) // 2]
    alert = _theme.hex_of(colorsys.hls_to_rgb(2 / 360, min(0.72, max(0.3, lit)), max(0.55, sat)))
    out = {"alert": _theme.lift(alert, bg, FLOOR)}          # first, so spreading moves the other slots and "wrong" stays red
    out.update({k: _theme.lift(v, bg, FLOOR) for k, v in slots.items()})
    return _spread(out, bg)


def _spread(slots: dict, bg: str) -> dict:
    """Push accents apart until no two read as one colour, moving each as little as possible. Corporate palettes are
    often three blues and two greys, and a grey has no hue to rotate: the candidates therefore carry a saturation floor,
    or the search would offer another grey and call it a change. Every round improves the worst pair by the most any one
    move can, rather than demanding one move that satisfies every pair at once, so it converges instead of giving up."""
    need = _theme.ACCENT_GAP
    keys = list(slots)

    def worst_pair():
        return min(((_theme.distance(slots[a], slots[b]), a, b)
                    for i, a in enumerate(keys) for b in keys[i + 1:]), key=lambda x: x[0])

    for _ in range(24):
        d, a, b = worst_pair()
        if d >= need:
            break
        moved = False
        for slot in (b, a):                                   # move the later slot first; a1 keeps its hue if it can
            others = [slots[k] for k in keys if k != slot]
            r, g, bl = _theme.rgb(slots[slot])
            h, l, s = colorsys.rgb_to_hls(r, g, bl)
            best, best_gap = None, min(_theme.distance(slots[slot], o) for o in others)
            for dh in [x / 40 for x in range(-16, 17)]:
                for dl in (0, 0.1, -0.1, 0.2, -0.2):
                    c = _theme.hex_of(colorsys.hls_to_rgb((h + dh) % 1.0, min(0.92, max(0.08, l + dl)),
                                                          min(1.0, max(0.45, s * 1.15))))
                    if _theme.contrast(c, bg) < FLOOR:
                        continue
                    gap = min(_theme.distance(c, o) for o in others)
                    if gap > best_gap + 0.5:
                        best, best_gap = c, gap
            if best:
                slots[slot] = best
                moved = True
                break
        if not moved:
            break                                             # nothing on offer improves it; validate() will refuse it
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
        if len(rest) < 2:
            sys.exit("usage: bin/themes.py preview <talk> <Scene>")
        cmd_preview(rest[0], rest[1])
    elif what == "from-pptx":
        if len(rest) < 2:
            sys.exit("usage: bin/themes.py from-pptx <file.pptx> <name>")
        cmd_from_pptx(rest[0], rest[1])
    else:
        sys.exit(__doc__)
