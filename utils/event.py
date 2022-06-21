
class Role:
    """Role class."""
    def __init__(self,
                 role,
                 value,
                 concept,
                 span=None,
                 head_pos=None,
                 ent_id=None):
        """Initialize a role.

        :param role: role type
        :param value: token span of this role
        :param concept: corresponding concept in amr graph
        :param span: span range of this role
        :param head_pos: head word position
        :param ent_id: entity id if it is a co-referent entity
        """
        self.role = role
        self.value = value
        self.concept = concept
        self.span = span
        self.head_pos = head_pos
        self.ent_id = ent_id

    def __repr__(self):
        _repr = f"-[{self.role}]->({self.concept}, {self.value}, {self.ent_id})"
        return _repr

    def to_json(self):
        """Convert to json object."""
        return {
            "role": self.role,
            "value": self.value,
            "concept": self.concept,
            "ent_id": self.ent_id,
        }


class Event:
    """Event class."""
    def __init__(self,
                 pb_frame,
                 verb_pos=None,
                 sent_id=None,
                 roles=None):
        """Initialize an event.

        :param pb_frame: ProbBank Frame
        :param verb_pos: verb position in sentence
        :param sent_id: sentence index
        :param roles: roles of this event
        """
        self.pb_frame = pb_frame
        self.verb_pos = verb_pos
        self.sent_id = sent_id
        self.roles = roles or []

    def __repr__(self):
        _repr = f"{self.pb_frame} ({self.sent_id}, {self.verb_pos})\n"
        for role in self.roles:
            _repr += f"\t{role}\n"
        return _repr

    def add_role(self, role, concept, value,
                 span=None, head_pos=None, ent_id=None):
        """Add a role."""
        if value is None:
            value = concept
        self.roles.append(
            Role(role=role,
                 value=value,
                 concept=concept,
                 span=span,
                 head_pos=head_pos,
                 ent_id=ent_id))

    def to_json(self):
        """Convert to json object."""
        return {
            "pb_frame": self.pb_frame,
            "verb_pos": self.verb_pos,
            "sent_id": self.sent_id,
            "roles": [r.to_json() for r in self.roles]
        }

