Sentiment
=========

polyglot has polarity lexicons for 136 languages. Each word is positive
(+1), neutral (0) or negative (-1).

Languages
---------

af als am an ar arz as ast az ba bar be bg bn bo bpy br bs ca ce ceb cs cv cy
da de diq dv el en eo es et eu fa fi fo fr fy ga gan gd gl gu gv he hi hif hr
hsb ht hu hy ia id ilo io is it ja jv ka kk km kn ko ku ky la lb li lmo lt lv
mg mk ml mn mr ms mt my ne nl nn no oc or os pa pam pl pms ps pt qu rm ro ru
sa sah scn sco se sh si sk sl sq sr su sv sw szl ta te tg th tk tl tr tt ug
uk ur uz vec vi vls vo wa war yi yo zh zhw

.. code:: bash

    polyglot download sentiment2.tr

Word polarity
-------------

.. code:: python

    from polyglot.text import Text

    text = Text("Bu film harika ama son kısmı berbat.")
    for w in text.words:
        print("{:<16}{:>2}".format(w, w.polarity))

.. parsed-literal::

    Bu               0
    film             0
    harika           1
    ama             -1
    son              0
    kısmı            0
    berbat          -1
    .                0

Text polarity
-------------

``Text.polarity`` and ``Sentence.polarity`` average the polarity of the
non-neutral words, giving a score between -1 and 1 (0 when no word is
polar):

.. code:: python

    text.polarity

.. parsed-literal::

    -0.3333333333333333

.. code:: python

    text = Text("Barack Obama gave a fantastic speech last night. "
                "Reports indicate he will move next to New Hampshire.")
    for sentence in text.sentences:
        print(sentence.polarity, sentence)

.. parsed-literal::

    1.0 Barack Obama gave a fantastic speech last night.
    0.0 Reports indicate he will move next to New Hampshire.

Entity sentiment
----------------

For languages with :doc:`NER <NamedEntityRecognition>` models, each entity
gets a positive and a negative score: the polar words around it, weighted
by their distance from the entity.

.. code:: python

    text = Text("Ankara güzel bir şehir ama İstanbul berbat bir trafiğe sahip.")
    for entity in text.entities:
        print(entity, entity.positive_sentiment, entity.negative_sentiment)

.. parsed-literal::

    ['Ankara'] 1.0454545454545454 1.727272727272727
    ['İstanbul'] 0.8636363636363636 2.0454545454545454

Command line
------------

.. code:: console

    $ echo "harika ama berbat" | polyglot --lang tr sentiment
    harika           1
    ama             -1
    berbat          -1

Citation
--------

The lexicons come from
`Building sentiment lexicons for all major languages
<https://aclanthology.org/P14-2063/>`__. Please cite it if you use them::

    @inproceedings{chen2014building,
      title     = {Building sentiment lexicons for all major languages},
      author    = {Chen, Yanqing and Skiena, Steven},
      booktitle = {Proceedings of the 52nd Annual Meeting of the Association for Computational Linguistics (Short Papers)},
      pages     = {383--389},
      year      = {2014}
    }
