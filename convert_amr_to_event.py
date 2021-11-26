"""Convert amr graph to event structure."""
import re

from amrgraph_new import AMRGraph, AMRNode

# Reserved relation patterns
from step_3 import align_graph
from step_5 import convert_align_info

RESERVED_RELATIONS = {
    ":ARG0", ":ARG1", ":ARG2", ":ARG3", ":ARG4",    # core roles
    # ":name",    # filter name
    ":op1", ":op2", ":op3", ":op4",     # operators
    ":location", ":destination", ":path",   # spatial
    ":instrument", ":manner", ":topic", ":medium",  # means
    ":mod", ":poss",    # modifiers
    # ":year", ":time", ":duration", ":decade", ":weekday",     # filter temporal
    # ":prep-",     # filter preposition
}


# Rules
def filter_relations(graph):
    """Filter relations."""
    for v in graph.nodes:
        remove_keys = []
        for key in v.relations:
            if key not in RESERVED_RELATIONS:
                remove_keys.append(key)
        for key in remove_keys:
            v.relations.pop(key)


def split_and_node(graph):
    """Split and node into different relations."""
    for h, r, t in graph.relations:
        if isinstance(t, AMRNode) and t.value == "and":
            for new_t in t.children:
                h.add_relation(r, new_t)
            h.remove_relation(r, t)


def add_reverse_of_argn_of(graph):
    """Add reverse of ARGN-of.

    Caution!!! After this step, there exist cycles in amr graph.
    """
    p = re.compile(r":ARG\d+-of")
    for h, r, t in graph.relations:
        if p.match(r):
            new_r = r.replace("-of", "")
            t.add_relation(new_r, h)
            # h.remove_relation(r, t)


# Main
def convert_amr_to_event(graph: AMRGraph):
    """Convert amr graph to event structure."""
    # Convert graph
    split_and_node(graph)
    add_reverse_of_argn_of(graph)
    filter_relations(graph)
    # # Export events
    for e in graph.get_event_nodes():
        for r in e.relations:
            for t in e.relations[r]:
                start, end = t.scope

                print(e, r, t, " || ", " ".join(tokens[start:end]))


if __name__ == "__main__":
    with open("test_samples/amr.txt", "r") as f:
        s = f.read()
    tokens_s = "With the nation 's attention riveted again on a Los Angeles courtroom , " \
               "a knife dealer testified that O.J. Simpson bought a 15 - inch knife " \
               "five weeks before the slashing deaths of his ex - wife and her friend ."
    tokens = tokens_s.split()
    align_s = align_graph(s)
    align = convert_align_info(align_s)
    g = AMRGraph.parse(s, alignments=align, tokens=tokens)
    for v in g.nodes:
        print(v)
        # print(g.find_tokens_by_node(v))
        print(v.scope)
        input()
    # convert_amr_to_event(g)
