#!/usr/bin/env bash
# Render one talk's scenes, one clip per step, then build its two pages.
# Usage: bin/render.sh <talk> [ql|qm|qh] [SceneName ...]     default quality qm, all scenes in file order
# Never run two renders at once: Manim processes share the rasterised-text cache and one will delete a file the
# other is about to read. Queue them.
set -euo pipefail
cd "$(dirname "$0")/.."
TALK=${1:?usage: bin/render.sh <talk> [ql|qm|qh] [Scene ...]}; Q=${2:-qm}; shift; shift || true
DIR=talks/$TALK; [[ -d $DIR/scenes ]] || { echo "no such talk: $DIR"; exit 1; }
export PYTHONPATH=.:$DIR/scenes
SCENES=("$@"); [[ ${#SCENES[@]} -eq 0 ]] && SCENES=($(grep -ho "^class [A-Za-z0-9]*(TalkSlide)" $DIR/scenes/s*.py | sed 's/class //; s/(TalkSlide)//'))
for s in "${SCENES[@]}"; do
  f=$(grep -l "^class $s(TalkSlide)" $DIR/scenes/s*.py)
  .venv/bin/manim -$Q --save_sections --disable_caching --media_dir "$DIR/media" "$f" "$s"
done
.venv/bin/python bin/build.py "$TALK" "$Q"
