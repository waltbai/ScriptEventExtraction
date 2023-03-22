"""Step 5: Map propbank frames to framenet frames."""

import logging
import os

import bs4

from config import CONFIG


def extract_frames(pb_dir, work_dir):
    pb_dir = os.path.join(pb_dir, "frames")
    xmls = [fn for fn in os.listdir(pb_dir) if fn.endswith(".xml")]
    frames = {}
    pb_frames = []
    for fn in xmls:
        fp = os.path.join(pb_dir, fn)
        with open(fp, "r") as f:
            dom = bs4.BeautifulSoup(f.read(), "lxml")
        for frame in dom.find_all("roleset"):
            frame_id = frame.get("id")
            pb_frames.append(frame_id)
    pb_path = os.path.join(work_dir, "frame.list")
    with open(pb_path, "w") as f:
        for frame_id in pb_frames:
            f.write(f"{frame_id}\n")
    logging.info(f"Save propbank frame file to {pb_path}")


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    extract_frames(CONFIG.pb_dir, CONFIG.work_dir)
