"""Generate dev/test questions."""
import json
import logging
import math
import os
import random
from copy import deepcopy

from config import CONFIG
from utils.narrative.document import Document


def sample_chain(doc_dir, context_size):
    """Sample a chain from a random document."""
    entity, chain, doc = None, None, None
    while chain is None:
        # Randomly sample a doc
        fn_list = list(os.listdir(doc_dir))
        fn_path = os.path.join(doc_dir, random.choice(fn_list))
        doc = Document.from_file(fn_path)
        # Randomly sample a chain
        chains = [(entity, chain) for entity, chain in doc.get_chains()
                  if len(chain) > context_size]
        if len(chains) == 0:
            continue
        else:
            entity, chain = random.choice(chains)
    return entity, chain, doc


def sample_neg_event(doc_dir, context_size):
    """Sample a negative event from doc."""
    entity, chain, doc = sample_chain(doc_dir, context_size)
    event = random.choice(chain)
    return entity, event


def sample_single_question(doc_dir,
                           context_size=8,
                           num_distractors=4):
    """Sample a single question from docs."""
    entity, chain, doc = sample_chain(doc_dir, context_size)
    answer_idx = random.choice(range(context_size, len(chain)))
    answer = chain[answer_idx]
    context = chain[answer_idx-context_size:answer_idx]
    # Generate distractors
    non_protagonist_entities = [e for e in doc.entities if e is not entity]
    distractors = []
    for _ in range(num_distractors):
        neg_protagonist, neg_event = sample_neg_event(doc_dir, context_size)
        event = deepcopy(neg_event)
        protagonist_id = neg_protagonist.ent_id
        # Replace each entity argument with a non-protagonist entity
        for role in event.roles:
            if role.ent_id is not None:
                if role.ent_id == protagonist_id:
                    # Replace the argument with protagonist
                    role.ent_id = entity.ent_id
                    role.value = entity.head
                    role.concept = entity.concept
                elif len(non_protagonist_entities) > 0:
                    # In some cases, there are no other entities
                    rand_ent = random.choice(non_protagonist_entities)
                    role.ent_id = rand_ent.ent_id
                    role.value = rand_ent.head
                    role.concept = rand_ent.concept
                else:
                    # if there are no other entities, view the arguments as common words
                    role.ent_id = None
        distractors.append(event)
    # Construct question
    entity_id = entity.ent_id
    choices = distractors + [answer]
    random.shuffle(choices)
    target = choices.index(answer)
    json_doc = doc.to_json()
    json_doc["entity_id"] = entity_id
    json_doc["context"] = [_.to_json() for _ in context]
    json_doc["choices"] = [_.to_json() for _ in choices]
    json_doc["target"] = target
    return json_doc


def sample_questions(doc_dir, question_dir, num_questions=1000):
    """Sample questions from docs."""
    num_zfill = math.ceil(math.log10(num_questions))
    for qid in range(num_questions):
        question_path = os.path.join(
            question_dir, f"question{str(qid).zfill(num_zfill)}.txt")
        question = sample_single_question(doc_dir)
        with open(question_path, "w") as f:
            json.dump(question, f)


def generate_eval_set(work_dir, num_questions=1000, seed=0):
    """Generate evaluation datasets."""
    logging.info("Generating dev set ...")
    random.seed(seed)
    dev_doc_dir = os.path.join(work_dir, "rich_docs", "dev")
    dev_question_dir = os.path.join(work_dir, "eval", "dev")
    os.makedirs(dev_question_dir, exist_ok=True)
    sample_questions(dev_doc_dir, dev_question_dir, num_questions)
    logging.info(f"Dev set generated to {dev_question_dir}, "
                 f"totally {num_questions} questions.")
    logging.info("Generating test set ...")
    random.seed(seed)
    test_doc_dir = os.path.join(work_dir, "rich_docs", "test")
    test_question_dir = os.path.join(work_dir, "eval", "test")
    os.makedirs(test_question_dir, exist_ok=True)
    sample_questions(test_doc_dir, test_question_dir, num_questions)
    logging.info(f"Test set generated to {test_question_dir}, "
                 f"totally {num_questions} questions.")


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    generate_eval_set(CONFIG.work_dir, CONFIG.num_questions, seed=CONFIG.seed)
