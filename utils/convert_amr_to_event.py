"""Convert amr graph to event structure."""
import re


# Reserved relation patterns
from utils.event import Event

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


CORE_ROLE = re.compile(r":ARG\d+")


def recognize_modalities(graph):
    """Remove modality verbs."""
    for h, r, t in graph.relations:
        if not isinstance(t, str) and \
                h.type == "verb" and t.type == "verb" and \
                CORE_ROLE.match(r):
            h.type = "modality"


# Main
def convert_amr_to_events(graph):
    """Convert amr graph to event structure."""
    # Convert graph
    filter_relations(graph)
    split_and_node(graph)
    recognize_modalities(graph)
    add_reverse_of_argn_of(graph)
    # # Export events
    events = []
    for e in graph.get_event_nodes():
        pb_frame = e.value
        verb_pos = e.pos
        event = Event(
            pb_frame=pb_frame,
            verb_pos=verb_pos)
        for r in e.relations:
            for t in e.relations[r]:
                if isinstance(t, str):
                    continue
                role = r
                concept = t.value
                span = t.span
                head_pos = span[1] if span is not None else None
                value = graph.find_tokens_by_span(span)
                event.add_role(
                    role=role,
                    concept=concept,
                    value=value,
                    span=span,
                    head_pos=head_pos
                )
        events.append(event)
    return events
