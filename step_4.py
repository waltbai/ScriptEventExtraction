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
    with tqdm(total=len(in_paths)) as pbar:
        for in_fp, out_fp in zip(process_in, process_out):
            if os.path.exists(out_fp):
                pbar.update()
                continue
            with open(in_fp, "r") as f:
                content = f.read().strip().split()
            # Predict raw doc
            # result = model.predict(docuent=" ".join(content))
            # Predict tokenized doc
            try:
                result = model.predict_tokenized(tokenized_document=content)
                clusters = result["clusters"]
                result_str = "\n".join(
                    ["\t".join([f"{start} {end+1}" for start, end in chain])
                     for chain in clusters])
                with open(out_fp, "w") as f:
                    f.write(result_str)
            except (RuntimeError, IndexError, ValueError):
                pass
            pbar.update()


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    logging.getLogger("allennlp").setLevel(logging.CRITICAL)
    coref_resolution(CONFIG.work_dir,
                     workers=CONFIG.workers,
                     worker_id=CONFIG.worker_id,
                     device=CONFIG.device)
