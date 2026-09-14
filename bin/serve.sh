#!/usr/bin/env bash
# Serve the repository over local http and open one talk's presenter window. Usage: bin/serve.sh <talk> [port]
# One server for every talk: pages live at http://localhost:<port>/<talk folder>/presenter.html, so opening a second
# talk never breaks the windows of the first. Two windows opened from file:// URLs cannot always talk to each other
# (opaque origins), and <video> needs byte-range requests to seek, which python's http.server does not offer;
# bin/serve.py does. Stop it with: pkill -f "serve.py <port>"
set -euo pipefail
cd "$(dirname "$0")/.."
TALK=${1:?usage: bin/serve.sh <talk> [port]}; PORT=${2:-8765}
# The port is quoted and checked because it is pasted into a command line: unquoted, "8765 /tmp" served /tmp instead.
[[ $PORT =~ ^[0-9]+$ ]] && (( PORT >= 1024 && PORT <= 65535 )) || { echo "port must be a number from 1024 to 65535, not $PORT"; exit 1; }
DIR=$(.venv/bin/python -c "import sys; sys.path.insert(0,'.'); from lib.talks import dir_of; print(dir_of(sys.argv[1]))" "$TALK")
[[ -f $DIR/presenter.html ]] || { echo "$DIR has no presenter.html yet: run bin/render.sh $TALK first"; exit 1; }
LOG=${TMPDIR:-/tmp}/manim-talks-serve-$PORT.log
if ! pgrep -f "serve.py $PORT" > /dev/null; then
  nohup .venv/bin/python bin/serve.py "$PORT" "$PWD" > "$LOG" 2>&1 &
  for _ in 1 2 3 4 5 6 7 8 9 10; do        # a port in use or out of reach fails here, not silently two minutes before a talk
    sleep 0.2
    curl -s -o /dev/null "http://localhost:$PORT/$DIR/presenter.html" && break
  done
  curl -s -o /dev/null "http://localhost:$PORT/$DIR/presenter.html" || { echo "the server did not come up on port $PORT:"; cat "$LOG"; exit 1; }
fi
open "http://localhost:$PORT/$DIR/presenter.html"
