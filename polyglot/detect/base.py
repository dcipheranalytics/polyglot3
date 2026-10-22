#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Detecting languages with fastText's lid.176 model (via fasttext-langdetect).

The model (~126MB) is downloaded on first use and cached in $FTLANG_CACHE,
or the system temp directory if that is unset.
"""


import logging

from ftlangdetect import detect as fasttext_detect

from polyglot.detect.langids import isoLangs

logger = logging.getLogger(__name__)

# Languages known to fastText's lid.176 model.
FASTTEXT_LANGUAGES = (
  "af als am an ar arz as ast av az azb ba bar bcl be bg bh bn bo bpy br bs "
  "bxr ca cbk ce ceb ckb co cs cv cy da de diq dsb dty dv el eml en eo es et "
  "eu fa fi fr frr fy ga gd gl gn gom gu gv he hi hif hr hsb ht hu hy ia id ie "
  "ilo io is it ja jbo jv ka kk km kn ko krc ku kv kw ky la lb lez li lmo lo "
  "lrc lt lv mai mg mhr min mk ml mn mr mrj ms mt mwl my myv mzn nah nap nds "
  "ne new nl nn no oc or os pa pam pfl pl pms pnb ps pt qu rm ro ru rue sa sah "
  "sc scn sco sd sh si sk sl so sq sr su sv sw ta te tg th tk tl tr tt tyv ug "
  "uk ur uz vec vep vi vls vo wa war wuu xal xmf yi yo yue zh").split()

# A top prediction below this probability is reported as unreliable.
RELIABILITY_THRESHOLD = 0.5


class Error(Exception):
  """Base exception class for this class."""


class UnknownLanguage(Error):
  """Raised if we can not detect the language of a text snippet."""


def canonical_code(code):
  """Normalize a language tag like ICU's Locale.getName(): "zh-hant" -> "zh_Hant"."""
  parts = code.replace("-", "_").split("_")
  out = [parts[0].lower()]
  for part in parts[1:]:
    out.append(part.title() if len(part) == 4 else part.upper())
  return "_".join(out)


class Language(object):
  def __init__(self, choice):
    basic_name, code, confidence, bytesize = choice
    self._code = canonical_code(code)
    self.confidence = float(confidence)
    self.read_bytes = int(bytesize)

  @property
  def name(self):
    lang = self._code.split("_")[0]
    return isoLangs.get(lang, {}).get("name", lang)

  @property
  def code(self):
    return self._code

  def __str__(self):
    return ("name: {:<12}code: {:<9}confidence: {:>5.1f} "
            "read bytes:{:>6}".format(self.name, self.code,
                                    self.confidence, self.read_bytes))

  @staticmethod
  def from_code(code):
    return Language(("", code, 100, 0))


class Detector(object):
  """ Detect the language used in a snippet of text.
  """

  def __init__(self, text, quiet=False):
    """ Detector of the language used in `text`.

    Args:
      text (string): unicode string.
    """
    self.__text = text
    self.reliable = True
    """False if the detector used Best Effort strategy in detection."""
    self.quiet = quiet
    """If true, exceptions will be silenced."""
    self.detect(text)

  @staticmethod
  def supported_languages():
    """Returns a list of the languages that can be detected by fastText's lid.176 model."""
    return [Language.from_code(code).name for code in FASTTEXT_LANGUAGES]

  def detect(self, text):
    """Decide which language is used to write the text.

    The top three fastText predictions are kept. If the best one has a
    probability below RELIABILITY_THRESHOLD, the detection is flagged as
    unreliable.

    Args:
      text (string): A snippet of text, the longer it is the more reliable we
                     can detect the language used to write the text.
    """
    read_bytes = len(text.encode("utf-8"))
    if not text.strip():
      self.reliable = False
      if not self.quiet:
        raise UnknownLanguage("Try passing a longer snippet of text")
      self.languages = [Language(("", "un", 0.0, read_bytes))]
    else:
      predictions = fasttext_detect(text, k=3)
      self.languages = [Language(("", p["lang"], 100 * p["score"], read_bytes))
                        for p in predictions]
      if predictions[0]["score"] < RELIABILITY_THRESHOLD:
        self.reliable = False
        if not self.quiet:
          logger.warning("Detector is not able to detect the language reliably.")

    self.language = self.languages[0]
    return self.language

  def __str__(self):
    text = "Prediction is reliable: {}\n".format(self.reliable)
    text += u"\n".join(["Language {}: {}".format(i+1, str(l))
                        for i,l in enumerate(self.languages)])
    return text
