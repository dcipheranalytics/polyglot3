# Language Detection

polyglot3 detects languages with fastText's pre-trained `lid.176` model
through [fasttext-langdetect](https://pypi.org/project/fasttext-langdetect/).
The model (about 126 MB) is downloaded on first use and cached in
`$FTLANG_CACHE` (default: the system temporary directory).

```python
from polyglot3.detect import Detector
```

## Example

```python
arabic_text = ("أفاد مصدر امني في قيادة عمليات صلاح الدين في العراق بأن القوات "
               "الامنية تتوقف لليوم الثالث على التوالي عن التقدم الى داخل مدينة تكريت.")
detector = Detector(arabic_text)
print(detector.language)
```

```text
name: Arabic      code: ar       confidence:  99.8 read bytes:   242
```

`language.code` is the ISO 639 code used by the models and the downloader,
`confidence` is fastText's probability in percent, and `read_bytes` is the
UTF-8 length of the text.

## Mixed text

The detector keeps fastText's three most probable languages:

```python
mixed_text = ("China (simplified Chinese: 中国; traditional Chinese: 中國), "
              "officially the People's Republic of China (PRC), "
              "is a sovereign state located in East Asia.")
for language in Detector(mixed_text).languages:
    print(language)
```

```text
name: English     code: en       confidence:  91.6 read bytes:   156
name: Italian     code: it       confidence:   1.4 read bytes:   156
name: Chinese     code: zh       confidence:   0.7 read bytes:   156
```

To find every language in a document, detect line by line or sentence by
sentence.

## Reliability

When the most probable language has a probability below 50%, the result is
flagged as unreliable and a warning is logged:

```python
detector = Detector("Mario")
print(detector.reliable)
print([(l.code, round(l.confidence, 1)) for l in detector.languages])
```

```text
False
[('it', 19.8), ('fr', 18.0), ('en', 13.9)]
```

Text without any letters raises `UnknownLanguage`. Pass `quiet=True` to
silence both: the warning is dropped and empty text is reported as the
unknown language `un`.

```python
Detector("   ", quiet=True).language.code   # 'un'
```

`Text` objects detect their language this way (quietly) unless you pass
`hint_language_code`:

```python
from polyglot3.text import Text
Text("Praha je hlavní město České republiky.").language.code   # 'cs'
Text("Ankara", hint_language_code="tr").language.code         # 'tr'
```

## Command line

```console
$ printf 'Bugün hava çok güzel.\nPraha je hlavní město České republiky.\n' | polyglot3 detect
Turkish             Bugün hava çok güzel.
Czech               Praha je hlavní město České republiky.
```

## Supported languages

`Detector.supported_languages()` lists the 176 languages fastText's
`lid.176` model knows:

af als am an ar arz as ast av az azb ba bar bcl be bg bh bn bo bpy br bs
bxr ca cbk ce ceb ckb co cs cv cy da de diq dsb dty dv el eml en eo es et
eu fa fi fr frr fy ga gd gl gn gom gu gv he hi hif hr hsb ht hu hy ia id ie
ilo io is it ja jbo jv ka kk km kn ko krc ku kv kw ky la lb lez li lmo lo
lrc lt lv mai mg mhr min mk ml mn mr mrj ms mt mwl my myv mzn nah nap nds
ne new nl nn no oc or os pa pam pfl pl pms pnb ps pt qu rm ro ru rue sa sah
sc scn sco sd sh si sk sl so sq sr su sv sw ta te tg th tk tl tr tt tyv ug
uk ur uz vec vep vi vls vo wa war wuu xal xmf yi yo yue zh

## Known limitations

- Malay (`ms`) is often detected as Indonesian (`id`), and Croatian (`hr`)
  occasionally as Serbo-Croatian (`sh`) or Serbian (`sr`). Pass
  `hint_language_code` when you know the language.
- polyglot used `iw` for Hebrew (from cld2); fastText returns `he`, which
  matches the model packages.
