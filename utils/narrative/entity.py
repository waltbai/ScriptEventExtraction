"""Entity class."""

import os


# Pronouns
from collections import Counter

PRONOUNS = [
    "i", "you", "he", "she", "it", "we", "they",
    "me", "him", "her", "us", "them",
    "myself", "yourself", "himself", "herself", "itself", "ourself", "ourselves", "themselves",
    "my", "your", "his", "its", "it's", "our", "their",
    "mine", "yours", "ours", "theirs",
    "this", "that", "those", "these",
    "-", ",",
]
# Load stop word list
with open(os.path.join("data", "english_stopwords.txt"), "r") as f:
    STOPWORDS = f.read().splitlines()


def filter_words_in_mention(words):
    """Filter stop words and pronouns in mention."""
    return [w for w in words if w not in PRONOUNS and w not in STOPWORDS]


def get_headword_for_mention(mention):
    """Get headword for mention."""
    mention = [w.lower() for w in mention]
    # Filter stop words
    words = filter_words_in_mention(mention)
    # Filter 1-letter word
    words = [w for w in words if len(w) > 1]
    # Use the rightmost word as the mention head.
    if len(words) > 0:
        return words[-1]
    else:
        return "None"


class Entity:
    """Entity class."""

    def __init__(self, mentions, ent_id, head=None, salient_mention=None, concept=None):
        self.mentions = mentions
        self.ent_id = ent_id
        self.head = head or self.get_head()
        self.salient_mention = salient_mention or self.get_salient_mention()
        self.concept = concept

    def to_json(self):
        return {
            "mentions": self.mentions,
            "ent_id": self.ent_id,
            "head": self.head,
            "salient_mention": self.salient_mention,
            "concept": self.concept,
        }

    def __repr__(self):
        return f"[{self.ent_id}, {self.head}, {self.salient_mention}, {self.concept}]"

    def get_head(self):
        """Get mention head.

        Similar with G&C16.
        """
        entity_head_words = Counter()
        for mention in self.mentions:
            headword = get_headword_for_mention(mention)
            if headword != "None":
                entity_head_words.update([headword])
        if len(entity_head_words):
            return entity_head_words.most_common()[0][0]
        else:
            return "None"

    def get_salient_mention(self):
        """Get salient mention."""
        salient_mention = []
        for mention in self.mentions:
            # Filter stopwords and pronouns.
            mention = [w.lower() for w in mention]
            words = filter_words_in_mention(mention)
            words = [w for w in words if len(w) > 1]
            # Use the longest mention as the salient mention
            if len(words) > len(salient_mention):
                salient_mention = words
        return salient_mention
