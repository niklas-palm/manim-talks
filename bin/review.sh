#!/usr/bin/env bash
# Contact sheets for reviewing a talk's scenes as images: one frame every N seconds, tiled 5 wide.
# Usage: bin/review.sh <talk> [ql|qm|qh] [seconds=2]   -> <talk folder>/media/review/<Scene>.png
# bin/shots.py (the frame each step holds on) is the first review; this one shows every layout a scene passes through.
set -euo pipefail
cd "$(dirname "$0")/.."
TALK=${1:?usage: bin/review.sh <talk> [ql|qm|qh] [seconds]}; Q=${2:-}; N=${3:-2}
[[ $N =~ ^[1-9][0-9]*$ ]] || { echo "seconds must be a whole number, 1 or more, not $N"; exit 1; }
# One call for all of it, so this script uses the same talk lookup, the same quality names, the same "is it rendered"
# rule, the same clip probe and the same sheet colour as every other tool: the folder, the padding, then one line per
# rendered scene with its duration. With no quality given the library infers it, or asks, as it does for every tool.
LINES=()
while IFS= read -r line; do LINES+=("$line"); done < <(.venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from lib import theme
from lib.talks import dir_of, duration, quality, rendered_or_exit
talk, q = sys.argv[1], sys.argv[2]
root = dir_of(talk)
print(root)
print(theme.sheet_hex(root))
for _stem, scene, video, _i, _n in rendered_or_exit(root, quality(q or None, root), talk):
    print(f'{scene}\t{video}\t{duration(video):.0f}')
print('END')                                     # the sentinel: a Python failure past the first two lines is visible here
" "$TALK" "$Q")            # a read loop, not mapfile: /bin/bash on macOS is still 3.2
[[ ${#LINES[@]} -ge 3 && ${LINES[${#LINES[@]}-1]} == END ]] || exit 1      # the Python said why; do not write half a review
DIR=${LINES[0]}; PAD=${LINES[1]}
M=$DIR/media; mkdir -p "$M/review"
for line in "${LINES[@]:2:${#LINES[@]}-3}"; do
  IFS=$'\t' read -r s f d <<< "$line"; rows=$(( (d / N + 5) / 5 ))
  ffmpeg -loglevel error -y -i "$f" -vf "fps=1/$N,scale=384:-1,tile=5x${rows}:margin=4:padding=4:color=$PAD" -frames:v 1 "$M/review/$s.png"
  echo "$M/review/$s.png  ($d s)"
done
