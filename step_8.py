"""Step 8: Count stop verbs."""
import logging
import os
from collections import Counter

from tqdm import tqdm

from config import CONFIG
from utils.narrative.document import Document


def stop_list(work_dir, num_verbs=10):
    """Generate stop list according to train documents."""
    event_dir = os.path.join(work_dir, "event")
    predicate_gr_counter = Counter()
    polar_count = 0
    with tqdm() as pbar:
        for root, dirs, files in os.walk(event_dir):
            for fn in files:
                fp = os.path.join(root, fn)
                doc = Document.from_file(fp)
                for entity, chain in doc.get_chains():
                    predicate_gr_counter.update([event.predicate_gr(entity) for event in chain])
                    # for event in chain:
                    #     for role in event.roles:
                    #         if role.role == ":polarity":
                    #             polar_count += 1
                    #             print(doc.doc_id)
                    #             print(role)
                    #             input()
                pbar.update(1)
    result = predicate_gr_counter.most_common(num_verbs)
    stop_list_path = os.path.join(work_dir, "stoplist.txt")
    with open(stop_list_path, "w") as f:
        for pgr, freq in result:
            f.write(f"{pgr[0]}\t{pgr[1]}\n")


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    stop_list(CONFIG.work_dir)
