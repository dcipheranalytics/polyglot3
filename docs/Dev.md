# Developer Guide

## Setup

```bash
git clone https://github.com/dcipheranalytics/polyglot3.git
cd polyglot3
pip install -e ".[test]" ruff build twine

ruff check polyglot3 tests tools   # errors only (syntax, undefined names, unused code)
python -m pytest
```

## Layout

| Path                               | Contents                                     |
|------------------------------------|----------------------------------------------|
| `polyglot3/`                        | the package                                  |
| `polyglot3/tokenize/breakiter.py`   | pure-Python port of ICU's break iterators    |
| `polyglot3/tokenize/_tables.py`     | generated state tables (do not edit)         |
| `polyglot3/tokenize/data/`          | ICU's Thai dictionary and ICU license        |
| `tests/`                           | test suite and fixtures                      |
| `tools/icu_port/`                  | generates and fuzzes the ICU port            |
| `tools/fixtures/`                  | generates the test fixtures                  |
| `tools/data/`                      | builds and uploads the model index           |

## Tests

`python -m pytest` runs everything that is available:

- `tests/test_segmentation.py` compares word and sentence boundaries with
  ICU's on every fixture paragraph. It needs nothing else.
- `tests/test_golden.py` checks words, sentences, entities, POS tags and
  polarity against the outputs of the original polyglot. It runs when the
  models are installed (`$POLYGLOT_DATA_PATH/polyglot_data`) and skips
  otherwise.
- `tests/test_detect.py` checks detection accuracy when fastText's `lid.176`
  model is cached, and unit-tests the wrapper otherwise.

To run the golden tests, install the models of the fixture languages, e.g.
`polyglot3 download TASK:ner2 TASK:pos2 TASK:embeddings2 TASK:sentiment2`.

## Fixtures

`tests/fixtures/corpus` holds Wikipedia paragraphs for the main languages
and hand-written edge cases. The other fixture directories were generated
from it once, with tools that need PyICU and pycld2 and must run in a
separate throwaway environment, never as project dependencies:

- `tools/fixtures/gen_icu_fixtures.py`: ICU's boundaries
  (`tests/fixtures/segmentation`).
- `tools/fixtures/gen_golden.py`: outputs of the original polyglot at commit
  `9b93b2e` (`tests/fixtures/golden`).

Regenerate them only on purpose (for example, to move to a newer ICU), and
review the diff.

## The ICU port

polyglot's NER and POS models were trained on tokens produced by ICU, so
tokenization must reproduce ICU's root-locale word and sentence break
iterators exactly. The port has three parts:

1. `tools/icu_port/build_tables.py` compiles ICU's rule files
   (`tools/icu_port/rules/word.txt` and `sent.txt`, from ICU 78.3) and
   Unicode 17 property data into DFA tables, following ICU's `rbbitblb.cpp`
   (position automaton, rule chaining, `{bof}`):

   ```bash
   python tools/icu_port/build_tables.py /tmp/ucd polyglot3/tokenize/_tables.py
   ```

2. `breakiter.py` runs the tables like ICU's `handleNext` and `BreakCache`.
3. Thai runs go through a line-by-line port of ICU's `ThaiBreakEngine` with
   ICU's Thai dictionary. Other dictionary scripts (CJK, Lao, Khmer, Burmese)
   are left unsplit.

`tools/icu_port/fuzz.py` compares the port with PyICU on random text. Run it
after any change to the tokenizer, in a throwaway environment with PyICU
built against ICU 78:

```bash
PYTHONPATH=. python tools/icu_port/fuzz.py 1000000 7
# 1000000 texts, 0 mismatches, ... expected differences in CJK/Lao/Khmer/Burmese text
```

## Model hosting

The downloader reads `index.json` from `Downloader.DEFAULT_URL` (or
`$POLYGLOT_DATA_URL`) and resolves package paths relative to it. To publish a
set of models:

```bash
python tools/data/build_index.py path/to/polyglot_data
pip install huggingface_hub && hf auth login
python tools/data/upload_to_hf.py path/to/polyglot_data polyglot3/polyglot3-data
```

If you host elsewhere, update `DEFAULT_URL` in `polyglot3/downloader.py`.

## Releasing

The version lives in `polyglot3/__init__.py` (`__version__`) and uses the
calendar scheme `YYYY.MM.N`.

1. Update `__version__` and add an entry to `HISTORY.md`.
2. Check the build locally:

   ```bash
   rm -rf dist && python -m build && python -m twine check --strict dist/*
   ```

3. Commit, tag and push: `git tag v2026.10.1 && git push --tags`.
4. Publish:

   - **GitHub Actions (recommended).** Create a GitHub release for the tag.
     `.github/workflows/publish.yml` builds the package and uploads it with
     PyPI trusted publishing. This needs a one-time setup: on
     <https://pypi.org/manage/account/publishing/> add a "pending publisher"
     for project `polyglot3` with your GitHub owner and repository, workflow
     `publish.yml` and environment `pypi`, then create an environment named
     `pypi` in the GitHub repository settings.
   - **Manually.** Create an API token at
     <https://pypi.org/manage/account/token/> and run
     `python -m twine upload dist/*` (user `__token__`, the token as
     password).

   To rehearse, upload to TestPyPI first
   (`python -m twine upload --repository testpypi dist/*`) and install with
   `pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ polyglot3`.

PyPI never accepts the same version twice, so a fix after a release needs a
new version number (e.g. `2026.10.2`).
