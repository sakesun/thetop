from ..util import assert_slotty
from ..model.models import Expression, make

class Row(object):
    __slots__ = 'table', 'cursor'
    labels = property(lambda self: self.table.labels)
    def __init__(self, table, cursor):
        self.table = table
        self.cursor = cursor
    def index_of_label(self, label): return self.table.index_of_label(label)
    def indices_of_labels(self, *labels): return self.table.indices_of_labels(*labels)
    def valid_labels(self, *labels): return self.table.valid_labels(*labels)
    def assert_valid_labels(self, *labels): self.table.assert_valid_labels(*labels)
    def __iter__(self): return iter(self._tuple_all())
    def __getitem__(self, label): return self._tuple_of(label)[0]
    def __setitem__(self, label, value):
        self._update(**{label: self.evaluate(value)})
    def tuple(self, *labels): return self._tuple_of(*labels) if labels else self._tuple_all()
    def update(self, **settings):
        evaluator = None
        kwargs = {}
        for k,v in settings.items():
            if isinstance(v, Expression):
                if evaluator is None: evaluator = self.evaluator()
                kwargs[k] = v.express(evaluator)
            else:
                kwargs[k] = v
        self._update(**kwargs)
    def _tuple_of(self, *labels):
        t = self._tuple_all()
        return tuple(t[self.index_of_label(n)] for n in labels)
    def _tuple_all(self): raise NotImplementedError()
    def _update(self, **setings): raise NotImplementedError()
    # def evaluator(self, **params):
    #     return Evaluator(items=self.dict(), params=params) \
    #            if self.table is None \
    #            else self.table.create_evaluator(items = self.dict(), params=params)
    # def evaluate(self, expression, params={}): return expr.make(expression).emit(self.evaluator(**params))
    def dict(self): return dict(zip(self.labels, self.tuple()))
    def delete(self): raise NotImplementedError()
assert_slotty(Row)
