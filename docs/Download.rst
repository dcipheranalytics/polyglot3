Downloading Models
==================

Models are downloaded once and stored under
``$POLYGLOT_DATA_PATH/polyglot_data`` (default: ``~/polyglot_data``,
``%APPDATA%\polyglot_data`` on Windows). Each download is checked against
the checksum in the server's index.

Packages and collections
------------------------

A package holds one model for one language and is named
``<task>.<language>``:

=================  ====================================  ===========
Task               Used by                               Languages
=================  ====================================  ===========
``embeddings2``    NER, POS, ``load_embeddings``         25
``ner2``           ``Text.entities``                     25
``pos2``           ``Text.pos_tags``                     7
``sentiment2``     ``Word.polarity``, ``Text.polarity``  136
=================  ====================================  ===========

NER and POS need the ``embeddings2`` package of the same language too.
Collections bundle packages: ``LANG:<code>`` has every package for one
language and ``TASK:<task>`` has one task for every language.

Command line
------------

.. code:: console

    $ polyglot download ner2.tr embeddings2.tr
    [polyglot_data] Downloading package ner2.tr to
    [polyglot_data]     /home/me/polyglot_data...
    [polyglot_data] Downloading package embeddings2.tr to
    [polyglot_data]     /home/me/polyglot_data...

    $ polyglot download LANG:cs
    [polyglot_data] Downloading collection 'LANG:cs'
    [polyglot_data]    |
    [polyglot_data]    | Downloading package embeddings2.cs to
    ...

Options: ``--dir DIR`` installs into another directory, ``--force``
downloads again even if a package is installed, ``--quiet`` hides the
progress messages, and ``--url URL`` uses another server.
``polyglot download`` without packages opens an interactive shell.

Python
------

.. code:: python

    from polyglot.downloader import downloader

    downloader.download("LANG:tr")
    downloader.download("embeddings2.cs", quiet=True)

    downloader.supported_tasks(lang="tr")
    # ['embeddings2', 'ner2', 'sentiment2']

    print(downloader.supported_languages_table("pos2"))

.. parsed-literal::

      1. Bulgarian                  2. Czech                      3. Finnish
      4. Hungarian                  5. Indonesian                 6. Slovene
      7. Swedish

``downloader.status("ner2.tr")`` returns ``'installed'``,
``'not installed'`` or ``'out of date'``.

Mirrors
-------

By default models come from the polyglot3 dataset on Hugging Face. To use
another server, set ``POLYGLOT_DATA_URL`` (or pass ``--url`` /
``Downloader(server_index_url=...)``). A mirror is any static file host
with the layout::

    index.json
    embeddings2/tr/embeddings_pkl.tar.bz2
    ner2/tr/tr_ner.pkl.tar.bz2
    ...

``index.json`` lists each file's path, size and MD5. Build it with
``python tools/data/build_index.py path/to/polyglot_data`` from the
source repository.

Offline use
-----------

Copy a ``polyglot_data`` directory to the target machine and point
``POLYGLOT_DATA_PATH`` at its parent directory. Installed packages are used
without contacting the server.
