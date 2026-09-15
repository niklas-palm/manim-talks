#!/usr/bin/env python3
"""Structural checks for a talk, the things a review should not have to find by eye. Usage: .venv/bin/python bin/check.py <talk> [ql|qm|qh]   (the quality is inferred when only one is rendered)
Reports, per talk: the style it presents in and whether that style is fit to present (contrast, accents that can be
told apart, fonts installed); any colour a scene names itself instead of taking from objects.py; the files a talk must
have; that objects.py declares its vocabulary with set_thread; that every scene class wrote as many notes as it
rendered steps, has a finish(), and imports lib.palette; that script.md has a title line; text sizes below 12, on-screen
strings that look like sentences (more than 14 words in a label), captions swapped more than once in a step, a scene in
a file that is not scenes/s*.py, two scenes with one class name, and a group animated together with one of its members
in one play (the trap that leaves the member behind). Below the flags it lists every Transform whose target is built
on the spot rather than named, for the reviewer to confirm by eye that the morph is intended (it does not affect the exit code). Exit code 1 if anything is
flagged. It is a checklist helper, not a judge: docs/review.md is the review."""
import glob, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import theme as _theme
from lib.talks import RES, SCENE_RE, from_argv, qualities_present, read_index, read_json, rendered, scenes_of

talk, root, Q = from_argv(__doc__)
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
# The pattern covers every colour constant Manim defines and lib/palette.py deletes from its namespace: the base hues,
# their DARK_/DARKER_/LIGHT_/LIGHTER_/PURE_ variants and their _A.._E shades, so this stays the friendly sentence before
# the NameError. Comments and docstrings are searched too; a word in capitals there is worth rewording.
_HUES = r"\b(?:(?:DARK|DARKER|LIGHT|LIGHTER|PURE)_)?(BLUE|YELLOW|VIOLET|TEAL|GREEN|ORANGE|RED|PURPLE|PINK|GOLD|MAROON|WHITE|BLACK|GREY|GRAY)(?:_[A-E])?\b"
_sources = {os.path.basename(f): open(f).read() for f in sorted(glob.glob(f"{root}/scenes/*.py"))}
for _n, _src in _sources.items():
    for _hue in sorted(set(m.group(0) for m in re.finditer(_HUES, _src))):
        flags.append(f"{_n} names the colour {_hue}: use the meaning from objects.py, or a slot (A1..A6, ALERT)")
    for _hex in sorted(set(re.findall(r"[\"']#[0-9A-Fa-f]{3,6}[\"']", _src))):
        flags.append(f"{_n} draws with the literal colour {_hex}: it cannot follow the theme (use a slot, BG, HI, ...)")

# Two scenes with one class name: bin/render.sh renders neither, and they would overwrite each other's notes.
_seen = {}
for _stem, _scene in scenes_of(root):
    if _scene in _seen:
        flags.append(f"{_scene} is defined in both {_seen[_scene]}.py and {_stem}.py: scene names must be unique")
    _seen[_scene] = _stem

# A scene in a file the tools do not look at renders nowhere and is reported by nothing else.
for _n, _src in _sources.items():
    if _n.startswith("s"):
        continue
    for _c in re.findall(SCENE_RE, _src, re.M):
        flags.append(f"{_n} defines the scene {_c}, but only scenes/s*.py is presented: rename the file")

for f, what in [("script.md", "the spine, moves and sources"), ("README.md", "what the talk is"), ("scenes/objects.py", "the talk's colours and shared drawings")]:
    if not os.path.exists(f"{root}/{f}"):
        flags.append(f"missing {f} ({what})")
if os.path.exists(f"{root}/script.md") and not any(l.startswith("# ") for l in open(f"{root}/script.md")):
    flags.append("script.md has no '# title' line (bin/build.py uses it as the deck title)")
if os.path.exists(f"{root}/scenes/objects.py") and "set_thread(" not in open(f"{root}/scenes/objects.py").read():
    flags.append("objects.py does not call set_thread: titles and captions will not colour the talk's nouns")

_done = {scene: (index, notes) for _stem, scene, _v, index, notes in rendered(root, Q)}   # the library owns these paths
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
    classes = list(re.finditer(SCENE_RE, src, re.M))
    for i, c in enumerate(classes):
        body = src[c.end(): classes[i + 1].start() if i + 1 < len(classes) else len(src)]
        if not re.search(r"self\.finish\(", body):
            flags.append(f"{name}: {c.group(1)} has no finish(): the last step has no note")
        idx, notes_file = _done.get(c.group(1), (None, None))
        if idx and os.path.exists(notes_file):   # both written by the render, so loops and branches are counted right
            steps, notes = len(read_index(idx)), len(read_json(notes_file))
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
        # a zoom that opens and closes inside one step: what it opened is on screen for a second and nobody reads it
        for step in re.split(r"self\.(?:next_slide|finish)\(", body)[:-1]:
            if len(re.findall(r"frame\.animate\.scale\(", step)) > 1:
                flags.append(f"{name}: {c.group(1)} zooms in and back out inside one step; the opened view needs its own click (docs/principles.md rule 10)")
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

# A Transform whose target is built on the spot, rather than a named object already on screen, redraws the whole target:
# a group that gains a member this way melts and re-forms instead of gaining the member. It is sometimes the point (a
# bar chart redrawn with new heights) and sometimes a defect the shot sheet cannot show, so it is listed, not flagged.
_morphs = []
for _n, _src in sorted(_sources.items()):
    for _i, _line in enumerate(_src.splitlines(), 1):
        for _m in re.finditer(r"\b(?:Replacement)?Transform\(\s*[\w.\[\]]+\s*,\s*([A-Za-z_][\w.]*\s*\()", _line):
            _morphs.append(f"{_n}:{_i}  {_line.strip()[:90]}")
if _morphs:
    print(f"  morphs to confirm by eye ({len(_morphs)}): the target is built on the spot, so the whole object redraws")
    for x in _morphs:
        print("   ", x)
sys.exit(1 if flags else 0)
