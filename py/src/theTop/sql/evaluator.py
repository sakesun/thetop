#! -*- coding: utf-8 -*-

import decimal
from .. import nullable
# from ..text import verse
from . import common
from . import expr
from . import table

class BaseEvaluator(common.Builder):
    items = None
    params = None

class TableEvaluator(BaseEvaluator):
    pass

class StoreEvaluator(BaseEvaluator):
    pass
