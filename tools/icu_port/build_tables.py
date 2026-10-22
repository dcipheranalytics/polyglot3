#!/usr/bin/env python
"""Compile ICU break rules into the state tables used by polyglot.tokenize.

This is a Python port of the parts of ICU's rule-based break iterator
builder (rbbiscan/rbbisetb/rbbitblb) needed for ICU's root word.txt and
sent.txt: rule parsing, character categories, the Aho position automaton,
rule chaining (!!chain, ^) and {bof}/{eof}. Look-ahead rules ('/') are not
supported since those files do not use them.

Inputs (pinned to ICU 78.3 / Unicode 17.0, matching the reference fixtures):
  tools/icu_port/rules/{word,sent}.txt   ICU rule files
  Unicode Character Database files, downloaded into a cache directory.

Usage: python tools/icu_port/build_tables.py UCD_CACHE_DIR polyglot/tokenize/_tables.py
"""

import os
import re
import sys
import urllib.request
from bisect import bisect_right
from pathlib import Path

HERE = Path(__file__).resolve().parent
UCD_URL = "https://www.unicode.org/Public/17.0.0/ucd/"
UCD_FILES = {
    "Word_Break": "auxiliary/WordBreakProperty.txt",
    "Sentence_Break": "auxiliary/SentenceBreakProperty.txt",
    "Grapheme_Cluster_Break": "auxiliary/GraphemeBreakProperty.txt",
    "Line_Break": "LineBreak.txt",
    "Script": "Scripts.txt",
    "General_Category": "extracted/DerivedGeneralCategory.txt",
    "PropList": "PropList.txt",
    "Emoji": "emoji/emoji-data.txt",
}
MAX_CP = 0x10FFFF

# Category numbers reserved by ICU.
EOF_CAT = 1
BOF_CAT = 2


# ---------------------------------------------------------------------------
# Code point sets as sorted lists of disjoint inclusive ranges.

class CPSet(object):
  def __init__(self, ranges=(), strings=()):
    self.ranges = _normalize(ranges)
    self.strings = frozenset(strings)  # only "bof" / "eof"

  def union(self, other):
    return CPSet(self.ranges + other.ranges, self.strings | other.strings)

  def complement(self):
    out, prev = [], 0
    for lo, hi in self.ranges:
      if lo > prev:
        out.append((prev, lo - 1))
      prev = hi + 1
    if prev <= MAX_CP:
      out.append((prev, MAX_CP))
    return CPSet(out)

  def difference(self, other):
    return CPSet(self.intersection(other.complement()).ranges,
                 self.strings - other.strings)

  def intersection(self, other):
    out, i, j = [], 0, 0
    a, b = self.ranges, other.ranges
    while i < len(a) and j < len(b):
      lo, hi = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
      if lo <= hi:
        out.append((lo, hi))
      if a[i][1] < b[j][1]:
        i += 1
      else:
        j += 1
    return CPSet(out, self.strings & other.strings)

  def contains(self, cp):
    k = bisect_right(self.ranges, (cp, MAX_CP + 1)) - 1
    return k >= 0 and self.ranges[k][0] <= cp <= self.ranges[k][1]


def _normalize(ranges):
  out = []
  for lo, hi in sorted(ranges):
    if out and lo <= out[-1][1] + 1:
      out[-1] = (out[-1][0], max(out[-1][1], hi))
    else:
      out.append((lo, hi))
  return out


# ---------------------------------------------------------------------------
# Unicode properties

class UCD(object):
  def __init__(self, cache_dir):
    self.cache_dir = Path(cache_dir)
    self.cache_dir.mkdir(parents=True, exist_ok=True)
    self._props = {}

  def _load(self, name):
    if name in self._props:
      return self._props[name]
    path = self.cache_dir / os.path.basename(UCD_FILES[name])
    if not path.exists():
      urllib.request.urlretrieve(UCD_URL + UCD_FILES[name], path)
    values = {}
    with open(path, encoding="utf-8") as fh:
      for line in fh:
        line = line.split("#", 1)[0].strip()
        if not line:
          continue
        fields = [f.strip() for f in line.split(";")]
        cps = fields[0].split("..")
        lo = int(cps[0], 16)
        hi = int(cps[-1], 16)
        values.setdefault(fields[1], []).append((lo, hi))
    self._props[name] = {k: CPSet(v) for k, v in values.items()}
    return self._props[name]

  def lookup(self, prop, value=None):
    """Resolve \\p{prop=value} / [:prop:] as used in the ICU rule files."""
    prop = prop.replace(" ", "")
    if value is not None:
      value = value.replace(" ", "")
    if value is None:
      if prop == "Extended_Pictographic":
        return self._load("Emoji")[prop]
      if prop == "Ideographic":
        return self._load("PropList")[prop]
      if prop in ("M", "Mark"):
        gc = self._load("General_Category")
        return gc["Mn"].union(gc["Mc"]).union(gc["Me"])
      scripts = self._load("Script")
      if prop in scripts:
        return scripts[prop]
      raise ValueError("unknown property " + prop)
    if prop in ("LineBreak", "Line_Break"):
      value = {"Complex_Context": "SA"}.get(value, value)
      return self._load("Line_Break")[value]
    return self._load(prop)[value]


# ---------------------------------------------------------------------------
# Rule parsing

class SetParser(object):
  """Parses the UnicodeSet pattern subset used by ICU's break rules."""

  def __init__(self, ucd, variables):
    self.ucd = ucd
    self.variables = variables

  def parse(self, s, i):
    assert s[i] == "["
    if s.startswith("[:", i):
      j = s.index(":]", i)
      body = s[i + 2:j]
      prop, _, value = body.partition("=")
      return self.ucd.lookup(prop.strip(), value.strip() or None), j + 2
    i += 1
    negate = s[i] == "^"
    if negate:
      i += 1
    acc = None
    op = None
    while True:
      i = _skip_ws(s, i)
      c = s[i]
      if c == "]":
        i += 1
        break
      if c in "-&" and acc is not None:
        op = c
        i += 1
        continue
      if c == "[":
        term, i = self.parse(s, i)
      elif c == "$":
        name, i = _name(s, i)
        term = self.variables[name].value
        assert isinstance(term, CPSet), name
      elif s.startswith("\\p{", i):
        j = s.index("}", i)
        prop, _, value = s[i + 3:j].partition("=")
        term = self.ucd.lookup(prop.strip(), value.strip() or None)
        i = j + 1
      elif s.startswith("\\u", i):
        lo = int(s[i + 2:i + 6], 16)
        i += 6
        hi = lo
        k = _skip_ws(s, i)
        if s[k] == "-" and s.startswith("\\u", _skip_ws(s, k + 1)):
          k = _skip_ws(s, k + 1)
          hi = int(s[k + 2:k + 6], 16)
          i = k + 6
        term = CPSet([(lo, hi)])
      elif c == "{":
        j = s.index("}", i)
        term = CPSet(strings=[s[i + 1:j]])
        i = j + 1
      else:
        raise ValueError("unexpected {!r} in set at {}".format(c, s[i:i + 20]))
      if acc is None:
        acc = term
      elif op == "-":
        acc = acc.difference(term)
      elif op == "&":
        acc = acc.intersection(term)
      else:
        acc = acc.union(term)
      op = None
    if negate:
      acc = CPSet(acc.complement().ranges)
    return acc, i


def _skip_ws(s, i):
  while i < len(s) and s[i].isspace():
    i += 1
  return i


def _name(s, i):
  m = re.compile(r"\$\w+").match(s, i)
  return m.group(0)[1:], m.end()


class Var(object):
  def __init__(self, name, value):
    self.name = name
    self.value = value  # CPSet or expression tuple


def parse_rules(text, ucd):
  """Return (variables, rules, chain) where each rule is (expr, chain_in)."""
  text = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
  variables = {}
  sets = []  # every set expression, for character categories
  rules = []
  chain = False
  sp = SetParser(ucd, variables)

  for stmt in text.split(";"):
    stmt = stmt.strip()
    if not stmt:
      continue
    if stmt.startswith("!!"):
      chain = chain or stmt == "!!chain"
      continue
    stmt = re.sub(r"\{\d+\}", "", stmt)  # rule status tags do not affect boundaries
    m = re.match(r"\$(\w+)\s*=\s*(.*)$", stmt, re.S)
    if m:
      expr = ExprParser(m.group(2), sp, variables, sets).parse()
      value = expr[1] if expr[0] == "set" else expr
      variables[m.group(1)] = Var(m.group(1), value)
      if expr[0] == "set":
        sets.append((m.group(1), expr[1]))
      continue
    chain_in = True
    if stmt.startswith("^"):
      chain_in = False
      stmt = stmt[1:]
    assert "/" not in stmt, "look-ahead rules are not supported"
    rules.append((ExprParser(stmt, sp, variables, sets).parse(), chain_in))
  return variables, rules, sets, chain


class ExprParser(object):
  """expr := seq ('|' seq)* ; seq := postfix+ ; postfix := atom [*+?]*"""

  def __init__(self, s, set_parser, variables, sets):
    self.s, self.i = s, 0
    self.sp, self.variables, self.sets = set_parser, variables, sets

  def parse(self):
    e = self.alt()
    assert _skip_ws(self.s, self.i) == len(self.s), self.s[self.i:]
    return e

  def peek(self):
    self.i = _skip_ws(self.s, self.i)
    return self.s[self.i] if self.i < len(self.s) else ""

  def alt(self):
    e = self.seq()
    while self.peek() == "|":
      self.i += 1
      e = ("or", e, self.seq())
    return e

  def seq(self):
    e = None
    while self.peek() not in ("", "|", ")"):
      a = self.postfix()
      e = a if e is None else ("cat", e, a)
    return e

  def postfix(self):
    a = self.atom()
    while self.peek() in ("*", "+", "?"):
      a = ({"*": "star", "+": "plus", "?": "opt"}[self.peek()], a)
      self.i += 1
    return a

  def atom(self):
    c = self.peek()
    if c == "(":
      self.i += 1
      e = self.alt()
      assert self.peek() == ")"
      self.i += 1
      return e
    if c == "[":
      cps, self.i = self.sp.parse(self.s, self.i)
      self.sets.append((None, cps))
      return ("set", cps)
    if c == "$":
      name, self.i = _name(self.s, self.i)
      v = self.variables[name].value
      return ("set", v) if isinstance(v, CPSet) else v
    if c == ".":
      self.i += 1
      return ("set", CPSet([(0, MAX_CP)]))
    raise ValueError("unexpected {!r} at {!r}".format(c, self.s[self.i:]))


# ---------------------------------------------------------------------------
# Character categories (rbbisetb)

def categories(sets, dictionary):
  """Partition code points by set membership; dictionary ranges get their own
  categories. Returns (range_starts, range_cats, cats_of_set, dict_flags)."""
  bounds = {0, MAX_CP + 1}
  all_sets = [cps for _, cps in sets] + [dictionary]
  for cps in all_sets:
    for lo, hi in cps.ranges:
      bounds.add(lo)
      bounds.add(hi + 1)
  bounds = sorted(bounds)

  signature_cat = {}
  starts, cats, dict_flags = [], [], {}
  next_cat = 3
  for lo, nxt in zip(bounds, bounds[1:]):
    sig = tuple(cps.contains(lo) for cps in all_sets)
    if sig not in signature_cat:
      signature_cat[sig] = next_cat
      dict_flags[next_cat] = sig[-1]
      next_cat += 1
    cat = signature_cat[sig]
    if cats and cats[-1] == cat:
      continue
    starts.append(lo)
    cats.append(cat)
  return starts, cats, dict_flags, next_cat


def cats_in(cps, starts, cats):
  """Categories of all ranges inside `cps`, plus {bof}/{eof} pseudo-categories."""
  found = set()
  for k, lo in enumerate(starts):
    if cps.contains(lo):
      found.add(cats[k])
  if "bof" in cps.strings:
    found.add(BOF_CAT)
  if "eof" in cps.strings:
    found.add(EOF_CAT)
  return sorted(found)


# ---------------------------------------------------------------------------
# Position automaton (rbbitblb)

class Node(object):
  __slots__ = ("kind", "cat", "kids", "nullable", "first", "last", "follow",
               "rule_root", "chain_in")

  def __init__(self, kind, cat=None, kids=()):
    self.kind, self.cat, self.kids = kind, cat, list(kids)
    self.follow = set()
    self.rule_root = self.chain_in = False


def build_tree(expr, starts, cats):
  kind = expr[0]
  if kind == "set":
    leaves = [Node("leaf", c) for c in cats_in(expr[1], starts, cats)]
    assert leaves, "empty set in rule"
    node = leaves[0]
    for leaf in leaves[1:]:
      node = Node("or", kids=[node, leaf])
    return node
  return Node(kind, kids=[build_tree(k, starts, cats) for k in expr[1:]])


def walk(node):
  yield node
  for k in node.kids:
    for n in walk(k):
      yield n


def calc_positions(node):
  for k in node.kids:
    calc_positions(k)
  if node.kind in ("leaf", "end"):
    node.nullable = False
    node.first = node.last = {node}
  elif node.kind == "or":
    a, b = node.kids
    node.nullable = a.nullable or b.nullable
    node.first, node.last = a.first | b.first, a.last | b.last
  elif node.kind == "cat":
    a, b = node.kids
    node.nullable = a.nullable and b.nullable
    node.first = a.first | b.first if a.nullable else set(a.first)
    node.last = a.last | b.last if b.nullable else set(b.last)
    for i in a.last:
      i.follow |= b.first
  else:  # star, plus, opt
    (a,) = node.kids
    node.nullable = node.kind != "plus"  # ICU treats x+ as non-nullable
    node.first, node.last = set(a.first), set(a.last)
    if node.kind in ("star", "plus"):
      for i in node.last:
        i.follow |= node.first


def build_dfa(rules, starts, cats, num_cats, chain):
  roots = []
  for expr, chain_in in rules:
    r = build_tree(expr, starts, cats)
    r.rule_root, r.chain_in = True, chain and chain_in
    roots.append(r)
  tree = roots[0]
  for r in roots[1:]:
    tree = Node("or", kids=[tree, r])

  saw_bof = any(n.kind == "leaf" and n.cat == BOF_CAT for n in walk(tree))
  bof = None
  if saw_bof:
    bof = Node("leaf", BOF_CAT)
    rest = tree
    tree = Node("cat", kids=[bof, rest])
  end = Node("end")
  tree = Node("cat", kids=[tree, end])
  calc_positions(tree)

  if chain:
    starts_ = set()
    for r in roots:
      if r.chain_in:
        starts_ |= {n for n in r.first if n.kind == "leaf"}
    # ICU augments followPos sets in place, but the result does not depend on
    # the order: an end node gains the original followPos of every chain-in
    # start node with its category, and any in-place augmentation of such a
    # start node only adds followPos sets of start nodes of that same category.
    base_follow = {n: set(n.follow) for n in walk(tree)}
    for e in walk(tree):
      if e.kind == "leaf" and end in base_follow[e]:
        for s in starts_:
          if s.cat == e.cat:
            e.follow |= base_follow[s]

  if saw_bof:
    for s in rest.first:
      if s.kind == "leaf" and s.cat == BOF_CAT:
        bof.follow |= s.follow

  # Subset construction. State 0 is the stop state, state 1 the start state.
  states = [frozenset(), frozenset(tree.first)]
  index = {states[0]: 0, states[1]: 1}
  trans = [[0] * num_cats, None]
  k = 1
  while k < len(states):
    row = [0] * num_cats
    for a in range(1, num_cats):
      u = set()
      for p in states[k]:
        if p.kind == "leaf" and p.cat == a:
          u |= p.follow
      if u:
        u = frozenset(u)
        if u not in index:
          index[u] = len(states)
          states.append(u)
          trans.append(None)
        row[a] = index[u]
    trans[k] = row
    k += 1
  accepting = [end in s for s in states]
  return trans, accepting, saw_bof


def compile_rules(path, ucd):
  variables, rules, sets, chain = parse_rules(Path(path).read_text(encoding="utf-8"), ucd)
  dictionary = variables["dictionary"].value if "dictionary" in variables else CPSet()
  starts, cats, dict_flags, num_cats = categories(sets, dictionary)
  trans, accepting, bof_required = build_dfa(rules, starts, cats, num_cats, chain)
  return {
      "starts": starts,
      "cats": cats,
      "dict": [bool(dict_flags.get(c)) for c in range(num_cats)],
      "trans": trans,
      "accepting": accepting,
      "bof_required": bof_required,
  }


def thai_sets(ucd):
  thai_word = ucd.lookup("Thai").intersection(ucd.lookup("LineBreak", "Complex_Context"))
  marks = thai_word.intersection(ucd.lookup("M")).union(CPSet([(0x20, 0x20)]))
  return {"thai_word": thai_word.ranges, "thai_marks": marks.ranges}


def emit(out_path, word, sent, extra):
  with open(out_path, "w", encoding="utf-8") as fh:
    fh.write('"""Break iterator state tables generated by tools/icu_port/build_tables.py.\n\n'
             'Derived from ICU 78.3 word.txt/sent.txt and Unicode 17.0 data.\n'
             'Copyright (C) 2016 and later: Unicode, Inc. and others.\n'
             'License & terms of use: see data/LICENSE-ICU (Unicode License V3)\n\n'
             'Do not edit by hand.\n"""\n\n')
    for name, t in (("WORD", word), ("SENTENCE", sent)):
      fh.write("{} = {!r}\n\n".format(name, t))
    for name, value in extra.items():
      fh.write("{} = {!r}\n\n".format(name.upper(), value))


def main(cache_dir, out_path):
  ucd = UCD(cache_dir)
  word = compile_rules(HERE / "rules" / "word.txt", ucd)
  sent = compile_rules(HERE / "rules" / "sent.txt", ucd)
  emit(out_path, word, sent, thai_sets(ucd))
  for name, t in (("word", word), ("sentence", sent)):
    print("{}: {} categories, {} states, {} ranges".format(
        name, len(t["dict"]), len(t["trans"]), len(t["starts"])))


if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])
