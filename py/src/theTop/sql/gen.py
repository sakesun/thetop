#! -*- coding: utf-8 -*-

import decimal
from functools import cached_property
from .. import util
from ..nullable import nullop
from ..model import models
from ..gen import structure, commandment

CONST_REPRS = {}
TYPE_REPRS = {}

def atomic(x):
    return isinstance(x, (
        models.ExpressionList,
        models.Parentheses,
        models.Constant,
        models.Value,
        models.Item,
        models.HostItem,
        models.Parameter,
        models.Call,
        models.Cast))

def simplechain(x, outer):
    sumsub = (models.Summarize, models.Sub)
    muldiv = (models.Multiply, models.Div)
    if (not (isinstance(x, sumsub) and isinstance(outer, sumsub))) and \
       (not (isinstance(x, muldiv) and isinstance(outer, muldiv))):
        return False
    left = None
    if isinstance(outer, (models.Summarize, models.Multiply)): left = outer.N[0]
    if isinstance(outer, (models.Sub, models.Div)): left = outer.n1
    return (x is left)

def sql_string(s): return "'" + s.replace("'", "''") + "'"

def sql_repr(x):
    if hasattr(x, '__sqlrepr__'): return x.__sqlrepr__()
    if nullop.isnull(x): return 'NULL'
    if isinstance(x, str): return sql_string(x)
    if isinstance(x, decimal.Decimal): return str(x)
    return repr(x)

class Dialect(object):
    TAB = '  '
    LOCK_SUPPORT = False
    LOCK_SELECT_ENDING = None
    LOCK_TABLE_ENDING = None
    DUAL_TABLE = None
    USE_AS_FOR_SOURCE_ALIAS = False
    USE_AS_FOR_RESULT_ALIAS = True
    USE_JOIN_CLAUSE = True
    USE_ORACLE_LEGACY_OUTER_JOIN = False
    USE_ROWNUM = False
    USE_LIMIT_OFFSET = True
    USE_ROWCOUNT = False
    USE_ANALYTIC_ROW_NUMBER = False
    BIND_BY_NAME = True
    PARAM_PREFIX = ':'
    CONCAT_BY_FUNCTION = True
    CONCAT_FUNCTION_MULTIARGS = True
    CONCAT_OPERATOR = '||'
    MULTI_COLUMNS_IN = False
    SQL_NOW = '{fn Now()}'
    TYPE_REPRS = None
    CONST_REPRS = None
    NEXTVAL_TEMPLATE = '%s.NEXTVAL'
    UNIQUE_QUALIFIERS = False

class SqlEmitterBase(models.Emitter):
    dialect = None
    def keyword(self, s): raise NotImplementedError()
    def line(self, *args): raise NotImplementedError()
    def join(self, sep, S): raise NotImplementedError()
    def QualifiedItem(self, qualifier, name): raise NotImplementedError()

class SqlEmitterDecorator(SqlEmitterBase, models.EmitterDecorator):
    dialect = cached_property(lambda self: self.decorated.dialect)
    def __init__(self, decorated):
        assert isinstance(decorated, SqlEmitterBase)
        self.decorated = decorated
    def keyword(self, s): return self.decorated.keyword(s)
    def line(self, *args): return self.decorated.line(*args)
    def join(self, sep, S): return self.decorated.join(sep, S)
    def QualifiedItem(self, qualifier, name): return self.decorated.QualifiedItem(qualifier, name)

class QualifyingDecorator(SqlEmitterDecorator):
    qualifier = None
    def __init__(self, decorated, qualifier=None):
        SqlEmitterDecorator.__init__(self, decorated)
        self.qualifier = qualifier
    def Item(self, name):
        q = self.qualifier
        return self.QualifiedItem(q, name) if q else self.decorated.Item(name)

class InclusionDecorator(SqlEmitterDecorator):
    def __init__(self, decorated, inclusions):
        SqlEmitterDecorator.__init__(self, decorated)
        self.inclusions = inclusions
    def Item(self, name):
        if name not in self.inclusions: raise util.NotFound('Cannot find label: ' + name)
        return SqlEmitterDecorator.Item(self, name)

class ExclusionDecorator(SqlEmitterDecorator):
    def __init__(self, decorated, exclusions):
        SqlEmitterDecorator.__init__(self, decorated)
        self.exclusions = exclusions
    def Item(self, name):
        if name in self.exclusions: raise util.NotFound('Cannot find label: ' + name)
        return SqlEmitterDecorator.Item(self, name)

class ItemDefDecorator(SqlEmitterDecorator):
    def __init__(self, decorated, defdict):
        SqlEmitterDecorator.__init__(self, decorated)
        self.defdict = defdict
    def ambiguous(self, x, outer):
        if isinstance(x, models.Item): x = self.defdict.get(x.name, x)
        return self.decorated.ambiguous(x, outer)
    def Item(self, name):
        d = self.defdict.get(name)
        return self.decorated.Item(name) \
               if d is None \
               else d.emit(self.decorated)

class RenameDecorator(SqlEmitterDecorator):
    def __init__(self, decorated, renamings):
        SqlEmitterDecorator.__init__(self, decorated)
        self.new2old = dict((v, k) for (k, v) in renamings.items())
    def Item(self, name):
        n = self.new2old.get(name, name)
        return self.decorated.Item(n)

class ParamSubstDecorator(SqlEmitterDecorator):
    def __init__(self, decorated, paramdict):
        SqlEmitterDecorator.__init__(self, decorated)
        self.paramdict = paramdict
    def ambiguous(self, x, outer):
        if isinstance(x, models.Parameter): x = self.paramdict.get(x.name, x)
        return self.decorated.ambiguous(x, outer)
    def Parameter(self, name):
        d = self.paramdict.get(name)
        return self.decorated.Parameter(name) \
               if d is None \
               else d.emit(self.decorated)

class CheckCompositeEmitter(models.NoneEmitter):
    sofar = 0
    grouped = False
    terminated = property(lambda self: (self.sofar > 1))
    def composer(self):
        self.sofar += 1
        return CheckCompositeComposer(self)

class CheckCompositeComposer(models.NoneComposer):
    def Nest(self, alias):
        if self.emitter.terminated: return
        self.emitter.sofar += 1
        models.NoneComposer.Nest(self, alias)
    def Group(self, groupbys):
        if self.emitter.grouped:
            self.emitter.sofar += 1
            assert self.emitter.terminated
        else:
            self.emitter.grouped = True
            models.NoneComposer.Group(self, groupbys)

def has_many_composites(m):
    emt = CheckCompositeEmitter()
    m.emit(emt)
    assert emt.sofar <= 2
    return emt.sofar > 1

class ContentEmitterDecorator(QualifyingDecorator):
    def __init__(self, content):
        QualifyingDecorator.__init__(self, content.rootemt, None)
        self.content = content
    def HostItem(self, name): return self.content.hostemt.Item(name)
    def composer(self): return SqlComposer(self.content.guest())

class SqlContent(object):
    rootemt = None
    def emit(self): raise NotImplementedError()
    def allvalue(self): raise NotImplementedError()
    def anyvalue(self): raise NotImplementedError()
    def existence(self): raise NotImplementedError()
    def count(self): raise NotImplementedError()
    def distinct(self): raise NotImplementedError()
    def orderby(self, orderbys): raise NotImplementedError()
    def slice(self, first, afterlast): raise NotImplementedError()
    def primary(self, name): raise NotImplementedError()
    def qualify(self): raise NotImplementedError()
    def alias(self, alias): raise NotImplementedError()
    def nest(self, alias): raise NotImplementedError()
    def include(self, inclusions): raise NotImplementedError()
    def exclude(self, exclusions): raise NotImplementedError()
    def rename(self, renamings): raise NotImplementedError()
    def define(self, deflist): raise NotImplementedError()
    def redefine(self, deflist): raise NotImplementedError()
    def where(self, predicate): raise NotImplementedError()
    def group(self, groupbys): raise NotImplementedError()
    def assign(self, assignments): raise NotImplementedError()
    def union(self, tables): raise NotImplementedError()
    def innerjoin(self, right): raise NotImplementedError()
    def outerjoin(self, right): raise NotImplementedError()
    def crossjoin(self, right): raise NotImplementedError()
    def inserting(self, setlist): raise NotImplementedError()
    def updatingall(self, setlist): raise NotImplementedError()
    def deletingall(self): raise NotImplementedError()
    def extending(self, extension): raise NotImplementedError()
    def merging(self, source, inserting): raise NotImplementedError()

class SqlQuery(SqlContent):
    def __init__(self, rootemt, host, hostemt):
        assert ((host is None) and (hostemt is None)) or \
               ((host is not None) and (hostemt is not None))
        self.rootemt = rootemt
        self.host = host
        self.hostemt = hostemt
    def get_labels(self): raise NotImplementedError()
    def alias_proposal(self): return 't'
    def emit(self): raise NotImplementedError()

class SqlUnion(SqlQuery):
    def __init__(self, rootemt, host, hostemt, selects):
        SqlQuery.__init__(self, rootemt, host, hostemt)
        self.selects = selects
    def get_labels(self): return self.selects[0].get_labels()
    def emit(self):
        r = structure.Roster()
        for s in self.selects:
            if r: r.line('\n', self.rootemt.keyword('union'), ' ', self.rootemt.keyword('all'), '\n')
            r.add(s.emit())
        return r
    def allvalue(self): raise NotImplementedError()
    def anyvalue(self): raise NotImplementedError()
    def existence(self): raise NotImplementedError()
    def count(self): raise NotImplementedError()
    def distinct(self): raise NotImplementedError()
    def orderby(self, orderbys): raise NotImplementedError()
    def slice(self, first, afterlast): raise NotImplementedError()
    def primary(self, name): raise NotImplementedError()
    def qualify(self): raise NotImplementedError()
    def alias(self, alias): raise NotImplementedError()
    def nest(self, alias): raise NotImplementedError()
    def include(self, inclusions): raise NotImplementedError()
    def exclude(self, exclusions): raise NotImplementedError()
    def rename(self, renamings): raise NotImplementedError()
    def define(self, deflist): raise NotImplementedError()
    def redefine(self, deflist): raise NotImplementedError()
    def where(self, predicate): raise NotImplementedError()
    def group(self, groupbys): raise NotImplementedError()
    def assign(self, assignments): raise NotImplementedError()
    def union(self, tables): raise NotImplementedError()
    def innerjoin(self, right): raise NotImplementedError()
    def outerjoin(self, right): raise NotImplementedError()
    def crossjoin(self, right): raise NotImplementedError()
    def inserting(self, setlist): raise NotImplementedError()
    def updatingall(self, setlist): raise NotImplementedError()
    def deletingall(self): raise NotImplementedError()
    def extending(self, extension): raise NotImplementedError()
    def merging(self, source, inserting): raise NotImplementedError()

class SqlSelect(SqlQuery):
    labels = None                           # ('label',)
    contentemt = None                       # ContentEmitterDecorator
    currentemt = None                       # Emitter
    principal_qualifier_finalized = False
    def __init__(self, rootemt, host, hostemt):
        SqlQuery.__init__(self, rootemt, host, hostemt)
        self.contentemt = ContentEmitterDecorator(self)
        self.currentemt = self.contentemt \
                          if self.hostemt is None else \
                          SqlCompositeEmitter(self.contentemt, self.hostemt)
        self.aliasings = set()              # set(['label'])
        self.principal_table = None         # 'table'
        self.principal_query = None         # SqlQuery
        self.principal_alias = None         # 'alias'
        self.joins = []                     # [SqlJoin]
        self.wheres = []                    # [(emitter, predicate)]
        self.groupbys = None                # (emitter, ['label'])
        self.havings = []                   # [(emitter, predicate)]
        self.orderbys = []                  # [(emitter, expr)]
        self.select_distinct = False
        self.first = None
        self.afterlast = None
        self.qualifiers = set()
    def guest(self): return SqlSelect(self.rootemt, self, self.currentemt)
    def finalize_guest_principal_qualifier(self, guest):
        self.finalize_principal_qualifier()
        if self.rootemt.qualify_whatever: return
        if self.dialect.UNIQUE_QUALIFIERS:
            self.rootemt.finalize_principal_qualifier(guest)
        else:
            guest.qualify()
            qualifier = guest.contentemt.qualifier
            assert qualifier
            if qualifier in self.qualifiers:
                alias = qualifier
                sep = '_' if qualifier[-1].isdigit() else ''
                index = 1
                while alias in self.qualifiers:
                    index += 1
                    alias = qualifier + sep + str(index)
                guest.alias(alias)
                assert guest.contentemt.qualifier == alias
            assert self.contentemt.qualifier not in self.qualifiers
            self.qualifiers.add(self.contentemt.qualifier)
    def finalize_principal_qualifier(self):
        if self.principal_qualifier_finalized: return
        if self.host is None:
            self.rootemt.finalize_principal_qualifier(self)
        else:
            self.host.finalize_guest_principal_qualifier(self)
        self.principal_qualifier_finalized = True
    def get_labels(self):
        if self.labels is None:
            if self.principal_table is not None:
                self.labels = self.rootemt.get_table_labels(self.principal_table)
            if self.principal_query is not None:
                self.labels = self.principal_query.get_labels()
        return self.labels
    def alias_proposal(self):
        if self.principal_table: return self.principal_table
        if self.principal_query: return self.principal_query.alias_proposal()
        return SqlQuery.alias_proposal(self)
    def emit(self):
        self.finalize_principal_qualifier()
        r = structure.Roster()
        # select
        title = self.rootemt.keyword('select')
        if self.select_distinct: title += (' ' + self.rootemt.keyword('distinct'))
        lst = r.titled(title).list(',')
        self.fill_selection(lst)
        if not lst: lst.line('*')
        # from
        lst = structure.List(',')
        frm = r
        self.fill_sources(lst)
        if lst:
            frm = r.titled(self.rootemt.keyword('from'))
            frm.add(lst)
        # join
        self.fill_join_clauses(frm)
        # where
        lst = structure.List(self.rootemt.keyword('and'))
        self.fill_wheres(lst)
        if lst: r.titled(self.rootemt.keyword('where')).add(lst)
        # group by
        lst = structure.List(',')
        self.fill_groupbys(lst)
        if lst: r.titled(self.rootemt.keyword('group') + ' ' + self.rootemt.keyword('by')).add(lst)
        # having
        lst = structure.List(self.rootemt.keyword('and'))
        self.fill_havings(lst)
        if lst: r.titled(self.rootemt.keyword('having')).add(lst)
        # order by
        lst = structure.List(',')
        self.fill_orderbys(lst)
        if lst: r.titled(self.rootemt.keyword('order') + ' ' + self.rootemt.keyword('by')).add(lst)
        return r
    def fill_selection(self, lst):
        labels = self.get_labels()
        if labels is None: return
        for n in labels:
            item = models.Item(n).emit_part(self.currentemt)
            if n not in self.aliasings: lst.line(item)
            else:
                if self.rootemt.dialect.USE_AS_FOR_RESULT_ALIAS:
                    lst.line(item, ' ', self.rootemt.keyword('as'), ' ', n)
                else:
                    lst.line(item, ' ', n)
    def emit_principal_source(self):
        ln = structure.Line()
        suffix = ''
        if self.principal_alias:
            suffix = (' ' + self.principal_alias)
            if self.rootemt.dialect.USE_AS_FOR_SOURCE_ALIAS:
                suffix = (' ' + self.emitter.keyword('as') + suffix)
        if self.principal_table is not None:
            assert self.principal_query is None
            ln.word(self.principal_table)
        if self.principal_query is not None:
            assert self.principal_table is None
            ln.scope('(', ')').line(self.principal_query.emit())
            assert suffix
        if ln and suffix: ln.word(suffix)
        return ln
    def fill_sources(self, lst):
        ln = self.emit_principal_source()
        if ln: lst.line(ln)
        for j in self.joins:
            j.fill_join_source(lst)
    def fill_join_clauses(self, r):
        for j in self.joins:
            j.fill_join_clause(r)
    def fill_wheres(self, lst):
        for (emt, pred) in self.wheres:
            lst.line(pred.emit_part(emt))
    def fill_groupbys(self, lst):
        pass
    def fill_havings(self, lst):
        pass
    def fill_orderbys(self, lst):
        pass
    def allvalue(self): raise NotImplementedError()
    def anyvalue(self): raise NotImplementedError()
    def existence(self): raise NotImplementedError()
    def count(self): raise NotImplementedError()
    def distinct(self):
        # assert not self.distinct, 'Cannot distinct twice'
        # assert (self.first is None) and (self.afterlast is None), \
        #        'Cannot distinct slice query'
        # self.assert_select()
        # self.distinct = True
        raise NotImplementedError()
    def orderby(self, orderbys):
        # self.assert_select()
        # raise NotImplementedError()
        raise NotImplementedError()
    def slice(self, first, afterlast):
        assert not self.select_distinct, 'Cannot slice distinct query'
        if self.first is not None:
            if first is not None: first += self.first
            if afterlast is not None: afterlast += self.first
        if first is not None: self.first = first
        if afterlast is not None:
            if self.afterlast is None: self.afterlast = afterlast
            else: self.afterlast = min(self.afterlast, afterlast)
        raise NotImplementedError()
    def primary(self, name):
        assert (self.principal_table is None) and (self.principal_query is None)
        if not name: raise Exception('Empty table name is not allowed')
        self.principal_table = name
        return self
    def qualify(self):
        if not self.contentemt.qualifier:
            assert self.principal_table
            assert not self.principal_alias
            assert self.principal_query is None
            self.contentemt.qualifier = self.principal_table
        return self
    def alias(self, alias):
        self.contentemt.qualifier = alias
        self.principal_alias = alias
        return self
    def nest(self, alias=None):
        select = SqlSelect(self.rootemt, self.host, self.hostemt)
        select.principal_query = self
        alias = alias if alias else self.alias_proposal()
        select.contentemt.qualifier = alias
        select.principal_alias = alias
        return select
    def include(self, inclusions):
        labels = self.get_labels()
        if labels is not None: check_illegal_labels(labels, inclusions)
        self.labels = tuple(inclusions)
        return self
    def exclude(self, exclusions):
        labels = self.get_labels()
        check_illegal_labels(labels, exclusions)
        self.labels = tuple(n for n in labels if n not in exclusions)
        return self
    def rename(self, renamings):
        newemt = RenameDecorator(self.currentemt, renamings)
        labels = models.renamed_labels(self.get_labels(), renamings)
        self.currentemt = newemt
        self.labels = labels
        self.aliasings.update(renamings.values())
        return self
    def define(self, deflist):
        newemt = ItemDefDecorator(self.currentemt, dict(deflist))
        labels = models.defined_labels(self.get_labels(), deflist)
        aliases = [k for (k, v) in deflist]
        self.currentemt = newemt
        self.labels = labels
        self.aliasings.update(aliases)
        return self
    def redefine(self, deflist):
        newemt = ItemDefDecorator(self.currentemt, dict(deflist))
        labels = models.defined_labels((), deflist)
        aliases = [k for (k, v) in deflist]
        self.currentemt = newemt
        self.labels = labels
        self.aliasings.update(aliases)
        return self
    def where(self, predicate):
        if not self.groupbys:
            self.wheres.append((self.currentemt, predicate))
        else:
            self.havings.append((self.currentemt, predicate))
        return self
    def group(self, groupbys):
        if self.groupbys: return self.nest().group(groupbys)
        labels = tuple(groupbys)
        self.groupbys = (self.currentemt, labels)
        self.labels = labels
        return self
    def assign(self, assignments): raise NotImplementedError()
    def union(self, tables): raise NotImplementedError()
    def innerjoin(self, right): raise NotImplementedError()
    def outerjoin(self, right): raise NotImplementedError()
    def crossjoin(self, right): raise NotImplementedError()
    def inserting(self, setlist): raise NotImplementedError()
    def updatingall(self, setlist): raise NotImplementedError()
    def deletingall(self): raise NotImplementedError()
    def extending(self, extension): raise NotImplementedError()
    def merging(self, source, inserting): raise NotImplementedError()

class SqlJoin(SqlContent):
    rootemt = property(lambda self: self.select.rootemt)
    JOIN_CLAUSE_PREFIX = None
    def __init__(self, select):
        assert not select.joins
        self.select = select
    def fill_join_source(self, lst):
        if self.rootemt.dialect.USE_JOIN_CLAUSE: return
        self.select.finalize_principal_qualifier()
        ln = self.select.emit_principal_source()
        if ln: lst.line(ln)
    def fill_join_clause(self, r):
        if not self.rootemt.dialect.USE_JOIN_CLAUSE: return
        self.select.finalize_principal_qualifier()
        ln = r.line(self.JOIN_CLAUSE_PREFIX)
        ln.word(' ', self.select.emit_principal_source())
        pred = self.emit_join_predicate()
        if pred: ln.word(' ', self.rootemt.keyword('on'), ' ', pred)
    def emit_join_predicate(self):
        ln = structure.Line()
        return ln

class SqlInnerJoin(SqlJoin):
    JOIN_CLAUSE_PREFIX = cached_property(lambda self: self.rootemt.keyword('join'))

class SqlOuterJoin(SqlJoin):
    JOIN_CLAUSE_PREFIX = cached_property(lambda self: (
        self.rootemt.keyword('left') + ' ' +
        self.rootemt.keyword('outer') + ' ' +
        self.rootemt.keyword('join')))

class SqlCrossJoin(SqlJoin):
    JOIN_CLAUSE_PREFIX = cached_property(lambda self: (
        self.rootemt.keyword('cross') + ' ' +
        self.rootemt.keyword('join')))
    def emit_join_predicate(self):
        # assert there is no hostitem
        return None

class SqlCommand(SqlContent):
    rootemt = property(lambda self: self.selects[0].rootemt)
    def __init__(self, select): self.select = select
    def emit_command(self): raise NotImplementedError()

class SqlInsert(SqlContent):
    def emit_command(self):
        # sub = w.text('insert', 'into', self.tablename()).scope('(', ')').list(',')
        # for k in settings.keys(): sub.text(k)
        # sub = w.text('values').scope('(', ')').list(',')
        # for v in settings.values(): sub.text(totext(v))
        ...

class SqlUpdate(SqlContent):
    def emit_command(self):
        # w.text('update', self.tablename())
        # sub = w.titled('set').list(',')
        # for (k,v) in settings.items(): sub.text(k, '=', f(v))
        # if self.wheres:
        #     sub = w.titled('where').list('and')
        #     #for x in self.wheres: sub.text(f(x))
        #     pass
        ...

class SqlDelete(SqlContent):
    def emit_command(self):
        # w.text('delete', 'from', self.tablename())
        # sub = w.titled('where').list('and')
        # for x in self.wheres: sub.text(f(x))
        ...

class SqlExtend(SqlContent):
    def emit_command(self):
        # w.text('insert', 'into', self.tablename())
        # sub = w.scope('(', ')').list(',')
        # for x in table..labels: sub.text(x)
        # sub.block().text(subquery(table))
        ...

class SqlMerge(SqlContent):
    pass

class SqlEmitter(SqlEmitterBase):
    dialect = None
    keyword = staticmethod(lambda s: s.upper())
    line = structure.Line
    join = staticmethod(structure.Line.join)
    qualify_whatever = False
    def QualifiedItem(self, qualifier, name): return self.line(qualifier, '.', name)
    def __init__(self, dialect=None):
        self.dialect = (dialect if dialect else Dialect())
        self.qualifiers = set()
    def emit_model(self, model):
        self.qualify_whatever = not has_many_composites(model)
        return SqlEmitterBase.emit_model(self, model)
    def finalize_principal_qualifier(self, select):
        if self.qualify_whatever: return
        select.qualify()
        qualifier = select.contentemt.qualifier
        assert qualifier
        if qualifier in self.qualifiers:
            alias = qualifier
            sep = '_' if qualifier[-1].isdigit() else ''
            index = 1
            while alias in self.qualifiers:
                index += 1
                alias = qualifier + sep + str(index)
            select.alias(alias)
            assert select.contentemt.qualifier == alias
        self.qualifiers.add(select.contentemt.qualifier)
    def get_table_labels(self, name): return None
    def type_repr(self, t):
        def custom(reprs, t):
            if reprs is None: return None
            r = reprs.get(t)
            if r is None: return None
            return r(t)
        x = custom(self.dialect.TYPE_REPRS, t)
        if x is not None: return x
        x = custom(TYPE_REPRS, t)
        if x is not None: return x
        if hasattr(t, '__sqlrepr__'): return x.__sqlrepr__()
        x = getattr(t, '__name__')
        if x is not None: return x
        return str(t)
    def const_repr(self, c):
        if nullop.isnull(c): return self.keyword('null')
        def custom(reprs, v):
            if reprs is None: return None
            r = reprs.get(type(v))
            if r is None: return None
            return r(v)
        x = custom(self.dialect.CONST_REPRS, c)
        if x is not None: return x
        x = custom(CONST_REPRS, c)
        if x is not None: return x
        return sql_repr(c)
    def sql_repr(self, x): return sql_repr(x)
    def ambiguous(self, x, outer):
        if isinstance(outer, models.Parentheses): return False
        if isinstance(x, models.Composite):
            unambiguouses = (models.ComparableAspect, models.Exists, models.Count)
            if not isinstance(x, unambiguouses): return True
        if simplechain(x, outer): return False
        if isinstance(outer, models.Call): return False
        return not self.atomic(x)
    def atomic(self, x):
        if self.dialect.CONCAT_BY_FUNCTION and isinstance(x, models.Concat): return True
        return atomic(x)
    def composer(self): return SqlComposer(SqlSelect(self, None, None))
    def ExpressionList(self, S): return self.Parentheses(self.join(', ', S))
    def DateTimePart(self, date, part): raise NotImplementedError()
    def PeriodStart(self, date, part, offset): raise NotImplementedError()
    def YYYY_MM_DD(self, date, sep): raise NotImplementedError()
    def HH_MM_SS(self, date, sep): raise NotImplementedError()
    def Parentheses(self, x): return self.line('(', x, ')')
    def Constant(self, c): return self.line(self.const_repr(c))
    def Value(self, v): return self.Constant(v)
    def Item(self, name): return self.line(name)
    def HostItem(self, name): raise NotImplementedError()
    def Parameter(self, name): return self.line(self.dialect.PARAM_PREFIX + name)
    def Call(self, name, args): return self.line(name, '(', self.join(', ', args), ')')
    def Cast(self, value, t):
        if isinstance(t, type): t = self.type_repr(t)
        return self.line(self.keyword('cast'), '(', self.join(' ', [value, self.keyword('as'), t]), ')')
    def Case(self, cases, whenelse):
        r = structure.Roster()
        s = r.section()
        s.header.line(self.keyword('case'))
        for (w, t) in cases:
            s.content.line(self.keyword('when'), ' ', w, ' ', self.keyword('then'), ' ', t)
        if not (whenelse is NotImplemented):
            s.content.line(self.keyword('else'), ' ', whenelse)
        r.line(self.keyword('end'))
        return r
    def Switch(self, switch, cases, whenelse):
        r = structure.Roster()
        s = r.section()
        s.header.line(self.keyword('case'), ' ', switch)
        for (w, t) in cases:
            s.content.line(self.keyword('when'), ' ', w, ' ', self.keyword('then'), ' ', t)
        if not (whenelse is NotImplemented):
            s.content.line(self.keyword('else'), ' ', whenelse)
        r.line(self.keyword('end'))
        return r
    def Neg(self, n): return self.line('-', n)
    def Pos(self, n): return self.line('+', n)
    def Summarize(self, N): return self.join(' + ', N)
    def Sub(self, n1, n2): return self.line(n1, ' - ', n2)
    def Multiply(self, N): return self.join(' * ', N)
    def Div(self, n1, n2): return self.line(n1, ' / ', n2)
    def Concat(self, S):
        return self.concat_by_function(S) \
               if self.dialect.CONCAT_BY_FUNCTION \
               else self.concat_by_operator(S)
    def concat_by_function(self, S):
        S = tuple(S)
        if len(S) == 0: return None
        if len(S) == 1: return S[0]
        if len(S) == 2: return self.Call(self.keyword('concat'), S)
        if self.dialect.CONCAT_FUNCTION_MULTIARGS: return self.Call(self.keyword('concat'), S)
        return self.Concat([self.Concat(S[:-1]), S[-1]])
    def concat_by_operator(self, S):
        return self.join(' ' + self.dialect.CONCAT_OPERATOR + ' ', S)
    def Comparison(self, op, a, b):
        return self.join(' ', [a, models.Comparison.OP_SQLS[op], b])
    def Between(self, a, lo, hi):
        return self.join(' ', [a, self.keyword('between'), lo, self.keyword('and'), hi])
    def IsNull(self, a):
        return self.join(' ', [a, self.keyword('is'), self.keyword('null')])
    def NotNull(self, a):
        return self.join(' ', [a, self.keyword('is'), self.keyword('not'), self.keyword('null')])
    def IsIn(self, a, S):
        return self.join(' ', [a, self.keyword('in'), S])
    def NotIn(self, a, S):
        return self.join(' ', [a, self.keyword('not'), self.keyword('in'), S])
    def Like(self, s, pattern, escape):
        items = [s, self.keyword('like'), pattern]
        if (escape is not None) and (escape is not NotImplemented):
            items.append(self.keyword('escape'))
            items.append(escape)
        return self.join(' ', items)
    def And(self, B): return self.join(' ' + self.keyword('and') + ' ', B)
    def Or(self, B): return self.join(' ' + self.keyword('or') + ' ', B)
    def Not(self, b): return self.line(self.keyword('not'), ' ', b)
    def Now(self): return self.line(self.dialect.SQL_NOW)
    def NextVal(self, sequence): return self.line(self.dialect.NEXTVAL_TEMPLATE % sequence)

class SqlComposer(models.Composer):
    def __init__(self, content): self.content = content
    def emit(self): return self.content.emit()
    def AllValue(self): self.content = self.content.allvalue()
    def AnyValue(self): self.content = self.content.anyvalue()
    def Existence(self): self.content = self.content.existence()
    def Count(self): self.content = self.content.count()
    def Distinct(self): self.content = self.content.distinct()
    def OrderBy(self, orderbys): self.content = self.content.orderby(orderbys)
    def Slice(self, first, afterlast): self.content = self.content.slice(first, afterlast)
    def Primary(self, name): self.content = self.content.primary(name)
    def Qualify(self): self.content = self.content.qualify()
    def Alias(self, alias): self.content = self.content.alias(alias)
    def Nest(self, alias): self.content = self.content.nest(alias)
    def Include(self, inclusions): self.content = self.content.include(inclusions)
    def Exclude(self, exclusions): self.content = self.content.exclude(exclusions)
    def Rename(self, renamings): self.content = self.content.rename(renamings)
    def Define(self, deflist): self.content = self.content.define(deflist)
    def Redefine(self, deflist): self.content = self.content.redefine(deflist)
    def Where(self, predicate): self.content = self.content.where(predicate)
    def Group(self, groupbys): self.content = self.content.group(groupbys)
    def Assign(self, assignments): self.content = self.content.Assign(assignments)
    def Union(self, tables): self.content = self.content.union(tables)
    def InnerJoin(self, right): self.content = self.content.innerjoin(right.content)
    def OuterJoin(self, right): self.content = self.content.outerjoin(right.content)
    def CrossJoin(self, right): self.content = self.content.crossjoin(right.content)
    def Inserting(self, setlist): self.content = self.content.inserting(setlist)
    def UpdatingAll(self, setlist): self.content = self.content.updatingall(setlist)
    def DeletingAll(self): self.content = self.content.deletingall()
    def Extending(self, extension): self.content = self.content.extending(extension.content)
    def Merging(self, source, inserting):
        ins = None if inserting is None else inserting.content
        self.content = self.content.merging(source.content, ins)

class SqlCompositeEmitter(models.EmitterDecorator):
    def __init__(self, dialect, composer):
        models.EmitterDecorator.__init__(self, composer.rootemt)
        self.composer = composer
    def composite_qualifier(self, qualifier): return self.composer.guest_qualifier(qualifier)
    def Item(self, name):
        if isinstance(self.table, models.Primary):
            return models.EmitterDecorator.Item(self, name)
        return self.line(name)
    def HostItem(self, name):
        return self.composer.emitter.Item(name)

def check_illegal_labels(labels, checkings):
    illegals = [n for n in checkings if n not in labels]
    if illegals: raise KeyError('Illegal labels: "%s"' % repr(illegals))

# class DialectEmitter(models.SqlExpressionEmitter):
#     BIND_BY_NAME = property(lambda self: self.dialect.BIND_BY_NAME)
#     PARAM_PREFIX = property(lambda self: self.dialect.PARAM_PREFIX)
#     CONCAT_BY_FUNCTION = property(lambda self: self.dialect.CONCAT_BY_FUNCTION)
#     CONCAT_OPERATOR = property(lambda self: self.dialect.CONCAT_OPERATOR)
#     def __init__(self, dialect): self.dialect = dialect
#     def call(self, name, args):
#         if name.upper() == 'NOW': return expr.PText.cast(self.dialect.CALL_NOW)
#         if name.upper() == 'TODAY': return expr.PText.cast(self.dialect.CALL_TODAY)
#         return expr.SqlBuilder.call(self, name, args)
