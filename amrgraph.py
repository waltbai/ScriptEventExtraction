"""Definition of AMR graph class."""
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


class AMRNode(dict):
    """Node in AMR graph."""

    def __init__(self, **kwargs):
        kwargs.setdefault("short", "")
        kwargs.setdefault("value", "")
        kwargs.setdefault("relations", {})
        kwargs.setdefault("scope", None)
        kwargs.setdefault("tokens", None)
        super(AMRNode, self).__init__(**kwargs)

    def __getattr__(self, item):
        if item == "children":
            children = []
            for rel_type in self["relations"]:
                for tail in self["relations"][rel_type]:
                    children.append(tail)
            return children
        else:
            return self[item]

    def __repr__(self):
        if self["scope"] is None:
            return "({},{})".format(self["short"], self["value"])
        else:
            return "({},{},{}-{})".format(self["short"], self["value"], self["scope"][0], self["scope"][1])

    def add_relation(self, rel_type, tail):
        """Add a relation."""
        self["relations"].setdefault(rel_type, []).append(tail)

    def update_scope(self, index):
        """Update node scope with a token index."""
        if self["scope"] is None:
            self["scope"] = (index, index+1)
        else:
            self["scope"] = (min(self["scope"] + (index, )), max(self["scope"] + (index+1, )))

    def update_scope_from_children(self):
        """Update scope from child nodes."""
        for child in self.children:
            if isinstance(child, AMRNode):
                child.update_scope_from_children()
        if self["scope"] is not None:
            start, end = self["scope"]
        else:
            start, end = None, None
        for child in self.children:
            if isinstance(child, AMRNode) and (child["scope"] is not None):
                if start is not None:
                    start = min(start, child["scope"][0])
                else:
                    start = child["scope"][0]
                if end is not None:
                    end = max(end, child["scope"][1])
                else:
                    end = child["scope"][1]
        if start is not None and end is not None:
            self["scope"] = (start, end)


def _parse_node(node_content, nodes, short2node):
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
        node = AMRNode(short=short, value=value)
        short2node.setdefault(short, node)
        nodes.append(node)
        for relation in relations:
            new_node = _parse_node(relation[1], nodes=nodes, short2node=short2node)
            node.add_relation(relation[0], new_node)
        return node


class AMRGraph(dict):
    """AMR graph class."""

    def __init__(self, **kwargs):
        kwargs.setdefault("nodes", [])
        kwargs.setdefault("short2node", {})
        kwargs.setdefault("root", None)
        kwargs.setdefault("tokens", None)
        super(AMRGraph, self).__init__(**kwargs)

    def __getattr__(self, item):
        return self[item]

    @property
    def relations(self):
        """Return all triples."""
        rels = []
        for head in self["nodes"]:
            for rel_type in head["relations"]:
                for tail in head["relations"][rel_type]:
                    rels.append((head, rel_type, tail))
        return rels

    def find_node_by_short(self, short):
        """Find node by short name."""
        if short in self["short2node"]:
            return self["short2node"][short]
        else:
            return None

    @classmethod
    def parse(cls, text, alignments=None):
        """Parse AMR graph from text."""
        # Handle comments
        lines = text.splitlines()
        comments = [_ for _ in lines if _.startswith("#")]
        content = [_ for _ in lines if _ not in comments]
        # Parse comment
        tokens = None
        # Parse content
        content = "\n".join(content)
        result = ROOT.parseString(content, parseAll=True).asList()
        # Build DAG
        nodes = []
        short2node = {}
        root = _parse_node(result[0], nodes=nodes, short2node=short2node)
        # Align nodes
        if alignments is not None:
            for idx, short in alignments:
                node = short2node[short]
                node.update_scope(idx)
            root.update_scope_from_children()
        # Build graph
        g = cls(nodes=nodes, short2node=short2node, root=root, tokens=tokens)
        return g
