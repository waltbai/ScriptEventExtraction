"""Event class."""
from utils.narrative.entity import get_headword_for_mention, Entity


class Role:
    """Role class."""

    def __init__(self, role, value, concept, ent_id, **kwargs):
        self.role = role
        self.value = value
        self.concept = concept
        self.ent_id = ent_id

    def __repr__(self):
        return f"-[{self.role}]->({self.value}, {self.concept}, {self.ent_id})"

    def to_json(self):
        """To json object."""
        return {
            "role": self.role,
            "value": self.value,
            "concept": self.concept,
            "ent_id": self.ent_id,
        }


def find_arg_word(role, entities):
    """Find value for the role."""
    if role.ent_id is not None:
        assert role.ent_id < len(entities), f"\n{role}\n {entities}"
        value = entities[role.ent_id].head
    else:
        value = get_headword_for_mention(role.value)
    return value


def find_arg(roles, relation, entities):
    """Find a kind of role."""
    value = "None"
    for r in roles:
        if r.role == relation:
            value = find_arg_word(r, entities)
    return value


class Event:
    """Event class."""

    def __init__(self, pb_frame, verb_pos, sent_id, roles):
        self.pb_frame = pb_frame    # propbank frame
        self.verb_pos = verb_pos
        self.sent_id = sent_id
        self.roles = [Role(**r) for r in roles]

    def __repr__(self):
        s = f"{self.pb_frame}:\n"
        for r in self.roles:
            s = s + f"\t{r}\n"
        return s

    @property
    def position(self):
        """Tuple position representation."""
        return self.sent_id, self.verb_pos

    def to_json(self):
        """To json object."""
        return {
            "pb_frame": self.pb_frame,
            "verb_pos": self.verb_pos,
            "sent_id": self.sent_id,
            "roles": [r.to_json() for r in self.roles]
        }

    def contains(self, entity: Entity):
        """If one of the event argument is the entity."""
        for r in self.roles:
            if r.ent_id == entity.ent_id:
                return True
        return False

    def find_role(self, entity: Entity):
        """Find role for an entity."""
        for r in self.roles:
            if r.ent_id == entity.ent_id:
                return r.role
        return None

    def quintuple(self, protagonist: Entity, entities):
        """Return (v, a0, a1, a2, role) quintuple."""
        verb = self.pb_frame
        role = self.find_role(protagonist)
        # protagonist_id = protagonist.ent_id
        # protagonist = protagonist.head
        arg0 = find_arg(self.roles, ":ARG0", entities)
        arg1 = find_arg(self.roles, ":ARG1", entities)
        arg2 = find_arg(self.roles, ":ARG2", entities)
        return verb, arg0, arg1, arg2, role

    def rich_repr(self, protagonist: Entity, entities):
        """Return rich event representation, as role-value list."""
        verb = self.pb_frame
        role = self.find_role(protagonist)
        roles = [r.role for r in self.roles]
        values = [find_arg_word(r, entities) for r in self.roles]
        return verb, role, roles, values

    def entities(self):
        """Return ids of all entities participate in this event."""
        ents = set()
        for r in self.roles:
            if r.ent_id is not None:
                ents.add(r.ent_id)
        return sorted(list(ents))

    def words(self, entities):
        """Return all words in event."""
        result = [self.pb_frame]
        for r in self.roles:
            if r.ent_id is None:
                result.append(r.value[-1])
            else:
                result.append(entities[r.ent_id].head)
        result = [w for w in result if w != "None"]
        return result
