"""The pure-Python break iterators must reproduce ICU's boundaries exactly.

Fixtures are produced by tools/fixtures/gen_icu_fixtures.py with ICU 78.3.
"""

import json
from pathlib import Path

import pytest

from polyglot3.tokenize.breakiter import sentence_boundaries, word_boundaries

SEGMENTATION_DIR = Path(__file__).parent / "fixtures" / "segmentation"


def load_records():
  for path in sorted(SEGMENTATION_DIR.glob("*.jsonl")):
    with open(path, encoding="utf-8") as fh:
      for i, line in enumerate(fh):
        yield pytest.param(json.loads(line), id="{}-{}".format(path.stem, i))


@pytest.mark.parametrize("record", list(load_records()))
def test_word_boundaries(record):
  if not record["text"]:
    return
  assert word_boundaries(record["text"]) == record["words"]


@pytest.mark.parametrize("record", list(load_records()))
def test_sentence_boundaries(record):
  if not record["text"]:
    return
  assert sentence_boundaries(record["text"]) == record["sentences"]
