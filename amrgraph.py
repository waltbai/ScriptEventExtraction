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
        return self[item]

    def add_relation(self, rel_type, tail):
        """Add a relation."""
        self["relation"].setdefault(rel_type, []).append(tail)


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
            pass
        # Build graph
        g = cls(nodes=nodes, short2node=short2node, root=root, tokens=tokens)
        return g
