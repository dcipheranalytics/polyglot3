#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Collection of general utilities."""

from os import path
import os
import tarfile


def _open(file_, mode='r'):
  """Open file object given filenames, open files or even archives."""
  if isinstance(file_, str):
    _, ext = path.splitext(file_)
    if ext in {'.bz2', '.gz'}:
      s = tarfile.open(file_)
      return s.extractfile(s.next())
    else:
      return open(file_, mode)
  return file_


def _print(text):
  print(text)

def pretty_list(items, cols=3):
  text = []
  width = 24
  col_width = u"{" + u":<" + str(width) + u"} "
  for i, lang in enumerate(items):
    if len(lang) > width:
      lang = lang[:width-3] + "..."
    text.append(u"{:>3}. ".format(i+1))
    text.append(col_width.format(lang))
    if (i+1) % cols  == 0:
      text.append(u"\n")
  return u"".join(text)

def _decode(s, encoding="utf-8"):
  if type(s) == str:
    return s.encode("utf-8").decode(encoding)
  else:
    return s.decode(encoding)
