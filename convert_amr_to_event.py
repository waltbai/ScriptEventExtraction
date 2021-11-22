"""Convert amr graph to event structure."""
import re

from amrgraph import AMRGraph


# Rules
def reduce_name(graph):
    """Reduce name nodes."""
    for v in graph.nodes:
        if v.value == "name":
            v.relations = {}
    return graph


def convert_argn_of(graph):
    """Convert ARGN-of to ARGN.

    Caution!!! After this step, there may exists cycle in amr graph.
    """
    p = re.compile(r":ARG\d+-of")
    for h, r, t in graph.relations():
        if p.match(r):
            new_r = r.replace("-of", "")
            t.add_relation(new_r, h)
            h.remove_relation(r, t)


# Main
def convert_amr_to_event(graph: AMRGraph):
    """Convert amr graph to event structure."""
    # Convert graph
    graph = reduce_name(graph)
    convert_argn_of(graph)
    # # Export events
    # for e in graph.get_event_nodes():
    #     pass
    for h, r, t in graph.relations():
        print(h, r, t)


if __name__ == "__main__":
    with open("test_samples/amr.txt", "r") as f:
        s = f.read()
    g = AMRGraph.parse(s)
    convert_amr_to_event(g)
