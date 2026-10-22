---
pretty_name: polyglot3 models
license: other
license_name: polyglot-models
license_link: https://github.com/aboSamoor/polyglot
language:
- ar
- bg
- cs
- et
- fa
- fi
- he
- hi
- hr
- hu
- id
- ko
- lv
- ms
- no
- pt
- ru
- sk
- sl
- sr
- sv
- th
- tr
- uk
- vi
- multilingual
task_categories:
- token-classification
- text-classification
tags:
- named-entity-recognition
- part-of-speech
- sentiment
- word-embeddings
- polyglot
---

# polyglot3 models

Pre-trained models for [polyglot3](https://github.com/dcipheranalytics/polyglot3),
the maintained Python 3 continuation of
[polyglot](https://github.com/aboSamoor/polyglot): word embeddings, named
entity recognition, part of speech tagging and sentiment lexicons.

These are the models originally published by the polyglot project at Stony
Brook University, whose download server is no longer online. This dataset
mirrors them, unchanged, so that polyglot3 can download them. It is maintained
by Dcipher Analytics AB (<info@dcipheranalytics.com>).

## Usage

The files are meant to be downloaded by polyglot3, which verifies each one
against the checksums in `index.json`:

```bash
pip install polyglot3
polyglot3 download LANG:tr        # every model for Turkish
```

```python
from polyglot3.text import Text

Text("Mustafa Kemal Atatürk Ankara'da yaşadı.").entities
# [I-PER(['Mustafa', 'Kemal', 'Atatürk'])]
```

See the [polyglot3 documentation](https://github.com/dcipheranalytics/polyglot3)
for details.

## Contents

| Package       | Contents                                                   | Languages | Size   |
|---------------|------------------------------------------------------------|-----------|--------|
| `embeddings2` | 64-dimensional word embeddings (100,000 words), NER/POS input | 25     | 635 MB |
| `ner2`        | named entity recognition (person, location, organization)  | 25        | 7 MB   |
| `pos2`        | part of speech tagging (universal POS tags)                | 7         | 1.5 MB |
| `sentiment2`  | word polarity lexicons (positive, neutral, negative)       | 136       | 1.4 MB |

Each package is a single file at `<task>/<language>/<file>`, e.g.
`ner2/tr/tr_ner.pkl.tar.bz2`. `index.json` lists every file with its size and
MD5.

Languages (ISO 639 codes):

- **Embeddings and NER:** ar bg cs et fa fi he hi hr hu id ko lv ms no pt ru sk
  sl sr sv th tr uk vi
- **POS:** bg cs fi hu id sl sv
- **Sentiment:** af als am an ar arz as ast az ba bar be bg bn bo bpy br bs ca
  ce ceb cs cv cy da de diq dv el en eo es et eu fa fi fo fr fy ga gan gd gl gu
  gv he hi hif hr hsb ht hu hy ia id ilo io is it ja jv ka kk km kn ko ku ky la
  lb li lmo lt lv mg mk ml mn mr ms mt my ne nl nn no oc or os pa pam pl pms ps
  pt qu rm ro ru sa sah scn sco se sh si sk sl sq sr su sv sw szl ta te tg th
  tk tl tr tt ug uk ur uz vec vi vls vo wa war yi yo zh zhw

The original polyglot project published models for more languages. This
mirror only contains the ones above.

## Source and license

The models were created by Rami Al-Rfou, Bryan Perozzi, Vivek Kulkarni,
Yanqing Chen, Steven Skiena and colleagues at the Data Science Lab, Stony
Brook University, and released with
[polyglot](https://github.com/aboSamoor/polyglot). They were trained on
Wikipedia (embeddings, NER, POS) and derived from it and other resources
(sentiment); see the papers below.

The polyglot code is licensed under GPLv3. The models are redistributed here
under the terms of their original release; refer to the
[polyglot project](https://github.com/aboSamoor/polyglot) for those terms. If
you are an author of these models and have questions about this mirror,
contact <info@dcipheranalytics.com>.

## Citation

If you use these models, please cite the original papers:

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
