#!/usr/bin/env python3
"""The seams of a talk: for every pair of consecutive scenes, the last frame of one beside the first frame of the next.
Scenes are separate videos, so this is where a deck can cut to a fresh picture; the rule is that it never does. The
first frame of a scene must be the last frame of the previous one, and the title changes in place as the picture
starts to change. Writes <talk>/media/seams/seams.png and prints a mean pixel difference per seam (0 is identical;
under 4 is a title change on an unchanged picture; more means the picture jumped).
Usage: bin/seams.py <talk> [ql|qm|qh]"""
import glob, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.talks import dir_of

talk = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
Q = {"ql": "480p15", "qm": "720p30", "qh": "1080p60"}[sys.argv[2] if len(sys.argv) > 2 else "qh"]
root = dir_of(talk)
out_dir = f"{root}/media/seams"   # its own folder: bin/shots.py clears media/shots before writing
os.makedirs(out_dir, exist_ok=True)

scenes = []
for f in sorted(glob.glob(f"{root}/scenes/s*.py")):
    stem = os.path.basename(f)[:-3]
    for scene in re.findall(r"^class (\w+)\(TalkSlide\)", open(f).read(), re.M):
        idx = f"{root}/media/videos/{stem}/{Q}/sections/{scene}.json"
        if os.path.exists(idx):
            scenes.append((scene, f"{root}/media/videos/{stem}/{Q}/{scene}.mp4"))


def frame(video: str, t: float, png: str):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", "-vf", "scale=960:-1", png], check=True)


def duration(video: str) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video], capture_output=True, text=True).stdout)


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
    sheet = Image.new("RGB", (w * 2 + 12, (h + 6) * len(rows) + 6), (42, 46, 56))
    for i, (la, fb) in enumerate(rows):
        sheet.paste(la, (6, 6 + i * (h + 6))); sheet.paste(fb, (w + 12, 6 + i * (h + 6)))
    sheet.save(f"{out_dir}/seams.png")
    print(f"-> {out_dir}/seams.png")
