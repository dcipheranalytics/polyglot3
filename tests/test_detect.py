"""Language detection tests.

The unit tests stub out fastText. The accuracy test uses the real lid.176
model and runs only if it is already cached (see ftlangdetect's FTLANG_CACHE).
"""

import json
from pathlib import Path

import pytest

from polyglot3.detect import Detector, Language
from polyglot3.detect import base
from polyglot3.detect.base import UnknownLanguage, canonical_code


@pytest.fixture
def fake_fasttext(monkeypatch):
  def fake(predictions):
    monkeypatch.setattr(base, "fasttext_detect", lambda text, k: predictions)
  return fake


def test_top_three_predictions(fake_fasttext):
  fake_fasttext([{"lang": "he", "score": 0.9}, {"lang": "yi", "score": 0.05},
                 {"lang": "en", "score": 0.01}])
  d = Detector(u"שלום עולם")
  assert [l.code for l in d.languages] == ["he", "yi", "en"]
  assert d.language.code == "he"
  assert d.language.confidence == pytest.approx(90.0)
  assert d.language.read_bytes == len(u"שלום עולם".encode("utf-8"))
  assert d.reliable


def test_low_confidence_is_unreliable(fake_fasttext):
  fake_fasttext([{"lang": "ms", "score": 0.4}, {"lang": "id", "score": 0.35}])
  d = Detector(u"Saya suka makan nasi.", quiet=True)
  assert not d.reliable
  assert d.language.code == "ms"


def test_empty_text():
  with pytest.raises(UnknownLanguage):
    Detector(u"   ")
  d = Detector(u"   ", quiet=True)
  assert d.language.code == "un" and not d.reliable


def test_language_codes_and_names():
  assert canonical_code("zh-hant") == "zh_Hant"
  assert canonical_code("EN-us") == "en_US"
  assert Language.from_code("tr").name == "Turkish"
  assert Language.from_code("xyz").name == "xyz"
  assert "Turkish" in Detector.supported_languages()


def model_cached():
  from ftlangdetect.detect import _default_cache_dir
  return (_default_cache_dir() / "lid.176.bin").exists()


@pytest.mark.skipif(not model_cached(), reason="fastText lid.176 model not cached")
def test_accuracy_on_corpus():
  correct = total = 0
  for path in (Path(__file__).parent / "fixtures" / "corpus").glob("*.jsonl"):
    if path.stem == "edge_cases":
      continue
    for line in path.read_text(encoding="utf-8").splitlines():
      total += 1
      correct += Detector(json.loads(line)["text"], quiet=True).language.code == path.stem
  assert correct / total >= 0.95
