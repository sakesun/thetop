from ..util import propattr
from ..nullable import nullop

##########
#  Model Rules
#    1. Model's constructor never call make(x)
#    2. Model's chain method call make(x) for arguments where appropriate
#    3. Model's emit() call self._inner(...) or self._inners(...) for it's own sub-models
#    3. Composite's compose() call self._compose_inner(...) for it's own sub-models
#    4. modeler tools call make(x) for arguments where appropriate
#    5. modeler tools can call model constructor directly
#    6. Composite.compose call composer.inner(..) for sub-model

def makeall(X): return type(X)(make(i) for i in X)

def make(x):
    if nullop.isnull(x): return NULL
    if x is True: return TRUE
    if x is False: return FALSE
    if isinstance(x, Model): return x
    if isinstance(x, (tuple, list)): return ExpressionList(makeall(x))
    return Constant(x)

def expr_as_text(expr):
    # FIXME
    # from . import sql
    # return expr.emit(sql.SqlTextEmitter())
    return ''

def eval_expr(expr, **kwargs):
    from . import evaluator
    return expr.emit(evaluator.Evaluator(items=kwargs, params=kwargs))

def defined_labels(labels, deflist):
    if labels is None: raise Exception('Cannot determine defined_labels')
    return labels + tuple(k for (k, v) in deflist if k not in labels)

def renamed_labels(labels, renamings):
    renamings = dict(renamings)
    new_labels = []
    for o in labels:
        n = renamings.pop(o, o)
        if n in new_labels: raise KeyError('Duplicated new label names in rename')
        new_labels.append(n)
    if renamings: raise KeyError('Illegal labels: "%s"' % repr(renamings.keys()))
    return tuple(new_labels)

def grouped_labels(labels, aggregations):
    if any(n in labels for n in aggregations):
        raise KeyError('Labels and aggregations cannot be overlapped')
    return labels + tuple(sorted(aggregations.keys()))

def setlist(*args, **kwargs):
    if args and kwargs: raise ValueError('Cannot mix arguments list with keyword arguments')
    if (not args) and (not kwargs): raise ValueError('The argument "args" or "kwargs" must be specified')
    if args:
        r = []
        labels = set()
        for x in args:
            k = v = None
            if isinstance(x, str):
                k = x
                v = Parameter(x)
            elif isinstance(x, (tuple, list)) and (len(x) == 2) and isinstance(x[0], str):
                k = x[0]
                v = make(x[1])
            else:
                raise ValueError('Invalid arguments: %s' % repr(args))
            if k in labels: raise KeyError('Duplicated key: %s' % repr(k))
            r.append((k, v))
            labels.add(k)
        return r
    else:
        assert kwargs
        return [(k, make(v)) for (k, v) in kwargs.items()]

def deflist(*args, **kwargs):
    if args and kwargs: raise ValueError('Cannot mix arguments list with keyword arguments')
    if (not args) and (not kwargs): raise ValueError('The argument "args" or "kwargs" must be specified')
    if args:
        r = []
        labels = set()
        for (k, v) in args:
            if k in labels: raise KeyError('Duplicated key: %s' % repr(k))
            r.append((k, make(v)))
            labels.add(k)
        return r
    else:
        assert kwargs
        return [(k, make(kwargs[k])) for k in sorted(kwargs.keys())]

def altogether(*predicates):
    if not predicates: return TRUE
    if len(predicates) == 1: return predicates[0]
    return And(predicates)

def matchings(*args, **kwargs):
    predicates = []
    for (k, v) in args: predicates.append(Item(k) == make(v))
    for (k, v) in kwargs.items(): predicates.append(Item(k) == make(v))
    return predicates

def where(*args, **kwargs):
    predicates = makeall(args)
    if kwargs: predicates.extend(matchings(**kwargs))
    return altogether(*predicates)

def can_assign(x):
    return isinstance(x, (
        Constant,
        Value,
        Parameter,
        HostItem))

class Model(object):
    def emit(self, emitter): raise NotImplementedError()
    def emit_part(self, emitter): return emitter.inner(emitter, self, None)
    def _inner(self, emitter, x): return emitter.inner(emitter, x, self)
    def _inners(self, emitter, xs): return [emitter.inner(emitter, x, self) for x in xs]
    __str__ = expr_as_text
    def __repr__(self): return '%s { %s }' % (type(self).__name__, expr_as_text(self))

class Associate(Model):
    model = None
    def __init__(self, model): self.model = model
    def emit(self, emitter): return emitter.Associate(emitter._inner(self.model))

class Composite(Model):
    def _compose_inner(self, composer, x): composer.inner(composer, x, self)
    def emit(self, emitter):
        composer = emitter.composer()
        self.compose(composer)
        return composer.emit()
    def compose(self, composer): raise NotImplementedError()

class Emitter(object):
    def emit_model(self, model): return model.emit(self)
    def inner(self, emitter, x, outer):
        if x is NotImplemented: return x
        if not isinstance(x, Expression): return emitter.Constant(x)
        if not isinstance(outer, Parentheses):
            if emitter.ambiguous(x, outer):
                return emitter.Parentheses(x.emit(emitter))
        return x.emit(emitter)
    def ambiguous(self, x, outer): return False
    def composer(self): raise NotImplementedError()
    def Associate(self, a): return a
    def ExpressionList(self, S): raise NotImplementedError()
    def DateTimePart(self, date, part): raise NotImplementedError()
    def PeriodStart(self, date, part, offset): raise NotImplementedError()
    def YYYY_MM_DD(self, date, sep): raise NotImplementedError()
    def HH_MM_SS(self, date, sep): raise NotImplementedError()
    def Parentheses(self, x): raise NotImplementedError()
    def Constant(self, c): raise NotImplementedError()
    def Value(self, v): raise NotImplementedError()
    def Item(self, name): raise NotImplementedError()
    def HostItem(self, name): raise NotImplementedError()
    def Parameter(self, name): raise NotImplementedError()
    def Call(self, name, args): raise NotImplementedError()
    def Cast(self, value, type): raise NotImplementedError()
    def Case(self, cases, whenelse): raise NotImplementedError()
    def Switch(self, switch, cases, whenelse): raise NotImplementedError()
    def Neg(self, n): raise NotImplementedError()
    def Pos(self, n): raise NotImplementedError()
    def Summarize(self, N): raise NotImplementedError()
    def Sub(self, n1, n2): raise NotImplementedError()
    def Multiply(self, N): raise NotImplementedError()
    def Div(self, n1, n2): raise NotImplementedError()
    def Concat(self, S): raise NotImplementedError()
    def Comparison(self, op, a, b): raise NotImplementedError()
    def Between(self, a, lo, hi): raise NotImplementedError()
    def IsNull(self, a): raise NotImplementedError()
    def NotNull(self, a): raise NotImplementedError()
    def IsIn(self, a, S): raise NotImplementedError()
    def NotIn(self, a, S): raise NotImplementedError()
    def Like(self, s, pattern, escape): raise NotImplementedError()
    def And(self, B): raise NotImplementedError()
    def Or(self, B): raise NotImplementedError()
    def Not(self, b): raise NotImplementedError()
    def Now(self): raise NotImplementedError()
    def NextVal(self, sequence): raise NotImplementedError()

class Composer(object):
    def emit(self): raise NotImplementedError()
    def inner(self, composer, x, outer): x.compose(composer)
    def AllValue(self): raise NotImplementedError()
    def AnyValue(self): raise NotImplementedError()
    def Existence(self): raise NotImplementedError()
    def Count(self): raise NotImplementedError()
    def Distinct(self): raise NotImplementedError()
    def OrderBy(self, orderbys): raise NotImplementedError()
    def Slice(self, first, afterlast): raise NotImplementedError()
    def Primary(self, name): raise NotImplementedError()
    def Qualify(self): raise NotImplementedError()
    def Alias(self, alias): raise NotImplementedError()
    def Nest(self, alias): raise NotImplementedError()
    def Include(self, inclusions): raise NotImplementedError()
    def Exclude(self, exclusions): raise NotImplementedError()
    def Rename(self, renamings): raise NotImplementedError()
    def Define(self, deflist): raise NotImplementedError()
    def Redefine(self, deflist): raise NotImplementedError()
    def Where(self, predicate): raise NotImplementedError()
    def Group(self, groupbys): raise NotImplementedError()
    def Assign(self, assignments): raise NotImplementedError()
    def Union(self, tables): raise NotImplementedError()
    def InnerJoin(self, right): raise NotImplementedError()
    def OuterJoin(self, right): raise NotImplementedError()
    def CrossJoin(self, right): raise NotImplementedError()
    def Inserting(self, setlist): raise NotImplementedError()
    def UpdatingAll(self, setlist): raise NotImplementedError()
    def DeletingAll(self): raise NotImplementedError()
    def Extending(self, extension): raise NotImplementedError()
    def Merging(self, source, inserting): raise NotImplementedError()

def _emitting_models():
    return ((k,v) for (k,v) in globals().items()
            if isinstance(v, type)
            and issubclass(v, Model)
            and (k in Emitter.__dict__))

def _not_emitting_models():
    return ((k,v) for (k,v) in globals().items()
            if isinstance(v, type)
            and issubclass(v, Model)
            and (k not in Emitter.__dict__))

def _composing_models():
    return ((k,v) for (k,v) in globals().items()
            if isinstance(v, type)
            and issubclass(v, Composite)
            and (k in Composer.__dict__))

def _not_composing_models():
    return ((k,v) for (k,v) in globals().items()
            if isinstance(v, type)
            and issubclass(v, Composite)
            and (k not in Composer.__dict__))

class NoneEmitter(Emitter):
    terminated = False
    def inner(self, emitter, x, outer):
        if self.terminated: return None
        return Emitter.inner(self, emitter, x, outer)
    def composer(self): return NoneComposer(self)
    def ExpressionList(self, S): return None
    def DateTimePart(self, date, part): return None
    def PeriodStart(self, date, part, offset): return None
    def YYYY_MM_DD(self, date, sep): return None
    def HH_MM_SS(self, date, sep): return None
    def Parentheses(self, x): return None
    def Constant(self, c): return None
    def Value(self, v): return None
    def Item(self, name): return None
    def HostItem(self, name): return None
    def Parameter(self, name): return None
    def Call(self, name, args): return None
    def Cast(self, value, type): return None
    def Case(self, cases, whenelse): return None
    def Switch(self, switch, cases, whenelse): return None
    def Neg(self, n): return None
    def Pos(self, n): return None
    def Summarize(self, N): return None
    def Sub(self, n1, n2): return None
    def Multiply(self, N): return None
    def Div(self, n1, n2): return None
    def Concat(self, S): return None
    def Comparison(self, op, a, b): return None
    def Between(self, a, lo, hi): return None
    def IsNull(self, a): return None
    def NotNull(self, a): return None
    def IsIn(self, a, S): return None
    def NotIn(self, a, S): return None
    def Like(self, s, pattern, escape): return None
    def And(self, B): return None
    def Or(self, B): return None
    def Not(self, b): return None
    def Now(self): return None
    def NextVal(self, sequence): return None

class NoneComposer(Composer):
    def __init__(self, emitter): self.emitter = emitter
    def inner(self, composer, x, outer):
        if self.emitter.terminated: return
        Composer.inner(self, composer, x, outer)
    def inner_model(self, m): return m.emit_part(self.emitter)
    def emit(self): return None
    def AllValue(self): return
    def AnyValue(self): return
    def Existence(self): return
    def Count(self): return
    def Distinct(self): return
    def OrderBy(self, orderbys):
        for o in orderbys:
            self.inner_model(o)
    def Slice(self, first, afterlast): return
    def Primary(self, name): return
    def Qualify(self): return
    def Alias(self, alias): return
    def Nest(self, alias): return
    def Include(self, inclusions): return
    def Exclude(self, exclusions): return
    def Rename(self, renamings): return
    def Define(self, deflist):
        for (k, v) in deflist:
            self.inner_model(v)
    def Redefine(self, deflist):
        for (k, v) in deflist:
            self.inner_model(v)
    def Where(self, predicate): self.inner_model(predicate)
    def Group(self, groupbys): return
    def Assign(self, assignments): return
    def Union(self, tables):
        for t in tables: self.inner_model(t)
    def InnerJoin(self, right): self.inner_model(right)
    def OuterJoin(self, right): self.inner_model(right)
    def CrossJoin(self, right): self.inner_model(right)
    def Inserting(self, setlist):
        for (k, v) in setlist: self.inner_model(v)
    def UpdatingAll(self, setlist):
        for (k, v) in setlist: self.inner_model(v)
    def DeletingAll(self): return
    def Extending(self, extension): self.inner_model(extension)
    def Merging(self, source, inserting):
        self.inner_model(source)
        self.inner_model(inserting)

class EmitterDecorator(Emitter):
    def __init__(self, decorated): self.decorated = decorated
    def inner(self, emitter, x, outer): return self.decorated.inner(emitter, x, outer)
    def ambiguous(self, x, outer): return self.decorated.ambiguous(x, outer)
    def decorate_composer(self, composer): return ComposerDecorator(composer)
    def composer(self): return self.decorate_composer(self.decorated.composer())
    def ExpressionList(self, S): return self.decorated.ExpressionList(S)
    def DateTimePart(self, date, part): return self.decorated.DateTimePart(date, part)
    def PeriodStart(self, date, part, offset): return self.decorated.PeriodStart(date, part, offset)
    def YYYY_MM_DD(self, date, sep): return self.decorated.YYYY_MM_DD(date, sep)
    def HH_MM_SS(self, date, sep): return self.decorated.HH_MM_SS(date, sep)
    def Parentheses(self, x): return self.decorated.Parentheses(x)
    def Constant(self, c): return self.decorated.Constant(c)
    def Value(self, v): return self.decorated.Value(v)
    def Item(self, name): return self.decorated.Item(name)
    def HostItem(self, name): return self.decorated.HostItem(name)
    def Parameter(self, name): return self.decorated.Parameter(name)
    def Call(self, name, args): return self.decorated.Call(name, args)
    def Cast(self, value, type): return self.decorated.Cast(value, type)
    def Case(self, cases, whenelse): return self.decorated.Case(cases, whenelse)
    def Switch(self, switch, cases, whenelse): return self.decorated.Switch(switch, cases, whenelse)
    def Neg(self, n): return self.decorated.Neg(n)
    def Pos(self, n): return self.decorated.Pos(n)
    def Summarize(self, N): return self.decorated.Summarize(N)
    def Sub(self, n1, n2): return self.decorated.Sub(n1, n2)
    def Multiply(self, N): return self.decorated.Multiply(N)
    def Div(self, n1, n2): return self.decorated.Div(n1, n2)
    def Concat(self, S): return self.decorated.Concat(S)
    def Comparison(self, op, a, b): return self.decorated.Comparison(op, a, b)
    def Between(self, a, lo, hi): return self.decorated.Between(a, lo, hi)
    def IsNull(self, a): return self.decorated.IsNull(a)
    def NotNull(self, a): return self.decorated.NotNull(a)
    def IsIn(self, a, S): return self.decorated.IsIn(a, S)
    def NotIn(self, a, S): return self.decorated.NotIn(a, S)
    def Like(self, s, pattern, escape): return self.decorated.Like(s, pattern, escape)
    def And(self, B): return self.decorated.And(B)
    def Or(self, B): return self.decorated.Or(B)
    def Not(self, b): return self.decorated.Not(b)
    def Now(self): return self.decorated.Now()
    def NextVal(self, sequence): return self.decorated.NextVal(sequence)

class ComposerDecorator(Composer):
    def __init__(self, decorated): self.decorated = decorated
    def emit(self): return self.decorated.emit()
    def inner(self, composer, x, outer): self.decorated.inner(composer, x, outer)
    def AllValue(self): self.decorated.AllValue()
    def AnyValue(self): self.decorated.AnyValue()
    def Existence(self): self.decorated.Existence()
    def Count(self): self.decorated.Count()
    def Distinct(self): self.decorated.Distinct()
    def OrderBy(self, orderbys): self.decorated.OrderBy(orderbys)
    def Slice(self, first, afterlast): self.decorated.Slice(first, afterlast)
    def Primary(self, name): self.decorated.Primary(name)
    def Qualify(self): self.decorated.Qualify()
    def Alias(self, alias): self.decorated.Alias(alias)
    def Nest(self, alias): self.decorated.Nest(alias)
    def Include(self, inclusions): self.decorated.Include(inclusions)
    def Exclude(self, exclusions): self.decorated.Exclude(exclusions)
    def Rename(self, renamings): self.decorated.Rename(renamings)
    def Define(self, deflist): self.decorated.Define(deflist)
    def Redefine(self, deflist): self.decorated.Redefine(deflist)
    def Where(self, predicate): self.decorated.Where(predicate)
    def Group(self, groupbys): self.decorated.Group(groupbys)
    def Assign(self, assignments): self.decorated.Assign(assignments)
    def Union(self, tables): self.decorated.Union(tables)
    def InnerJoin(self, right): self.decorated.InnerJoin(right)
    def OuterJoin(self, right): self.decorated.OuterJoin(right)
    def CrossJoin(self, right): self.decorated.CrossJoin(right)
    def Inserting(self, setlist): self.decorated.Inserting(setlist)
    def UpdatingAll(self, setlist): self.decorated.UpdatingAll(setlist)
    def DeletingAll(self): self.decorated.DeletingAll()
    def Extending(self, extension): self.decorated.Extending(extension)
    def Merging(self, source, inserting): self.decorated.Merging(source, inserting)

class CollectParamEmitter(NoneEmitter):
    def __init__(self):
        self.params = set()
        self.assignments = []
    def assigned(self, name):
        return any(
            (name in assignment)
            for assignment in self.assignments)
    def composer(self): return CollectParamComposer(self)
    def Parameter(self, name):
        if not self.assigned(name): self.params.add(name)
        return NoneEmitter.Parameter(self, name)

class CollectParamComposer(NoneComposer):
    def __init__(self, emitter): self.emitter = emitter
    def inner(self, composer, x, outer):
        if isinstance(outer, Assign): self.emitter.assignments.append(outer.assignments)
        NoneComposer.inner(self, composer, x, outer)
    def Assign(self, assignments):
        a = self.emitter.assignments.pop()
        assert a is assignments

def params(m):
    emitter = CollectParamEmitter()
    m.emit(emitter)
    assert not emitter.assignments
    return emitter.params

class Expression(Model):
    eval = eval_expr

class Containable(object):
    def contains(self, value): return self._contains(self, make(value))
    def _contains(self, value): return IsIn(value, self)
    def not_contains(self, value): return self._not_contains(self, make(value))
    def _not_contains(self, value): return NotIn(value, self)

class Boolean(Expression):
    def and_(self, other):
        other = make(other)
        if isinstance(other, And): return other._rand_(self)
        return self._and_(other)
    def _and_(self, other): return And([self, other])
    def or_(self, other):
        other = make(other)
        if isinstance(other, Or): return other._ror_(self)
        return self._or_(other)
    def _or_(self, other): return Or([self, other])
    not_ = propattr(lambda self: Not(self))

class Comparable(Expression):
    def __lt__(self, other): return Comparison.lt(self, make(other))
    def __le__(self, other): return Comparison.le(self, make(other))
    def __eq__(self, other): return Comparison.eq(self, make(other))
    def __ne__(self, other): return Comparison.ne(self, make(other))
    def __ge__(self, other): return Comparison.ge(self, make(other))
    def __gt__(self, other): return Comparison.gt(self, make(other))
    def between(self, lo, hi): return Between(self, make(lo), make(hi))
    def in_range(self, first, afterlast):
        return And([
            Comparison.le(make(first), self),
            Comparison.lt(self, make(afterlast))])
    def in_(self, S): return make(S)._contains(self)
    def not_in_(self, S): return make(S)._not_contains(self)
    is_null = propattr(lambda self: IsNull(self))
    is_not_null = propattr(lambda self: NotNull(self))

class ExpressionList(Comparable, Containable):
    def __init__(self, exprs): self.exprs = exprs
    def __bool__(self): return bool(self.exprs)
    __nonzero__ = __bool__
    def __len__(self): return len(self.exprs)
    def __iter__(self): return iter(self.exprs)
    def __getitem__(self, i): return self.exprs[i]
    def emit(self, emitter): return emitter.ExpressionList(self._inners(emitter, self.exprs))

class Numeric(Comparable):
    def __neg__(self): return Neg(self)
    def __pos__(self): return Pos(self)
    def __abs__(self): return Call('ABS', [self])
    def __add__(self, other):
        if isinstance(other, Summarize): return other.__radd__(self)
        return Summarize([self, make(other)])
    def __radd__(self, other):
        if isinstance(other, Summarize): return other.__add__(self)
        return Summarize([make(other), self])
    def __sub__(self, other): return Sub(self, make(other))
    def __rsub__(self, other): return Sub(make(other), self)
    def __mul__(self, other):
        if isinstance(other, Multiply): return other.__rmul__(self)
        return Multiply([self, make(other)])
    def __rmul__(self, other):
        if isinstance(other, Multiply): return other.__mul__(self)
        return Multiply([make(other), self])
    def __div__(self, other): return Div(self, make(other))
    def __truediv__(self, other): return Div(self, make(other))
    def __rdiv__(self, other): return Div(make(other), self)
    def __rtruediv__(self, other): return Div(make(other), self)
    def __pow__(self, other): return Call('POWER', [self, make(other)])
    def __rpow__(self, other): return Call('POWER', [make(other), self])
    def __mod__(self, other): return Call('MOD', [self, make(other)])
    def __rmod__(self, other): return Call('MOD', [make(other), self])

class String(Comparable):
    def append(self, suffix):
        if isinstance(suffix, Concat): return suffix.prepend(self)
        return Concat([self, make(suffix)])
    def prepend(self, prefix):
        if isinstance(prefix, Concat): return prefix.append(self)
        return Concat([make(prefix), self])
    __add__ = append
    __radd__ = prepend
    def upper(self): return Call('UCASE', [self])
    def lower(self): return Call('LCASE', [self])
    def startswith(self, prefix): return self.like(make(prefix).append('%'))
    def endswith(self, suffix): return self.like(make(suffix).prepend('%'))
    def replace(self, old, new): return Call('REPLACE', [self, make(old), make(new)])
    def lstrip(self): return Call('LTRIM', [self])
    def rstrip(self): return Call('RTRIM', [self])
    def strip(self): return Call('TRIM', [self])
    def like(self, pattern, escape=NotImplemented):
        pattern = make(pattern)
        if escape is not NotImplemented: escape = make(escape)
        return Like(self, pattern, escape)

class DateTimePart(Numeric):
    (YEAR, MONTH, DAY, HOUR, MINUTE, SECOND, MICROSECOND) = range(7)
    (yearof, monthof, dayof, hourof, minuteof, secondof, microsecondof) = [
        (lambda p: staticmethod(lambda d: DateTimePart(make(d), p)))(p)
        for p in range(7)]
    def __init__(self, date, part):
        self.date = date
        self.part = part
    def emit(self, emitter):
        date = self._inner(emitter, self.date)
        return emitter.DateTimePart(date, self.part)

class DateTime(Comparable):
    def date(self): return self.daystart
    # part
    year = propattr(DateTimePart.yearof)
    month = propattr(DateTimePart.monthof)
    day = propattr(DateTimePart.dayof)
    hour = propattr(DateTimePart.hourof)
    minute = propattr(DateTimePart.minuteof)
    second = propattr(DateTimePart.secondof)
    microsecond = propattr(DateTimePart.microsecondof)
    # start
    def yearstart(self): return PeriodStart(self, DateTimePart.YEAR, 0)
    def monthstart(self): return PeriodStart(self, DateTimePart.MONTH, 0)
    def daystart(self): return PeriodStart(self, DateTimePart.DAY, 0)
    def hourstart(self): return PeriodStart(self, DateTimePart.HOUR, 0)
    def minutestart(self): return PeriodStart(self, DateTimePart.MINUTE, 0)
    def secondstart(self): return PeriodStart(self, DateTimePart.SECOND, 0)
    def microsecondstart(self): return PeriodStart(self, DateTimePart.MICROSECOND, 0)
    def yyyy_mm_dd(self, sep='-'): return YYYY_MM_DD(self, sep)
    def hh_mm_ss(self, sep=':'): return HH_MM_SS(self, sep)

class PeriodStart(DateTime):
    def __init__(self, date, part, offset):
        self.date = date
        self.part = part
        self.offset = make(offset)
    def next(self, offset=1): return PeriodStart(self.date, self.part, self.offset + offset)
    def prev(self, offset=1): return PeriodStart(self.date, self.part, self.offset - offset)
    def emit(self, emitter):
        date = self._inner(emitter, self.date)
        offset = self._inner(emitter, self.offset)
        return emitter.PeriodStart(date, self.part, offset)

class YYYY_MM_DD(String):
    def __init__(self, date, sep):
        self.date = date
        self.sep = sep
    def emit(self, emitter):
        date = self._inner(emitter, self.date)
        return emitter.YYYY_MM_DD(
            self._inner(emitter, self.date),
            self._inner(emitter, self.sep))

class HH_MM_SS(String):
    def __init__(self, date, sep):
        self.date = date
        self.sep = sep
    def emit(self, emitter):
        date = self._inner(emitter, self.date)
        return emitter.HH_MM_SS(
            self._inner(emitter, self.date),
            self._inner(emitter, self.sep))

class Generic(Numeric, String, Boolean, DateTime):
    def __add__(self, other):
        if isinstance(other, str): return String.__add__(self, other)
        return Numeric.__add__(self, other)
    def __radd__(self, other):
        if isinstance(other, str): return String.__radd__(self, other)
        return Numeric.__radd__(self, other)

class Parentheses(Generic):
    def __init__(self, x): self.x = x
    def emit(self, emitter):
        x = self._inner(emitter, self.x)
        return emitter.Parentheses(x)

class Constant(Generic):
    def __init__(self, constant):
        Generic.__init__(self)
        self.constant = constant
    def emit(self, emitter):
        return emitter.Constant(self.constant)

NULL = Constant(None)
TRUE = Constant(True)
FALSE = Constant(False)

class Value(Generic):
    def __init__(self, value):
        Generic.__init__(self)
        self.value = value
    def emit(self, emitter):
        return emitter.Value(self.value)

class Item(Generic):
    def __init__(self, name):
        Generic.__init__(self)
        self.name = name
    def emit(self, emitter):
        return emitter.Item(self.name)

class HostItem(Generic):
    def __init__(self, name):
        Generic.__init__(self)
        self.name = name
    def emit(self, emitter):
        return emitter.HostItem(self.name)

class Parameter(Generic):
    def __init__(self, name):
        Generic.__init__(self)
        self.name = name
    def emit(self, emitter):
        return emitter.Parameter(self.name)

class Call(Generic):
    def __init__(self, name, args):
        Generic.__init__(self)
        self.name = name
        self.args = args
    def emit(self, emitter):
        args = self._inners(emitter, self.args)
        return emitter.Call(self.name, args)

class Cast(Generic):
    def __init__(self, value, type):
        Generic.__init__(self)
        self.value = value
        self.type = type
    def emit(self, emitter):
        v = self._inner(emitter, self.value)
        return emitter.Cast(v, self.type)

class CaseBase(Generic):
    def _inner_cases(self, emitter):
        return [(self._inner(emitter, w),
                 self._inner(emitter, t))
                for (w, t) in self.cases]
    def _inner_else(self, emitter):
        return self._inner(emitter, self.whenelse)

class Case(CaseBase):
    def __init__(self, cases, whenelse):
        self.cases = cases
        self.whenelse = whenelse
    def emit(self, emitter):
        cases = self._inner_cases(emitter)
        whenelse = self._inner_else(emitter)
        return emitter.Case(cases, whenelse)

class Switch(CaseBase):
    def __init__(self, switch, cases, whenelse):
        self.switch = switch
        self.cases = cases
        self.whenelse = whenelse
    def emit(self, emitter):
        switch = self._inner(emitter, self.switch)
        cases = self._inner_cases(emitter)
        whenelse = self._inner_else(emitter)
        return emitter.Switch(switch, cases, whenelse)

class Neg(Numeric):
    def __init__(self, n):
        Numeric.__init__(self)
        self.n = n
    def emit(self, emitter):
        n = self._inner(emitter, self.n)
        return emitter.Neg(n)

class Pos(Numeric):
    def __init__(self, n):
        Numeric.__init__(self)
        self.n = n
    def emit(self, emitter):
        n = self._inner(emitter, self.n)
        return emitter.Pos(n)

class Summarize(Numeric):
    def __init__(self, N):
        Numeric.__init__(self)
        self.N = N
    def __add__(self, other):
        more = [make(other)] if not isinstance(other, Summarize) else other.N
        return Summarize(self.N + more)
    def __radd__(self, other):
        more = [make(other)] if not isinstance(other, Summarize) else other.N
        return Summarize(more + self.N)
    def emit(self, emitter):
        N = self._inners(emitter, self.N)
        return emitter.Summarize(N)

class Sub(Numeric):
    def __init__(self, n1, n2):
        Numeric.__init__(self)
        self.n1 = n1
        self.n2 = n2
    def emit(self, emitter):
        n1 = self._inner(emitter, self.n1)
        n2 = self._inner(emitter, self.n2)
        return emitter.Sub(n1, n2)

class Multiply(Numeric):
    def __init__(self, N):
        Numeric.__init__(self)
        self.N = N
    def __mul__(self, other):
        more = [make(other)] if not isinstance(other, Multiply) else other.N
        return Multiply(self.N + more)
    def __rmul__(self, other):
        more = [make(other)] if not isinstance(other, Multiply) else other.N
        return Multiply(more + self.N)
    def emit(self, emitter):
        N = self._inners(emitter, self.N)
        return emitter.Multiply(N)

class Div(Numeric):
    def __init__(self, n1, n2):
        Numeric.__init__(self)
        self.n1 = n1
        self.n2 = n2
    def emit(self, emitter):
        n1 = self._inner(emitter, self.n1)
        n2 = self._inner(emitter, self.n2)
        return emitter.Div(n1, n2)

class Concat(String):
    def __init__(self, S):
        String.__init__(self)
        self.S = S
    def append(self, other):
        more = [make(other)] if not isinstance(other, Concat) else other.S
        return Concat(self.S + more)
    def prepend(self, other):
        more = [make(other)] if not isinstance(other, Concat) else other.S
        return Concat(more + self.S)
    def emit(self, emitter):
        S = self._inners(emitter, self.S)
        return emitter.Concat(S)

class Comparison(Boolean):
    (LT, LE, EQ, NE, GE, GT) = range(6)
    (lt, le, eq, ne, ge, gt) = [
        (lambda i: staticmethod(lambda a, b: Comparison(i, a, b)))(i)
        for i in range(6)]
    OP_SQLS = { LT: '<', LE: '<=', EQ: '=', NE: '<>', GE: '>=', GT: '>' }
    OP_IDS = dict((v,k) for (k,v) in OP_SQLS.items())
    def __init__(self, op, a, b):
        Boolean.__init__(self)
        self.op = op
        self.a = a
        self.b = b
    def emit(self, emitter):
        a = self._inner(emitter, self.a)
        b = self._inner(emitter, self.b)
        return emitter.Comparison(self.op, a, b)

class Between(Boolean):
    def __init__(self, a, lo, hi):
        Boolean.__init__(self)
        self.a = a
        self.lo = lo
        self.hi = hi
    def emit(self, emitter):
        a = self._inner(emitter, self.a)
        lo = self._inner(emitter, self.lo)
        hi = self._inner(emitter, self.hi)
        return emitter.Between(a, lo, hi)

class IsNull(Boolean):
    def __init__(self, a):
        Boolean.__init__(self)
        self.a = a
    def emit(self, emitter):
        a = self._inner(emitter, self.a)
        return emitter.IsNull(a)

class NotNull(Boolean):
    def __init__(self, a):
        Boolean.__init__(self)
        self.a = a
    def emit(self, emitter):
        a = self._inner(emitter, self.a)
        return emitter.NotNull(a)

class IsIn(Boolean):
    def __init__(self, a, S):
        Boolean.__init__(self)
        self.a = a
        self.S = S
    def emit(self, emitter):
        a = self._inner(emitter, self.a)
        S = self._inner(emitter, self.S)
        return emitter.IsIn(a, S)

class NotIn(Boolean):
    def __init__(self, a, S):
        Boolean.__init__(self)
        self.a = a
        self.S = S
    def emit(self, emitter):
        a = self._inner(emitter, self.a)
        S = self._inner(emitter, self.S)
        return emitter.NotIn(a, S)

class Like(Boolean):
    def __init__(self, s, pattern, escape=NotImplemented):
        Boolean.__init__(self)
        self.s = s
        self.pattern = pattern
        self.escape = escape
    def emit(self, emitter):
        s = self._inner(emitter, self.s)
        pattern = self._inner(emitter, self.pattern)
        esc = self._inner(emitter, self.escape)
        return emitter.Like(s, pattern, esc)

class And(Boolean):
    def __init__(self, B):
        Boolean.__init__(self)
        self.B = B
    def _and_(self, other):
        more = [make(other)] if not isinstance(other, And) else other.B
        return And(self.B + more)
    def _rand_(self, other):
        more = [make(other)] if not isinstance(other, And) else other.B
        return And(more + self.B)
    def emit(self, emitter):
        B = self._inners(emitter, self.B)
        return emitter.And(B)

class Or(Boolean):
    def __init__(self, B):
        Boolean.__init__(self)
        self.B = B
    def _or_(self, other):
        more = [make(other)] if not isinstance(other, Or) else other.B
        return Or(self.B + more)
    def _ror_(self, other):
        more = [make(other)] if not isinstance(other, Or) else other.B
        return Or(more + self.B)
    def emit(self, emitter):
        B = self._inners(emitter, self.B)
        return emitter.Or(B)

class Not(Boolean):
    def __init__(self, b):
        Boolean.__init__(self)
        self.b = b
    def emit(self, emitter):
        b = self._inner(emitter, self.b)
        return emitter.Not(b)

class Now(DateTime):
    def emit(self, emitter): return emitter.Now()

class NextVal(Numeric):
    def __init__(self, sequence): self.sequence = sequence
    def emit(self, emitter): return emitter.NextVal(self.sequence)

class ComparableAspect(Composite, Comparable):
    def __init__(self, t): self.table = t

class AllValue(ComparableAspect):
    def compose(self, composer):
        self._compose_inner(composer, self.table)
        composer.AllValue()

class AnyValue(ComparableAspect):
    def compose(self, composer):
        self._compose_inner(composer, self.table)
        composer.AnyValue()

class Existence(Composite, Boolean):
    def __init__(self, t): self.table = t
    def compose(self, composer):
        self._compose_inner(composer, self.table)
        composer.Existence()

class Count(Composite, Numeric):
    def __init__(self, t): self.table = t
    def compose(self, composer):
        self._compose_inner(composer, self.table)
        composer.Count()

class Table(Composite, Generic, Containable):
    origin = None
    all = propattr(AllValue)
    any = propattr(AnyValue)
    exists = propattr(Existence)
    not_exists = propattr(lambda self: self.exists.not_)
    count = propattr(Count)
    def qualify(self): return Qualify(self)
    def alias(self, alias): return Alias(self, alias)
    def nest(self, alias=None): return Nest(self, alias)
    def include(self, *inclusions): return Include(self, inclusions)
    def exclude(self, *exclusions): return Exclude(self, exclusions)
    __call__ = include
    def rename(self, **renamings): return Rename(self, renamings)
    def where(self, *args, **kwargs):
        pred = where(*args, **kwargs)
        return Where(self, pred)
    def define(self, *args, **kwargs): return Define(self, deflist(*args, **kwargs))
    def redefine(self, *args, **kwargs): return Redefine(self, deflist(*args, **kwargs))
    def group(self, *groupbys): return Group(self, groupbys)
    def assign(self, **assignments): return Assign(self, dict(deflist(**assignments)))
    def union(self, other):
        other = make(other)
        if isinstance(other, Union): return other._runion(self)
        return Union([self, other])
    def innerjoin(self, right): return InnerJoin(self, make(right))
    def outerjoin(self, right): return OuterJoin(self, make(right))
    def crossjoin(self, right): return CrossJoin(self, make(right))
    def distinct(self): return Distinct(self)
    def orderby(self, *args): return OrderBy(self, args)
    def inserting(self, *labels, **settings):
        return Inserting(self, setlist(*labels, **settings))
    def updatingall(self, *labels, **settings):
        return UpdatingAll(self, setlist(*labels, **settings))
    def deletingall(self): return DeletingAll(self)
    def extending(self, extension): return Extending(self, extension)
    def merging(self, source, inserting=None): return Merging(self, make(source), make(inserting))

class Origin(Table):
    origin = property(lambda self: self)

class Derivative(Table):
    origin = propattr(lambda self: self.parent.origin)
    def __init__(self, parent): self.parent = parent

class Distinct(Derivative):
    def compose(self, composer):
        self._compose_inner(composer, self.parent)
        composer.Distinct()

class OrderBy(Derivative):
    orderbys = None  # [ expr ]
    def __init__(self, parent, orderbys):
        Derivative.__init__(self, parent)
        self.orderbys = orderbys
    def compose(self, composer):
        self._compose_inner(composer, self.parent)
        composer.OrderBy(self.orderbys)

class Slice(Derivative):
    def __init__(self, parent, first, afterlast):
        Derivative.__init__(self, parent)
        self.first = first
        self.afterlast = afterlast
    def compose(self, composer):
        self._compose_inner(composer, self.parent)
        composer.Slice(self.first, self.afterlast)

class Primary(Origin):
    def __init__(self, name): self.name = name
    def compose(self, composer): composer.Primary(self.name)

class Qualify(Origin):
    def __init__(self, parent): self.parent = parent
    def compose(self, composer):
        self._compose_inner(composer, self.parent)
        composer.Qualify()

class Alias(Origin):
    def __init__(self, parent, alias):
        self.parent = parent
        self.alias = alias
    def compose(self, composer):
        self._compose_inner(composer, self.parent)
        composer.Alias(self.alias)

class Nest(Origin):
    def __init__(self, parent, alias):
        self.parent = parent
        self.alias = alias
    def compose(self, composer):
        self._compose_inner(composer, self.parent)
        composer.Nest(self.alias)

class Include(Derivative):
    inclusions = None  # [ 'name' ]
    def __init__(self, parent, inclusions):
        Derivative.__init__(self, parent)
        self.inclusions = inclusions
    def compose(self, composer):
        self._compose_inner(composer, self.parent)
        composer.Include(self.inclusions)

class Exclude(Derivative):
    exclusions = None  # [ 'name' ]
    def __init__(self, parent, exclusions):
        Derivative.__init__(self, parent)
        self.exclusions = exclusions
    def compose(self, composer):
        self._compose_inner(composer, self.parent)
        composer.Exclude(self.exclusions)

class Arrange(Derivative):
    deflist = None
    deforder = None

class Rename(Arrange):
    renamings = None  # { 'old': 'name' }
    def __init__(self, parent, renamings):
        Arrange.__init__(self, parent)
        self.renamings = renamings
    def compose(self, composer):
        self._compose_inner(composer, self.parent)
        composer.Rename(self.renamings)

class Define(Arrange):
    deflist = None  # [('name', expr)]
    defdict = propattr(lambda self: dict(self.deflist))
    def __init__(self, parent, deflist):
        Arrange.__init__(self, parent)
        self.deflist = deflist
    def compose(self, composer):
        self._compose_inner(composer, self.parent)
        composer.Define(self.deflist)

class Redefine(Arrange):
    deflist = None  # [('name', expr)]
    defdict = propattr(lambda self: dict(self.deflist))
    def __init__(self, parent, deflist):
        Arrange.__init__(self, parent)
        self.deflist = deflist
    def compose(self, composer):
        self._compose_inner(composer, self.parent)
        composer.Redefine(self.deflist)

class Filter(Derivative):
    pass

class Where(Filter):
    def __init__(self, parent, predicate):
        Filter.__init__(self, parent)
        self.predicate = predicate
    def compose(self, composer):
        self._compose_inner(composer, self.parent)
        composer.Where(self.predicate)

class Group(Origin):
    groupbys = None  # ['name']
    def __init__(self, parent, groupbys):
        self.parent = parent
        self.groupbys = groupbys
    def compose(self, composer):
        self._compose_inner(composer, self.parent)
        composer.Group(self.groupbys)

class Assign(Derivative):
    assignments = None  # { 'name': expr }
    def __init__(self, parent, assignments):
        Derivative.__init__(self, parent)
        self.assignments = assignments
    def compose(self, composer):
        self._compose_inner(composer, self.parent)
        composer.Assign(self.assignments)

class Union(Origin):
    tables = None  # [ table ]
    def __init__(self, tables):
        self.tables = tables
    def union(self, other):
        more = [make(other)] if not isinstance(other, Union) else other.tables
        return Union(self.table + more)
    def _runion(self, other):
        more = [make(other)] if not isinstance(other, Union) else other.tables
        return Union(more + self.table)
    def compose(self, composer): composer.Union(self.tables)

class Join(Origin):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class InnerJoin(Join):
    def compose(self, composer):
        self._compose_inner(composer, self.left)
        composer.InnerJoin(self.right)

class OuterJoin(Join):
    def compose(self, composer):
        self._compose_inner(composer, self.left)
        composer.OuterJoin(self.right)

class CrossJoin(Join):
    def compose(self, composer):
        self._compose_inner(composer, self.left)
        composer.CrossJoin(self.right)

class Manipulation(Composite):
    def __init__(self, table):
        self.table = table

class Inserting(Manipulation):
    setlist = None  # [('name', expr)]
    setdict = propattr(lambda self: dict(self.setlist))
    def __init__(self, table, setlist):
        Manipulation.__init__(self, table)
        self.setlist = setlist
    def compose(self, composer):
        self._compose_inner(composer, self.table)
        composer.Inserting(self.setlist)

class UpdatingAll(Manipulation):
    setlist = None  # [('name', expr)]
    setdict = propattr(lambda self: dict(self.setlist))
    def __init__(self, table, setlist):
        Manipulation.__init__(self, table)
        self.setlist = setlist
    def compose(self, composer):
        self._compose_inner(composer, self.table)
        composer.UpdatingAll(self.setlist)

class DeletingAll(Manipulation):
    def compose(self, composer):
        self._compose_inner(composer, self.table)
        composer.DeleteAll()

class Extending(Manipulation):
    def __init__(self, table, extension):
        Manipulation.__init__(self, table)
        self.extension = extension
    def compose(self, composer):
        self._compose_inner(composer, self.table)
        composer.Extending(self.extension)

class Merging(Manipulation):
    def __init__(self, table, source, inserting):
        Manipulation.__init__(self, table)
        self.source = source
        self.inserting = inserting
    def compose(self, composer):
        self._compose_inner(composer, self.table)
        composer.Merging(self.source, self.inserting)
