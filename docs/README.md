# polyglot3

[![PyPI](https://img.shields.io/pypi/v/polyglot3.svg)](https://pypi.org/project/polyglot3/)
[![Tests](https://github.com/dcipheranalytics/polyglot3/actions/workflows/tests.yml/badge.svg)](https://github.com/dcipheranalytics/polyglot3/actions/workflows/tests.yml)
[![Python](https://img.shields.io/pypi/pyversions/polyglot3.svg)](https://pypi.org/project/polyglot3/)

polyglot3 is a maintained, Python 3 only continuation of
[polyglot](https://github.com/aboSamoor/polyglot), a natural language
pipeline for massively multilingual applications. It keeps polyglot's API
and models under the package name `polyglot3`, and removes the native
dependencies that made polyglot hard to install. It is maintained by
Dcipher Analytics AB.

- Free software: GPLv3 license
- Source: https://github.com/dcipheranalytics/polyglot3
- Install: `pip install polyglot3` (Python 3.9+, no system libraries)

## Features

- Tokenization: word and sentence segmentation for all languages
- Language detection: 176 languages
- Named entity recognition: 25 languages
- Part of speech tagging: 7 languages
- Sentiment analysis: 136 languages
- Word embeddings: 25 languages

See [Supported languages](#supported-languages) for the exact lists.

## What changed from polyglot

- **New name.** Import `polyglot3` instead of `polyglot`
  (`from polyglot3.text import Text`) and run the `polyglot3` command. The
  API is otherwise the same, models and `~/polyglot_data` are shared, and
  polyglot3 can be installed next to the original package.
- **No PyICU.** Word and sentence segmentation use a pure-Python port of
  ICU's break iterators, generated from ICU 78.3's own rules, including the
  Thai dictionary engine. Outside Chinese, Japanese, Korean, Lao, Khmer and
  Burmese (which ICU segments with dictionaries that are not bundled), the
  boundaries match ICU's exactly, so the existing NER and POS models see the
  tokens they were trained on.
- **No pycld2.** Language detection uses fastText's `lid.176` model via
  [fasttext-langdetect](https://pypi.org/project/fasttext-langdetect/).
- **Python 3.9 to 3.13 only**; Python 2 support and `six` are gone.
- **New model host.** Models are downloaded from a Hugging Face dataset and
  verified against checksums. The original Stony Brook server is offline.
- **Removed**: morphological analysis and transliteration (their models are
  no longer available), and the TextBlob/NLTK leftovers that never worked.
- **Fixed**: tokens after emoji and other non-BMP characters were garbled;
  the `sentiment` subcommand did nothing; several downloader bugs.

## Quick tutorial

Download the models for the languages you need (once):

```bash
polyglot3 download LANG:tr LANG:cs
```

```python
from polyglot3.text import Text, Word
```

### Language detection

```python
text = Text("Bugün hava çok güzel, parka gidelim.")
print(text.language.code, text.language.name)
```

```text
tr Turkish
```

### Tokenization

```python
zen = Text("Beautiful is better than ugly. "
           "Explicit is better than implicit. "
           "Simple is better than complex.")
print(zen.words)
print(zen.sentences)
```

```text
['Beautiful', 'is', 'better', 'than', 'ugly', '.', 'Explicit', 'is', 'better', 'than', 'implicit', '.', 'Simple', 'is', 'better', 'than', 'complex', '.']
[Sentence("Beautiful is better than ugly."), Sentence("Explicit is better than implicit."), Sentence("Simple is better than complex.")]
```

### Part of speech tagging

```python
text = Text("Petr Novák pracuje v Praze pro společnost Škoda.")
for word, tag in text.pos_tags:
    print("{:<16}{}".format(word, tag))
```

```text
Petr            PROPN
Novák           PROPN
pracuje         ADJ
v               ADP
Praze           NOUN
pro             ADP
společnost      NOUN
Škoda           PROPN
.               PUNCT
```

### Named entity recognition

```python
text = Text("Mustafa Kemal Atatürk, 1923 yılında Ankara'da "
            "Türkiye Cumhuriyeti'ni ilan etti.")
print(text.entities)
```

```text
[I-PER(['Mustafa', 'Kemal', 'Atatürk']), I-LOC(['Türkiye'])]
```

### Polarity

```python
text = Text("Bu film harika ama son kısmı berbat.")
for w in text.words:
    print("{:<16}{:>2}".format(w, w.polarity))
```

```text
Bu               0
film             0
harika           1
ama             -1
son              0
kısmı            0
berbat          -1
.                0
```

### Embeddings

```python
from polyglot3.load import load_embeddings

embeddings = load_embeddings("tr")
print(embeddings.nearest_neighbors("Ankara"))
```

```text
['İstanbul', 'İzmir', 'Bursa', 'Antalya', 'Adana', 'Trabzon', 'Balıkesir', 'Konya', ...]
```

## Supported languages

| Task                     | Languages (ISO 639 codes)                                                                 |
|--------------------------|-------------------------------------------------------------------------------------------|
| Named entity recognition | ar bg cs et fa fi he hi hr hu id ko lv ms no pt ru sk sl sr sv th tr uk vi                |
| Part of speech tagging   | bg cs fi hu id sl sv                                                                      |
| Word embeddings          | same as named entity recognition                                                          |
| Sentiment                | 136 languages (see the Sentiment docs)                                                    |
| Language detection       | 176 languages (see the Detection docs)                                                    |
| Tokenization             | all languages (see the Tokenization docs)                                                 |

## Credits and citation

polyglot was created by **Rami Al-Rfou** with contributions from Yingtao Tian
and others at the Data Science Lab, Stony Brook University. The models come
from their research. If you use them, please cite the papers:

- Word embeddings and part of speech tagging:
  [Polyglot: Distributed Word Representations for Multilingual NLP](https://aclanthology.org/W13-3520/)
  (CoNLL 2013)
- Named entity recognition:
  [POLYGLOT-NER: Massive Multilingual Named Entity Recognition](https://arxiv.org/abs/1410.3791)
  (SDM 2015)
- Sentiment:
  [Building sentiment lexicons for all major languages](https://aclanthology.org/P14-2063/)
  (ACL 2014)

```bibtex
@InProceedings{polyglot:2013:ACL-CoNLL,
  author    = {Al-Rfou, Rami and Perozzi, Bryan and Skiena, Steven},
  title     = {Polyglot: Distributed Word Representations for Multilingual NLP},
  booktitle = {Proceedings of the Seventeenth Conference on Computational Natural Language Learning},
  month     = {August},
  year      = {2013},
  address   = {Sofia, Bulgaria},
  publisher = {Association for Computational Linguistics},
  pages     = {183--192},
  url       = {https://aclanthology.org/W13-3520}
}

@inproceedings{polyglotner,
  author    = {Al-Rfou, Rami and Kulkarni, Vivek and Perozzi, Bryan and Skiena, Steven},
  title     = {{Polyglot-NER}: Massive Multilingual Named Entity Recognition},
  booktitle = {Proceedings of the 2015 {SIAM} International Conference on Data Mining},
  month     = {April},
  year      = {2015},
  publisher = {SIAM}
}

@inproceedings{chen2014building,
  title     = {Building sentiment lexicons for all major languages},
  author    = {Chen, Yanqing and Skiena, Steven},
  booktitle = {Proceedings of the 52nd Annual Meeting of the Association for Computational Linguistics (Short Papers)},
  pages     = {383--389},
  year      = {2014}
}
```

Segmentation is derived from [ICU](https://icu.unicode.org/) (Unicode
License V3) and language detection uses
[fastText](https://fasttext.cc/docs/en/language-identification.html)'s
`lid.176` model.

polyglot3 is maintained by **Dcipher Analytics AB**
(<info@dcipheranalytics.com>). This repository has been updated by the
Dcipher Analytics dev team with help from Claude Opus. Many thanks to the
original polyglot authors for their work.
