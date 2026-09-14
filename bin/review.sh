#!/usr/bin/env bash
# Contact sheets for reviewing a talk's scenes as images: one frame every N seconds, tiled 5 wide.
# Usage: bin/review.sh <talk> [ql|qm|qh] [seconds=2]   -> <talk folder>/media/review/<Scene>.png
# bin/shots.py (the frame each step holds on) is the first review; this one shows every layout a scene passes through.
set -euo pipefail
cd "$(dirname "$0")/.."
TALK=${1:?usage: bin/review.sh <talk> [ql|qm|qh] [seconds]}; Q=${2:-ql}; N=${3:-2}
case $Q in ql) R=480p15;; qm) R=720p30;; qh) R=1080p60;; *) echo "quality must be ql, qm or qh, not $Q"; exit 1;; esac
[[ $N -gt 0 ]] || { echo "seconds must be 1 or more"; exit 1; }
DIR=$(.venv/bin/python -c "import sys; sys.path.insert(0,'.'); from lib.talks import dir_of; print(dir_of(sys.argv[1]))" "$TALK")
PAD=$(.venv/bin/python -c "import sys; sys.path.insert(0,'.'); from lib import theme
t = theme.load(theme.active_name(sys.argv[1])); print('0x' + theme.sheet_bg(t)[1:])" "$DIR")   # the padding follows the deck's style
M=$DIR/media; mkdir -p "$M/review"
shopt -s nullglob
CLIPS=("$M"/videos/*/$R/*.mp4)
[[ ${#CLIPS[@]} -gt 0 ]] || { echo "$TALK: nothing rendered at $Q. Run bin/render.sh $TALK $Q first."; exit 1; }
for f in "${CLIPS[@]}"; do
  s=$(basename "$f" .mp4)
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" | cut -d. -f1); rows=$(( (d / N + 5) / 5 ))
  ffmpeg -loglevel error -y -i "$f" -vf "fps=1/$N,scale=384:-1,tile=5x${rows}:margin=4:padding=4:color=$PAD" -frames:v 1 "$M/review/$s.png"
  echo "$M/review/$s.png  ($d s)"
done
