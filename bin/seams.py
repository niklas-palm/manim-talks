#!/usr/bin/env python3
"""The seams of a talk: for every pair of consecutive scenes, the last frame of one beside the first frame of the next.
Scenes are separate videos, so this is where a deck can cut to a fresh picture; the rule is that it never does. The
first frame of a scene must be the last frame of the previous one, and the title changes in place as the picture
starts to change. Writes <talk>/media/seams/seams.png and prints a mean pixel difference per seam (0 is identical;
under 4 is a title change on an unchanged picture; more means the picture jumped).
Usage: bin/seams.py <talk> [ql|qm|qh|qp]   the quality is inferred when the talk has only one rendered"""
import os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import theme as _theme
from lib.talks import duration, from_argv, rendered_or_exit, report_unrendered, scenes_of

talk, root, Q = from_argv(__doc__)
PAD = _theme.sheet_rgb(root)
out_dir = f"{root}/media/seams"   # its own folder: bin/shots.py clears media/shots before writing
os.makedirs(out_dir, exist_ok=True)

items = rendered_or_exit(root, Q, talk)
report_unrendered(root, items)
if len(items) != len(scenes_of(root)):    # a gap would pair two scenes that are not neighbours and call it a jump
    sys.exit("some scenes are missing from this render: the seams between them cannot be judged. Re-render the talk.")
scenes = [(scene, video) for _, scene, video, _, _ in items]


def frame(video: str, t: float, png: str):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", "-vf", "scale=960:-1", png], check=True)


pairs = []
for (a, va), (b, vb) in zip(scenes, scenes[1:]):
    last, first = f"{out_dir}/seam-{a}-last.png", f"{out_dir}/seam-{b}-first.png"
    frame(va, max(0.0, duration(va) - 0.08), last)
    frame(vb, 0.0, first)      # the very first frame: the retitle may start at once, so 0.05 s would already be mid-change
    pairs.append((a, b, last, first))

from PIL import Image, ImageChops, ImageStat
rows = []
for a, b, last, first in pairs:
    la, fb = Image.open(last).convert("RGB"), Image.open(first).convert("RGB")
    diff = ImageStat.Stat(ImageChops.difference(la, fb)).mean
    d = sum(diff) / 3
    flag = "identical" if d < 0.5 else ("title only" if d < 4 else "PICTURE JUMPS")
    print(f"{a:>18} -> {b:<18} {d:6.1f}  {flag}")
    rows.append((la, fb))
if rows:
    w, h = rows[0][0].size
    sheet = Image.new("RGB", (w * 2 + 12, (h + 6) * len(rows) + 6), PAD)
    for i, (la, fb) in enumerate(rows):
        sheet.paste(la, (6, 6 + i * (h + 6))); sheet.paste(fb, (w + 12, 6 + i * (h + 6)))
    sheet.save(f"{out_dir}/seams.png")
    print(f"-> {out_dir}/seams.png")
