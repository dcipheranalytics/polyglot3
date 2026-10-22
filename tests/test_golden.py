"""Regression test: current outputs must match the golden outputs of the original polyglot.

Fixtures are produced by tools/fixtures/gen_golden.py. Language detection is
recorded there for reference only and is not compared here.
Needs the models under $POLYGLOT_DATA_PATH/polyglot_data; skipped otherwise.
"""

import json
import os
from pathlib import Path

import pytest

from polyglot3 import polyglot_path
from polyglot3.text import Text

GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden"


def load_records():
    for path in sorted(GOLDEN_DIR.glob("*.jsonl")):
        with open(path, encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                yield pytest.param(json.loads(line), id="{}-{}".format(path.stem, i))


pytestmark = pytest.mark.skipif(
    not os.path.isdir(polyglot_path), reason="polyglot models not available"
)


@pytest.mark.parametrize("record", list(load_records()))
def test_matches_golden(record):
    if "error" in record:
        with pytest.raises(Exception) as excinfo:
            Text(record["text"], hint_language_code=record["lang"]).words
        assert type(excinfo.value).__name__ == record["error"]
        return

    t = Text(record["text"], hint_language_code=record["lang"])
    assert list(t.words) == record["words"]
    assert [[s.start, s.end, s.raw] for s in t.sentences] == record["sentences"]
    if "entities" in record:
        assert [[e.tag, e.start, e.end, list(e)] for e in t.entities] == record[
            "entities"
        ]
    if "pos_tags" in record:
        assert [[w, tag] for w, tag in t.pos_tags] == record["pos_tags"]
    if "polarity" in record:
        assert t.polarity == pytest.approx(record["polarity"])
