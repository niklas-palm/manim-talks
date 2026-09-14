#!/usr/bin/env python3
"""Structural checks for a talk, the things a review should not have to find by eye. Usage: bin/check.py <talk> [ql|qm|qh]
Reports, per talk: the style it presents in and whether that style is fit to present (contrast, accents that can be
told apart, fonts installed); any colour a scene names itself instead of taking from objects.py; the files a talk must
have; that objects.py declares its vocabulary with set_thread; that scene names are unique; that every scene class
wrote as many notes as it rendered steps, text sizes below 12, on-screen strings that look like sentences (more
than 14 words in a label), captions swapped more than once in a step, and a group animated together with one of its
members in one play (the trap that leaves the member behind). Exit code 1 if anything is
flagged. It is a checklist helper, not a judge: docs/review.md is the review."""
import glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import theme as _theme
from lib.talks import RES, SCENE_RE, dir_of, quality, qualities_present, read_json, scenes_of

talk = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
root = dir_of(talk)
Q = quality(sys.argv[2] if len(sys.argv) > 2 else None, root)
flags = []

# The look this talk presents in, and whether it is fit to present: contrast against the background, accents that can
# be told apart, fonts that are installed. bin/themes.py check says the same for every theme.
_name = _theme.active_name(root)
_th = _theme.load(_name)
flags += [f"theme {_name}: {b}" for b in _theme.validate(_th)]
_missing = _theme.missing_fonts(_th)
if _missing is None:
    print(f"  (fonts not checked: Pango is not available under {os.path.basename(sys.executable)}; "
          f"use .venv/bin/python)")
else:
    flags += [f"theme {_name}: the font '{fam}' is not installed; Pango will substitute one nobody chose"
              for fam in _missing]

# A colour a scene names itself is a colour that will not follow the theme: objects.py maps the talk's nouns onto the
# accent slots, and every scene uses those names. objects.py is checked too, because that is where the mapping lives.
for _f in sorted(glob.glob(f"{root}/scenes/*.py")):
    _src, _n = open(_f).read(), os.path.basename(_f)
    for _hue in set(re.findall(r"\b(BLUE|YELLOW|VIOLET|TEAL|GREEN|ORANGE|RED)\b", _src)):
        flags.append(f"{_n} names the colour {_hue}: use the meaning from objects.py, or a slot (A1..A6, ALERT)")
    for _hex in set(re.findall(r"[\"']#[0-9A-Fa-f]{3,6}[\"']", _src)):
        flags.append(f"{_n} draws with the literal colour {_hex}: it cannot follow the theme (use a slot, BG, HI, ...)")

# Two scenes with one class name: bin/render.sh renders neither, and they would overwrite each other's notes.
_seen = {}
for _stem, _scene in scenes_of(root):
    if _scene in _seen:
        flags.append(f"{_scene} is defined in both {_seen[_scene]}.py and {_stem}.py: scene names must be unique")
    _seen[_scene] = _stem

# A scene in a file the tools do not look at renders nowhere and is reported by nothing else.
for _f in sorted(glob.glob(f"{root}/scenes/*.py")):
    if os.path.basename(_f).startswith("s"):
        continue
    for _c in re.findall(SCENE_RE, open(_f).read(), re.M):
        flags.append(f"{os.path.basename(_f)} defines the scene {_c}, but only scenes/s*.py is presented: rename the file")

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
        idx = f"{root}/media/videos/{name[:-3]}/{Q}/sections/{c.group(1)}.json"
        notes_file = f"{root}/media/notes/{c.group(1)}.json"
        if os.path.exists(idx) and os.path.exists(notes_file):   # both written by the render, so loops and branches are counted right
            steps, notes = len(read_json(idx)), len(read_json(notes_file))
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

# The notes-per-step check compares what the render wrote with what the scene declared, so it needs a render at the
# quality being checked. Silence there used to look like a pass.
_have_q = qualities_present(root)
if not _have_q:
    flags.append(f"never rendered: the notes-per-step check needs one (bin/render.sh {talk} ql)")
elif Q not in [RES[q] for q in _have_q]:
    flags.append(f"nothing rendered at {Q}: the notes-per-step check was skipped (this talk has {', '.join(_have_q)})")

print(f"{talk}: {'ok' if not flags else str(len(flags)) + ' flags'}  (theme {_name}, {_th['mode']})")
for x in flags:
    print("  -", x)
sys.exit(1 if flags else 0)
