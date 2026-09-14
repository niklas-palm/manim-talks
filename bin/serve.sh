#!/usr/bin/env bash
# Serve one talk over local http and open its presenter window. Usage: bin/serve.sh <talk> [port]
# Two windows opened from file:// URLs cannot always talk to each other (opaque origins), and <video> needs byte-range
# requests to seek, which python's http.server does not offer; bin/serve.py does.
cd "$(dirname "$0")/.."
TALK=${1:?usage: bin/serve.sh <talk> [port]}; PORT=${2:-8765}
[[ -f talks/$TALK/presenter.html ]] || { echo "talks/$TALK has no presenter.html yet: run bin/render.sh $TALK first"; exit 1; }
pkill -f "serve.py $PORT" 2>/dev/null; sleep 0.2
(cd "talks/$TALK" && nohup python3 ../../bin/serve.py $PORT > /dev/null 2>&1 &)
sleep 0.5; open "http://localhost:$PORT/presenter.html"
