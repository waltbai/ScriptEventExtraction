"""Step 5: Event extraction."""
import logging
import os

import penman
from amrlib.alignments.rbw_aligner import RBWAligner

from config import CONFIG
from utils.amrgraph import AMRGraph
from utils.convert_amr_to_event import convert_amr_to_event


def convert_align_info(align_text):
    """Convert align info string into list."""
    toks = align_text.split()
    alignments = []
    for i in range(len(toks) // 2):
        idx = int(toks[i * 2])
        short = toks[i * 2 + 1]
        alignments.append((idx, short))
    return alignments


def event_extraction(work_dir):
    """Extract events."""
    amr_dir = os.path.join(work_dir, "amr")
    align_dir = os.path.join(work_dir, "align")
    # coref_dir = os.path.join(work_dir, "coref")
    event_dir = os.path.join(work_dir, "event")
    tokenized_dir = os.path.join(work_dir, "tokenized")
    # Load coreference chain
    pass
    # Build amr graph
    for subdir in os.listdir(amr_dir):
        base_amr_dir = os.path.join(amr_dir, subdir)
        base_align_dir = os.path.join(align_dir, subdir)
        base_tokenized_dir = os.path.join(tokenized_dir, subdir)
        for fn in os.listdir(base_amr_dir):
            if os.path.exists(os.path.join(base_align_dir, fn)):
                # Both amr graph and align info exist
                with open(os.path.join(base_amr_dir, fn), "r") as f:
                    amr_texts = f.read().split("\n\n")
                with open(os.path.join(base_align_dir, fn), "r") as f:
                    align_texts = f.read().split("\n")
                with open(os.path.join(base_tokenized_dir, fn), "r") as f:
                    tokens = f.read().split("\n")
                for amr_text, align_text, token in zip(amr_texts, align_texts, tokens):
                    align_info = convert_align_info(align_text)
                    token = token.split()
                    g = AMRGraph.parse(amr_text, align_info, token)
                    print(amr_text)
                    for event in convert_amr_to_event(graph=g):
                        print(event)
                        input()


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    logging.getLogger("penman").setLevel(logging.CRITICAL)
    logging.getLogger("allennlp").setLevel(logging.WARNING)
    event_extraction(CONFIG.work_dir)
