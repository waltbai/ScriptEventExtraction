"""Step 3: Parse documents with AMR parser."""
import logging
import math
import os

import amrlib
from tqdm import tqdm

from utils.amrgraph import align_graph
from config import CONFIG
from utils.common import map_input_output

logger = logging.getLogger(__name__)


def batch_parse_amrlib(docs, parser):
    """Parse documents in batch."""
    # GSII is much faster
    spans = []
    sents = []
    for doc in docs:
        spans.append((len(spans), len(doc)))
        sents.extend(doc)
    graphs = parser.parse_sents(sents)
    results = []
    for start, offset in spans:
        # results.append("\n".join(graphs[start:start+offset]))   # for gsii
        results.append("\n\n".join(graphs[start:start+offset]))   # for t5 and spring
    return results


def parse(work_dir, batch_size=10, workers=1, worker_id=0, device=0):
    """Parse documents."""
    logger.info("Parsing documents with amr parser")
    # parser = amrlib.load_stog_model(batch_size=5000)    # for gsii
    parser = amrlib.load_stog_model(device=device)   # for t5 and spring
    tokenized_dir = os.path.join(work_dir, "tokenized")
    amr_dir = os.path.join(work_dir, "amr")
    if not os.path.exists(amr_dir):
        os.makedirs(amr_dir)
    in_paths, out_paths = map_input_output(tokenized_dir, amr_dir)
    in_paths = [_ for idx, _ in enumerate(in_paths) if (idx % workers) == worker_id]
    out_paths = [_ for idx, _ in enumerate(out_paths) if (idx % workers) == worker_id]
    # Filter parsed docs
    process_in, process_out = [], []
    for fin, fout in zip(in_paths, out_paths):
        if not os.path.exists(fout):
            process_in.append(fin)
            process_out.append(fout)
    # Parse
    error_in_paths = []
    error_out_paths = []
    tot_num = len(process_in)
    success_num = 0
    with tqdm(total=tot_num) as pbar:
        for i in range(math.ceil(tot_num / batch_size)):
            start, end = i * batch_size, (i+1) * batch_size
            docs = []
            for fp in process_in[start:end]:
                with open(fp, "r") as f:
                    content = f.read().splitlines()
                docs.append(content)
            try:
                results = batch_parse_amrlib(docs, parser)
                # results = batch_parse_transition(docs, parser)
                for idx, fp in enumerate(process_out[start:end]):
                    with open(fp, "w") as f:
                        f.write(results[idx])
                        success_num += 1
                pbar.update(batch_size)
            except (AttributeError, RuntimeError, IndexError, TypeError):
                # logger.info("Parse error detected.")
                error_in_paths.extend(process_in[start:end])
                error_out_paths.extend(process_out[start:end])
    # Re-do error batches
    error_files = []
    for fp_i, fp_o in zip(error_in_paths, error_out_paths):
        with open(fp_i, "r") as f:
            content = f.read().splitlines()
        try:
            results = batch_parse_amrlib([content], parser)
            with open(fp_o, "w") as f:
                f.write(results[0])
                success_num += 1
        except (AttributeError, RuntimeError, IndexError, TypeError):
            error_files.append(fp_i)
    logger.info("Totally {} docs succeeded, {} failed.".format(
        success_num, len(error_files)))
    logger.info("\n{}".format("\n".join(error_files)))


def align(work_dir):
    """Align amr graphs to sentences."""
    logger.info("Aligning amr graphs to sentences")
    # set directories
    amr_dir = os.path.join(work_dir, "amr")
    align_dir = os.path.join(work_dir, "align")
    if not os.path.exists(align_dir):
        os.makedirs(align_dir)
    # map input and output paths
    in_paths, out_paths = map_input_output(amr_dir, align_dir)
    # align
    with tqdm(total=len(in_paths)) as pbar:
        for in_fp, out_fp in zip(in_paths, out_paths):
            with open(in_fp, "r") as f:
                graphs = f.read().split("\n\n")
            align_results = []
            for graph_string in graphs:
                result = align_graph(graph_string)
                result = ret_val = "\t".join(["{} {}".format(i, s) for i, s in result])
                align_results.append(result)
            with open(out_fp, "w") as f:
                f.write("\n".join(align_results))
            # update progress bar
            pbar.update()


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    logging.getLogger("penman").setLevel(logging.CRITICAL)
    logging.getLogger("amrlib").setLevel(logging.CRITICAL)
    # parse(CONFIG.work_dir,
    #       batch_size=10,
    #       workers=CONFIG.workers,
    #       worker_id=CONFIG.worker_id,
    #       device=CONFIG.device)
    align(CONFIG.work_dir)
