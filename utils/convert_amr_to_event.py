"""Convert amr graph to event structure."""
import re


# Reserved relation patterns
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
        if not isinstance(t, str) and t.value == "and":
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


def recognize_modalities(graph):
    """Remove modality verbs."""
    for h, r, t in graph.relations:
        if h.type == "verb" and t.type == "verb":
            h.type = "modality"


# Main
def convert_amr_to_event(graph):
    """Convert amr graph to event structure."""
    # Convert graph
    filter_relations(graph)
    split_and_node(graph)
    recognize_modalities(graph)
    add_reverse_of_argn_of(graph)
    # # Export events
    events = []
    for e in graph.get_event_nodes():
        event = {
            "pb-frame": e.value,
            "fn-frame": "",
            "roles": {}
        }
        for r in e.relations:
            for t in e.relations[r]:
                start, end = t.span
                head_idx = end

