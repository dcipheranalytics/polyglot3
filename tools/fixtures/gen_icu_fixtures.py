#!/usr/bin/env python
"""Record ICU word/sentence boundaries for every corpus paragraph.

This is the only place PyICU is used, and it is not a project dependency:
run it from a throwaway environment that has PyICU installed.

Boundaries are stored as Python code-point offsets (ICU reports UTF-16
offsets) and include whitespace segments, i.e. exactly what
BreakIterator returns for the root locale, which is what polyglot always used.

Usage: python tools/fixtures/gen_icu_fixtures.py tests/fixtures/corpus tests/fixtures/segmentation
"""

import json
import sys
from pathlib import Path

import icu


def utf16_to_codepoint(text):
  """Map each UTF-16 offset of `text` to its code-point offset."""
  mapping = {}
  u16 = 0
  for cp, ch in enumerate(text):
    mapping[u16] = cp
    u16 += 2 if ord(ch) > 0xFFFF else 1
  mapping[u16] = len(text)
  return mapping


def boundaries(breaker, text):
  breaker.setText(text)
  to_cp = utf16_to_codepoint(text)
  return [to_cp[0]] + [to_cp[b] for b in breaker]


def main(corpus_dir, out_dir):
  out_dir = Path(out_dir)
  out_dir.mkdir(parents=True, exist_ok=True)
  locale = icu.Locale.getRoot()
  words = icu.BreakIterator.createWordInstance(locale)
  sentences = icu.BreakIterator.createSentenceInstance(locale)
  for corpus in sorted(Path(corpus_dir).glob("*.jsonl")):
    with open(corpus, encoding="utf-8") as fh:
      records = [json.loads(line) for line in fh]
    with open(out_dir / corpus.name, "w", encoding="utf-8") as fh:
      for rec in records:
        text = rec["text"]
        fh.write(json.dumps({
            "lang": rec.get("lang", corpus.stem),
            "text": text,
            "words": boundaries(words, text),
            "sentences": boundaries(sentences, text),
        }, ensure_ascii=False) + "\n")
    print("{}: {} records".format(corpus.name, len(records)))
  with open(out_dir / "META.json", "w") as fh:
    json.dump({"icu_version": icu.ICU_VERSION,
               "unicode_version": icu.UNICODE_VERSION,
               "locale": "root"}, fh, indent=2)


if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])
