"""Entity sentiment uses every polar word in the text. Needs the Turkish models."""

import os

import pytest

from polyglot3 import polyglot_path
from polyglot3.text import Text

pytestmark = pytest.mark.skipif(
    not all(os.path.isdir(os.path.join(polyglot_path, task, "tr"))
            for task in ("ner2", "embeddings2", "sentiment2")),
    reason="Turkish models not available")


def test_entity_sentiment_counts_all_polar_words():
  # güzel (+1) precedes both entities; berbat (-1) follows İstanbul.
  text = Text(u"Ankara güzel bir şehir ama İstanbul berbat bir trafiğe sahip.",
              hint_language_code="tr")
  ankara, istanbul = text.entities
  assert ankara.positive_sentiment > 0
  assert istanbul.negative_sentiment > ankara.negative_sentiment > 0


def test_entity_sentiment_without_polar_words():
  text = Text(u"Ankara bir şehir.", hint_language_code="tr")
  (ankara,) = text.entities
  assert (ankara.positive_sentiment, ankara.negative_sentiment) == (0, 0)
