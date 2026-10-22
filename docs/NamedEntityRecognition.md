# Named Entity Extraction

Named entity extraction finds phrases that refer to people (`I-PER`),
locations (`I-LOC`) and organizations (`I-ORG`).

## Languages

Arabic (ar), Bulgarian (bg), Czech (cs), Estonian (et), Persian (fa), Finnish
(fi), Hebrew (he), Hindi (hi), Croatian (hr), Hungarian (hu), Indonesian (id),
Korean (ko), Latvian (lv), Malay (ms), Norwegian (no), Portuguese (pt),
Russian (ru), Slovak (sk), Slovene (sl), Serbian (sr), Swedish (sv), Thai
(th), Turkish (tr), Ukrainian (uk) and Vietnamese (vi).

The models were trained on data extracted automatically from Wikipedia and
Freebase. Extraction needs both the `ner2` and the `embeddings2` package of
the language:

```bash
polyglot3 download embeddings2.tr ner2.tr
```

## Example

```python
from polyglot3.text import Text

text = Text("Mustafa Kemal Atatürk, 1923 yılında Ankara'da "
            "Türkiye Cumhuriyeti'ni ilan etti.")
print(text.entities)
```

```text
[I-PER(['Mustafa', 'Kemal', 'Atatürk']), I-LOC(['Türkiye'])]
```

Each entity is a `Chunk`: a list of words with a `tag` and the positions of
its first word and of the word after its last in `text.words`:

```python
for entity in text.entities:
    print(entity.tag, list(entity), entity.start, entity.end)
```

```text
I-PER ['Mustafa', 'Kemal', 'Atatürk'] 0 3
I-LOC ['Türkiye'] 7 8
```

Another example, in Czech:

```python
Text("Václav Havel se narodil v Praze a byl prezidentem Československa.").entities
```

```text
[I-PER(['Václav', 'Havel']), I-LOC(['Praze']), I-LOC(['Československa'])]
```

The language is detected automatically; pass
`Text(..., hint_language_code="tr")` to skip detection. The models make
mistakes: above, "Ankara'da" is missed and "Türkiye Cumhuriyeti'ni" is only
partly tagged.

## Command line

```console
$ echo "Ankara Türkiye'nin başkentidir." | polyglot3 --lang tr tokenize | polyglot3 --lang tr ner
Ankara          I-LOC
Türkiye'nin     O
başkentidir     O
.               O
```

## Citation

This is an implementation of the research described in
[POLYGLOT-NER: Massive Multilingual Named Entity Recognition](https://arxiv.org/abs/1410.3791).
Please cite it if you use the models:

```bibtex
@inproceedings{polyglotner,
  author    = {Al-Rfou, Rami and Kulkarni, Vivek and Perozzi, Bryan and Skiena, Steven},
  title     = {{Polyglot-NER}: Massive Multilingual Named Entity Recognition},
  booktitle = {Proceedings of the 2015 {SIAM} International Conference on Data Mining},
  month     = {April},
  year      = {2015},
  publisher = {SIAM}
}
```
