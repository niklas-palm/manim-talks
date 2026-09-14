"""Where a talk lives. Two roots, one lookup.

    talks/<slug>/     the samples that are part of this repository, built to be read as examples
    out/<slug>/       real talks for real audiences: git ignores the whole folder

A talk is a folder with a `scenes/` directory; everything else about the two roots is identical, so every tool takes a
name and finds it. `out/` is searched first, so a real deck may carry the name of a sample and shadow it. Put a deck in
`out/` when it is for an audience rather than for the next person reading this repository: a company's theme, a
customer's numbers, anything that should not be committed here.
"""
import glob
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOTS = ["out", "talks"]


RES = {"ql": "480p15", "qm": "720p30", "qh": "1080p60"}   # the folder Manim renders into, per quality flag


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


def quality(arg: str = None, default: str = "qh") -> str:
    """The resolution folder a quality flag means. One place, because five tools take the same argument and a typo in
    it should be a sentence, not a KeyError two frames deep."""
    q = arg or default
    if q not in RES:
        raise SystemExit(f"quality must be one of {', '.join(RES)}, not {q!r}")
    return RES[q]


def scenes_of(root: str) -> list:
    """Every (module stem, scene class) a talk defines, in the order it is presented: file order, then order within the
    file. One reader, because the tools that each had their own pattern for this disagreed about what a scene is."""
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, root, "scenes", "s*.py"))):
        stem = os.path.basename(f)[:-3]
        with open(f) as fh:
            out += [(stem, c) for c in re.findall(r"^class (\w+)\(TalkSlide\)", fh.read(), re.M)]
    return out


def qualities_present(root: str) -> list:
    """Which qualities this talk has actually been rendered at, for an error message worth reading."""
    have = {os.path.basename(d) for d in glob.glob(os.path.join(REPO, root, "media", "videos", "*", "*"))}
    return [q for q, folder in RES.items() if folder in have]


def rendered(root: str, q: str) -> list:
    """Every scene of a talk that exists at this quality, as (stem, scene, video, section index). The four tools that
    read a render need exactly these paths, and the one that reports on a render needs to know what is missing."""
    out = []
    for stem, scene in scenes_of(root):
        base = os.path.join(root, "media", "videos", stem, q)
        index = os.path.join(base, "sections", f"{scene}.json")
        if os.path.exists(index):
            out.append((stem, scene, os.path.join(base, f"{scene}.mp4"), index))
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


def names() -> list:
    """Every talk in both roots, samples first, each name once."""
    out = []
    for r in reversed(ROOTS):
        d = os.path.join(REPO, r)
        if os.path.isdir(d):
            out += [n for n in sorted(os.listdir(d))
                    if os.path.isdir(os.path.join(d, n, "scenes")) and not n.startswith("_") and n not in out]
    return out
