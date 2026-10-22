#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""fastText's lid.176 language identification model, run with NumPy.

Reads fastText's binary model format and reproduces fastText's predictions
for supervised models that use hierarchical softmax and are not quantized,
which is what lid.176.bin is.

The model (~126MB) is downloaded on first use and cached in $FTLANG_CACHE,
or in the fasttext-langdetect directory of the system temp directory if that
is unset (the same place fasttext-langdetect keeps it).
"""

import logging
import os
import re
import struct
import tempfile
from pathlib import Path
from urllib.request import urlopen

import numpy as np

from polyglot3.decorators import memoize

logger = logging.getLogger(__name__)

MODEL_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"

FASTTEXT_MAGIC = 793712314
FASTTEXT_VERSION = 12
LOSS_HS = 1
EOS = b"</s>"
LABEL_PREFIX = "__label__"
LABEL_PREFIX_BYTES = LABEL_PREFIX.encode("ascii")

# fasttext-langdetect collapses whitespace before predicting.
WHITESPACE_RE = re.compile(r"\s+")
# Bytes fastText splits words on (Dictionary::readWord).
FASTTEXT_SPACE_RE = re.compile(rb"[ \n\r\t\v\f\0]+")


def cache_dir():
    override = os.environ.get("FTLANG_CACHE")
    if override:
        return Path(override).expanduser()
    return Path(tempfile.gettempdir()) / "fasttext-langdetect"


def download_model():
    """Return the path of lid.176.bin, downloading it if it is not cached."""
    target = cache_dir() / "lid.176.bin"
    if target.exists():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading fastText model from %s", MODEL_URL)
    # Download to a temporary file so that an interrupted download leaves no
    # partial model behind.
    part = target.with_suffix(".bin.part")
    try:
        with urlopen(MODEL_URL, timeout=60) as response, part.open("wb") as fp:
            while True:
                chunk = response.read(1 << 20)
                if not chunk:
                    break
                fp.write(chunk)
        part.replace(target)
    except BaseException:
        if part.exists():
            part.unlink()
        raise
    return target


def fasttext_hash(data):
    """fastText's FNV-1a hash, which sign-extends each byte (Dictionary::hash)."""
    h = 2166136261
    for b in data:
        h ^= b if b < 0x80 else b | 0xFFFFFF00
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def char_ngrams(word, minn, maxn):
    """Character n-grams of `word` (UTF-8 bytes), as Dictionary::computeSubwords."""
    size = len(word)
    for i in range(size):
        if word[i] & 0xC0 == 0x80:
            continue
        j = i
        n = 1
        while j < size and n <= maxn:
            j += 1
            while j < size and word[j] & 0xC0 == 0x80:
                j += 1
            if n >= minn and not (n == 1 and (i == 0 or j == size)):
                yield word[i:j]
            n += 1


class FastTextModel(object):
    """A supervised fastText model with hierarchical softmax loss."""

    def __init__(self, path):
        data = Path(path).read_bytes()
        try:
            self._load(data)
        except (struct.error, ValueError) as e:
            raise ValueError("{} is not a valid fastText model: {}".format(path, e))

    def _load(self, data):
        magic, version = struct.unpack_from("<ii", data, 0)
        if magic != FASTTEXT_MAGIC or version != FASTTEXT_VERSION:
            raise ValueError("unsupported file format")
        args = struct.unpack_from("<12id", data, 8)
        dim, _, _, _, _, word_ngrams, loss, _, self.bucket = args[:9]
        self.minn, self.maxn = args[9:11]
        if loss != LOSS_HS or word_ngrams != 1:
            raise ValueError(
                "only hierarchical softmax models without word n-grams are supported"
            )

        pos = 64
        size, nwords, nlabels, _, pruneidx_size = struct.unpack_from(
            "<iiiqq", data, pos
        )
        pos += 28
        self.word_ids = {}
        self.labels = []
        counts = []
        for i in range(size):
            end = data.index(b"\0", pos)
            entry = data[pos:end]
            count, entry_type = struct.unpack_from("<qb", data, end + 1)
            pos = end + 10
            if entry_type == 0:
                self.word_ids[entry] = i
            else:
                self.labels.append(entry.decode("utf-8")[len(LABEL_PREFIX) :])
                counts.append(count)
        self.nwords = nwords
        pos += 8 * max(pruneidx_size, 0)

        self.input, pos = self._read_matrix(data, pos)
        self.output, pos = self._read_matrix(data, pos)
        if self.input.shape[1] != dim or len(self.labels) != nlabels:
            raise ValueError("inconsistent dimensions")
        self._build_tree(counts)

    @staticmethod
    def _read_matrix(data, pos):
        if data[pos]:
            raise ValueError("quantized models are not supported")
        m, n = struct.unpack_from("<qq", data, pos + 1)
        pos += 17
        matrix = np.frombuffer(data, dtype="<f4", count=m * n, offset=pos)
        return matrix.reshape(m, n), pos + 4 * m * n

    def _build_tree(self, counts):
        """Builds the Huffman tree of the labels (HierarchicalSoftmaxLoss::buildTree).

        Stores, for each label, which internal nodes are on its path from the
        root and whether the path goes left or right at each of them.
        """
        osz = len(counts)
        count = list(counts) + [1e15] * (osz - 1)
        parent = [-1] * (2 * osz - 1)
        right = [False] * (2 * osz - 1)
        leaf, node = osz - 1, osz
        for i in range(osz, 2 * osz - 1):
            mini = []
            for _ in range(2):
                if leaf >= 0 and count[leaf] < count[node]:
                    mini.append(leaf)
                    leaf -= 1
                else:
                    mini.append(node)
                    node += 1
            count[i] = count[mini[0]] + count[mini[1]]
            parent[mini[0]] = parent[mini[1]] = i
            right[mini[1]] = True

        self.goes_left = np.zeros((osz, osz - 1), dtype=np.float32)
        self.goes_right = np.zeros((osz, osz - 1), dtype=np.float32)
        for label in range(osz):
            node = label
            while parent[node] != -1:
                path = self.goes_right if right[node] else self.goes_left
                path[label, parent[node] - osz] = 1
                node = parent[node]

    def subword_ids(self, word):
        """Input rows of a word: its own row if known, and its character n-grams."""
        ids = []
        wid = self.word_ids.get(word, -1)
        if wid >= 0:
            ids.append(wid)
        if word != EOS:
            for ngram in char_ngrams(b"<" + word + b">", self.minn, self.maxn):
                ids.append(self.nwords + fasttext_hash(ngram) % self.bucket)
        return ids

    def line_ids(self, line):
        """Input rows of a line of text (Dictionary::getLine)."""
        words = FASTTEXT_SPACE_RE.split(line.encode("utf-8")) + [EOS]
        ids = []
        for word in words:
            # fastText reads words that look like labels as labels.
            if word and not word.startswith(LABEL_PREFIX_BYTES):
                ids.extend(self.subword_ids(word))
        return ids

    def predict(self, line, k=1, threshold=0.0):
        """Returns up to `k` (label, probability) pairs, the most probable first."""
        hidden = self.input[self.line_ids(line)].mean(axis=0, dtype=np.float32)
        f = 1.0 / (1.0 + np.exp(-(self.output[: len(self.labels) - 1] @ hidden)))
        scores = self.goes_left @ np.log(1.0 - f + 1e-5) + self.goes_right @ np.log(
            f + 1e-5
        )
        best = np.argsort(-scores, kind="stable")[:k]
        return [
            (self.labels[i], min(float(np.exp(scores[i])), 1.0))
            for i in best
            if scores[i] >= np.log(threshold + 1e-5)
        ]


@memoize
def load_model():
    return FastTextModel(download_model())


def detect(text, k=1):
    """Detect the language of `text` with lid.176, like fasttext-langdetect.

    Returns a list of up to `k` {"lang": code, "score": probability} dicts,
    the most probable first.
    """
    line = WHITESPACE_RE.sub(" ", text).strip()
    return [
        {"lang": lang, "score": score} for lang, score in load_model().predict(line, k)
    ]
