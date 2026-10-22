# Installation

polyglot3 needs Python 3.9 or newer and no system libraries:

```bash
pip install polyglot3
```

This installs the `polyglot3` package (`import polyglot3`) and the `polyglot3`
command-line tool. Its only dependency is NumPy.

## Migrating from polyglot

polyglot3 has the same API under a new name, and can be installed next to
the original `polyglot`. Replace the imports and the command name:

```python
# polyglot
from polyglot.text import Text

# polyglot3
from polyglot3.text import Text
```

```bash
polyglot download LANG:tr   # before
polyglot3 download LANG:tr  # after
```

Downloaded models (`~/polyglot_data`) and the `POLYGLOT_*` environment
variables are shared, so existing models keep working. PyICU and pycld2 are
no longer needed.

## Models

Tokenization works out of the box. Every other task needs models, which are
downloaded once per language and task:

```bash
polyglot3 download LANG:tr        # all models for Turkish
polyglot3 download ner2.cs pos2.cs embeddings2.cs
```

See [Downloading Models](Download.md) for the package names. The language
detection model (fastText `lid.176`, about 126 MB) is downloaded
automatically on first use.

## Environment variables

- `POLYGLOT_DATA_PATH`: directory under which models are stored, in
  `polyglot_data/`. Defaults to the home directory (`%APPDATA%` on Windows).
- `POLYGLOT_DATA_URL`: server to download models from. Defaults to the
  polyglot3 Hugging Face dataset; set it to use a mirror.
- `FTLANG_CACHE`: directory where the fastText language detection model is
  cached. Defaults to the system temporary directory.

## From source

```bash
git clone https://github.com/dcipheranalytics/polyglot3.git
cd polyglot3
pip install -e ".[test]"
python -m pytest
```
