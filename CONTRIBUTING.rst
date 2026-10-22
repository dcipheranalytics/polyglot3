============
Contributing
============

Contributions are welcome. Report bugs and propose features at
https://github.com/dcipheranalytics/polyglot3/issues. For bugs, include your
operating system, Python version, polyglot3 version and the steps to
reproduce.

Development setup
-----------------

1. Fork and clone the repository::

    $ git clone git@github.com:your_name_here/polyglot3.git
    $ cd polyglot3

2. Install it in a virtual environment in editable mode::

    $ python -m venv .venv && source .venv/bin/activate
    $ pip install -e ".[test]" ruff

3. Create a branch, make your changes, then run the checks::

    $ ruff check polyglot tests tools
    $ python -m pytest

   Tests that need models skip themselves unless the models are installed
   (see the developer guide, ``docs/Dev.rst``).

4. Push your branch and open a pull request.

Pull request guidelines
-----------------------

1. Include tests for bug fixes and new features.
2. Update the documentation in ``docs/`` when behaviour changes.
3. The tests must pass on Python 3.9 to 3.13 on Linux, macOS and Windows;
   GitHub Actions runs them for every pull request.
4. Tokenization must stay identical to ICU's (see ``docs/Dev.rst``); the
   NER and POS models depend on it.
