"""Step 4: Coreference resolution."""
import logging
import os
import sklearn  # avoid error when import allennlp

from allennlp.predictors import Predictor
from tqdm import tqdm

from config import CONFIG
from utils.common import map_input_output


def coref_resolution(work_dir, model_path=None, workers=1, worker_id=0, device=0):
    """Coreference resolution."""
    tokenized_dir = os.path.join(work_dir, "tokenized")
    coref_dir = os.path.join(work_dir, "coref")
    # Load model
    default_model_path = "https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2021.03.10.tar.gz"
    model_path = model_path or default_model_path
    model = Predictor.from_path(model_path, cuda_device=device)
    # Map input and output paths
    in_paths, out_paths = map_input_output(tokenized_dir, coref_dir)
    in_paths = [_ for idx, _ in enumerate(in_paths) if (idx % workers) == worker_id]
    out_paths = [_ for idx, _ in enumerate(out_paths) if (idx % workers) == worker_id]
    # Filter parsed docs
    process_in, process_out = [], []
    for fin, fout in zip(in_paths, out_paths):
        if not os.path.exists(fout):
            process_in.append(fin)
            process_out.append(fout)
    # Predict
    error_in_paths = []
    error_out_paths = []
    tot_num = len(process_in)
    success_num = 0
    with tqdm(total=len(process_in)) as pbar:
        for in_fp, out_fp in zip(process_in, process_out):
            with open(in_fp, "r") as f:
                content = f.read().strip().split()
            try:
                # Predict raw doc
                # result = model.predict(docuent=" ".join(content))
                # Predict tokenized doc
                result = model.predict_tokenized(tokenized_document=content)
                clusters = result["clusters"]
                result_str = "\n".join(
                    ["\t".join([f"{start} {end+1}" for start, end in chain])
                     for chain in clusters])
                with open(out_fp, "w") as f:
                    f.write(result_str)
                success_num += 1
            except (RuntimeError, IndexError, ValueError):
                error_in_paths.append(in_fp)
                error_out_paths.append(out_fp)
            pbar.update()
    logging.info(f"Totally {success_num} docs succeeded, {len(error_in_paths)} failed.")
    logging.info("\n" + "\n".join(error_in_paths))


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    logging.getLogger("allennlp").setLevel(logging.CRITICAL)
    coref_model_path = CONFIG.coref_model_path or None
    coref_resolution(CONFIG.work_dir,
                     model_path=coref_model_path,
                     workers=CONFIG.workers,
                     worker_id=CONFIG.worker_id,
                     device=CONFIG.device)
