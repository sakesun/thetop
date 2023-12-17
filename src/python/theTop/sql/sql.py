#! -*- coding: utf-8 -*-

from ..util import propattr
from ..model import models
from . import gen

class StoreItem(models.Associate):
    def __init__(self, store, model):
        models.Associate.__init__(self, model)
        self.store = store

class Containable(StoreItem):
    def contains(self, value): return Boolean(self.store, self.model.contains(value))
    def not_contains(self, value): return Boolean(self.store, self.model.not_contains(value))

class Boolean(StoreItem):
    def and_(self, other): return Boolean(self.store, self.model.and_(other))
    def or_(self, other): return Boolean(self.store, self.model.or_(other))
    not_ = propattr(lambda self: Boolean(self.store, self.model.not_))

class Comparable(StoreItem):
    def __lt__(self, other): return Boolean(self.store, self.model.__lt__(other))
    def __le__(self, other): return Boolean(self.store, self.model.__le__(other))
    def __eq__(self, other): return Boolean(self.store, self.model.__eq__(other))
    def __ne__(self, other): return Boolean(self.store, self.model.__ne__(other))
    def __ge__(self, other): return Boolean(self.store, self.model.__ge__(other))
    def __gt__(self, other): return Boolean(self.store, self.model.__gt__(other))
    def between(self, lo, hi): return Boolean(self.store, self.model.between(lo, hi))
    def in_range(self, first, afterlast): return Boolean(self.store, self.model.inrange(first, afterlast))
    def in_(self, S): return Boolean(self.store, self.model.in_(S))
    def not_in_(self, S): return Boolean(self.store, self.model.not_in_(S))
    is_null = propattr(lambda self: Boolean(self.store, self.model.is_null))
    is_not_null = propattr(lambda self: Boolean(self.store, self.model.is_not_null))

class Numeric(StoreItem):
    def __neg__(self): return Numeric(self.store, self.model.__neg__())
    def __pos__(self): return Numeric(self.store, self.model.__pos__())
    def __abs__(self): return Numeric(self.store, self.model.__abs__())
    def __add__(self, other): return Numeric(self.store, self.model.__add__(other))
    def __radd__(self, other): return Numeric(self.store, self.model.__radd__(other))
    def __sub__(self, other): return Numeric(self.store, self.model.__sub__(other))
    def __rsub__(self, other): return Numeric(self.store, self.model.__rsub__(other))
    def __mul__(self, other): return Numeric(self.store, self.model.__mul__(other))
    def __rmul__(self, other): return Numeric(self.store, self.model.__rmul__(other))
    def __div__(self, other): return Numeric(self.store, self.model.__div__(other))
    def __truediv__(self, other): return Numeric(self.store, self.model.__truediv__(other))
    def __rdiv__(self, other): return Numeric(self.store, self.model.__rdiv__(other))
    def __rtruediv__(self, other): return Numeric(self.store, self.model.__rtruediv__(other))
    def __pow__(self, other): return Numeric(self.store, self.model.__pow__(other))
    def __rpow__(self, other): return Numeric(self.store, self.model.__rpow__(other))
    def __mod__(self, other): return Numeric(self.store, self.model.__mod__(other))
    def __rmod__(self, other): return Numeric(self.store, self.model.__rmod__(other))

class String(StoreItem):
    def append(self, suffix): return String(self.store, self.model.append(suffix))
    def prepend(self, prefix): return String(self.store, self.model.prepend(prefix))
    __add__ = append
    __radd__ = prepend
    def upper(self): return String(self.store, self.model.upper())
    def lower(self): return String(self.store, self.model.lower())
    def startswith(self, prefix): return String(self.store, self.model.startswith(prefix))
    def endswith(self, suffix): return String(self.store, self.model.endswith(suffix))
    def replace(self, old, new): return String(self.store, self.model.replace(old, new))
    def lstrip(self): return String(self.store, self.model.lstrip())
    def rstrip(self): return String(self.store, self.model.rstrip())
    def strip(self): return String(self.store, self.model.strip())
    def like(self, pattern, escape=NotImplemented): return Boolean(self.store, self.model.like(pattern, escape))

class DateTime(StoreItem):
    def date(self): return DateTime(self.store, self.model.date())
    # part
    year = propattr(lambda self: Numeric(self.store, self.model.year))
    month = propattr(lambda self: Numeric(self.store, self.model.month))
    day = propattr(lambda self: Numeric(self.store, self.model.day))
    hour = propattr(lambda self: Numeric(self.store, self.model.hour))
    minute = propattr(lambda self: Numeric(self.store, self.model.minute))
    second = propattr(lambda self: Numeric(self.store, self.model.second))
    microsecond = propattr(lambda self: Numeric(self.store, self.model.microsecond))
    # start
    def yearstart(self): return DateTime(self.store, self.model.yearstart())
    def monthstart(self): return DateTime(self.store, self.model.monthstart())
    def daystart(self): return DateTime(self.store, self.model.daystart())
    def hourstart(self): return DateTime(self.store, self.model.hourstart())
    def minutestart(self): return DateTime(self.store, self.model.minutestart())
    def secondstart(self): return DateTime(self.store, self.model.secondstart())
    def microsecondstart(self): return DateTime(self.store, self.model.microsecondstart())
    def yyyy_mm_dd(self, sep='-'): return String(self.store, self.model.yyyy_mm_dd(sep))
    def hh_mm_ss(self, sep=':'): return String(self.store, self.model.hh_mm_ss(sep))

class Generic(Numeric, String, Boolean, DateTime):
    def __add__(self, other):
        if isinstance(other, basestring): return String.__add__(self, other)
        return Numeric.__add__(self, other)
    def __radd__(self, other):
        if isinstance(other, basestring): return String.__radd__(self, other)
        return Numeric.__radd__(self, other)

class AllValue(Generic):
    pass

class AnyValue(Generic):
    pass

class Existence(Boolean):
    pass

class Count(Numeric):
    pass

class Inserting(StoreItem):
    pass

class UpdatingAll(StoreItem):
    pass

class DeletingAll(StoreItem):
    pass

class Extending(StoreItem):
    pass

class Merging(StoreItem):
    pass

class SqlStoreEmitter(gen.SqlEmitter):
    def __init__(self, store):
        gen.SqlEmitter.__init__(self, store.dialect)
        self.store = store
    def check_store(self, a):
        assert isinstance(a, StoreItem)
        if store is not self.store:
            raise Exception('Mismatched store (%s, %s)', repr(store), repr(self.store))
    def Associate(self, a):
        self.check_store(a)
        return gen.SqlEmitter.Associate(self, a)

class Table(Generic, Containable):
    def emit(self, emitter):
        # check store ?
        return self.model.emit(emitter)
    def _new(self, model): return Table(self.store, model)
    emitter = propattr(lambda self: SqlStoreEmitter(self.store))
    def gen_select(self):
        s = self.model.emit(self.emitter)
        p = structure.PrettyVisitor(self.dialect.TAB)
        s.visit(p)
        return (p.pretty(), p.tags)
    def gen_insert(self):
        pass
    all = propattr(AllValue)
    any = propattr(AnyValue)
    exists = propattr(Existence)
    not_exists = propattr(lambda self: self.exists.not_)
    count = propattr(Count)
    def qualify(self): return self._new(self.model.qualify())
    def alias(self, alias): return self._new(self.model.alias(alias))
    def nest(self, alias): return self._new(self.model.nest(alias))
    def include(self, *inclusions): return self._new(self.model.include(*inclusions))
    def exclude(self, *exclusions): return self._new(self.model.include(*exclusions))
    __call__ = include
    def rename(self, **renamings): return self._new(self.model.rename(**renamings))
    def where(self, *args, **kwargs): return self._new(self.model.where(*args, **kwargs))
    def whereof(self, ref): return self._new(self.model.whereof(ref))
    def define(self, *args, **kwargs): return self._new(self.model.define(*args, **kwargs))
    def redefine(self, *args, **kwargs): return self._new(self.model.redefine(*args, **kwargs))
    def group(self, *groupbys): return self._new(self.model.group(*groupbys))
    def assign(self, **assignments): return self._new(self.model.assign(**assignments))
    def union(self, other): return self._new(self.model.union(other.model))
    def innerjoin(self, right): return self._new(self.model.innerjoin(right.model))
    def outerjoin(self, right): return self._new(self.model.outerjoin(right.model))
    def crossjoin(self, right): return self._new(self.model.crossjoin(right.model))
    def distinct(self): return self._new(self.model.distinct())
    def orderby(self, *args): return self._new(self.model.orderby(*args))
    def inserting(self, *labels, **settings): return Inserting(self.model.inserting(*labels, **settings))
    def updatingall(self, *labels, **settings): return UpdatingAll(self.model.updatingall(*labels, **settings))
    def deletingall(self): return DeletingAll(self.model.deletingall())
    def extending(self, extension): return Extending(self.model.extending(extension))
    def merging(self, source, inserting=None): return Merging(self.model.merging(source, inserting))
    def __nonzero__(self): return self.exists()
    def __contains__(self, x): return self.contains(x)()
    def __len__(self): return self.count()
    labels = ()
    def cursor(self): raise NotImplementedError()
    def rowset(self): raise NotImplementedError()
    def order(self): raise NotImplementedError()
    def slice(self): raise NotImplementedError()
    def insert(self): raise NotImplementedError()
    def updateall(self): raise NotImplementedError()
    def deleteall(self): raise NotImplementedError()
    def extend(self, source): raise NotImplementedError()
    def merge(self, source): raise NotImplementedError()
    row = propattr(lambda self: Row(self))

def valid_labels(self, *labels):
    return labels and all(n in self.labels for n in labels)

def assert_valid_labels(self, *labels):
    if not labels:
        raise LookupError('Empty labels is not allowed')
    if not self.valid_labels(*labels):
        raise LookupError(repr(labels))
