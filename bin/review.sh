#!/usr/bin/env bash
# Contact sheets for reviewing a talk's scenes as images: one frame every N seconds, tiled 5 wide.
# Usage: bin/review.sh <talk> [ql|qm|qh] [seconds=2]   -> talks/<talk>/media/review/<Scene>.png
# bin/shots.py (the frame each step holds on) is the first review; this one shows every layout a scene passes through.
set -euo pipefail
cd "$(dirname "$0")/.."
TALK=${1:?usage: bin/review.sh <talk> [ql|qm|qh] [seconds]}; Q=${2:-ql}; N=${3:-2}
case $Q in ql) R=480p15;; qm) R=720p30;; qh) R=1080p60;; esac
M=talks/$TALK/media; mkdir -p $M/review
for f in $M/videos/*/$R/*.mp4; do
  s=$(basename "$f" .mp4)
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" | cut -d. -f1); rows=$(( (d / N + 5) / 5 ))
  ffmpeg -loglevel error -y -i "$f" -vf "fps=1/$N,scale=384:-1,tile=5x${rows}:margin=4:padding=4:color=0x0f1116" -frames:v 1 "$M/review/$s.png"
  echo "$M/review/$s.png  ($d s)"
done
