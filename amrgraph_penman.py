"""Definition of AMR graph class."""
import re

import penman
import spacy
from amrlib.alignments.rbw_aligner import RBWAligner
from penman.models import noop

VERB_FRAME_PATTERN = re.compile(r".+-\d+")
STATIC_FRAMES = ["have-rel-role-91", "have-org-role-91"]
CONJUNCTION_FRAMES = ["and"]
# Tokenizer
_exclude_components = ["tok2vec", "tagger", "parser",
                       "attribute_ruler", "lemmatizer", "ner"]
TOKENIZER = spacy.load("en_core_web_sm", exclude=_exclude_components)


def align_graph(graph):
    """Align single amr graph."""
    align_result = RBWAligner.from_string_w_json(graph)
    ret_val = []
    # Return in one line, "<index0> <short0>\t<index1> <short1>\t..."
    for i, t in enumerate(align_result.alignments):
        if t is not None:
            # t.triple: (short, ":instance", name)
            ret_val.append((i, t.triple[0]))
    # ret_val = "\t".join(["{} {}".format(i, s) for i, s in ret_val])
    return ret_val


# We define amr node/graph class instead of
#   directly using penman graph for extensibility.
class AMRNode:
    """Node in AMR graph."""

    def __init__(self,
                 id_="",
                 value="",
                 relations=None,
                 token_num=None):
        # Accessible
        self.id = id_
        self.value = value
        self.relations = relations or {}
        self.scope = [False] * (token_num or 0)
        # Unaccessible
        self._token_num = token_num
        # Check type
        type_ = "concept"
        if VERB_FRAME_PATTERN.match(value):
            type_ = "verb"
        if value in STATIC_FRAMES:
            type_ = "static"
        if value in CONJUNCTION_FRAMES:
            type_ = "conjunction"
        self.type = type_

    def __repr__(self):
        start, end = self.span
        if start is None or end is None:
            return f"({self.id},{self.value})"
        else:
            return f"({self.id},{self.value},{start}-{end})"

    @property
    def children(self):
        """Return all children of this node."""
        children = []
        for r in self.relations:
            for t in self.relations[r]:
                children.append(t)
        return children

    @property
    def head_idx(self):
        """Return head word index."""
        for i in range(len(self.scope))[::-1]:
            if self.scope[i]:
                return i
        return None

    @property
    def span(self):
        """Return rightmost continuous scope."""
        start, end = None, None
        # TODO: Continuity is a really strong constraint.
        #   Try discrete tolerant = 1
        skip = 0
        tolerant = 1
        for i in range(len(self.scope))[::-1]:
            if end is None and self.scope[i]:
                end = i + 1
            if end is not None:
                if self.scope[i]:
                    skip = 0
                    start = i
                elif skip < tolerant:
                    skip += 1
                else:
                    break
        return start, end

    def add_relation(self, rel_type, tail):
        """Add a relation."""
        self.relations.setdefault(rel_type, []).append(tail)

    def remove_relation(self, rel_type, tail):
        """Remove a relation."""
        idx = self.relations[rel_type].index(tail)
        del self.relations[rel_type][idx]

    def update_scope(self, align_idx):
        """Update node scope with aligned token index."""
        if len(self.scope) >= align_idx:
            self.scope[align_idx] = True

    def update_scope_from_children(self):
        """Update scope from child nodes."""
        # First, determine the scope of each child
        for child in self.children:
            if isinstance(child, AMRNode):
                child.update_scope_from_children()
        # Second, update scope to cover each child
        for child in self.children:
            if isinstance(child, AMRNode):
                for i in range(len(self.scope)):
                    self.scope[i] = self.scope[i] or child.scope[i]
        # print(self)
        # print(self.scope)
        # input()


class AMRGraph:
    """AMR graph class."""

    def __init__(self,
                 nodes=None,
                 id2node=None,
                 root=None,
                 tokens=None):
        self.nodes = nodes or []
        self.id2node = id2node or {}
        self.root = root or None
        self.tokens = tokens or []

    @property
    def relations(self):
        """Relation triple list."""
        triples = []
        for h in self.nodes:
            for r in h.relations:
                for t in h.relations[r]:
                    triples.append((h, r, t))
        return triples

    def get_event_nodes(self):
        """Get event nodes (i.e., verbs)."""
        return [_ for _ in self.nodes if _.type == "verb"]

    def find_node_by_id(self, short):
        """Find node by id."""
        if short in self.id2node:
            return self.id2node[short]
        else:
            return None

    def find_tokens_by_span(self, span):
        """Find tokens by span."""
        if self.tokens is not None:
            start, end = span
            if start is not None and end is not None:
                return self.tokens[start: end]
            else:
                return None
        else:
            return None

    def find_tokens_by_node(self, node):
        """Find tokens by node."""
        return self.find_tokens_by_span(node.span)

    @classmethod
    def parse(cls, text, alignments=None, tokens=None):
        """Parse AMR graph from text."""
        # TODO: forbid auto-transform!
        g = penman.decode(text, model=noop.model)
        # Get tokens
        if tokens is None and "snt" in g.metadata:
            tokens = [_.text for _ in TOKENIZER(g.metadata["snt"])]
        else:
            pass
        if tokens is not None:
            token_num = len(tokens)
        else:
            token_num = None
        # Construct nodes
        nodes = []
        id2node = {}
        for id_, _, value in g.instances():
            node = AMRNode(id_=id_, value=value, token_num=token_num)
            nodes.append(node)
            id2node.setdefault(id_, node)
        # Construct relations
        for h, r, t in g.edges():
            head = id2node[h]
            tail = id2node[t]
            head.add_relation(r, tail)
        # Construct attributes
        for h, r, t in g.attributes():
            head = id2node[h]
            head.add_relation(r, t)
        # Construct graph
        root = id2node[g.top]
        graph = cls(root=root, nodes=nodes, id2node=id2node, tokens=tokens)
        # Compute scope
        if alignments is None:
            alignments = align_graph(text)
        else:
            pass
        for idx, id_ in alignments:
            graph.find_node_by_id(id_).update_scope(idx)
        graph.root.update_scope_from_children()
        return graph


if __name__ == "__main__":
    with open("test_samples/amr.txt", "r") as f:
        s = f.read()
    g = AMRGraph.parse(s)
    for v in g.nodes:
        print(v)
        print(" ".join(g.find_tokens_by_span(v.span)))
    # for h, r, t in g.relations:
    #     print(h, r, t)
    # align = RBWAligner.from_penman_w_json(g)
    # for t in align.alignments:
    #     print(t)
