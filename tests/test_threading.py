"""Concurrency tests: shared lazy state is initialised once and results match
a sequential run."""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

from polyglot3.decorators import memoize
from polyglot3.tokenize import breakiter
from polyglot3.tokenize.breakiter import word_boundaries


def test_memoize_computes_once_per_key_under_contention():
    calls = []
    start = threading.Barrier(16)

    @memoize
    def load(lang):
        calls.append(lang)
        time.sleep(0.05)
        return object()

    def work(i):
        start.wait()
        return load("tr" if i % 2 else "cs")

    with ThreadPoolExecutor(16) as pool:
        results = list(pool.map(work, range(16)))

    assert sorted(calls) == ["cs", "tr"]
    assert len({id(r) for r in results}) == 2


def test_memoize_nested_calls_do_not_deadlock():
    @memoize
    def inner(lang):
        return lang.upper()

    @memoize
    def outer(lang):
        return inner(lang) + inner(lang + "x")

    with ThreadPoolExecutor(8) as pool:
        assert list(pool.map(outer, ["a", "b"] * 8)) == ["AAX", "BBX"] * 8


def test_thai_segmentation_is_thread_safe(monkeypatch):
    monkeypatch.setattr(breakiter, "_thai_engine", None)
    texts = [
        "ภาษาไทยเป็นภาษาที่สวยงาม",
        "กรุงเทพมหานครเป็นเมืองหลวง",
        "Hello world. ทดสอบระบบตัดคำ",
    ] * 20
    expected = [list(word_boundaries(t)) for t in texts]
    monkeypatch.setattr(breakiter, "_thai_engine", None)
    loads = []
    real = breakiter._ThaiDictionary

    def counting(words):
        loads.append(1)
        return real(words)

    monkeypatch.setattr(breakiter, "_ThaiDictionary", counting)

    with ThreadPoolExecutor(16) as pool:
        got = list(pool.map(lambda t: list(word_boundaries(t)), texts))

    assert got == expected
    assert len(loads) == 1
