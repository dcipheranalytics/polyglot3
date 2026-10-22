#!/usr/bin/env python
"""Record the outputs of the original polyglot (ICU + pycld2) as golden fixtures.

Must run against the pre-refactor code (commit 9b93b2e) in a throwaway
environment with PyICU, pycld2, six, morfessor and numpy<2 installed, and
POLYGLOT_DATA_PATH pointing at a directory containing polyglot_data/.

The original Breaker used ICU's UTF-16 offsets as Python string indices,
which garbles every token after an astral character (e.g. emoji). That bug is
patched here so the fixtures capture the intended behaviour.

Usage: python tools/fixtures/gen_golden.py tests/fixtures/corpus tests/fixtures/golden
"""

import json
import os
import sys
from pathlib import Path

from polyglot import polyglot_path
from polyglot.base import Sequence
from polyglot.text import Text
from polyglot.tokenize import base as tokenize_base

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_icu_fixtures import utf16_to_codepoint  # noqa: E402


def _transform(self, sequence):
  seq = Sequence(sequence.text)
  seq.idx = [0]
  for segment in sequence:
    offset = seq.idx[-1]
    self.breaker.setText(segment)
    to_cp = utf16_to_codepoint(segment)
    seq.idx.extend([offset + to_cp[x] for x in self.breaker])
  return seq


tokenize_base.Breaker.transform = _transform


def available(task, lang):
  return os.path.isdir(os.path.join(polyglot_path, task, lang))


def detection(text):
  try:
    t = Text(text)
    lang = t.language
    return {"code": lang.code, "confidence": lang.confidence,
            "reliable": t.detected_languages.reliable,
            "languages": [[l.code, l.confidence] for l in t.detected_languages.languages]}
  except Exception as e:
    return {"error": type(e).__name__}


def golden(text, lang):
  t = Text(text, hint_language_code=lang)
  out = {
      "lang": lang,
      "text": text,
      "detection": detection(text),
      "words": list(t.words),
      "sentences": [[s.start, s.end, s.raw] for s in t.sentences],
  }
  if available("ner2", lang):
    out["entities"] = [[e.tag, e.start, e.end, list(e)] for e in t.entities]
  if available("pos2", lang):
    out["pos_tags"] = [[w, tag] for w, tag in t.pos_tags]
  if available("sentiment2", lang):
    out["polarity"] = t.polarity
  return out


def main(corpus_dir, out_dir):
  out_dir = Path(out_dir)
  out_dir.mkdir(parents=True, exist_ok=True)
  for corpus in sorted(Path(corpus_dir).glob("*.jsonl")):
    with open(corpus, encoding="utf-8") as fh:
      records = [json.loads(line) for line in fh]
    with open(out_dir / corpus.name, "w", encoding="utf-8") as fh:
      for rec in records:
        lang = rec.get("lang", corpus.stem)
        try:
          result = golden(rec["text"], lang)
        except Exception as e:
          result = {"lang": lang, "text": rec["text"], "error": type(e).__name__}
        fh.write(json.dumps(result, ensure_ascii=False) + "\n")
    print("{}: {} records".format(corpus.name, len(records)))


if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])
