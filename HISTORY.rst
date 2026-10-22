.. :changelog:

History
-------

2026.10.1 (2026-10-22)
----------------------

First release as **polyglot3**, by the Dcipher Analytics dev team.

* Python 3.9 to 3.13 only; Python 2 support and ``six`` removed.
* Removed the PyICU dependency: word and sentence segmentation use a
  pure-Python port of ICU 78.3's break iterators (including the Thai
  dictionary engine) that reproduces ICU's boundaries.
* Removed the pycld2 dependency: language detection uses fastText's
  ``lid.176`` model via fasttext-langdetect. Hebrew is now ``he``, not ``iw``.
* Models are downloaded from a new server (Hugging Face) with checksum
  verification; ``POLYGLOT_DATA_URL`` selects a mirror.
* Packaging with ``pyproject.toml``; ``polyglot3`` console script added.
* Removed morphological analysis and transliteration (models unavailable)
  and the TextBlob leftovers ``correct()``, ``tokenize()`` and
  ``np_counts`` (they always raised errors).
* Bug fixes: garbled tokens after emoji and other non-BMP characters;
  ``polyglot sentiment`` did nothing; entity sentiment only used the first
  polar word; ``Embedding.normalize_words()`` failed on expanded
  vocabularies; ``Downloader.status()`` returned ``None`` for a custom
  download directory; ``Downloader.supported_language()`` crashed; the CLI
  closed stdin repeatedly on Python 3.13.

"14.11" (2014-01-11)
---------------------

* First release on PyPI.


"15.5.2" (2015-05-02)
---------------------

* Polyglot is feature complete.


"15.10.03" (2015-10-03)
---------------------------

* Change the polyglot models mirror to Stony Brook University DSL lab instead
  of Google cloud storage.


"16.07.04" (2016-07-03)
---------------------------

* New Features:
  - Support Transfer POS Tagging.
  - Support supplying `hint_language_code` for `Text`.

* Bug Fix: 
  - Improve sentence serialization (PR #34)
  - Fix rare unicode encode error (PR #35)
  - Fix transliteration from languages other than English (PR 46)
  - Add link to Github in README (PR #49)
  - Make handling of paths more coherent (RP #55)
  - Fix normalizing embedding in place for NER corrupts the features of POS (issue #60, PR #62)

