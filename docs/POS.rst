Part of Speech Tagging
======================

Part of speech tagging assigns each word a syntactic category. polyglot's
taggers use the `universal part of speech tags
<https://universaldependencies.org/u/pos/>`__ (17 tags):

=====  =========================  =====  =========================
Tag    Meaning                    Tag    Meaning
=====  =========================  =====  =========================
ADJ    adjective                  NUM    numeral
ADP    adposition                 PART   particle
ADV    adverb                     PRON   pronoun
AUX    auxiliary verb             PROPN  proper noun
CONJ   coordinating conjunction   PUNCT  punctuation
DET    determiner                 SCONJ  subordinating conjunction
INTJ   interjection               SYM    symbol
NOUN   noun                       VERB   verb
X      other
=====  =========================  =====  =========================

Languages
---------

Bulgarian (bg), Czech (cs), Finnish (fi), Hungarian (hu), Indonesian (id),
Slovene (sl) and Swedish (sv). Tagging needs both the ``pos2`` and the
``embeddings2`` package of the language:

.. code:: bash

    polyglot download embeddings2.hu pos2.hu

Example
-------

.. code:: python

    from polyglot.text import Text

    text = Text("Budapest Magyarország fővárosa és legnépesebb városa.")
    for word, tag in text.pos_tags:
        print("{:<16}{}".format(word, tag))

.. parsed-literal::

    Budapest        PROPN
    Magyarország    PROPN
    fővárosa        ADJ
    és              CONJ
    legnépesebb     ADJ
    városa          NOUN
    .               PUNCT

The language is detected automatically; pass
``Text(..., hint_language_code="hu")`` to skip detection. After calling
``pos_tags``, each word also carries its tag in ``word.pos_tag``.

Command line
------------

.. code:: console

    $ echo "Petr Novák pracuje v Praze ." | polyglot --lang cs pos
    Petr            PROPN
    Novák           PROPN
    pracuje         ADJ
    v               ADP
    Praze           NOUN
    .               PUNCT

The ``pos`` subcommand splits lines on whitespace; pipe raw text through
``polyglot tokenize`` first (see :doc:`CLI`).

Citation
--------

The taggers are built on the embeddings described in
`Polyglot: Distributed Word Representations for Multilingual NLP
<https://aclanthology.org/W13-3520/>`__. Please cite it if you use them::

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
