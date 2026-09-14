#!/usr/bin/env bash
# Every sample deck in both styles, as the sheets bin/shots.py makes:
#   media/gallery/<style>/<talk>-<Scene>.png     one tiled sheet per scene, the frame every step holds on
# Usage: bin/gallery.sh [ql|qm|qh] [jobs]       ql is enough to compare styles; the run is two renders per deck.
# Each deck is rendered in the other style first and in its own style last, so its media folder and its two pages are
# left as its .theme says. Renders of one deck never overlap (they share its text cache); different decks do, `jobs` at
# a time. Only the samples under talks/ are in the gallery; what is in out/ is nobody else's business.
set -euo pipefail
cd "$(dirname "$0")/.."

one() {                                    # one deck, both styles, the deck's own style last
  local t=$1 Q=$2 own=dark other
  [[ -f .theme ]] && own=$(tr -d '[:space:]' < .theme)
  [[ -f talks/$t/.theme ]] && own=$(tr -d '[:space:]' < "talks/$t/.theme")
  other=dark; [[ $own == dark ]] && other=bright
  for th in $other $own; do
    local log=/tmp/gallery-$t-$th.log                          # renders are chatty; keep the log, print the path if one fails
    if ! THEME=$th bin/render.sh "$t" "$Q" > "$log" 2>&1; then echo "  FAILED $t $th: see $log"; return 1; fi
    .venv/bin/python bin/shots.py "$t" "$Q" >> "$log" 2>&1
    mkdir -p "media/gallery/$th"
    for f in talks/$t/media/shots/*.png; do
      local b; b=$(basename "$f"); [[ $b == *-* ]] && continue    # the per-scene sheets, not every single step
      cp "$f" "media/gallery/$th/$t-$b"
    done
    echo "  $t  $th"
  done
}

if [[ ${1:-} == --one ]]; then one "$2" "${3:-ql}"; exit 0; fi

Q=${1:-ql}; JOBS=${2:-3}
rm -rf media/gallery; mkdir -p media/gallery
n=0
for d in talks/*/scenes; do
  t=$(basename "$(dirname "$d")"); [[ $t == _* ]] && continue
  "$0" --one "$t" "$Q" &
  n=$((n + 1)); if (( n % JOBS == 0 )); then wait; fi
done
wait
echo "-> media/gallery/{dark,bright}/  ($(ls media/gallery/dark | wc -l | tr -d ' ') sheets each)"
