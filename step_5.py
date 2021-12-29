"""Step 5: Event extraction."""
import json
import logging
import os

from tqdm import tqdm

from config import CONFIG
from utils.amrgraph import AMRGraph
from utils.convert_amr_to_event import convert_amr_to_events


def convert_align_info(align_text):
    """Convert align info string into list."""
    toks = align_text.split()
    alignments = []
    for i in range(len(toks) // 2):
        idx = int(toks[i * 2])
        short = toks[i * 2 + 1]
        alignments.append((idx, short))
    return alignments


def match_entity(head_idx, entities):
    """Match event argument head with an entity."""
    if head_idx is None:
        return None, None
    ent_id, ent_span = None, None
    for idx, entity in enumerate(entities):
        for span in entity:
            if span[0] <= head_idx <= span[1]:
                if ent_span is None:
                    ent_id, ent_span = idx, span
                # Find the smallest coref span that contains the headword
                elif ent_span[1] - ent_span[0] > span[1] - span[0]:
                    ent_id, ent_span = idx, span
    return ent_id, ent_span


def merge_events_in_doc(amr_dir, align_dir, tokenized_dir, coref_dir, doc_name):
    """Integrate information for a document."""
    # Load coreference chain
    entities = []
    with open(os.path.join(coref_dir, doc_name), "r") as f:
        coref_text = f.read()
    for line in coref_text.splitlines():
        spans = line.split("\t")
        entity_span = []
        for span in spans:
            span = span.split(" ")
            entity_span.append((int(span[0]), int(span[1])))
        entities.append(entity_span)
    # Load amr info
    with open(os.path.join(amr_dir, doc_name), "r") as f:
        amr_texts = f.read().split("\n\n")
    with open(os.path.join(tokenized_dir, doc_name), "r") as f:
        tokenized_texts = [sent.split() for sent in f.read().strip().split("\n")]
    with open(os.path.join(align_dir, doc_name), "r") as f:
        align_texts = f.read().split("\n")
    # Sentence offset
    sent_offsets = []
    cur_pos = 0
    tot_tokens = []
    for sent in tokenized_texts:
        sent_offsets.append(cur_pos)
        cur_pos += len(sent)
        tot_tokens.extend(sent)
    # Get entity mention spans
    doc_entities = []
    for eid, ent in enumerate(entities):
        mentions = [tot_tokens[span[0]:span[1]] for span in ent]
        doc_entities.append(mentions)
    # Integrate
    sent_num = len(tokenized_texts)
    doc_events = []
    for sent_id in range(sent_num):
        amr_text = amr_texts[sent_id]
        tokens = tokenized_texts[sent_id]
        align_text = align_texts[sent_id]
        sent_offset = sent_offsets[sent_id]
        # Process
        align_info = convert_align_info(align_text)
        graph = AMRGraph.parse(amr_text, align_info, tokens)
        events = convert_amr_to_events(graph)
        # Merge
        for event in events:
            event.sent_id = sent_id
            for role in event.roles:
                if role.head_pos is not None:
                    head_idx = role.head_pos + sent_offset
                    ent_id, span = match_entity(head_idx, entities)
                    if ent_id is not None:
                        # Reduce offset
                        span = (span[0] - sent_offset, span[1] - sent_offset)
                        # update span and value
                        role.span = span
                        role.value = tokens[span[0]:span[1]]
                        role.ent_id = ent_id
            # If the verb position cannot be found,
            # set to sentence length
            if event.verb_pos is None:
                event.verb_pos = len(tokens)
        doc_events.extend(events)
    return doc_entities, doc_events


def completeness_check(amr_dir, align_dir, tokenized_dir, coref_dir, doc_name):
    """Check information completeness."""
    for base_dir in [amr_dir, align_dir, tokenized_dir, coref_dir]:
        base_path = os.path.join(base_dir, doc_name)
        if not os.path.exists(base_path):
            return False
    return True


def event_extraction(work_dir):
    """Extract events."""
    amr_dir = os.path.join(work_dir, "amr")
    align_dir = os.path.join(work_dir, "align")
    coref_dir = os.path.join(work_dir, "coref")
    event_dir = os.path.join(work_dir, "event")
    tokenized_dir = os.path.join(work_dir, "tokenized")
    # Build amr graph
    with tqdm() as pbar:
        for subdir in os.listdir(amr_dir):
            # Prepare sub directory
            base_amr_dir = os.path.join(amr_dir, subdir)
            base_align_dir = os.path.join(align_dir, subdir)
            base_tokenized_dir = os.path.join(tokenized_dir, subdir)
            base_coref_dir = os.path.join(coref_dir, subdir)
            base_event_dir = os.path.join(event_dir, subdir)
            if not os.path.exists(base_event_dir):
                os.makedirs(base_event_dir)
            for fn in os.listdir(base_amr_dir):
                pbar.set_description(f"Processing {fn}")
                # Completeness check
                flag = completeness_check(amr_dir=base_amr_dir,
                                          tokenized_dir=base_tokenized_dir,
                                          align_dir=base_align_dir,
                                          coref_dir=base_coref_dir,
                                          doc_name=fn)
                if flag:
                    entities, events = merge_events_in_doc(amr_dir=base_amr_dir,
                                                           tokenized_dir=base_tokenized_dir,
                                                           align_dir=base_align_dir,
                                                           coref_dir=base_coref_dir,
                                                           doc_name=fn)
                    events = sorted(events, key=lambda x: (x.sent_id, x.verb_pos))
                    doc = {
                        "doc_id": fn.replace(".txt", ""),
                        "entities": entities,
                        "events": [e.to_json() for e in events]
                    }
                    with open(os.path.join(base_event_dir, fn), "w") as f:
                        json.dump(doc, f)
                else:
                    pass
                pbar.update(1)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    logging.getLogger("penman").setLevel(logging.CRITICAL)
    logging.getLogger("allennlp").setLevel(logging.WARNING)
    event_extraction(CONFIG.work_dir)
