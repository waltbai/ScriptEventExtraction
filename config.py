import argparse


USER_DIR = "/home/jinxiaolong"


def parse_args():
    """Parse arguments."""
    # Load config files
    parser = argparse.ArgumentParser(prog="ScriptExtraction")
    # Basic arguments
    parser.add_argument("--corp_dir", default=f"{USER_DIR}/bl/data/gigaword_eng_5",
                        help="the decompressed directory of gigaword corpus")
    parser.add_argument("--work_dir", default=f"{USER_DIR}/bl/data/new_scripts",
                        help="the directory to store dataset")
    parser.add_argument("--pb_dir", default=f"{USER_DIR}/bl/data/propbank-frames",
                        help="the propbank frames directory")
    parser.add_argument("--fn_dir", default=f"{USER_DIR}/bl/data/fndata-1.7",
                        help="the framenet corpus directory")
    parser.add_argument("--coref_model_path",
                        # default=None,
                        default=f"{USER_DIR}/bl/data/coref-spanbert-large-2021.03.10.tar.gz",
                        help="the local coref model path")
    parser.add_argument("--start_year", default=1994, type=int,
                        help="the start year of the corpus, used only in step 1")
    parser.add_argument("--end_year", default=1994, type=int,
                        help="the end year of the corpus, used only in step 1")
    parser.add_argument("--workers", default=1, type=int,
                        help="total number of processors, used in step 3 and 4")
    parser.add_argument("--worker_id", default=0, type=int,
                        help="the worker id of this processor, used in step 3 and 4")
    parser.add_argument("--device", default=0, type=int,
                        help="the cuda device used by this processor, used in step 3 and 4")
    parser.add_argument("--seed", default=10000019, type=int,
                        help="the random seed when generating questions.")
    parser.add_argument("--num_questions", default=5000, type=int,
                        help="number of questions to be sampled.")
    return parser.parse_args()


CONFIG = parse_args()
