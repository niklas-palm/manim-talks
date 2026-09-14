#!/usr/bin/env python3
"""End-state screenshots of every step of one talk, from the rendered videos: <talk>/media/shots/<Scene>-<k>.png
and one tiled sheet per scene, <Scene>.png. The presenter holds on exactly these frames, so this is what the audience
sits with while the speaker talks: the fastest review of captions, spacing and colour there is. Frames are taken 0.08 s
before each step ends, so a fade that is the step's last animation is finished; end every step on a settled picture.
Usage: bin/shots.py <talk> [ql|qm|qh]"""
import glob, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.talks import dir_of

talk = sys.argv[1]
Q = {"ql": "480p15", "qm": "720p30", "qh": "1080p60"}[sys.argv[2] if len(sys.argv) > 2 else "qh"]
root = dir_of(talk)
out_dir = f"{root}/media/shots"
os.makedirs(out_dir, exist_ok=True)
for old in glob.glob(f"{out_dir}/*.png"):   # a frame ffmpeg cannot produce must not leave last run's file in its place
    os.remove(old)
for f in sorted(glob.glob(f"{root}/scenes/s*.py")):
    stem = os.path.basename(f)[:-3]
    for scene in re.findall(r"^class (\w+)\(TalkSlide\)", open(f).read(), re.M):
        idx = f"{root}/media/videos/{stem}/{Q}/sections/{scene}.json"
        if not os.path.exists(idx):
            continue
        video = f"{root}/media/videos/{stem}/{Q}/{scene}.mp4"
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video], capture_output=True, text=True).stdout)
        t, frames = 0.0, []
        for k, sec in enumerate(json.load(open(idx))):
            t += float(sec["duration"])
            out = f"{out_dir}/{scene}-{k:02d}.png"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{max(0, min(t - 0.08, dur - 0.08)):.3f}", "-i", video,
                            "-frames:v", "1", "-vf", "scale=960:-1", out], check=True)
            frames.append(out)
        rows = (len(frames) + 1) // 2
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-pattern_type", "glob", "-i", f"{out_dir}/{scene}-*.png",
                        "-vf", f"tile=2x{rows}:margin=6:padding=6:color=0x2a2e38", "-frames:v", "1", f"{out_dir}/{scene}.png"], check=True)
        print(scene, len(frames))
