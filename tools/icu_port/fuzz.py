#!/usr/bin/env python
"""Differential fuzzing of polyglot3.tokenize.breakiter against PyICU.

Dev-only: run from a throwaway environment with PyICU (ICU 78.x) installed.

Usage: python tools/icu_port/fuzz.py [iterations] [seed]
"""

import random
import sys

import icu

from polyglot3.tokenize import breakiter
from polyglot3.tokenize.breakiter import sentence_boundaries, word_boundaries

# Characters exercising the break rules: letters, digits, MidLetter/MidNum
# punctuation, quotes, Hebrew, Katakana/Hiragana/Han/Hangul, Thai (dictionary),
# emoji and ZWJ, regional indicators, Extend/Format, spaces and newlines,
# sentence terminators, closing punctuation and SContinue.
POOL = (
    u"aZéß09٣.,:;'\"’-_!?…()[]«»“”’‘ \t\u00a0\u3000\r\n\u2028\u0085"
    u"אבגד׳״" u"カタナひら漢字한국" u"กขคงจ\u0e31า\u0e34\u0e35\u0e36\u0e37\u0e38\u0e39เแโใไๆฯ\u0e48\u0e49\u0e4a\u0e4b\u0e4c" u"ກາ"
    u"\u0301\u0308\u200b\u200c\u200d\u00ad\u2060\ufeff"
    u"😀👍\U0001f3fd👨🇹🇷\U0001F3FB❤\ufe0f" u"Ⅷ½"
)


def uses_unported_dictionary(text):
  """ICU segments non-Thai dictionary characters (CJK, Lao, Khmer, Burmese...)
  with dictionaries we do not ship."""
  rules = breakiter._word_iterator.rules
  thai = breakiter._get_thai_engine().word_set
  return any(rules.dict[rules.category(c)] and c not in thai for c in text)


def icu_boundaries(kind, text):
  it = getattr(icu.BreakIterator, "create{}Instance".format(kind))(icu.Locale.getRoot())
  it.setText(text)
  to_cp, u16 = {}, 0
  for cp, ch in enumerate(text):
    to_cp[u16] = cp
    u16 += 2 if ord(ch) > 0xFFFF else 1
  to_cp[u16] = len(text)
  return [0] + [to_cp[b] for b in it]


def random_text(rng):
  if rng.random() < 0.1:
    # Arbitrary code points (excluding surrogates).
    cps = [rng.choice((rng.randrange(0x20, 0x3000), rng.randrange(0x10000, 0x20000)))
           for _ in range(rng.randrange(1, 12))]
    return u"".join(chr(c) for c in cps if not 0xD800 <= c <= 0xDFFF) or u"x"
  if rng.random() < 0.2:
    # Long Thai runs drive the dictionary engine.
    thai = [chr(c) for c in range(0x0E01, 0x0E5C) if chr(c).isprintable()]
    return u"".join(rng.choice(thai) for _ in range(rng.randrange(5, 30)))
  return u"".join(rng.choice(POOL) for _ in range(rng.randrange(1, 16)))


def main(iterations=200000, seed=0):
  rng = random.Random(seed)
  failures = expected_diffs = 0
  for n in range(iterations):
    text = random_text(rng)
    for kind, ours in (("Word", word_boundaries), ("Sentence", sentence_boundaries)):
      expected = icu_boundaries(kind, text)
      got = ours(text)
      if got != expected and kind == "Word" and uses_unported_dictionary(text):
        expected_diffs += 1
      elif got != expected:
        failures += 1
        if failures <= 20:
          print("{} mismatch for {!r}\n  icu:  {}\n  ours: {}".format(kind, text, expected, got))
  print("{} texts, {} mismatches, {} expected differences in CJK/Lao/Khmer/Burmese "
        "text".format(iterations, failures, expected_diffs))
  return failures


if __name__ == "__main__":
  args = [int(a) for a in sys.argv[1:]]
  sys.exit(1 if main(*args) else 0)
