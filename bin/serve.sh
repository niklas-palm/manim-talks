#!/usr/bin/env bash
# Serve the repository over local http and open one talk's presenter window. Usage: bin/serve.sh <talk> [port]
# One server for every talk: pages live at http://localhost:<port>/<talk folder>/presenter.html, so opening a second
# talk never breaks the windows of the first. Two windows opened from file:// URLs cannot always talk to each other
# (opaque origins), and <video> needs byte-range requests to seek, which python's http.server does not offer;
# bin/serve.py does.
cd "$(dirname "$0")/.."
TALK=${1:?usage: bin/serve.sh <talk> [port]}; PORT=${2:-8765}
DIR=$(python3 -c "import sys; sys.path.insert(0,'.'); from lib.talks import dir_of; print(dir_of('$TALK'))")
[[ -f $DIR/presenter.html ]] || { echo "$DIR has no presenter.html yet: run bin/render.sh $TALK first"; exit 1; }
pgrep -f "serve.py $PORT" > /dev/null || (nohup python3 bin/serve.py $PORT "$PWD" > /dev/null 2>&1 &)
sleep 0.5; open "http://localhost:$PORT/$DIR/presenter.html"
