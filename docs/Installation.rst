Installation
============

polyglot3 needs Python 3.9 or newer and no system libraries:

.. code:: bash

    pip install polyglot3

This installs the ``polyglot`` package (imported as ``import polyglot``)
and the ``polyglot`` and ``polyglot3`` command-line tools. Its only
dependencies are NumPy and
`fasttext-langdetect <https://pypi.org/project/fasttext-langdetect/>`__.

.. note::

    polyglot3 and the original ``polyglot`` package both install a module
    named ``polyglot``. Uninstall the original first:
    ``pip uninstall polyglot``. PyICU and pycld2 are no longer needed.

Models
------

Tokenization works out of the box. Every other task needs models, which
are downloaded once per language and task:

.. code:: bash

    polyglot download LANG:tr        # all models for Turkish
    polyglot download ner2.cs pos2.cs embeddings2.cs

See :doc:`Download` for the package names. The language detection model
(fastText ``lid.176``, about 126 MB) is downloaded automatically on first
use.

Environment variables
---------------------

``POLYGLOT_DATA_PATH``
    Directory under which models are stored, in ``polyglot_data/``.
    Defaults to the home directory (``%APPDATA%`` on Windows).

``POLYGLOT_DATA_URL``
    Server to download models from. Defaults to the polyglot3 Hugging Face
    dataset; set it to use a mirror.

``FTLANG_CACHE``
    Directory where the fastText language detection model is cached.
    Defaults to the system temporary directory.

From source
-----------

.. code:: bash

    git clone https://github.com/dcipheranalytics/polyglot3.git
    cd polyglot3
    pip install -e ".[test]"
    python -m pytest
