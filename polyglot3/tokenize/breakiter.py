#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Pure-Python port of ICU's rule-based word and sentence break iterators.

Reproduces ICU 78's root-locale BreakIterator: the state tables in _tables.py
are compiled from ICU's word.txt/sent.txt by tools/icu_port/build_tables.py,
and Thai text is subdivided with a port of ICU's ThaiBreakEngine (dictbe.cpp)
using ICU's Thai dictionary. Other dictionary scripts (Lao, Khmer, Burmese,
Chinese, Japanese, Korean) behave as ICU does without a dictionary for them:
their runs are not subdivided.

Copyright (C) 2016 and later: Unicode, Inc. and others.
License & terms of use: see data/LICENSE-ICU (Unicode License V3)
"""

import gzip
import os
import threading
from bisect import bisect_left, bisect_right

from . import _tables

STOP_STATE = 0
START_STATE = 1
EOF_CATEGORY = 1
BOF_CATEGORY = 2


class _RangeSet(object):
    def __init__(self, ranges):
        self.starts = [lo for lo, _ in ranges]
        self.ends = [hi for _, hi in ranges]

    def __contains__(self, ch):
        cp = ord(ch)
        k = bisect_right(self.starts, cp) - 1
        return k >= 0 and cp <= self.ends[k]


class _RuleTable(object):
    """A compiled break rule set and ICU's handleNext() state machine."""

    def __init__(self, table):
        self.starts = table["starts"]
        self.cats = table["cats"]
        self.dict = table["dict"]
        self.trans = table["trans"]
        self.accepting = table["accepting"]
        self.bof_required = table["bof_required"]
        self._cache = {}

    def category(self, ch):
        cat = self._cache.get(ch)
        if cat is None:
            cat = self.cats[bisect_right(self.starts, ord(ch)) - 1]
            self._cache[ch] = cat
        return cat

    def handle_next(self, text, pos):
        """Return (next boundary after `pos`, number of dictionary chars seen)."""
        n = len(text)
        result = pos
        dict_count = 0
        state = START_STATE
        i = pos
        if self.bof_required:
            start_mode, end_mode = True, False
            category = BOF_CATEGORY
        else:
            start_mode, end_mode = False, False
        while True:
            if i >= n:
                if end_mode:
                    break
                end_mode = True
                category = EOF_CATEGORY
            elif not start_mode:
                category = self.category(text[i])
                dict_count += self.dict[category]

            state = self.trans[state][category]
            if self.accepting[state] and not start_mode:
                result = n if end_mode else i + 1
            if state == STOP_STATE:
                break
            if start_mode:
                start_mode = False
            elif not end_mode:
                i += 1

        if result == pos:
            result = pos + 1
        return result, dict_count


class _UText(object):
    """The subset of ICU's UText iteration used by the Thai engine (code points)."""

    def __init__(self, text):
        self.text = text
        self.pos = 0

    def current32(self):
        return self.text[self.pos] if self.pos < len(self.text) else None

    def next32(self):
        if self.pos >= len(self.text):
            return None
        self.pos += 1
        return self.text[self.pos - 1]

    def previous32(self):
        if self.pos <= 0:
            return None
        self.pos -= 1
        return self.text[self.pos]


class _ThaiDictionary(object):
    """ICU's thaidict word list with UCharsDictionaryMatcher::matches() semantics."""

    def __init__(self, words):
        self.words = sorted(words)

    def matches(self, text, start, max_length, limit):
        """Return (word lengths, code points consumed) for words prefixing text[start:]."""
        words = self.words
        lengths = []
        matched = 0
        for k in range(start, len(text)):
            prefix = text[start : k + 1]
            matched += 1
            i = bisect_left(words, prefix)
            if i == len(words) or not words[i].startswith(prefix):
                break  # USTRINGTRIE_NO_MATCH
            if words[i] == prefix:
                if len(lengths) < limit:
                    lengths.append(matched)
                if i + 1 == len(words) or not words[i + 1].startswith(prefix):
                    break  # USTRINGTRIE_FINAL_VALUE
            if matched >= max_length:
                break
        return lengths, matched


POSSIBLE_WORD_LIST_MAX = 20


class _PossibleWord(object):
    def __init__(self):
        self.count = 0
        self.prefix = 0
        self.offset = -1
        self.mark = 0
        self.current = 0
        self.lengths = []

    def candidates(self, ut, dictionary, range_end):
        start = ut.pos
        if start != self.offset:
            self.offset = start
            self.lengths, self.prefix = dictionary.matches(
                ut.text, start, range_end - start, POSSIBLE_WORD_LIST_MAX
            )
            self.count = len(self.lengths)
            if self.count <= 0:
                ut.pos = start
        if self.count > 0:
            ut.pos = start + self.lengths[self.count - 1]
        self.current = self.count - 1
        self.mark = self.current
        return self.count

    def accept_marked(self, ut):
        ut.pos = self.offset + self.lengths[self.mark]
        return self.lengths[self.mark]

    def back_up(self, ut):
        if self.current > 0:
            self.current -= 1
            ut.pos = self.offset + self.lengths[self.current]
            return True
        return False

    def mark_current(self):
        self.mark = self.current

    def marked_length(self):
        return self.lengths[self.mark]


THAI_LOOKAHEAD = 3
THAI_ROOT_COMBINE_THRESHOLD = 3
THAI_PREFIX_COMBINE_THRESHOLD = 3
THAI_PAIYANNOI = "ฯ"
THAI_MAIYAMOK = "ๆ"
THAI_MIN_WORD = 2
THAI_MIN_WORD_SPAN = THAI_MIN_WORD * 2


class _ThaiBreakEngine(object):
    """Port of ICU's ThaiBreakEngine::divideUpDictionaryRange()."""

    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.word_set = _RangeSet(_tables.THAI_WORD)
        self.mark_set = _RangeSet(_tables.THAI_MARKS)
        self.begin_word = _RangeSet([(0x0E01, 0x0E2E), (0x0E40, 0x0E44)])
        self.suffix_set = {THAI_PAIYANNOI, THAI_MAIYAMOK}

    def in_end_word_set(self, ch):
        # fEndWordSet: the Thai word set minus MAI HAN-AKAT and SARA E..SARA AI MAIMALAI.
        return ch in self.word_set and ch != "ั" and not "เ" <= ch <= "ไ"

    def divide(self, text, range_start, range_end, found_breaks):
        """Append breaks inside [range_start, range_end) to found_breaks; return the word count."""
        if min(range_start + THAI_MIN_WORD_SPAN, len(text)) >= range_end:
            return 0  # Not enough characters for two words

        d = self.dictionary
        ut = _UText(text)
        ut.pos = range_start
        words_found = 0
        words = [_PossibleWord() for _ in range(THAI_LOOKAHEAD)]

        while ut.pos < range_end:
            current = ut.pos
            word_length = 0

            # Look for candidate words at the current position
            candidates = words[words_found % THAI_LOOKAHEAD].candidates(
                ut, d, range_end
            )

            if candidates == 1:
                word_length = words[words_found % THAI_LOOKAHEAD].accept_marked(ut)
                words_found += 1
            elif candidates > 1:
                # See which candidate can take us forward the most words.
                if ut.pos < range_end:
                    found_best = False
                    while True:
                        if (
                            words[(words_found + 1) % THAI_LOOKAHEAD].candidates(
                                ut, d, range_end
                            )
                            > 0
                        ):
                            # Followed by another dictionary word; mark first word as a good candidate
                            words[words_found % THAI_LOOKAHEAD].mark_current()
                            if ut.pos >= range_end:
                                break
                            # See if any of the possible second words is followed by a third word
                            while True:
                                if words[(words_found + 2) % THAI_LOOKAHEAD].candidates(
                                    ut, d, range_end
                                ):
                                    words[words_found % THAI_LOOKAHEAD].mark_current()
                                    found_best = True
                                    break
                                if not words[
                                    (words_found + 1) % THAI_LOOKAHEAD
                                ].back_up(ut):
                                    break
                            if found_best:
                                break
                        if not words[words_found % THAI_LOOKAHEAD].back_up(ut):
                            break
                word_length = words[words_found % THAI_LOOKAHEAD].accept_marked(ut)
                words_found += 1

            # If the next text is not a dictionary word, combine it with the word we
            # just found (if there is one), unless that word exceeds the threshold.
            uc = None
            if ut.pos < range_end and word_length < THAI_ROOT_COMBINE_THRESHOLD:
                if words[words_found % THAI_LOOKAHEAD].candidates(
                    ut, d, range_end
                ) <= 0 and (
                    word_length == 0
                    or words[words_found % THAI_LOOKAHEAD].prefix
                    < THAI_PREFIX_COMBINE_THRESHOLD
                ):
                    # Look for a plausible word boundary
                    remaining = range_end - (current + word_length)
                    chars = 0
                    while True:
                        pc = ut.next32()
                        chars += 1
                        remaining -= 1
                        if remaining <= 0:
                            break
                        uc = ut.current32()
                        if self.in_end_word_set(pc) and uc in self.begin_word:
                            # Maybe. See if it's in the dictionary.
                            num_candidates = words[
                                (words_found + 1) % THAI_LOOKAHEAD
                            ].candidates(ut, d, range_end)
                            ut.pos = current + word_length + chars
                            if num_candidates > 0:
                                break
                    # Bump the word count if there wasn't already one
                    if word_length <= 0:
                        words_found += 1
                    # Update the length with the passed-over characters
                    word_length += chars
                else:
                    # Back up to where we were for next iteration
                    ut.pos = current + word_length

            # Never stop before a combining mark.
            while ut.pos < range_end and ut.current32() in self.mark_set:
                ut.next32()
                word_length += 1

            # Look ahead for possible suffixes if a dictionary word does not follow.
            if ut.pos < range_end and word_length > 0:
                if (
                    words[words_found % THAI_LOOKAHEAD].candidates(ut, d, range_end)
                    <= 0
                    and ut.current32() in self.suffix_set
                ):
                    uc = ut.current32()
                    if uc == THAI_PAIYANNOI:
                        if ut.previous32() not in self.suffix_set:
                            # Skip over previous end and PAIYANNOI
                            ut.next32()
                            ut.next32()
                            word_length += 1  # Add PAIYANNOI to word
                            uc = ut.current32()  # Fetch next character
                        else:
                            # Restore prior position
                            ut.next32()
                    if uc == THAI_MAIYAMOK:
                        if ut.previous32() != THAI_MAIYAMOK:
                            # Skip over previous end and MAIYAMOK
                            ut.next32()
                            ut.next32()
                            word_length += 1  # Add MAIYAMOK to word
                        else:
                            # Restore prior position
                            ut.next32()
                else:
                    ut.pos = current + word_length

            # Did we find a word on this iteration? If so, push it on the break stack
            if word_length > 0:
                found_breaks.append(current + word_length)

        # Don't return a break for the end of the dictionary range if there is one there.
        if found_breaks and found_breaks[-1] >= range_end:
            found_breaks.pop()
            words_found -= 1
        return words_found


_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
_thai_engine = None
_thai_engine_lock = threading.Lock()


def _get_thai_engine():
    global _thai_engine
    if _thai_engine is None:
        with _thai_engine_lock:
            if _thai_engine is None:
                words = []
                with gzip.open(
                    os.path.join(_DATA_DIR, "thaidict.txt.gz"),
                    "rt",
                    encoding="utf-8-sig",
                ) as fh:
                    for line in fh:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            words.append(line.split()[0])
                _thai_engine = _ThaiBreakEngine(_ThaiDictionary(words))
    return _thai_engine


class _BreakIterator(object):
    """Forward iteration as in ICU's BreakCache/DictionaryCache."""

    def __init__(self, rules, use_dictionary):
        self.rules = rules
        self.use_dictionary = use_dictionary

    def _dictionary_breaks(self, text, start, end):
        """DictionaryCache::populateDictionary: breaks for [start, end] or None."""
        engine = _get_thai_engine()
        breaks = []
        found = 0
        i = start
        while i < end:
            if text[i] not in engine.word_set:
                i += 1
                continue
            j = i
            while j < end and text[j] in engine.word_set:
                j += 1
            found += engine.divide(text, i, j, breaks)
            i = j
        if found <= 0:
            return None
        if start < breaks[0]:
            breaks.insert(0, start)
        if end > breaks[-1]:
            breaks.append(end)
        return breaks

    def boundaries(self, text):
        """All boundary positions in `text`, including 0 and len(text)."""
        result = [0]
        pos = 0
        n = len(text)
        cache = None  # dictionary breaks covering [cache[0], cache[-1]]
        while pos < n:
            if cache is not None and cache[0] <= pos < cache[-1]:
                pos = cache[bisect_right(cache, pos)]
                result.append(pos)
                continue
            end, dict_count = self.rules.handle_next(text, pos)
            if self.use_dictionary and dict_count > 0 and end - pos > 1:
                cache = self._dictionary_breaks(text, pos, end)
                if cache is not None:
                    pos = cache[bisect_right(cache, pos)]
                    result.append(pos)
                    continue
            pos = end
            result.append(pos)
        return result


_word_iterator = _BreakIterator(_RuleTable(_tables.WORD), use_dictionary=True)
_sentence_iterator = _BreakIterator(_RuleTable(_tables.SENTENCE), use_dictionary=False)


def word_boundaries(text):
    """Word boundaries of `text` as ICU's root-locale word BreakIterator finds them."""
    return _word_iterator.boundaries(text)


def sentence_boundaries(text):
    """Sentence boundaries of `text` as ICU's root-locale sentence BreakIterator finds them."""
    return _sentence_iterator.boundaries(text)
