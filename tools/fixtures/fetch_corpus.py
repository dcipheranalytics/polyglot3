#!/usr/bin/env python
"""Fetch a small Wikipedia prose corpus for the segmentation/golden fixtures.

For each English seed article, follow the interlanguage link to every target
language and keep the first paragraphs of the plain-text extract.

Usage: python tools/fixtures/fetch_corpus.py tests/fixtures/corpus
"""

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

LANGUAGES = [
    "ar", "bg", "cs", "et", "fa", "ga", "he", "hi", "hr", "hu", "id",
    "lv", "ms", "no", "sk", "sl", "sr", "th", "tr", "uk", "vi",
]
SEEDS = ["Albert Einstein", "European Union", "Water", "Association football"]
# Thai is the only priority language that needs dictionary-based word breaking,
# so it gets extra text.
EXTRA_SEEDS = {"th": ["Bangkok", "Buddhism", "Thai cuisine", "Moon"]}
PARAGRAPHS_PER_ARTICLE = 6
MIN_PARAGRAPH_CHARS = 80

USER_AGENT = "polyglot3-fixtures/0.1 (https://github.com/aboSamoor/polyglot)"


def api(lang, **params):
  params.update(action="query", format="json", formatversion="2")
  url = "https://{}.wikipedia.org/w/api.php?{}".format(
      lang, urllib.parse.urlencode(params))
  req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
  with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.load(resp)
  time.sleep(0.2)
  return data["query"]["pages"][0]


def localized_title(seed, lang):
  page = api("en", titles=seed, prop="langlinks", lllang=lang, redirects=1)
  links = page.get("langlinks", [])
  return links[0]["title"] if links else None


def paragraphs(title, lang):
  page = api(lang, titles=title, prop="extracts", explaintext=1, redirects=1)
  text = page.get("extract", "")
  paras = [p.strip() for p in text.split("\n")]
  # Section headings come through as short "== Heading ==" lines.
  paras = [p for p in paras if len(p) >= MIN_PARAGRAPH_CHARS and not p.startswith("=")]
  return paras[:PARAGRAPHS_PER_ARTICLE]


def main(out_dir):
  out_dir = Path(out_dir)
  out_dir.mkdir(parents=True, exist_ok=True)
  for lang in LANGUAGES:
    records = []
    for seed in SEEDS + EXTRA_SEEDS.get(lang, []):
      title = localized_title(seed, lang)
      if title is None:
        print("{}: no article for {!r}".format(lang, seed), file=sys.stderr)
        continue
      for para in paragraphs(title, lang):
        records.append({"source": "{}.wikipedia.org/wiki/{}".format(lang, title),
                        "text": para})
    with open(out_dir / "{}.jsonl".format(lang), "w", encoding="utf-8") as fh:
      for rec in records:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("{}: {} paragraphs".format(lang, len(records)))


if __name__ == "__main__":
  main(sys.argv[1])
