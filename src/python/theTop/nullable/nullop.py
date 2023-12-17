#! -*- coding: utf-8 -*-

from __future__ import division
import re
import operator
import string

null_detectors = [(lambda v: (v is None) or (hasattr(v, '__isnull__') and v.__isnull__))]

def inarg(x):
    return x.__unfolded__ \
           if hasattr(x, '__unfolded__') \
           else x

try:
    import clr
    from System import DBNull
    null_detectors.append(lambda v: v == DBNull.Value)
except ImportError:
    pass

def isnull(v):
    v = inarg(v)
    for f in null_detectors:
        if f(v): return True
    return False

def notnull(v): return not isnull(v)

def accept(v):
    v = inarg(v)
    return bool(notnull(v) and v)

def hasnull(S):
    S = inarg(S)
    for x in S:
        if isnull(x): return True
    return False

def Any(S):
    S = inarg(S)
    for x in S:
        if accept(x): return True
    return False

def All(S):
    S = inarg(S)
    for x in S:
        if not accept(x): return False
    return True

def neg(n):
    n = inarg(n)
    if isnull(n): return None
    return - n

def pos(n):
    n = inarg(n)
    if isnull(n): return None
    return + n

def summarize(*N):
    N = inarg(N)
    if hasnull(N): return None
    return sum(N)

def sub(n1, n2):
    n1 = inarg(n1)
    n2 = inarg(n2)
    if isnull(n1) or isnull(n2): return None
    return n1 - n2

def multiply(*N):
    N = inarg(N)
    if hasnull(N): return None
    return reduce(operator.mul, N)

def floordiv(n1, n2):
    n1 = inarg(n1)
    n2 = inarg(n2)
    if isnull(n1) or isnull(n2): return None
    return operator.floordiv(n1, n2)

def truediv(n1, n2):
    n1 = inarg(n1)
    n2 = inarg(n2)
    if isnull(n1) or isnull(n2): return None
    return operator.truediv(n1, n2)

def divmod(n1, n2):
    n1 = inarg(n1)
    n2 = inarg(n2)
    if isnull(n1) or isnull(n2): return None
    return __builtins__.divmod(n1, n2)

def pow(n1, n2):
    n1 = inarg(n1)
    n2 = inarg(n2)
    if isnull(n1) or isnull(n2): return None
    return n1 ** n2

def mod(n1, n2):
    n1 = inarg(n1)
    n2 = inarg(n2)
    if isnull(n1) or isnull(n2): return None
    return n1 % n2

def concat(*S):
    S = inarg(S)
    if hasnull(S): return None
    return ''.join(S)

def concat2(s1, s2):
    s1 = inarg(s1)
    s2 = inarg(s2)
    if isnull(s1) or isnull(s2): return None
    return operator.concat(s1, s2)

def isin(a, S):
    a = inarg(a)
    S = inarg(S)
    if isnull(a): return None
    if a in S: return True
    if hasnull(S): return None
    return False

def notin(a, S):
    a = inarg(a)
    S = inarg(S)
    if isnull(a): return None
    if a in S: return False
    if hasnull(S): return None
    return True

def lt(a, b):
    a = inarg(a)
    b = inarg(b)
    if isnull(a) or isnull(b): return None
    return a < b

def le(a, b):
    a = inarg(a)
    b = inarg(b)
    if isnull(a) or isnull(b): return None
    return a <= b

def eq(a, b):
    a = inarg(a)
    b = inarg(b)
    if isnull(a) or isnull(b): return None
    return a == b

def ne(a, b):
    a = inarg(a)
    b = inarg(b)
    if isnull(a) or isnull(b): return None
    return a != b

def ge(a, b):
    a = inarg(a)
    b = inarg(b)
    if isnull(a) or isnull(b): return None
    return a >= b

def gt(a, b):
    a = inarg(a)
    b = inarg(b)
    if isnull(a) or isnull(b): return None
    return a > b

REGEX_SPECIALS = '\\.^$*+?{}[]()<>|'   # always put backslash first
_like_cache = {}
_MAXLIKECACHE = 50

def _get_like_regex_pattern(pattern, escape=None):
    if escape:
        pattern = pattern.replace(escape + '%', '\\%')
        pattern = pattern.replace(escape + '_', '\\_')
    for c in REGEX_SPECIALS: pattern = pattern.replace(c, '\\' + c)
    pattern = pattern.replace('%', '.*')
    pattern = pattern.replace('_', '.')
    if escape:
        pattern = pattern.replace('\\.*', '%')
        pattern = pattern.replace('\\.', '_')
    return pattern

def like(s, pattern, escape=None):
    s = inarg(s)
    pattern = inarg(pattern)
    escape = inarg(escape)
    if isnull(s) or isnull(pattern): return None
    regex = _like_cache.get((pattern, escape), None)
    if regex is None:
        regex = re.compile(_get_like_regex_pattern(pattern, escape))
        _like_cache[(pattern, escape)] = regex
        if len(_like_cache) > _MAXLIKECACHE: _like_cache.clear()
    m = regex.match(s)
    if m is None: return False
    return (m.start() == 0) and (m.end() == len(s))

def between(a, lo, hi):
    a = inarg(a)
    lo = inarg(lo)
    hi = inarg(hi)
    vlo = ge(a, lo)
    vhi = le(a, hi)
    return And(vlo, vhi)

def And(*B):
    B = inarg(B)
    r = True
    for x in B:
        if isnull(x): r = None
        elif not x: return False
    return r

def Or(*B):
    B = inarg(B)
    r = False
    for x in B:
        if isnull(x): r = None
        elif x: return True
    return r

def Not(b):
    b = inarg(b)
    if isnull(b): return None
    return not b

and_ = And
or_ = Or
not_ = Not

def ucase(s):
    s = inarg(s)
    if isnull(s): return None
    return s.upper()

def lcase(s):
    s = inarg(s)
    if isnull(s): return None
    return s.lower()

def replace(s, old, new):
    s = inarg(s)
    old = inarg(old)
    new = inarg(new)
    if isnull(s) or isnull(old) or isnull(new): return None
    return string.replace(s, old, new)

def ltrim(s):
    s = inarg(s)
    if isnull(s): return None
    return s.lstrip()

def rtrim(s):
    s = inarg(s)
    if isnull(s): return None
    return s.rstrip()

def trim(s):
    s = inarg(s)
    if isnull(s): return None
    return s.strip()

def cast(a, t):
    a = inarg(a)
    t = inarg(t)
    if isnull(a): return None
    if isinstance(t, type): return t(a)
    return eval(t + '(' + repr(a) + ')')

def aggregate_summary(S):
    S = inarg(S)
    r = None
    for v in S:
        if notnull(v):
            if isnull(r): r = v
            else: r += v
    return r

def aggregate_minimum(S):
    S = inarg(S)
    r = None
    for v in S:
        if notnull(v):
            if isnull(r): r = v
            elif v < r: r = v
    return r

def aggregate_maximum(S):
    S = inarg(S)
    r = None
    for v in S:
        if notnull(v):
            if isnull(r): r = v
            elif v > r: r = v
    return r

def aggregate_count(S):
    S = inarg(S)
    r = 0
    for v in S:
        if notnull(v): r += 1
    return r

def aggregate_summaries(size, S):
    size = inarg(size)
    S = inarg(S)
    r = size * [None]
    for v in S:
        for i in xrange(size):
            if notnull(v[i]):
                if isnull(r[i]): r[i] = v[i]
                else: r[i] += v[i]
    return tuple(r)

def aggregate_minimums(size, S):
    size = inarg(size)
    S = inarg(S)
    r = size * [None]
    for v in S:
        for i in xrange(size):
            if notnull(v[i]):
                if isnull(r[i]): r[i] = v[i]
                elif v[i] < r[i]: r[i] = v[i]
    return tuple(r)

def aggregate_maximums(size, S):
    size = inarg(size)
    S = inarg(S)
    r = size * [None]
    for v in S:
        for i in xrange(size):
            if notnull(v[i]):
                if isnull(r[i]): r[i] = v[i]
                elif v[i] > r[i]: r[i] = v[i]
    return tuple(r)

def aggregate_counts(size, S):
    size = inarg(size)
    S = inarg(S)
    r = size * [0]
    for v in S:
        for i in xrange(size):
            if notnull(v[i]): r[i] += 1
    return tuple(r)
