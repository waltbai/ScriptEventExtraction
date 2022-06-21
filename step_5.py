"""Step 5: Map propbank frames to framenet frames."""

import logging
import os

import bs4

from config import CONFIG


def map_frames(pb_dir, work_dir):
    """Map propbank frames to framenet frames.

    :param pb_dir: propbank directory
    :param work_dir: working directory
    """
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
            for alias in frame.find("aliases").find_all("alias"):
                fn_frame = alias.get("framenet")
                if fn_frame and fn_frame != "-":
                    frames.setdefault(frame_id, set()).update(fn_frame.split(" "))
    map_path = os.path.join(work_dir, "frame.map")
    with open(map_path, "w") as f:
        for frame_id in frames:
            v = "\t".join(frames[frame_id])
            f.write(f"{frame_id}\t{v}\n")
    logging.info(f"Save mapping file to {map_path}")
    pb_path = os.path.join(work_dir, "frame.list")
    with open(pb_path, "w") as f:
        for frame_id in pb_frames:
            f.write(f"{frame_id}\n")
    logging.info(f"Save propbank frame file to {pb_path}")


def extract_frame_relations(fn_dir, work_dir):
    """Extract relations between framenet frames.

    :param fn_dir: framenet directory
    :param work_dir: working directory
    """
    rel_path = os.path.join(fn_dir, "frRelation.xml")
    with open(rel_path, "r") as f:
        dom = bs4.BeautifulSoup(f.read(), "lxml")
    relations = []
    relation_type = []
    for rel_type in dom.find_all("framerelationtype"):
        rel_name = rel_type.get("name")
        for rel_inst in rel_type.find_all("framerelation"):
            sup_frame = rel_inst.get("superframename")
            sub_frame = rel_inst.get("subframename")
            relations.append((sup_frame, rel_name, sub_frame))
            if rel_name not in relation_type:
                relation_type.append(rel_name)
    relations_path = os.path.join(work_dir, "frame.rel")
    with open(relations_path, "w") as f:
        for rel in relations:
            f.write("{}\n".format("\t".join(rel)))
    logging.info(f"Save relation to {relations_path}")
    relation_type_path = os.path.join(work_dir, "fr_relation.list")
    with open(relation_type_path, "w") as f:
        for rel in relation_type:
            f.write(f"{rel}\n")
    logging.info(f"Save relation list to {relation_type_path}")


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    map_frames(CONFIG.pb_dir, CONFIG.work_dir)
    extract_frame_relations(CONFIG.fn_dir, CONFIG.work_dir)
