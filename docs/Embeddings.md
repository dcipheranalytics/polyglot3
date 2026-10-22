# Word Embeddings

Word embeddings map each word to a real-valued vector that captures semantic
and syntactic similarity. polyglot's embeddings were trained on Wikipedia and
are also the input features of the NER and POS taggers.

Models: `embeddings2.<lang>` for ar bg cs et fa fi he hi hr hu id ko lv ms no
pt ru sk sl sr sv th tr uk vi (see [Downloading Models](Download.md)).

## Loading

```python
from polyglot3.load import load_embeddings

embeddings = load_embeddings("tr")
print(embeddings.shape)
```

```text
(100004, 64)
```

Each language has the 100,000 most frequent Wikipedia words (plus special
tokens), each a 64-dimensional vector:

```python
embeddings["Ankara"][:5]
```

```text
array([-0.25176665, -0.05952398, -0.31523946, -0.46134406,  0.35282844],
      dtype=float32)
```

## Nearest neighbors

```python
neighbors = embeddings.nearest_neighbors("Ankara")
print(neighbors)
print(embeddings.distances("Ankara", neighbors))
```

```text
['İstanbul', 'İzmir', 'Bursa', 'Antalya', 'Adana', 'Trabzon', 'Balıkesir', 'Konya', 'Eskişehir', 'Sivas']
[0.6327 0.6346 0.7299 0.8311 0.8655 0.8789 0.9045 0.914  0.9154 0.9259]
```

`nearest_neighbors(word, top_k=10)` ranks words by Euclidean distance.

## Vocabulary expansion

`load_embeddings` applies two expansions so that more words get a vector:

- `CaseExpander`: a word missing from the vocabulary falls back to its
  lowercase, title case or uppercase form ("ANKARA" uses "Ankara").
- `DigitExpander`: the embeddings were trained with every digit replaced by
  `#`, so "1923" uses the vector of "####".

```python
"ANKARA" in embeddings, "1923" in embeddings   # (True, True)
```

To load the raw embeddings without expansions:

```python
from polyglot3.load import locate_resource
from polyglot3.mapping import Embedding

raw = Embedding.load(locate_resource("embeddings2", "tr"))
"ANKARA" in raw, "1923" in raw                 # (True, False)
```

## Normalization

```python
normalized = embeddings.normalize_words()      # unit-length rows (L2)
normalized.nearest_neighbors("Ankara", top_k=5)
```

```text
['İstanbul', 'İzmir', 'Bursa', 'Antalya', 'Adana']
```

`load_embeddings(lang, normalize=True)` normalizes in place.

## Other formats

`Embedding` also reads other common formats into the same API:

```python
Embedding.from_word2vec("vectors.bin", binary=True)
Embedding.from_word2vec("vectors.txt", binary=False)
Embedding.from_glove("glove.6B.50d.txt")
Embedding.from_gensim(gensim_model)   # gensim 0.x/3.x KeyedVectors API
```

and saves to polyglot's own format with `embedding.save(path)`.

> **Note:** `Word("...").vector` and `Word("...").neighbors` use a second set
> of embeddings (`sgns2`) that is not available from the polyglot3 model
> server. Use `load_embeddings` as shown above.

## Citation

This is an implementation of the research described in
[Polyglot: Distributed Word Representations for Multilingual NLP](https://aclanthology.org/W13-3520/).
Please cite it if you use the embeddings:

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
```
