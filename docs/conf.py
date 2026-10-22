"""Sphinx configuration for polyglot3."""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

import polyglot  # noqa: E402

project = "polyglot3"
author = "Rami Al-Rfou and the Dcipher Analytics dev team"
copyright = "2014-2016, Rami Al-Rfou; 2026, Dcipher Analytics"
version = release = polyglot.__version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
# Avoid downloading the fastText model while importing modules for autodoc.
autodoc_mock_imports = ["ftlangdetect"]
autodoc_default_options = {"members": True, "undoc-members": True,
                           "show-inheritance": True}

master_doc = "index"
exclude_patterns = ["_build", "index_latex.rst"]
html_theme = "sphinx_rtd_theme"

latex_documents = [
    ("index_latex", "polyglot3.tex", "polyglot3 Documentation", author, "manual"),
]
