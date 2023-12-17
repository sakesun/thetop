#! -*- coding: utf-8 -*-

from functools import reduce
import re
import operator
import string

def _is_None(x): return x is None
def _custom_isnull(x): return hasattr(x, '__isnull__') and x.__isnull__
null_detectors = [_is_None, _custom_isnull]

try:
    clr = __import__('clr')
    System = __import__('System')
    DBNull = System.DBNull
    null_detectors.append(lambda v: v == DBNull.Value)
except ImportError:
    pass

def inarg(x):
    """call this function for every input argument of nullop functions to support folded object"""
    if hasattr(x, '__unfolded__'): return x.__unfolded__
    else: return x

def isnull(v):
    """return whetner value v considered null"""
    v = inarg(v)
    for f in null_detectors:
        if f(v): return True
    return False

def notnull(v):
    """return whetner value v considered not null"""
    return not isnull(v)

def accept(v):
    """return whether the value v is considered Truthy"""
    v = inarg(v)
    return bool(notnull(v) and v)

def hasnull(S):
    """return whether the sequence S has some value considered as null"""
    S = inarg(S)
    for x in S:
        if isnull(x): return True
    return False

def Any(S):
    """return whether the sequence S has some Truthy value"""
    S = inarg(S)
    for x in S:
        if accept(x): return True
    return False

def All(S):
    """return whether all the members of the sequence S are Truthy"""
    S = inarg(S)
    for x in S:
        if not accept(x): return False
    return True

def neg(n):
    """return whether the value n is considiered as negative value"""
    n = inarg(n)
    if isnull(n): return None
    return - n

def pos(n):
    """return whether the value n is considiered as positive value"""
    n = inarg(n)
    if isnull(n): return None
    return + n

def summarize(*N):
    """return summary of all values in sequence N. if any item is null, return None"""
    N = inarg(N)
    if hasnull(N): return None
    return sum(N)

def sub(n1, n2):
    """return substraction of n1 and n2. if any item is null, return None"""
    n1 = inarg(n1)
    n2 = inarg(n2)
    if isnull(n1) or isnull(n2): return None
    return n1 - n2

def multiply(*N):
    """return multiplication of all values in sequence N. if any item is null, return None"""
    N = inarg(N)
    if hasnull(N): return None
    return reduce(operator.mul, N)

def floordiv(n1, n2):
    """return operator.floordiv of n1 and n2. if any item is null, return None"""
    n1 = inarg(n1)
    n2 = inarg(n2)
    if isnull(n1) or isnull(n2): return None
    return operator.floordiv(n1, n2)

def truediv(n1, n2):
    """return operator.truediv of n1 and n2. if any item is null, return None"""
    n1 = inarg(n1)
    n2 = inarg(n2)
    if isnull(n1) or isnull(n2): return None
    return operator.truediv(n1, n2)

def divmod(n1, n2):
    """return divmod of n1 and n2. if any item is null, return None"""
    n1 = inarg(n1)
    n2 = inarg(n2)
    if isnull(n1) or isnull(n2): return None
    return __builtins__.divmod(n1, n2)

def pow(n1, n2):
    """return n1 power n2. if any item is null, return None"""
    n1 = inarg(n1)
    n2 = inarg(n2)
    if isnull(n1) or isnull(n2): return None
    return n1 ** n2

def mod(n1, n2):
    """return n1 % n2. if any item is null, return None"""
    n1 = inarg(n1)
    n2 = inarg(n2)
    if isnull(n1) or isnull(n2): return None
    return n1 % n2

def concat(*S):
    """return concatenation of all values in sequence S. if any item is null, return None"""
    S = inarg(S)
    if hasnull(S): return None
    return ''.join(S)

def concat2(s1, s2):
    """return concatenation of s1 and s2. if any item is null, return None"""
    s1 = inarg(s1)
    s2 = inarg(s2)
    if isnull(s1) or isnull(s2): return None
    return operator.concat(s1, s2)

def isin(a, S):
    """return whether Sequence S contains item a. if a or S is null, return None"""
    a = inarg(a)
    S = inarg(S)
    if isnull(a): return None
    if a in S: return True
    if hasnull(S): return None
    return False

def notin(a, S):
    """return whether Sequence S does not contain item a. if a or S is null, return None"""
    a = inarg(a)
    S = inarg(S)
    if isnull(a): return None
    if a in S: return False
    if hasnull(S): return None
    return True

def lt(a, b):
    """return whether a less than b. if a or b is null, return None"""
    a = inarg(a)
    b = inarg(b)
    if isnull(a) or isnull(b): return None
    return a < b

def le(a, b):
    """return whether a less than or equals to b. if a or b is null, return None"""
    a = inarg(a)
    b = inarg(b)
    if isnull(a) or isnull(b): return None
    return a <= b

def eq(a, b):
    """return whether a equals to b. if a or b is null, return None"""
    a = inarg(a)
    b = inarg(b)
    if isnull(a) or isnull(b): return None
    return a == b

def ne(a, b):
    """return whether a does not equal to b. if a or b is null, return None"""
    a = inarg(a)
    b = inarg(b)
    if isnull(a) or isnull(b): return None
    return a != b

def ge(a, b):
    """return whether a greater than b. if a or b is null, return None"""
    a = inarg(a)
    b = inarg(b)
    if isnull(a) or isnull(b): return None
    return a >= b

def gt(a, b):
    """return whether a greater than or equals to b. if a or b is null, return None"""
    a = inarg(a)
    b = inarg(b)
    if isnull(a) or isnull(b): return None
    return a > b

REGEX_SPECIALS = '\\.^$*+?{}[]()<>|'   # always put backslash first
_like_cache = {}
_MAXLIKECACHE = 50

def _add_to_dict_with_limit(dic, limit, k, v):
    dic[k] = v
    if len(dic) > limit:
        deletings = list(dic.keys())[:-limit]
        for k in deletings:
            if len(dic) <= limit: break
            dic.pop(k)

def _add_to_like_cache(k, v):
    _add_to_dict_with_limit(_like_cache, _MAXLIKECACHE, k, v)

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
    """return whether s match pattern, if s or match is null, return None. escape char can be specified"""
    s = inarg(s)
    pattern = inarg(pattern)
    escape = inarg(escape)
    if isnull(s) or isnull(pattern): return None
    regex = _like_cache.get((pattern, escape), None)
    if regex is None:
        regex = re.compile(_get_like_regex_pattern(pattern, escape))
        _add_to_like_cache((pattern, escape), regex)
    m = regex.match(s)
    if m is None: return False
    return (m.start() == 0) and (m.end() == len(s))

def between(a, lo, hi):
    """return whether s is between lo and hi, null-aware"""
    a = inarg(a)
    lo = inarg(lo)
    hi = inarg(hi)
    vlo = ge(a, lo)
    vhi = le(a, hi)
    return And(vlo, vhi)

def And(*B):
    """null-aware and"""
    B = inarg(B)
    r = True
    for x in B:
        if isnull(x): r = None
        elif not x: return False
    return r

def Or(*B):
    """null-aware or"""
    B = inarg(B)
    r = False
    for x in B:
        if isnull(x): r = None
        elif x: return True
    return r

def Not(b):
    """null-aware not"""
    b = inarg(b)
    if isnull(b): return None
    return not b

and_ = And
or_ = Or
not_ = Not

def ucase(s):
    """null-aware string uppercase"""
    s = inarg(s)
    if isnull(s): return None
    return s.upper()

def lcase(s):
    """null-aware string lowercase"""
    s = inarg(s)
    if isnull(s): return None
    return s.lower()

def replace(s, old, new):
    """null-aware string replace"""
    s = inarg(s)
    old = inarg(old)
    new = inarg(new)
    if isnull(s) or isnull(old) or isnull(new): return None
    return s.replace(old, new)

def ltrim(s):
    """null-aware string ltrim"""
    s = inarg(s)
    if isnull(s): return None
    return s.lstrip()

def rtrim(s):
    """null-aware string rtrim"""
    s = inarg(s)
    if isnull(s): return None
    return s.rstrip()

def trim(s):
    """null-aware string trim"""
    s = inarg(s)
    if isnull(s): return None
    return s.strip()

def cast(a, t):
    """null-aware type cast"""
    a = inarg(a)
    t = inarg(t)
    if isnull(a): return None
    if isinstance(t, type): return t(a)
    return eval(t + '(' + repr(a) + ')')

def aggregate_summary(S):
    """sum of sequence S, ignoring null"""
    S = inarg(S)
    r = None
    for v in S:
        if notnull(v):
            if isnull(r): r = v
            else: r += v
    return r

def aggregate_minimum(S):
    """min of sequence S, ignoring null"""
    S = inarg(S)
    r = None
    for v in S:
        if notnull(v):
            if isnull(r): r = v
            elif v < r: r = v
    return r

def aggregate_maximum(S):
    """max of sequence S, ignoring null"""
    S = inarg(S)
    r = None
    for v in S:
        if notnull(v):
            if isnull(r): r = v
            elif v > r: r = v
    return r

def aggregate_count(S):
    """count of sequence S, ignoring null"""
    S = inarg(S)
    r = 0
    for v in S:
        if notnull(v): r += 1
    return r

def aggregate_summaries(size, S):
    """sum of sequence S, ignoring null, with defined size"""
    size = inarg(size)
    S = inarg(S)
    r = size * [None]
    for v in S:
        for i in range(size):
            if notnull(v[i]):
                if isnull(r[i]): r[i] = v[i]
                else: r[i] += v[i]
    return tuple(r)

def aggregate_minimums(size, S):
    """min of sequence S, ignoring null, with defined size"""
    size = inarg(size)
    S = inarg(S)
    r = size * [None]
    for v in S:
        for i in range(size):
            if notnull(v[i]):
                if isnull(r[i]): r[i] = v[i]
                elif v[i] < r[i]: r[i] = v[i]
    return tuple(r)

def aggregate_maximums(size, S):
    """max of sequence S, ignoring null, with defined size"""
    size = inarg(size)
    S = inarg(S)
    r = size * [None]
    for v in S:
        for i in range(size):
            if notnull(v[i]):
                if isnull(r[i]): r[i] = v[i]
                elif v[i] > r[i]: r[i] = v[i]
    return tuple(r)

def aggregate_counts(size, S):
    """count of sequence S, ignoring null, with defined size"""
    size = inarg(size)
    S = inarg(S)
    r = size * [0]
    for v in S:
        for i in range(size):
            if notnull(v[i]): r[i] += 1
    return tuple(r)
