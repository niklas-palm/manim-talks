#!/usr/bin/env python3
"""Structural checks for a talk, the things a review should not have to find by eye. Usage: bin/check.py <talk> [ql|qm|qh]
Reports, per talk: the files a talk must have, that objects.py declares its colours with set_thread, that every scene
class has as many notes as steps (once rendered), text sizes below 12 outside small(), on-screen strings that look like
sentences (more than 12 words in a label), and captions swapped more than once in a step. Exit code 1 if anything is
flagged. It is a checklist helper, not a judge: docs/review.md is the review."""
import glob, json, os, re, sys

talk = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
Q = {"ql": "480p15", "qm": "720p30", "qh": "1080p60"}[sys.argv[2] if len(sys.argv) > 2 else "qh"]
root = f"talks/{talk}"
flags = []

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
    for m in re.finditer(r"label\(([^()]*?),\s*(\d+(?:\.\d+)?)", src):
        if float(m.group(2)) < 12:
            flags.append(f"{name}: label size {m.group(2)} below 12: {m.group(1)[:40]}")
    for m in re.finditer(r"(?:label|caption|swap_caption)\((?:self,\s*(?:cap,\s*)?)?\"([^\"]{60,})\"", src):
        if len(m.group(1).split()) > 14:
            flags.append(f"{name}: an on-screen sentence of {len(m.group(1).split())} words; move it to the note: \"{m.group(1)[:50]}...\"")
    # notes versus steps, per class
    classes = list(re.finditer(r"^class (\w+)\(TalkSlide\):", src, re.M))
    for i, c in enumerate(classes):
        body = src[c.end(): classes[i + 1].start() if i + 1 < len(classes) else len(src)]
        notes = len(re.findall(r"self\.(?:next_slide|finish)\(", body))
        if not re.search(r"self\.finish\(", body):
            flags.append(f"{name}: {c.group(1)} has no finish(): the last step has no note")
        idx = glob.glob(f"{root}/media/videos/{name[:-3]}/{Q}/sections/{c.group(1)}.json")
        if idx:
            steps = len(json.load(open(idx[0])))
            if steps != notes:
                flags.append(f"{name}: {c.group(1)} rendered {steps} steps but has {notes} notes")
        for step in re.split(r"self\.next_slide\(", body)[:-1]:
            if step.count("swap_caption(") + step.count("caption(self") > 1:
                flags.append(f"{name}: {c.group(1)} changes the caption more than once inside one step")

print(f"{talk}: {'ok' if not flags else str(len(flags)) + ' flags'}")
for x in flags:
    print("  -", x)
sys.exit(1 if flags else 0)
