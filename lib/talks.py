"""Where a talk lives. Two roots, one lookup.

    talks/<slug>/     the samples that are part of this repository, built to be read as examples
    out/<slug>/       real talks for real audiences: git ignores the whole folder

A talk is a folder with a `scenes/` directory; everything else about the two roots is identical, so every tool takes a
name and finds it. `out/` is searched first, so a real deck may carry the name of a sample and shadow it. Put a deck in
`out/` when it is for an audience rather than for the next person reading this repository: a company's theme, a
customer's numbers, anything that should not be committed here.
"""
import glob
import json
import math
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOTS = ["out", "talks"]


RES = {"ql": "480p15", "qm": "720p30", "qh": "1080p60", "qp": "1440p60"}   # the folder Manim renders into, per quality flag

SCENE_RE = r"^class (\w+)\(TalkSlide\)"                 # what a scene is, in one place: the tools disagreed before


def dir_of(talk: str) -> str:
    """The folder of a talk, relative to the repository root. Exits with a clear message if there is no such talk,
    because every tool takes a name from the command line."""
    if not talk or "/" in talk or ".." in talk or talk.startswith("_"):
        raise SystemExit(f"not a talk name: {talk!r} (a name, not a path; leading underscore is reserved for the template)")
    for r in ROOTS:
        if os.path.isdir(os.path.join(REPO, r, talk, "scenes")):
            return f"{r}/{talk}"
    raise SystemExit(f"no such talk: {talk} (looked for {', '.join(f'{r}/{talk}/scenes' for r in ROOTS)}). "
                     f"Available: {', '.join(names()) or 'none'}")


def quality(arg: str = None, root: str = None) -> str:
    """The resolution folder a quality flag means. One place, because every tool takes the same argument and a typo in
    it should be a sentence, not a KeyError two frames deep. With no flag and a talk that has been rendered at exactly
    one quality, that is the one meant; otherwise say so rather than guessing, because guessing wrong used to destroy
    the previous output."""
    if not arg:
        have = qualities_present(root) if root else []
        if len(have) == 1:
            return RES[have[0]]
        raise SystemExit(f"which quality? one of {', '.join(RES)}"
                         + (f"; this talk has {', '.join(have)}" if have else ""))
    if arg not in RES:
        raise SystemExit(f"quality must be one of {', '.join(RES)}, not {arg!r}")
    return RES[arg]


def scenes_of(root: str) -> list:
    """Every (module stem, scene class) a talk defines, in the order it is presented: file order, then order within the
    file. One reader, because the tools that each had their own pattern for this disagreed about what a scene is."""
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, root, "scenes", "s*.py"))):
        stem = os.path.basename(f)[:-3]
        with open(f) as fh:
            out += [(stem, c) for c in re.findall(SCENE_RE, fh.read(), re.M)]
    return out


def qualities_present(root: str) -> list:
    """Which qualities this talk has a rendered scene at. An interrupted render leaves an empty quality folder behind,
    and counting that as a render made the tools offer a choice that could not be taken."""
    have = {os.path.basename(os.path.dirname(f))
            for f in glob.glob(os.path.join(REPO, root, "media", "videos", "*", "*", "*.mp4"))}
    return [q for q, folder in RES.items() if folder in have]


def rendered(root: str, q: str) -> list:
    """Every scene of a talk that a render finished at this quality, as (stem, scene, video, index, notes). Both the
    section index and the scene's video must exist: Manim writes the per-step clips before it combines them, so an
    interrupted render leaves an index with no video, and a tool that trusted the index alone wrote pages pointing at
    a file that was not there. It backs rendered_or_exit, which is what a tool that must not proceed without a render
    calls; bin/check.py calls this one directly, because for the checker a missing render is a flag rather than a stop."""
    out = []
    for stem, scene in scenes_of(root):
        base = os.path.join(root, "media", "videos", stem, q)
        index, video = os.path.join(base, "sections", f"{scene}.json"), os.path.join(base, f"{scene}.mp4")
        if os.path.exists(index) and os.path.exists(video):
            out.append((stem, scene, video, index, os.path.join(root, "media", "notes", f"{scene}.json")))
    return out


def rendered_or_exit(root: str, q: str, talk: str) -> list:
    """The same, but a tool that would otherwise delete or overwrite its previous output stops here instead. A quality
    that was never rendered used to leave a blank deck behind and report success."""
    out = rendered(root, q)
    if not out:
        have = qualities_present(root)
        raise SystemExit(f"{talk}: nothing rendered at {q}"
                         + (f"; this talk has {', '.join(have)}" if have else "; it has never been rendered")
                         + f". Run bin/render.sh {talk} <ql|qm|qh> first.")
    return out


def report_unrendered(root: str, items: list):
    """Name the scenes a talk defines that this render does not have; the tools that build from a render say so rather
    than quietly leaving them out."""
    have = {(stem, scene) for stem, scene, _, _, _ in items}
    for stem, scene in scenes_of(root):
        if (stem, scene) not in have:
            print(f"not rendered: {scene} ({stem}.py)")


def title_of(root: str, talk: str) -> str:
    """A deck's title: the first "# " line of its script.md, which is what the pages and the export both show."""
    p = os.path.join(REPO, root, "script.md")
    if os.path.exists(p):
        with open(p) as f:
            for l in f:
                if l.startswith("# "):
                    return l[2:].strip()
    return talk


def read_json(path: str):
    """A JSON file a render wrote, or a sentence naming it. An interrupted render leaves a truncated section index, and
    a traceback with no file name in it is not a thing to debug two minutes before a talk."""
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise SystemExit(f"{path} is not valid JSON ({e}); re-render this talk")
    except OSError as e:
        raise SystemExit(f"cannot read {path}: {e}")


def read_index(path: str) -> list:
    """A scene's section index: one entry per step, each with a duration and the clip it names. Checked here rather than
    trusted, because the tools that read it delete or overwrite their own output, and a file of the wrong shape used to
    take that output with it."""
    index = read_json(path)
    if not isinstance(index, list) or not index:
        raise SystemExit(f"{path} is not a list of steps; re-render this talk")
    for i, sec in enumerate(index):
        if not isinstance(sec, dict) or not isinstance(sec.get("duration", None), (int, float, str)):
            raise SystemExit(f"{path}: step {i + 1} has no duration; re-render this talk")
        try:
            d = float(sec["duration"])
            if isinstance(sec["duration"], bool) or not math.isfinite(d) or d < 0:
                raise ValueError            # NaN passes every comparison, and a page whose step ends at NaN never pauses
        except ValueError:
            raise SystemExit(f"{path}: step {i + 1} has duration {sec['duration']!r}; re-render this talk")
        if not isinstance(sec.get("video", None), str) or not sec["video"]:
            raise SystemExit(f"{path}: step {i + 1} names no clip; re-render this talk")   # export_pptx reads this one
    return index


def from_argv(doc: str) -> tuple:
    """The three things every tool that reads a render needs from its command line: the talk, its folder and the
    resolution to work at. One reader, because five tools asked the same three questions in the same three lines."""
    talk = sys.argv[1] if len(sys.argv) > 1 else sys.exit(doc)
    root = dir_of(talk)
    return talk, root, quality(sys.argv[2] if len(sys.argv) > 2 else None, root)


def duration(video: str) -> float:
    """How long a clip is, in seconds. ffprobe says nothing at all for a missing or truncated file, and float("")
    is the traceback two tools used to end in."""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                       capture_output=True, text=True)
    try:
        if r.returncode:
            raise ValueError
        return float(r.stdout)
    except ValueError:
        raise SystemExit(f"{video} is missing or unreadable ({r.stdout.strip() or 'no duration'}): re-render this talk")


def names() -> list:
    """Every talk in both roots, samples first, each name once."""
    out = []
    for r in reversed(ROOTS):
        d = os.path.join(REPO, r)
        if os.path.isdir(d):
            out += [n for n in sorted(os.listdir(d))
                    if os.path.isdir(os.path.join(d, n, "scenes")) and not n.startswith("_") and n not in out]
    return out
