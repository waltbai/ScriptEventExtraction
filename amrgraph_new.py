"""Definition of AMR graph class."""
import re

from pyparsing import Literal, Word, printables, Combine, Group, Forward, Suppress, ZeroOrMore

"""Parser for AMR.

BNF:

LB := "("
RB := ")"
SLASH := "/"
SPACE := " "
TERMINATE := SPACE | LB | RB | SLASH
ROLE := ":" NO_TERMINATE
INSTANCE := NO_TERMINATE SLASH NO_TERMINATE
CONCEPT := LB INSTANCE RELATION* RB
RELATION := ROLE TAIL
TAIL := NO_TERMINATE | CONCEPT
"""

LB, RB, SLASH = map(Literal, "()/")
NO_TERMINTATE = Word(printables, excludeChars=" ()/")
ROLE = Combine(":" + NO_TERMINTATE)
INSTANCE = Group(NO_TERMINTATE + SLASH + NO_TERMINTATE)
TAIL = Forward()
CONCEPT = Forward()
RELATION = Group(ROLE + TAIL)
TAIL <<= NO_TERMINTATE | CONCEPT
CONCEPT <<= Group(Suppress(LB) + INSTANCE + Group(ZeroOrMore(RELATION)) + Suppress(RB))
ROOT = CONCEPT


VERB_FRAME_PATTERN = re.compile(r".+-\d+")
STATIC_FRAMES = ["have-rel-role-91", "have-org-role-91"]
CONJUNCTION_FRAMES = ["and"]


class AMRNode:
    """Node in AMR graph."""

    def __init__(self,
                 short="",
                 value="",
                 relations=None,
                 token_num=None):
        # Accessible
        self.short = short
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
            return f"({self.short},{self.value})"
        else:
            return f"({self.short},{self.value},{start}-{end})"

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
        # Continuity is a really strong constraint.
        # Try discrete tolerant = 1
        start, end = None, None
        # TODO
        for i in range(len(self.scope))[::-1]:
            if end is None and self.scope[i]:
                end = i + 1
            if end is not None and self.scope[i]:
                start = i
            if start is not None and end is not None and not self.scope[i]:
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


# TODO: parse amr graph with penman
def _parse_node(node_content, nodes, short2node, token_num=None):
    """Parse node content."""
    if isinstance(node_content, str):
        # Value or short name
        if node_content in short2node:
            return short2node[node_content]
        else:
            if node_content.startswith("\"") and node_content.endswith("\""):
                node_content = node_content[1:-1]
            return node_content
    else:
        short, _, value = node_content[0]
        relations = node_content[1]
        node = AMRNode(short=short, value=value, token_num=token_num)
        short2node.setdefault(short, node)
        nodes.append(node)
        for relation in relations:
            new_node = _parse_node(relation[1],
                                   nodes=nodes,
                                   short2node=short2node,
                                   token_num=token_num)
            node.add_relation(relation[0], new_node)
        return node


class AMRGraph:
    """AMR graph class."""

    def __init__(self,
                 nodes=None,
                 short2node=None,
                 root=None,
                 tokens=None):
        self.nodes = nodes or []
        self.short2node = short2node or {}
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

    def find_node_by_short(self, short):
        """Find node by short name."""
        if short in self.short2node:
            return self.short2node[short]
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
        # Handle comments
        lines = text.splitlines()
        comments = [_ for _ in lines if _.startswith("#")]
        content = [_ for _ in lines if _ not in comments]
        # Get tokens
        if tokens is not None:
            token_num = len(tokens)
        else:
            sent = [_ for _ in comments if _.startswith("# ::snt")]
            if len(sent) > 0:
                tokens = sent[0].replace("# ::snt", "").strip().split()
                token_num = len(tokens)
            else:
                token_num = None
        # Parse graph text
        content = "\n".join(content)
        parse_result = ROOT.parseString(content, parseAll=True).asList()
        # Build graph
        nodes = []
        short2node = {}
        root = _parse_node(parse_result[0],
                           nodes=nodes,
                           short2node=short2node,
                           token_num=token_num)
        # Update alignment information
        if alignments is not None and tokens is not None:
            for idx, short in alignments:
                node = short2node[short]
                node.update_scope(idx)
            root.update_scope_from_children()
        return cls(nodes=nodes, short2node=short2node, root=root, tokens=tokens)


if __name__ == "__main__":
    with open("test_samples/amr.txt", "r") as f:
        s = f.read()
    g = AMRGraph.parse(s)

