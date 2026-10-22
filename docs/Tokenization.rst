Tokenization
============

Tokenization identifies the boundaries of words and sentences. polyglot
follows the `Unicode Text Segmentation <https://www.unicode.org/reports/tr29/>`__
algorithm exactly as ICU implements it for its root locale, which is what
the original polyglot used and what its NER and POS models were trained on.

polyglot3 does not need ICU: ``polyglot.tokenize.breakiter`` is a
pure-Python port of ICU 78.3's rule-based break iterator. Its state tables
are compiled from ICU's own ``word.txt`` and ``sent.txt`` rules, and Thai is
split with a port of ICU's dictionary-based Thai engine and ICU's Thai
dictionary. The boundaries are tested against ICU on a multilingual corpus
and on a million random strings.

.. code:: python

    from polyglot.text import Text

Word tokenization
-----------------

.. code:: python

    text = Text("Dr. Ahmet Bey, 3,14 değerini hesapladı! Sonra İstanbul'a gitti 😀 ve döndü.")
    print(text.words)

.. parsed-literal::

    ['Dr', '.', 'Ahmet', 'Bey', ',', '3,14', 'değerini', 'hesapladı', '!', 'Sonra', "İstanbul'a", 'gitti', '😀', 've', 'döndü', '.']

Numbers with separators, apostrophes inside words and emoji stay single
tokens. Thai, which is written without spaces between words, is split with
a dictionary:

.. code:: python

    Text("กรุงเทพมหานครเป็นเมืองหลวงของประเทศไทย").words

.. parsed-literal::

    ['กรุงเทพมหานคร', 'เป็น', 'เมือง', 'หลวง', 'ของ', 'ประเทศไทย']

Sentence segmentation
---------------------

.. code:: python

    print(text.sentences)

.. parsed-literal::

    [Sentence("Dr."), Sentence("Ahmet Bey, 3,14 değerini hesapladı!"), Sentence("Sonra İstanbul'a gitti 😀 ve döndü.")]

ICU's root rules do not know abbreviations, so a period after ``Dr`` ends a
sentence. ``Sentence`` objects support the same properties as ``Text``,
e.g. ``text.sentences[1].words``.

Lower-level API
---------------

``WordTokenizer`` and ``SentenceTokenizer`` work on ``Sequence`` objects and
return boundary offsets; ``polyglot.tokenize.breakiter`` exposes the
boundaries of a plain string:

.. code:: python

    from polyglot.tokenize.breakiter import word_boundaries, sentence_boundaries

    sentence_boundaries("Bugün hava güzel. Yarın yağmur var.")   # [0, 18, 35]

The ``locale`` argument of the tokenizers is accepted for compatibility but
ignored: segmentation is the same for every language.

Command line
------------

``polyglot tokenize`` prints one sentence per line with words separated by
spaces. ``--only-word`` prints one token per line, ``--only-sent`` one
sentence per line:

.. code:: console

    $ echo "Bugün hava çok güzel. Yarın İstanbul'a gidiyorum." | polyglot --lang tr tokenize
    Bugün hava çok güzel .
    Yarın İstanbul'a gidiyorum .

Limitations
-----------

ICU also splits Chinese, Japanese, Korean, Lao, Khmer and Burmese with
large dictionaries that polyglot3 does not bundle. For these scripts a run
of characters is not subdivided (as in ICU without those dictionaries):

.. code:: python

    Text("该超市1月9日遭受枪手袭击。").words

.. parsed-literal::

    ['该超市', '1', '月', '9', '日遭受枪手袭击', '。']

References
----------

-  `Unicode Text Segmentation (UAX #29) <https://www.unicode.org/reports/tr29/>`__
-  `ICU boundary analysis <https://unicode-org.github.io/icu/userguide/boundaryanalysis/>`__
