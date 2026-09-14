#!/usr/bin/env python3
"""Structural checks for a talk, the things a review should not have to find by eye. Usage: bin/check.py <talk> [ql|qm|qh]
Reports, per talk: the files a talk must have, that objects.py declares its colours with set_thread, that every scene
class wrote as many notes as it rendered steps, text sizes below 12, on-screen strings that look like sentences (more
than 14 words in a label), captions swapped more than once in a step, and a group animated together with one of its
members in one play (the trap that leaves the member behind). Exit code 1 if anything is
flagged. It is a checklist helper, not a judge: docs/review.md is the review."""
import glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import theme as _theme

talk = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
Q = {"ql": "480p15", "qm": "720p30", "qh": "1080p60"}[sys.argv[2] if len(sys.argv) > 2 else "qh"]
root = f"talks/{talk}"
flags = []

# The look this talk presents in, and whether it is fit to present: contrast against the background, accents that can
# be told apart, fonts that are installed. bin/themes.py check says the same for every theme.
_name = open(f"{root}/.theme").read().strip() if os.path.exists(f"{root}/.theme") else _theme.active_name()
_th = _theme.load(_name, probe_fonts=True)
flags += [f"theme {_name}: {b}" for b in _theme.validate(_th)]
_have = _theme.fonts_available()
flags += [f"theme {_name}: the {k} font '{_th[k]}' is not installed; Pango will substitute one"
          for k in ("font", "code_font") if _have and _th[k] not in _have]

# A hue named in a scene is a hue that will not follow the theme: a talk maps its nouns onto slots in objects.py.
for _f in sorted(glob.glob(f"{root}/scenes/s*.py")):
    for _hue in re.findall(r"\b(BLUE|YELLOW|VIOLET|TEAL|GREEN|ORANGE|RED)\b", open(_f).read()):
        flags.append(f"{os.path.basename(_f)} names the colour {_hue}: use the meaning from objects.py instead")

for f, what in [("script.md", "the spine, moves and sources"), ("README.md", "what the talk is"), ("scenes/objects.py", "the talk's colours and shared drawings")]:
    if not os.path.exists(f"{root}/{f}"):
        flags.append(f"missing {f} ({what})")
if os.path.exists(f"{root}/script.md") and not any(l.startswith("# ") for l in open(f"{root}/script.md")):
    flags.append("script.md has no '# title' line (bin/build.py uses it as the deck title)")
if os.path.exists(f"{root}/scenes/objects.py") and "set_thread(" not in open(f"{root}/scenes/objects.py").read():
    flags.append("objects.py does not call set_thread: titles and captions will not colour the talk's nouns")

for f in sorted(glob.glob(f"{root}/scenes/s*.py")):
    src = open(f).read()
    name = os.path.basename(f)
    if "from lib.palette import *" not in src:
        flags.append(f"{name}: does not import lib.palette")
    for m in re.finditer(r"label\((\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|[\w.\[\]]+(?:\([^()]*\))?),\s*(\d+(?:\.\d+)?)\b", src):
        if float(m.group(2)) < 12:
            flags.append(f"{name}: label size {m.group(2)} below 12: {m.group(1)[:40]}")
    for m in re.finditer(r"(?:label|caption|swap_caption)\((?:self,\s*(?:cap,\s*)?)?\"([^\"]{60,})\"", src):
        if len(m.group(1).split()) > 14:
            flags.append(f"{name}: an on-screen sentence of {len(m.group(1).split())} words; move it to the note: \"{m.group(1)[:50]}...\"")
    # notes versus steps, per class
    classes = list(re.finditer(r"^class (\w+)\(TalkSlide\):", src, re.M))
    for i, c in enumerate(classes):
        body = src[c.end(): classes[i + 1].start() if i + 1 < len(classes) else len(src)]
        if not re.search(r"self\.finish\(", body):
            flags.append(f"{name}: {c.group(1)} has no finish(): the last step has no note")
        idx = glob.glob(f"{root}/media/videos/{name[:-3]}/{Q}/sections/{c.group(1)}.json")
        notes_file = f"{root}/media/notes/{c.group(1)}.json"
        if idx and os.path.exists(notes_file):   # both written by the render, so loops and branches are counted right
            steps, notes = len(json.load(open(idx[0]))), len(json.load(open(notes_file)))
            if steps != notes:
                flags.append(f"{name}: {c.group(1)} rendered {steps} steps but wrote {notes} notes")
        # a group and one of its members animated in the same play: the member's target is taken before the group moves
        for m in re.finditer(r"self\.play\((.*?)\)\s*\n", body, re.S):
            call = m.group(1)
            groups = set(re.findall(r"(?<![\w.\]])([A-Za-z_]\w*)\.animate", call))
            members = set(re.findall(r"([A-Za-z_]\w*)(?:\[[^\]]+\]|\.[a-z_]\w*)\.animate", call))
            both = sorted(groups & members)
            if both:
                flags.append(f"{name}: {c.group(1)} animates {', '.join(both)} and one of its members in the same play (see docs/manim.md); do the member change in its own play first")
        for step in re.split(r"self\.next_slide\(", body)[:-1]:
            if len(re.findall(r"(?<!swap_)caption\(self", step)) + step.count("swap_caption(") > 1:
                flags.append(f"{name}: {c.group(1)} changes the caption more than once inside one step")

print(f"{talk}: {'ok' if not flags else str(len(flags)) + ' flags'}  (theme {_name}, {_th['mode']})")
for x in flags:
    print("  -", x)
sys.exit(1 if flags else 0)
