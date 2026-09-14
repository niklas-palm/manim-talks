#!/usr/bin/env python3
"""Serve the deck over local http with byte-range support.

The standard library's `python3 -m http.server` answers every request with the whole file and no Accept-Ranges header.
Chrome then treats a video as unseekable: setting currentTime is ignored, so the player replayed each scene from its
start on every step and the hold at a step boundary left the element blank. This handler honours Range requests, which
is all a <video> needs to seek. Usage: python3 serve.py [port] [folder]   (serves the current folder by default)"""
import os
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class RangeHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        rng = self.headers.get("Range")
        if not rng or not os.path.isfile(path):
            return super().send_head()
        size = os.path.getsize(path)
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        start = int(m.group(1)) if m and m.group(1) else 0
        end = int(m.group(2)) if m and m.group(2) else size - 1
        end = min(end, size - 1)
        if start > end:
            self.send_error(416, "Range Not Satisfiable")
            return None
        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._remaining = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        n = getattr(self, "_remaining", None)
        if n is None:
            return super().copyfile(source, outputfile)
        while n > 0:
            chunk = source.read(min(n, 1 << 16))
            if not chunk:
                break
            outputfile.write(chunk)
            n -= len(chunk)
        self._remaining = None

    def end_headers(self):
        if self.command == "GET" and "Accept-Ranges" not in "".join(map(str, self._headers_buffer)):
            self.send_header("Accept-Ranges", "bytes")   # tells Chrome up front that the media is seekable
        super().end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    if len(sys.argv) > 2:          # optional folder to serve; default is the current directory (bin/serve.sh starts it inside the talk folder)
        os.chdir(sys.argv[2])
    ThreadingHTTPServer(("127.0.0.1", port), RangeHandler).serve_forever()
