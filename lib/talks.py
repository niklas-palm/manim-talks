"""Where a talk lives. Two roots, one lookup.

    talks/<slug>/     the samples that are part of this repository, built to be read as examples
    out/<slug>/       real talks for real audiences: git ignores the whole folder

A talk is a folder with a `scenes/` directory; everything else about the two roots is identical, so every tool takes a
name and finds it. `out/` is searched first, so a real deck may carry the name of a sample and shadow it. Put a deck in
`out/` when it is for an audience rather than for the next person reading this repository: a company's theme, a
customer's numbers, anything that should not be committed here.
"""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOTS = ["out", "talks"]


def dir_of(talk: str) -> str:
    """The folder of a talk, relative to the repository root. Exits with a clear message if there is no such talk,
    because every tool takes a name from the command line."""
    for r in ROOTS:
        if os.path.isdir(os.path.join(REPO, r, talk, "scenes")):
            return f"{r}/{talk}"
    raise SystemExit(f"no such talk: {talk} (looked for {'/, '.join(ROOTS)}/{talk}/scenes). "
                     f"Available: {', '.join(names()) or 'none'}")


def names() -> list:
    """Every talk in both roots, samples first, each name once."""
    out = []
    for r in reversed(ROOTS):
        d = os.path.join(REPO, r)
        if os.path.isdir(d):
            out += [n for n in sorted(os.listdir(d))
                    if os.path.isdir(os.path.join(d, n, "scenes")) and not n.startswith("_") and n not in out]
    return out
