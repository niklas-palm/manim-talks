#!/usr/bin/env bash
# Render one talk's scenes, one clip per step, then build its two pages.
# Usage: bin/render.sh <talk> [ql|qm|qh] [SceneName ...]     default quality qm, all scenes in file order
# Never run two renders at once: Manim processes share the rasterised-text cache and one will delete a file the
# other is about to read. Queue them.
set -euo pipefail
cd "$(dirname "$0")/.."
TALK=${1:?usage: bin/render.sh <talk> [ql|qm|qh] [Scene ...]}; Q=${2:-qm}; shift; shift || true
DIR=$(.venv/bin/python -c "import sys; sys.path.insert(0,'.'); from lib.talks import dir_of; print(dir_of('$TALK'))")
export PYTHONPATH=.:$DIR/scenes
# The look: THEME wins, then this talk's .theme, then the repository's .theme (lib/theme.py). Exported so the render,
# the pages bin/build.py writes and the PowerPoint export all use one theme.
if [[ -z ${THEME:-} && -f $DIR/.theme ]]; then export THEME=$(tr -d '[:space:]' < "$DIR/.theme"); fi
if [[ -z ${THEME:-} && -f .theme ]]; then export THEME=$(tr -d '[:space:]' < .theme); fi
echo "theme: ${THEME:-studio-dark}"
SCENES=("$@"); [[ ${#SCENES[@]} -eq 0 ]] && SCENES=($(grep -ho "^class [A-Za-z0-9]*(TalkSlide)" $DIR/scenes/s*.py | sed 's/class //; s/(TalkSlide)//'))
for s in "${SCENES[@]}"; do
  f=$(grep -l "^class $s(TalkSlide)" $DIR/scenes/s*.py)
  .venv/bin/manim -$Q --save_sections --disable_caching --media_dir "$DIR/media" "$f" "$s"
done
.venv/bin/python bin/build.py "$TALK" "$Q"
