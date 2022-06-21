"""Step 7: Split data."""
import json
import logging
import os
from shutil import copyfile

from tqdm import tqdm

from config import CONFIG


def split_data(work_dir):
    """Split train/dev/test documents."""
    logging.info("Splitting train/dev/test documents.")
    # Filter file list
    with open("data/duplicates", "r") as f:
        duplicates = set([f"{fn}.txt" for fn in f.read().splitlines()])
    # Dev document list
    with open("data/dev.list", "r") as f:
        dev_list = set(f.read().splitlines())
    # Test document list.
    with open("data/test.list", "r") as f:
        test_list = set(f.read().splitlines())
    # Dataset directories
    train_dir = os.path.join(work_dir, "rich_docs", "train")
    if not os.path.exists(train_dir):
        os.makedirs(train_dir)
    dev_dir = os.path.join(work_dir, "rich_docs", "dev")
    if not os.path.exists(dev_dir):
        os.makedirs(dev_dir)
    test_dir = os.path.join(work_dir, "rich_docs", "test")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    # Split
    event_dir = os.path.join(work_dir, "event")
    total_train, total_dev, total_test = 0, 0, 0
    with tqdm() as pbar:
        for root, dirs, files in os.walk(event_dir):
            for fn in files:
                # Skip duplicate document
                if fn in duplicates:
                    continue
                # Read document content
                event_fp = os.path.join(root, fn)
                # Save to corresponding directory
                if fn in dev_list:
                    target_fp = os.path.join(dev_dir, fn)
                    total_dev += 1
                elif fn in test_list:
                    target_fp = os.path.join(test_dir, fn)
                    total_test += 1
                else:
                    target_fp = os.path.join(train_dir, fn)
                    total_train += 1
                copyfile(event_fp, target_fp)
                pbar.update()
    logging.info(f"Totally {total_train} train docs,"
                 f"{total_dev} dev docs,"
                 f"{total_test} test docs.")


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    split_data(CONFIG.work_dir)
