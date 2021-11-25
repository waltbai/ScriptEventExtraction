import argparse


def parse_args():
    """Parse arguments."""
    # Load config files
    parser = argparse.ArgumentParser(prog="ScriptExtraction")
    # Basic arguments
    parser.add_argument("--corp_dir", default="/home/jinxiaolong/bl/data/gigaword_eng_5",
                        help="gigaword corpus directory")
    parser.add_argument("--work_dir", default="/home/jinxiaolong/bl/data/new_scripts",
                        help="work directory and result directory")
    parser.add_argument("--workers", default=1, type=int,
                        help="workers to process files.")
    parser.add_argument("--worker_id", default=0, type=int,
                        help="worker ID for this processor.")
    parser.add_argument("--device", default=0, type=int,
                        help="cuda device")
    return parser.parse_args()


CONFIG = parse_args()
