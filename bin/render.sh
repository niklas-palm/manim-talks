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
export THEME=$(.venv/bin/python -c "import sys; sys.path.insert(0,'.'); from lib import theme; print(theme.active_name(sys.argv[1]))" "$DIR")
echo "theme: $THEME"
SCENES=("$@")
if [[ ${#SCENES[@]} -eq 0 ]]; then
  # The same reader the Python tools use, so the set that renders is the set they report on.
  while IFS= read -r s; do SCENES+=("$s"); done < <(.venv/bin/python -c \
    "import sys; sys.path.insert(0,'.'); from lib.talks import scenes_of; print('\n'.join(c for _, c in scenes_of(sys.argv[1])))" "$DIR")
fi
[[ ${#SCENES[@]} -eq 0 ]] && { echo "no TalkSlide classes in $DIR/scenes"; exit 1; }
for s in "${SCENES[@]}"; do
  f=$(grep -l "^class $s(TalkSlide)" "$DIR"/scenes/s*.py) || { echo "no scene $s in $DIR/scenes"; exit 1; }
  [[ $(wc -l <<< "$f") -eq 1 ]] || { echo "scene $s is defined in more than one file:"$'\n'"$f"; exit 1; }
  .venv/bin/manim -$Q --save_sections --disable_caching --media_dir "$DIR/media" "$f" "$s"
done
.venv/bin/python bin/build.py "$TALK" "$Q"
