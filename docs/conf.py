"""Sphinx configuration for polyglot3."""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

import polyglot3  # noqa: E402

project = "polyglot3"
author = "Dcipher Analytics AB"
copyright = "2026, Dcipher Analytics AB; 2014-2016, Rami Al-Rfou (polyglot)"
version = release = polyglot3.__version__

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
source_suffix = {".md": "markdown"}
# Anchors for in-page links such as [Supported languages](#supported-languages).
myst_heading_anchors = 3

# Avoid downloading the fastText model while importing modules for autodoc.
autodoc_mock_imports = ["ftlangdetect"]
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

master_doc = "index"
# README.md is included in index.md rather than built on its own.
exclude_patterns = ["_build", "README.md"]
html_theme = "sphinx_rtd_theme"
