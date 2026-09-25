"""The clip encoder, for renders meant for a large screen. Manim encodes every clip with x264 at a constant rate factor
of 23 and offers no setting for it; that is fine for a page that must load fast and soft for thin text scaled up on a
big display. When CRF is set in the environment (bin/render.sh sets it for the export quality, qp), this makes Manim's
writer use it, with the preset and tuning x264 has for flat-colour animation. Unset, nothing changes."""
import os

import av as _av
from manim.scene import scene_file_writer as _writer

CRF = os.environ.get("CRF", "")


class _Container:
    """An output container whose libx264 streams take the rate factor above; everything else passes through."""

    def __init__(self, container):
        self._c = container

    def add_stream(self, *args, **kwargs):
        codec = args[0] if args else kwargs.get("codec_name")
        opts = kwargs.get("options")
        if codec == "libx264" and opts and "crf" in opts:
            kwargs["options"] = {**opts, "crf": CRF, "preset": "slow", "tune": "animation"}
        return self._c.add_stream(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._c, name)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return self._c.__exit__(*exc)


class _AV:
    """The av module as the writer sees it, with open() returning the container above for files it writes."""

    def __getattr__(self, name):
        return getattr(_av, name)

    @staticmethod
    def open(*args, **kwargs):
        c = _av.open(*args, **kwargs)
        writing = kwargs.get("mode") == "w" or (len(args) > 1 and args[1] == "w")
        return _Container(c) if writing else c


if CRF:
    _writer.av = _AV()
