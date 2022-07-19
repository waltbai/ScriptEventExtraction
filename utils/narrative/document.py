"""Document class."""
import json
import os

from utils.narrative.entity import Entity
from utils.narrative.event import Event


def _between(pos, start_pos, end_pos):
    """If the position is between the start and the end."""
    start_check = start_pos is None or start_pos <= pos
    end_check = end_pos is None or end_pos >= pos
    return start_check and end_check


class Document:
    """Document class."""

    def __init__(self, doc_id, entities, events, **kwargs):
        self.doc_id = doc_id
        self.entities = entities
        self.events = events

    @classmethod
    def from_file(cls, fpath, tokens=None):
        """Read document from path.

        :param fpath: file path.
        :param tokens: tokens of the original text.
        """
        with open(fpath, "r") as f:
            doc = json.load(f)
        tokens = tokens or []
        doc.setdefault("tokens", tokens)
        doc_id = doc["doc_id"]
        entities = [Entity(**e) for e in doc["entities"]]
        events = [Event(**e) for e in doc["events"]]
        return cls(doc_id, entities, events)

    def to_json(self):
        """Convert document to json object."""
        return {
            "doc_id": self.doc_id,
            "entities": [_.to_json() for _ in self.entities],
            "events": [_.to_json() for _ in self.events],
        }

    def get_chain_by_entity_id(self, entity, stoplist=None):
        """Get chain by entity id."""
        if stoplist is None:
            return [e for e in self.events if e.contains(entity)]
        else:
            return [e for e in self.events if e.contains(entity) and e.predicate_gr(entity) not in stoplist]

    def get_chains(self, stoplist=None):
        """Get entities and chains."""
        for entity in self.entities:
            yield entity, self.get_chain_by_entity_id(entity, stoplist)

    def get_events(self, start_pos=None, end_pos=None):
        """Get events between start and end position."""
        return [
            e for e in self.events
            if _between(e.position, start_pos, end_pos)
        ]


def document_iterator(doc_dir):
    """Iterate each document."""
    for root, dirs, files in os.walk(doc_dir):
        for f in files:
            if f.endswith(".txt"):
                fpath = os.path.join(root, f)
                doc = Document.from_file(fpath=fpath)
                yield doc
