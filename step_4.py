"""Step 4: Coreference resolution."""
import logging
import os

from allennlp.predictors import Predictor

from config import CONFIG
from common import map_input_output


def coref_resolution(work_dir, model_path=None):
    """Coreference resolution."""
    tokenized_dir = os.path.join(work_dir, "tokenized")
    coref_dir = os.path.join(work_dir, "coref")
    # Load model
    default_model_path = "https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2021.03.10.tar.gz"
    model_path = model_path or default_model_path
    model = Predictor.from_path(model_path)
    # Map input and output paths
    in_paths, out_paths = map_input_output(tokenized_dir, coref_dir)
    # Predict
    for in_fp, out_fp in zip(in_paths, out_paths):
        with open(in_fp, "r") as f:
            content = f.read().split()
        # Predict raw doc
        # result = model.predict(docuent=" ".join(content))
        # Predict tokenized doc
        result = model.predict_tokenized(tokenized_document=content)
        clusters = result["clusters"]
        for chain in clusters:
            for start, end in chain:
                print(content[start:end+1], end="\t")
        # print(result)
        input()


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    logging.getLogger("allennlp").setLevel(logging.WARNING)
    coref_resolution(CONFIG.work_dir)


