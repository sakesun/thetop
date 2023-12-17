#! -*- coding: utf-8 -*-

from __future__ import division
import operator

from . import nullop

def fold(x):
    if isinstance(x, Fold): return x
    if isinstance(x, (tuple, list)): return type(x)(fold(i) for i in x)
    return Fold(x)

def unfold(x):
    if isinstance(x, Fold): return x.inner
    if isinstance(x, (tuple, list)): return type(x)(unfold(i) for i in x)
    return x

def unfold_instance(x, t):
    return isinstance(x, t) \
        or (isinstance(x, Fold) and isinstance(x.inner, t))

def foldfn(f):
    return (lambda *args, **kwargs: fold(f(*args, **kwargs)))

isnull = foldfn(nullop.isnull)
accept = foldfn(nullop.accept)
hasnull = foldfn(nullop.hasnull)
Any = foldfn(nullop.Any)
All = foldfn(nullop.All)
neg = foldfn(nullop.neg)
pos = foldfn(nullop.pos)
summarize = foldfn(nullop.summarize)
sub = foldfn(nullop.sub)
multiply = foldfn(nullop.multiply)
floordiv = foldfn(nullop.floordiv)
truediv = foldfn(nullop.truediv)
divmod = foldfn(nullop.divmod)
pow = foldfn(nullop.pow)
mod = foldfn(nullop.mod)
concat = foldfn(nullop.concat)
concat2 = foldfn(nullop.concat2)
isin = foldfn(nullop.isin)
notin = foldfn(nullop.notin)
lt = foldfn(nullop.lt)
le = foldfn(nullop.le)
eq = foldfn(nullop.eq)
ne = foldfn(nullop.ne)
ge = foldfn(nullop.ge)
gt = foldfn(nullop.gt)
like = foldfn(nullop.like)
between = foldfn(nullop.between)
And = foldfn(nullop.And)
Or = foldfn(nullop.Or)
Not = foldfn(nullop.Not)
ucase = foldfn(nullop.ucase)
lcase = foldfn(nullop.lcase)
replace = foldfn(nullop.replace)
ltrim = foldfn(nullop.ltrim)
rtrim = foldfn(nullop.rtrim)
trim = foldfn(nullop.trim)
cast = foldfn(nullop.cast)
aggregate_summary = foldfn(nullop.aggregate_summary)
aggregate_minimum = foldfn(nullop.aggregate_minimum)
aggregate_maximum = foldfn(nullop.aggregate_maximum)
aggregate_count = foldfn(nullop.aggregate_count)
aggregate_summaries = foldfn(nullop.aggregate_summaries)
aggregate_minimums = foldfn(nullop.aggregate_minimums)
aggregate_maximums = foldfn(nullop.aggregate_maximums)
aggregate_counts = foldfn(nullop.aggregate_counts)

class Containable(object):
    def contains(self, value): raise NotImplementedError()
    def notcontains(self, value): raise NotImplementedError()

class Fold(object):
    __slots__ = 'inner'
    def __init__(self, inner): self.inner = unfold(inner)
    def __repr__(self): return 'Fold(%s)' % repr(self.inner)
    def __hash__(self):
        if isnull(self.inner): return hash(None)
        return hash(self.inner)
    def __index__(self): return operator.index(self.inner)
    def __bool__(self): return bool(nullop.accept(self.inner))
    __nonzero__ = __bool__
    def __coerce__(self, other): return (self, fold(other))
    def And(self, other): return And(self.inner, other)
    def Or(self, other): return Or(self.inner, other)
    def Not(self): return Not(self.inner)
    and_ = And
    or_ = Or
    not_ = property(Not)
    def isnull(self): return isnull(self.inner)
    def notnull(self): return fold(not self.isnull())
    is_null = property(isnull)
    is_not_null = property(notnull)
    __isnull__ = property(isnull)
    __unfolded__ = property(lambda self: self.inner)
    def __lt__(self, other): return lt(self.inner, other)
    def __le__(self, other): return le(self.inner, other)
    def __eq__(self, other): return eq(self.inner, other)
    def __ne__(self, other): return ne(self.inner, other)
    def __ge__(self, other): return ge(self.inner, other)
    def __gt__(self, other): return gt(self.inner, other)
    def between(self, lo, hi): return between(self.inner, lo, hi)
    def inrange(self, first, afterlast):
        return And(le(first, self.inner), lt(self.inner, afterlast))
    def isin(self, S):
        if unfold_instance(S, Containable): return S.contains(self)
        return isin(self.inner, S)
    def notin(self, S):
        if unfold_instance(S, Containable): return S.notcontains(self)
        return notin(self.inner, S)
    def in_(self, *S):
        if len(S) == 0: return fold(False)
        if (len(S) == 1) and unfold_instance(S[0], Containable): S = S[0]
        return self.isin(S)
    def not_in_(self, *S):
        if len(S) == 0: return fold(True)
        if (len(S) == 1) and unfold_instance(S[0], Containable): S = S[0]
        return self.notin(S)
    def __neg__(self): return neg(self.inner)
    def __pos__(self): return pos(self.inner)
    def __add__(self, other):
        other = unfold(other)
        if isinstance(self.inner, str) or unfold_instance(other, str):
            return concat2(self.inner, other)
        else:
            return summarize(self.inner, other)
    def __radd__(self, other):
        other = other
        if isinstance(self.inner, str) or unfold_instance(other, str):
            return concat2(other, self.inner)
        else:
            return summarize(other, self.inner)
    def __sub__(self, other): return sub(self.inner, other)
    def __rsub__(self, other): return sub(other, self.inner)
    def __mul__(self, other): return multiply(self.inner, other)
    def __rmul__(self, other): return multiply(other, self.inner)
    def __truediv__(self, other): return truediv(self.inner, other)
    def __rtruediv__(self, other): return truediv(other, self.inner)
    def __floordiv__(self, other): return floordiv(self.inner, other)
    def __rfloordiv__(self, other): return floordiv(other, self.inner)
    __div__ = __truediv__
    __rdiv__ = __rtruediv__
    def __divmod__(self, other): return divmod(self.inner, other)
    def __pow__(self, other): return pow(self.inner, other)
    def __rpow__(self, other): return pow(other, self.inner)
    def __mod__(self, other): return mod(self.inner, other)
    def __rmod__(self, other): return mod(other, self.inner)
    def append(self, suffix): return concat2(self.inner, suffix)
    def prepend(self, prefix): return concat2(prefix, self.inner)
    def upper(self): return ucase(self.inner)
    def lower(self): return lcase(self.inner)
    def startswith(self, prefix): return like(self.inner, prefix + '%')
    def endswith(self, suffix): return like(self.inner, '%' + suffix)
    def replace(self, old, new): return replace(self.inner, old, new)
    def lstrip(self): return ltrim(self.inner)
    def rstrip(self): return rtrim(self.inner)
    def strip(self): return trim(self.inner)
    def like(self, pattern, escape=None): return like(self.inner, pattern, escape)
    def cast(self, t): return cast(self.inner, t)
