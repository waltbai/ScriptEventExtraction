"""Step 1: extract documents."""
import gzip
import logging
import os

import bs4
from tqdm import tqdm

from config import CONFIG


logger = logging.getLogger(__name__)


def qualified_files(file_list, start_year=1994, end_year=2004):
    """Check if the file is qualified."""
    result = []
    for fn in file_list:
        if not fn.endswith(".gz"):
            continue
        flag = False
        for year in range(start_year, end_year+1):
            if fn.startswith("nyt_eng_{}".format(year)):
                flag = True
                break
        if flag:
            result.append(fn)
    return result


def extract_documents(corp_dir, work_dir):
    """Extract documents."""
    gz_dir = os.path.join(corp_dir, "data/nyt_eng")
    gz_list = qualified_files(os.listdir(gz_dir), end_year=1994)
    # extract documents
    total_docs = 0
    raw_dir = os.path.join(work_dir, "raw")
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)
    with tqdm(total=len(gz_list)) as pbar:
        for gz in gz_list:
            pbar.set_description("Extracting {}".format(gz))
            gzip_path = os.path.join(gz_dir, gz)
            subdir = os.path.join(raw_dir, gz.replace(".gz", ""))
            if not os.path.exists(subdir):
                os.makedirs(subdir)
            with gzip.open(gzip_path, "rb") as f:
                dom = bs4.BeautifulSoup(f.read(), "lxml")
            for doc in dom.find_all("doc", type="story"):
                # find doc content
                doc_id = doc["id"]
                headline = doc.find("headline")
                dateline = doc.find("dateline")
                text = doc.find("text").get_text()
                # write to file
                file_path = os.path.join(subdir, "{}.txt".format(doc_id))
                with open(file_path, "w") as f:
                    f.write(text)
                # doc counter
                total_docs += 1
            pbar.update(1)
    logger.info("Totally {} docs extracted and tokenized.".format(total_docs))


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    extract_documents(corp_dir=CONFIG.corp_dir, work_dir=CONFIG.work_dir)
