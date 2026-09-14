#!/usr/bin/env bash
# Contact sheets for reviewing a talk's scenes as images: one frame every N seconds, tiled 5 wide.
# Usage: bin/review.sh <talk> [ql|qm|qh] [seconds=2]   -> <talk folder>/media/review/<Scene>.png
# bin/shots.py (the frame each step holds on) is the first review; this one shows every layout a scene passes through.
set -euo pipefail
cd "$(dirname "$0")/.."
TALK=${1:?usage: bin/review.sh <talk> [ql|qm|qh] [seconds]}; Q=${2:-ql}; N=${3:-2}
[[ $N =~ ^[1-9][0-9]*$ ]] || { echo "seconds must be a whole number, 1 or more, not $N"; exit 1; }
# One call for all of it, so this script uses the same talk lookup, the same quality names, the same "is it rendered"
# rule and the same sheet colour as every other tool: the folder, the padding, then one line per rendered scene.
LINES=()
while IFS= read -r line; do LINES+=("$line"); done < <(.venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from lib import theme
from lib.talks import dir_of, quality, rendered_or_exit
talk, q = sys.argv[1], sys.argv[2]
root = dir_of(talk)
print(root)
print(theme.sheet_hex(root))
for _stem, scene, video, _i, _n in rendered_or_exit(root, quality(q, root), talk):
    print(f'{scene}\t{video}')
" "$TALK" "$Q")            # a read loop, not mapfile: /bin/bash on macOS is still 3.2
DIR=${LINES[0]}; PAD=${LINES[1]}
M=$DIR/media; mkdir -p "$M/review"
for line in "${LINES[@]:2}"; do
  s=${line%%$'\t'*}; f=${line#*$'\t'}
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" | cut -d. -f1); rows=$(( (d / N + 5) / 5 ))
  ffmpeg -loglevel error -y -i "$f" -vf "fps=1/$N,scale=384:-1,tile=5x${rows}:margin=4:padding=4:color=$PAD" -frames:v 1 "$M/review/$s.png"
  echo "$M/review/$s.png  ($d s)"
done
