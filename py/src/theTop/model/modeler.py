from . import models

class ValueModeler(models.Item):
    __call__ = models.Value

class ConstantModeler(models.Item):
    __call__ = models.Constant
    NULL = models.NULL
    TRUE = models.TRUE
    FALSE = models.FALSE

class ParameterModeler(models.Item):
    __getattr__ = __getitem__ = models.Parameter

class HostItemModeler(models.Item):
    __getattr__ = __getitem__ = models.HostItem

class ItemModeler(object):
    value = ValueModeler('value')
    const = ConstantModeler('const')
    param = ParameterModeler('param')
    host = HostItemModeler('host')
    __getattr__ = __getitem__ = models.Item
    __call__ = value

class TableModeler(object):
    __getitem__ = models.Primary

class FunctionCaller(object):
    def __init__(self, name): self.name = name
    def __call__(self, *args): return models.Call(self.name, models.makeall(args))

class BooleanOperations(object):
    def And(self, *exprs): return models.And(models.makeall(exprs))
    def Or(self, *exprs): return models.Or(models.makeall(exprs))
    def Not(self, x): return models.Not(models.make(x))

class StaticOperations(object):
    def isnull(self, x): return models.make(x).is_null
    def same(self, x1, x2):
        x1 = models.make(x1)
        x2 = models.make(x2)
        bothnull = models.And(x1.is_null, x2.is_null)
        bothequal = (x1 == x2)
        return models.Or(bothnull, bothequal)
    def cast(self, x, type): return models.Cast(models.make(x), type)
    def concat(self, *exprs): return models.Concat(models.makeall(exprs))
    def paren(self, x): return models.Parentheses(models.make(x))
    def case(self, cases, whenelse=NotImplemented): return models.Case(cases, whenelse)
    def switch(self, switch, cases, whenelse=NotImplemented): return models.Switch(switch, cases, whenelse)

class PortableOperations(object):
    def now(self): return models.Now()
    def nextval(self, sequence): return models.NextVal(sequence)

class DynamicOperations(object):
    __getattr__ = __getitem__ = FunctionCaller

class OperationModeler(BooleanOperations, StaticOperations, PortableOperations, DynamicOperations):
    __call__ = StaticOperations.paren

class UniversalModeler(object):
    ...

class ContextModeler(object):
    ...

being, at, the, T, op = UniversalModeler, ContextModeler, ItemModeler(), TableModeler(), OperationModeler()
