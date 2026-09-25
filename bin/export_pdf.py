#!/usr/bin/env python3
"""Export a rendered talk as a PDF: one page per scene, showing the settled picture the scene ends on, and nothing else.
No notes, no clips. This is the file to send when someone asks for "the slides" afterwards: each move's illustration,
complete, as the audience last saw it.

Why the last frame of each scene: a move is one picture that grows, so its final frame contains everything the move
drew. With --steps every step's end frame becomes a page instead (the frame the presenter holds on), for a fuller
record at the price of many near-identical pages.

Usage: bin/export_pdf.py <talk> [ql|qm|qh|qp] [out.pdf] [--steps]   output <talk folder>/<talk>.pdf;
the quality is inferred when the talk has only one rendered.
Requires ffmpeg (the frames) and Pillow (the PDF), which manim already brings."""
import os, subprocess, sys, tempfile
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.talks import duration, from_argv, read_index, rendered_or_exit, report_unrendered

STEPS = "--steps" in sys.argv
sys.argv = [a for a in sys.argv if a != "--steps"]
talk, root, Q = from_argv(__doc__)
out = sys.argv[3] if len(sys.argv) > 3 else f"{root}/{talk}.pdf"
if os.path.isdir(out) or os.path.islink(out) or not os.path.isdir(os.path.dirname(os.path.abspath(out))):
    sys.exit(f"cannot write {out}: give a file path, not a folder or a symlink, in a folder that exists")
items = rendered_or_exit(root, Q, talk)
report_unrendered(root, items)


def frame(video: str, t: float, png: str):
    """The frame at t seconds, clamped inside the clip: a seek past the end writes nothing and the previous file survives."""
    t = max(0.0, min(t, duration(video) - 0.08))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", png], check=True)


pages = []
with tempfile.TemporaryDirectory() as tmp:
    for stem, scene, video, index, _notes in items:
        # Shots are taken a few frames before a boundary, where the picture has settled: the same rule bin/shots.py uses.
        if STEPS:
            t, times = 0.0, []
            for sec in read_index(index):
                t += float(sec["duration"]); times.append(t - 0.08)
        else:
            times = [duration(video) - 0.08]
        for k, t in enumerate(times):
            png = f"{tmp}/{scene}-{k}.png"
            frame(video, t, png)
            pages.append(Image.open(png).convert("RGB"))
    if not pages:
        sys.exit(f"{talk}: nothing to export")
    pages[0].save(out, save_all=True, append_images=pages[1:], resolution=150)
print(f"{talk}: {len(pages)} pages -> {out}")
