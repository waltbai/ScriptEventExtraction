"""Step 2: tokenize documents."""
import logging
import math
import os
import re

import spacy
from tqdm import tqdm

from config import CONFIG
from utils.common import map_input_output

logger = logging.getLogger(__name__)


def preprocess_text(text):
    """Preprocess text before sentence segmentation."""
    text = text.replace("\n", " ")
    text = text.replace("``", "''")
    return text


# def batch_tokenize_stanza(docs, tokenizer):
#     """Tokenize documents in batch using stanza."""
#     in_docs = [stanza.Document([], text=d) for d in docs]
#     out_docs = tokenizer(in_docs)
#     out_docs = [
#         "\n".join([
#             " ".join([
#                 token.text for token in sent.tokens
#             ]).strip() for sent in doc.sentences
#         ])
#         for doc in out_docs
#     ]
#     return out_docs


# def batch_tokenize_nltk(docs):
#     """Tokenize documents in batch using nltk."""
#     in_docs = [nltk.sent_tokenize(doc) for doc in docs]
#     out_docs = [
#         "\n".join([" ".join(nltk.word_tokenize(sent)) for sent in doc])
#         for doc in in_docs
#     ]
#     return out_docs


def batch_tokenize_spacy(docs, nlp):
    """Tokenize documents in batch using spacy."""
    docs = list(nlp.pipe(docs))
    out_docs = [
        re.sub(r"\n\n+", "\n",
               "\n".join([
                   " ".join([
                       token.text.strip() for token in sent
                   ]).strip() for sent in doc.sents
               ]))
        for doc in docs
    ]
    return out_docs


def tokenize(work_dir, batch_size=100):
    """Tokenize documents."""
    exclude_components = ["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"]
    nlp = spacy.load("en_core_web_lg", exclude=exclude_components)
    nlp.enable_pipe("senter")
    logger.info("Tokenizer loaded.")
    # Record all documents
    raw_dir = os.path.join(work_dir, "raw")
    tokenized_dir = os.path.join(work_dir, "tokenized")
    if not os.path.exists(tokenized_dir):
        os.makedirs(tokenized_dir)
    in_paths, out_paths = map_input_output(raw_dir, tokenized_dir)
    # Tokenize documents in batches
    tot_num = len(in_paths)
    batch_num = math.ceil(tot_num / batch_size)
    with tqdm(total=tot_num) as pbar:
        for batch_id in range(batch_num):
            # Read raw documents
            start_idx, end_idx = batch_id * batch_size, (batch_id+1) * batch_size
            in_docs = []
            for fp in in_paths[start_idx:end_idx]:
                with open(fp, "r") as f:
                    content = f.read()
                in_docs.append(preprocess_text(content))
            # Tokenize
            out_docs = batch_tokenize_spacy(docs=in_docs, nlp=nlp)
            for fp, content in zip(out_paths[start_idx:end_idx], out_docs):
                with open(fp, "w") as f:
                    f.write(content)
            pbar.update(len(in_docs))


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    tokenize(work_dir=CONFIG.work_dir,
             batch_size=100)
