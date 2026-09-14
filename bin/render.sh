#!/usr/bin/env bash
# Render one talk's scenes, one clip per step, then build its two pages.
# Usage: bin/render.sh <talk> [ql|qm|qh] [SceneName ...]     default quality qm, all scenes in file order
# Never run two renders of the SAME talk at once: they share its rasterised-text cache under media/ and one will
# delete a file the other is about to read. Different talks, including a talk and its -bright sibling, are safe.
set -euo pipefail
cd "$(dirname "$0")/.."
TALK=${1:?usage: bin/render.sh <talk> [ql|qm|qh] [Scene ...]}; Q=${2:-qm}; shift; shift || true
# Validate before Manim sees it: manim itself accepts -qp and -qk, which would render for tens of minutes into a folder
# no tool in this repository reads, and only bin/build.py at the end would say the quality was wrong.
case $Q in ql|qm|qh) ;; *) echo "quality must be ql, qm or qh, not $Q"; exit 1;; esac
# The talk folder and the style both come from the library, so every tool answers these two questions the same way.
# The name is passed as an argument, never interpolated into the program: a talk name is user input.
DIR=$(.venv/bin/python -c "import sys; sys.path.insert(0,'.'); from lib.talks import dir_of; print(dir_of(sys.argv[1]))" "$TALK")
export PYTHONPATH=".:$DIR/scenes"
# Assigned, then exported: `export X=$(cmd)` returns 0 even when cmd fails, and the render would proceed with no style.
THEME=$(.venv/bin/python -c "import sys; sys.path.insert(0,'.'); from lib import theme; print(theme.active_name(sys.argv[1]))" "$DIR")
export THEME
echo "theme: $THEME"
# One call for the whole list: which scenes this talk has, and which file defines each. The library answers, so the set
# that renders is the set the Python tools report on, and a name typed by hand is never treated as a pattern. Given
# scene names it returns just those, and fails if one is unknown or defined in two files.
PAIRS=()
while IFS= read -r line; do PAIRS+=("$line"); done < <(.venv/bin/python -c "
import sys; sys.path.insert(0,'.')
from lib.talks import scenes_of
root, want = sys.argv[1], sys.argv[2:]
have = scenes_of(root)
if not have:
    raise SystemExit(f'no TalkSlide classes in {root}/scenes')
for name in want:
    files = [stem for stem, scene in have if scene == name]
    if not files:
        raise SystemExit(f'no scene {name} in {root}/scenes')
    if len(files) > 1:
        raise SystemExit(f'scene {name} is defined in more than one file: ' + ', '.join(files))
for stem, scene in have:
    if not want or scene in want:
        print(f'{stem}\t{scene}')" "$DIR" "$@")
[[ ${#PAIRS[@]} -gt 0 ]] || exit 1                 # the Python already said why
for line in "${PAIRS[@]}"; do
  IFS=$'\t' read -r stem scene <<< "$line"
  .venv/bin/manim -$Q --save_sections --disable_caching --media_dir "$DIR/media" "$DIR/scenes/$stem.py" "$scene"
done
.venv/bin/python bin/build.py "$TALK" "$Q"
