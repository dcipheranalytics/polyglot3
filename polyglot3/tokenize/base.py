#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Basic text segmenters."""

from polyglot3.base import Sequence
from polyglot3.tokenize.breakiter import sentence_boundaries, word_boundaries


class Breaker(object):
    """Base class to segment text."""

    def __init__(self, locale):
        # Segmentation follows ICU's root-locale rules for every language.
        self.locale = locale
        self.boundaries = None

    def transform(self, sequence):
        seq = Sequence(sequence.text)
        seq.idx = [0]
        for segment in sequence:
            offset = seq.idx[-1]
            seq.idx.extend([offset + x for x in self.boundaries(segment)[1:]])
        return seq


class SentenceTokenizer(Breaker):
    """Segment text to sentences."""

    def __init__(self, locale="en"):
        super(SentenceTokenizer, self).__init__(locale)
        self.boundaries = sentence_boundaries


class WordTokenizer(Breaker):
    """Segment text to words or tokens."""

    def __init__(self, locale="en"):
        super(WordTokenizer, self).__init__(locale)
        self.boundaries = word_boundaries
