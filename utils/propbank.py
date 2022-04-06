"""Propbank frames."""

import os

import bs4


class Frame:
    """Propbank frame."""


class PropBank:
    """Propbank."""

    def __init__(self, frames):
        self._frames = frames

    @classmethod
    def from_dir(cls, pb_dir):
        """Load propbank from directory."""
        pb_dir = os.path.join(pb_dir, "frames")
        xmls = [fn for fn in os.listdir(pb_dir) if fn.endswith(".xml")]
        frames = {}
        for fn in xmls:
            fp = os.path.join(pb_dir, fn)
            with open(fp, "r") as f:
                dom = bs4.BeautifulSoup(f.read(), "lxml")
            for frame in dom.find_all("roleset"):
                frame_id = frame.get("id")
                for alias in frame.find("aliases").find_all("alias"):
                    fn_frame = alias.get("framenet")
                    if fn_frame and fn_frame != "-":
                        frames.setdefault(frame_id, set()).update(fn_frame.split(" "))
