#! -*- coding: utf-8 -*-

import textwrap
import unittest
from theTop.model import *
from .. import gen

class TestMisc(unittest.TestCase):
    def test_check_illegal_labels(self):
        with self.assertRaises(KeyError): gen.check_illegal_labels(('A', 'B', 'C'), ('A', 'X'))
        gen.check_illegal_labels(('A', 'B', 'C'), ('A', 'C'))

class Test_has_many_composites(unittest.TestCase):
    def test_has_many_composites(self):
        self.assertFalse(gen.has_many_composites(the.ITEM_ID))
        self.assertFalse(gen.has_many_composites(T['T']))
        self.assertTrue(gen.has_many_composites(
            T['ORDER'].innerjoin(T['ITEM'].where(
                the.host.ITEM_ID == the.ITEM_ID))))
        self.assertTrue(gen.has_many_composites(
            T['ORDER'] \
            .innerjoin(T['ITEM'].where(
                the.host.ITEM_ID == the.ITEM_ID)) \
            .outerjoin(T['CATEGORY'].where(
                the.host.CATEGORY == the.CATEGORY))))
        self.assertTrue(gen.has_many_composites(
            T['ORDER'] \
            .innerjoin(T['ITEM'].where(
                the.host.ITEM_ID == the.ITEM_ID)) \
            .outerjoin(T['CATEGORY'].where(
                the.host.CATEGORY == the.CATEGORY)) \
            .nest('yo')))
        self.assertFalse(gen.has_many_composites(T['T'].where(the.ID == 101)))
        self.assertTrue(gen.has_many_composites(T['T'].nest('x')))
        self.assertTrue(gen.has_many_composites(T['T'].nest('x').nest('y').nest('z')))
        self.assertTrue(gen.has_many_composites(T['T'].define(YX = T['Y']('X'))))
        self.assertFalse(gen.has_many_composites(the.param.X))

class BaseTestSql(unittest.TestCase):
    def setUp(self): self.emitter = gen.SqlEmitter()
    def sql(self, expr): return self.emitter.emit_model(expr).pretty()
    def assertSql(self, sql, expr): self.assertEqual(sql, self.sql(expr))

class TestSql(BaseTestSql):
    def testItem(self):
        self.assertSql('ITEM_ID', the.ITEM_ID)
    def testParameter(self):
        self.assertSql(':Param1', the.param.Param1)
    def testConstant(self):
        self.assertSql('NULL', the.const.NULL)
        self.assertSql('NULL', the.const(None))
        self.assertSql('0', the.const(0))
        self.assertSql('1', the.const(1))
        self.assertSql('1.5', the.const(1.5))
        self.assertSql("''", the.const(''))
        self.assertSql("'one'", the.const('one'))
        self.assertSql("'two'", the.const('two'))
        self.assertSql("'three'", the.const('three'))
        self.assertSql("'It''s good'", the.const("It's good"))
    def testFunc(self):
        self.assertSql('ExecuteFunc(1, 2, 3)', op.ExecuteFunc(1, 2, 3))
        self.assertSql("ExecuteFunc('one', 'two', 3)", op.ExecuteFunc('one', 'two', 3))
        self.assertSql("ExecuteFunc(A, B, C)", op.ExecuteFunc(the.A, the.B, the.C))
    def testCast(self):
        self.assertSql('CAST(2.5 AS int)', op.cast(2.5, 'int'))
        self.assertSql('CAST(2.5 AS float)', op.cast(2.5, float))
        self.assertSql('CAST(PRICE AS int)', op.cast(the.PRICE, int))
    def testComparison(self):
        self.assertSql('1 > 2', the.const(1) > the.const(2))
        self.assertSql('1 < 2', the.const(1) < the.const(2))
        self.assertSql('1 = 2', the.const(1) == the.const(2))
        self.assertSql('1 <> 2', the.const(1) != the.const(2))
        self.assertSql('1 >= 2', the.const(1) >= the.const(2))
        self.assertSql('1 <= 2', the.const(1) <= the.const(2))
        self.assertSql('FIRST > SECOND', the.FIRST > the.SECOND)
        self.assertSql('FIRST < SECOND', the.FIRST < the.SECOND)
        self.assertSql('FIRST = SECOND', the.FIRST == the.SECOND)
        self.assertSql('FIRST <> SECOND', the.FIRST != the.SECOND)
        self.assertSql('FIRST >= SECOND', the.FIRST >= the.SECOND)
        self.assertSql('FIRST <= SECOND', the.FIRST <= the.SECOND)
    def testBetween(self):
        self.assertSql('1 BETWEEN 2 AND 3', the.const(1).between(the.const(2), the.const(3)))
        self.assertSql('VALUE BETWEEN VMIN AND VMAX', the.VALUE.between(the.VMIN, the.VMAX))
    def testInRange(self):
        self.assertSql('(3 <= 1) AND (1 < 21)', the.const(1).in_range(3, 21))
    def testIsNull(self):
        self.assertSql('1 IS NULL', the.const(1).is_null)
        self.assertSql('ITEM_ID IS NULL', the.ITEM_ID.is_null)
    def testNotNull(self):
        self.assertSql('1 IS NOT NULL', the.const(1).is_not_null)
        self.assertSql('ITEM_ID IS NOT NULL', the.ITEM_ID.is_not_null)
    def testIsIn(self):
        self.assertSql('1 IN (3, 4, 5, 6)', the.const(1).in_([3, 4, 5, 6]))
        self.assertSql("ITEM_TYPE IN ('A', 'B', 'C')", the.ITEM_TYPE.in_(['A', 'B', 'C']))
    def testNotIn(self):
        self.assertSql('1 NOT IN (3, 4, 5, 6)', the.const(1).not_in_([3, 4, 5, 6]))
        self.assertSql("ITEM_TYPE NOT IN ('A', 'B', 'C')", the.ITEM_TYPE.not_in_(['A', 'B', 'C']))
    def testLike(self):
        self.assertSql("'text' LIKE 't%'", the.const('text').like('t%'))
        self.assertSql("NAME LIKE 'Sa%'", the.NAME.like('Sa%'))
        self.assertSql("DISCOUNT LIKE '__!%' ESCAPE '!'", the.DISCOUNT.like('__!%', '!'))
    def testAnd(self):
        self.assertSql('(PRICE > 100) AND (COST < 30)', (the.PRICE > 100).and_(the.COST < 30))
        self.assertSql('(PRICE > 100) AND (COST < 30)', op.And(the.PRICE > 100, the.COST < 30))
    def testOr(self):
        self.assertSql('(PRICE > 100) OR (COST < 30)', (the.PRICE > 100).or_(the.COST < 30))
        self.assertSql('(PRICE > 100) OR (COST < 30)', op.Or(the.PRICE > 100, the.COST < 30))
    def testNot(self):
        self.assertSql('NOT (PRICE > 1000)', (the.PRICE > 1000).not_)
        self.assertSql('NOT (PRICE > 1000)', op.Not(the.PRICE > 1000))
    def testCase(self):
        self.assertSql(textwrap.dedent("""\
            CASE
              WHEN (PRICE > 100) THEN 'EXPENSIVE'
              WHEN (PRICE < 10) THEN 'CHEAP'
            END"""),
            op.case(
                ((the.PRICE > 100, 'EXPENSIVE'),
                 (the.PRICE < 10, 'CHEAP'))))
        self.assertSql(textwrap.dedent("""\
            CASE
              WHEN (PRICE > 100) THEN 'EXPENSIVE'
              WHEN (PRICE < 10) THEN 'CHEAP'
              ELSE 'MODERATE'
            END"""),
            op.case(
                ((the.PRICE > 100, 'EXPENSIVE'),
                 (the.PRICE < 10, 'CHEAP')),
                'MODERATE'))
    def testSwitch(self):
        self.assertSql(textwrap.dedent("""\
            CASE PRICE_TAG
              WHEN 'EXPENSIVE' THEN 'like'
              WHEN 'CHEAP' THEN 'dislike'
            END"""),
            op.switch(
              the.PRICE_TAG,
              (('EXPENSIVE', 'like'),
               ('CHEAP', 'dislike'))))
        self.assertSql(textwrap.dedent("""\
            CASE PRICE_TAG
              WHEN 'EXPENSIVE' THEN 'like'
              WHEN 'CHEAP' THEN 'dislike'
              ELSE '...'
            END"""),
            op.switch(
              the.PRICE_TAG,
              (('EXPENSIVE', 'like'),
               ('CHEAP', 'dislike')),
              '...'))
    def testNeg(self):
        self.assertSql('-100', - the.const(100))
        self.assertSql('-AMOUNT', - the.AMOUNT)
    def testPos(self):
        self.assertSql('+100', + the.const(100))
        self.assertSql('+AMOUNT', + the.AMOUNT)
    def testSummarize(self):
        self.assertSql('A + B + 1 + 2', the.A + the.B + 1 + 2)
        self.assertSql('A + B + 1 + 2', the.A + (the.B + 1) + 2)
        self.assertSql('A + (B + 1) + 2', the.A + op(the.B + 1) + 2)
    def testSub(self):
        self.assertSql('A - B', the.A - the.B)
        self.assertSql('A - B - 5', the.A - the.B - 5)
        self.assertSql('A - (B - 5)', the.A - (the.B - 5))
    def testMultiply(self):
        self.assertSql('A * B * 1 * 2', the.A * the.B * 1 * 2)
        self.assertSql('A * B * 1 * 2', the.A * (the.B * 1) * 2)
        self.assertSql('A * (B * 1) * 2', the.A * op(the.B * 1) * 2)
    def testDiv(self):
        self.assertSql('A / B / 5', the.A / the.B / 5)
        self.assertSql('A / (B / 5)', the.A / (the.B / 5))
    def testMixedMath(self):
        self.assertSql('(A * B) + (C * D)', the.A * the.B + the.C * the.D)
        self.assertSql('(A - B) * (C + D)', (the.A - the.B) * (the.C + the.D))
        self.assertSql('(A / B) + (C / D)', the.A / the.B + the.C / the.D)
        self.assertSql('(A - B) / (C + D)', (the.A - the.B) / (the.C + the.D))
    def testConcat(self):
        self.emitter.dialect.CONCAT_BY_FUNCTION = True
        self.assertSql("CONCAT(A, B, '.')", op.concat(the.A, the.B, '.'))
        self.emitter.dialect.CONCAT_FUNCTION_MULTIARGS = False
        self.assertSql("CONCAT(CONCAT(A, B), '.')", op.concat(the.A, the.B, '.'))
        self.emitter.dialect.CONCAT_BY_FUNCTION = False
        self.assertSql("A || B || '.'", op.concat(the.A, the.B, '.'))
        self.emitter.dialect.CONCAT_OPERATOR = '+'
        self.assertSql("A + B + '.'", op.concat(the.A, the.B, '.'))
    def testNow(self):
        self.assertSql('{fn Now()}', op.now())
        self.emitter.dialect.SQL_NOW = 'GETDATE()'
        self.assertSql('GETDATE()', op.now())
        self.emitter.dialect.SQL_NOW = 'SYSDATE'
        self.assertSql('SYSDATE', op.now())
    def testNextVal(self):
        self.assertSql('SEQ.NEXTVAL', op.nextval('SEQ'))
        self.emitter.dialect.NEXTVAL_TEMPLATE = "NEXTVAL('%s')"
        self.assertSql("NEXTVAL('SEQ')", op.nextval('SEQ'))
        self.emitter.dialect.NEXTVAL_TEMPLATE = 'NEXT VALUE FOR %s'
        self.assertSql('NEXT VALUE FOR SEQ', op.nextval('SEQ'))
    def testPrimary(self):
        self.assertSql(textwrap.dedent('''\
            SELECT
              *
            FROM
              TABLE'''),
            T['TABLE'])
    def testInclusion(self):
        abc = T['TABLE'].include('A', 'B', 'C')
        self.assertSql(textwrap.dedent('''\
            SELECT
              A,
              B,
              C
            FROM
              TABLE'''),
            abc)
        d = abc.include('D')
        with self.assertRaises(KeyError): self.sql(d)
    def testExclusion(self):
        abc = T['TABLE'].include('A', 'B', 'C')
        self.assertSql(textwrap.dedent('''\
            SELECT
              A,
              C
            FROM
              TABLE'''),
            abc.exclude('B'))
        x = abc.exclude('X')
        with self.assertRaises(KeyError): self.sql(x)
    def testWhere(self):
        w = T['TABLE'].where(the.PRICE > 100)
        self.assertSql(textwrap.dedent('''\
            SELECT
              *
            FROM
              TABLE
            WHERE
              (PRICE > 100)'''), w)
        w = w.where(the.COST < 10)
        self.assertSql(textwrap.dedent('''\
            SELECT
              *
            FROM
              TABLE
            WHERE
              (PRICE > 100) AND
              (COST < 10)'''), w)
    def testDefine(self):
        w = T['TABLE'].include('ITEM_ID', 'NAME', 'PRICE', 'COST')
        w = w.where(the.PRICE > 100)
        w = w.define(PRICE = the.COST * 3)
        w = w.where(the.PRICE < 1000)
        self.assertSql(textwrap.dedent('''\
            SELECT
              ITEM_ID,
              NAME,
              (COST * 3) AS PRICE,
              COST
            FROM
              TABLE
            WHERE
              (PRICE > 100) AND
              ((COST * 3) < 1000)'''), w)
    def testRename(self):
        w = T['TABLE'].include('ITEM_ID', 'NAME', 'PRICE', 'COST')
        w = w.where(the.PRICE > 100)
        w = w.rename(PRICE = 'Cost', COST = 'Price')
        w = w.define(Price = the.Cost * 3)
        w = w.where(the.Price < 1000)
        self.assertSql(textwrap.dedent('''\
            SELECT
              ITEM_ID,
              NAME,
              PRICE AS Cost,
              (PRICE * 3) AS Price
            FROM
              TABLE
            WHERE
              (PRICE > 100) AND
              ((PRICE * 3) < 1000)'''), w)
        with self.assertRaises(KeyError):
            w = w.rename(B = 'x')
            self.sql(w)
    def testQualify(self):
        t = T['TABLE'].qualify()
        self.assertSql(textwrap.dedent('''\
            SELECT
              *
            FROM
              TABLE'''),
            t)
        t = t.include('A', 'B', 'C')
        self.assertSql(textwrap.dedent('''\
            SELECT
              TABLE.A,
              TABLE.B,
              TABLE.C
            FROM
              TABLE'''),
            t)
    def testAlias(self):
        t = T['TABLE'].alias('t')
        self.assertSql(textwrap.dedent('''\
            SELECT
              *
            FROM
              TABLE t'''),
            t)
        t = t.include('A', 'B', 'C')
        self.assertSql(textwrap.dedent('''\
            SELECT
              t.A,
              t.B,
              t.C
            FROM
              TABLE t'''),
            t)
    def testNest(self):
        t = T['TABLE'].nest('t')
        self.assertSql(textwrap.dedent('''\
            SELECT
              *
            FROM
              (
                SELECT
                  *
                FROM
                  TABLE
              ) t'''),
            t)

class TestQualifyingDecorator(BaseTestSql):
    def setUp(self):
        BaseTestSql.setUp(self)
        self.emitter = gen.QualifyingDecorator(self.emitter, 'T')
    def testItem(self):
        self.assertSql('T.ITEM_ID', the.ITEM_ID)
    def testFunc(self):
        self.assertSql("ExecuteFunc(T.A, T.B, T.C)", op.ExecuteFunc(the.A, the.B, the.C))
    def testCast(self):
        self.assertSql('CAST(T.PRICE AS int)', op.cast(the.PRICE, int))
    def testComparison(self):
        self.assertSql('T.FIRST > T.SECOND', the.FIRST > the.SECOND)
        self.assertSql('T.FIRST < T.SECOND', the.FIRST < the.SECOND)
        self.assertSql('T.FIRST = T.SECOND', the.FIRST == the.SECOND)
        self.assertSql('T.FIRST <> T.SECOND', the.FIRST != the.SECOND)
        self.assertSql('T.FIRST >= T.SECOND', the.FIRST >= the.SECOND)
        self.assertSql('T.FIRST <= T.SECOND', the.FIRST <= the.SECOND)
    def testBetween(self):
        self.assertSql('T.VALUE BETWEEN T.VMIN AND T.VMAX', the.VALUE.between(the.VMIN, the.VMAX))
    def testIsNull(self):
        self.assertSql('T.ITEM_ID IS NULL', the.ITEM_ID.is_null)
    def testNotNull(self):
        self.assertSql('T.ITEM_ID IS NOT NULL', the.ITEM_ID.is_not_null)
    def testIsIn(self):
        self.assertSql("T.ITEM_TYPE IN ('A', 'B', 'C')", the.ITEM_TYPE.in_(['A', 'B', 'C']))
    def testNotIn(self):
        self.assertSql("T.ITEM_TYPE NOT IN ('A', 'B', 'C')", the.ITEM_TYPE.not_in_(['A', 'B', 'C']))
    def testLike(self):
        self.assertSql("T.NAME LIKE 'Sa%'", the.NAME.like('Sa%'))
        self.assertSql("T.DISCOUNT LIKE '__!%' ESCAPE '!'", the.DISCOUNT.like('__!%', '!'))
    def testAnd(self):
        self.assertSql('(T.PRICE > 100) AND (T.COST < 30)', (the.PRICE > 100).and_(the.COST < 30))
        self.assertSql('(T.PRICE > 100) AND (T.COST < 30)', op.And(the.PRICE > 100, the.COST < 30))
    def testOr(self):
        self.assertSql('(T.PRICE > 100) OR (T.COST < 30)', (the.PRICE > 100).or_(the.COST < 30))
        self.assertSql('(T.PRICE > 100) OR (T.COST < 30)', op.Or(the.PRICE > 100, the.COST < 30))
    def testNot(self):
        self.assertSql('NOT (T.PRICE > 1000)', (the.PRICE > 1000).not_)
        self.assertSql('NOT (T.PRICE > 1000)', op.Not(the.PRICE > 1000))
    def testCase(self):
        self.assertSql(textwrap.dedent("""\
            CASE
              WHEN (T.PRICE > 100) THEN 'EXPENSIVE'
              WHEN (T.PRICE < 10) THEN 'CHEAP'
            END"""),
            op.case(
                ((the.PRICE > 100, 'EXPENSIVE'),
                 (the.PRICE < 10, 'CHEAP'))))
        self.assertSql(textwrap.dedent("""\
            CASE
              WHEN (T.PRICE > 100) THEN 'EXPENSIVE'
              WHEN (T.PRICE < 10) THEN 'CHEAP'
              ELSE 'MODERATE'
            END"""),
            op.case(
                ((the.PRICE > 100, 'EXPENSIVE'),
                 (the.PRICE < 10, 'CHEAP')),
                'MODERATE'))
    def testSwitch(self):
        self.assertSql(textwrap.dedent("""\
            CASE T.PRICE_TAG
              WHEN 'EXPENSIVE' THEN 'like'
              WHEN 'CHEAP' THEN 'dislike'
            END"""),
            op.switch(
              the.PRICE_TAG,
              (('EXPENSIVE', 'like'),
               ('CHEAP', 'dislike'))))
        self.assertSql(textwrap.dedent("""\
            CASE T.PRICE_TAG
              WHEN 'EXPENSIVE' THEN 'like'
              WHEN 'CHEAP' THEN 'dislike'
              ELSE '...'
            END"""),
            op.switch(
              the.PRICE_TAG,
              (('EXPENSIVE', 'like'),
               ('CHEAP', 'dislike')),
              '...'))
    def testNeg(self):
        self.assertSql('-T.AMOUNT', - the.AMOUNT)
    def testPos(self):
        self.assertSql('+T.AMOUNT', + the.AMOUNT)
    def testSummarize(self):
        self.assertSql('T.A + T.B + 1 + 2', the.A + the.B + 1 + 2)
        self.assertSql('T.A + T.B + 1 + 2', the.A + (the.B + 1) + 2)
        self.assertSql('T.A + (T.B + 1) + 2', the.A + op(the.B + 1) + 2)
    def testSub(self):
        self.assertSql('T.A - T.B', the.A - the.B)
        self.assertSql('T.A - T.B - 5', the.A - the.B - 5)
        self.assertSql('T.A - (T.B - 5)', the.A - (the.B - 5))
    def testMultiply(self):
        self.assertSql('T.A * T.B * 1 * 2', the.A * the.B * 1 * 2)
        self.assertSql('T.A * T.B * 1 * 2', the.A * (the.B * 1) * 2)
        self.assertSql('T.A * (T.B * 1) * 2', the.A * op(the.B * 1) * 2)
    def testDiv(self):
        self.assertSql('T.A / T.B / 5', the.A / the.B / 5)
        self.assertSql('T.A / (T.B / 5)', the.A / (the.B / 5))
    def testMixedMath(self):
        self.assertSql('(T.A * T.B) + (T.C * T.D)', the.A * the.B + the.C * the.D)
        self.assertSql('(T.A - T.B) * (T.C + T.D)', (the.A - the.B) * (the.C + the.D))
        self.assertSql('(T.A / T.B) + (T.C / T.D)', the.A / the.B + the.C / the.D)
        self.assertSql('(T.A - T.B) / (T.C + T.D)', (the.A - the.B) / (the.C + the.D))
    def testConcat(self):
        self.emitter.dialect.CONCAT_BY_FUNCTION = True
        self.assertSql("CONCAT(T.A, T.B, '.')", op.concat(the.A, the.B, '.'))
        self.emitter.dialect.CONCAT_FUNCTION_MULTIARGS = False
        self.assertSql("CONCAT(CONCAT(T.A, T.B), '.')", op.concat(the.A, the.B, '.'))
        self.emitter.dialect.CONCAT_BY_FUNCTION = False
        self.assertSql("T.A || T.B || '.'", op.concat(the.A, the.B, '.'))
        self.emitter.dialect.CONCAT_OPERATOR = '+'
        self.assertSql("T.A + T.B + '.'", op.concat(the.A, the.B, '.'))

class TestItemDefDecorator(BaseTestSql):
    def setUp(self):
        BaseTestSql.setUp(self)
        self.emitter = gen.ItemDefDecorator(self.emitter, dict(
            ITEM_ID = the.const('16782'),
            ITEM_TYPE = the.const('Raw Material'),
            aaa = the.AAA,
            innerBee = the.BBB + 1,
            B = op.Bee(the.BBB + 1),
            C = the.const('CCC'),
            PRICE = the.const(1000),
            COST = the.const(20),
            FIRST = the.First,
            VMIN = op.GetMin()))
        self.emitter = gen.ItemDefDecorator(self.emitter, dict(
            A = the.aaa,
            B = op.Bee(the.innerBee),
            VALUE = the.Value,
            VMAX = op.GetMax(),
            NAME = the.const('Somchai'),
            DISCOUNT = the.const('30%'),
            PRICE_TAG = the.const('CHEAP'),
            AMOUNT = the.QUANTITY * the.VALUE))
    def testItem(self):
        self.assertSql("'16782'", the.ITEM_ID)
    def testFunc(self):
        self.assertSql("ExecuteFunc(AAA, Bee(BBB + 1), 'CCC')", op.ExecuteFunc(the.A, the.B, the.C))
    def testCast(self):
        self.assertSql('CAST(1000 AS int)', op.cast(the.PRICE, int))
    def testComparison(self):
        self.assertSql('First > SECOND', the.FIRST > the.SECOND)
        self.assertSql('First < SECOND', the.FIRST < the.SECOND)
        self.assertSql('First = SECOND', the.FIRST == the.SECOND)
        self.assertSql('First <> SECOND', the.FIRST != the.SECOND)
        self.assertSql('First >= SECOND', the.FIRST >= the.SECOND)
        self.assertSql('First <= SECOND', the.FIRST <= the.SECOND)
    def testBetween(self):
        self.assertSql('Value BETWEEN GetMin() AND GetMax()', the.VALUE.between(the.VMIN, the.VMAX))
    def testIsNull(self):
        self.assertSql("'16782' IS NULL", the.ITEM_ID.is_null)
    def testNotNull(self):
        self.assertSql("'16782' IS NOT NULL", the.ITEM_ID.is_not_null)
    def testIsIn(self):
        self.assertSql("'Raw Material' IN ('A', 'B', 'C')", the.ITEM_TYPE.in_(['A', 'B', 'C']))
    def testNotIn(self):
        self.assertSql("'Raw Material' NOT IN ('A', 'B', 'C')", the.ITEM_TYPE.not_in_(['A', 'B', 'C']))
    def testLike(self):
        self.assertSql("'Somchai' LIKE 'Sa%'", the.NAME.like('Sa%'))
        self.assertSql("'30%' LIKE '__!%' ESCAPE '!'", the.DISCOUNT.like('__!%', '!'))
    def testAnd(self):
        self.assertSql('(1000 > 100) AND (20 < 30)', (the.PRICE > 100).and_(the.COST < 30))
        self.assertSql('(1000 > 100) AND (20 < 30)', op.And(the.PRICE > 100, the.COST < 30))
    def testOr(self):
        self.assertSql('(1000 > 100) OR (20 < 30)', (the.PRICE > 100).or_(the.COST < 30))
        self.assertSql('(1000 > 100) OR (20 < 30)', op.Or(the.PRICE > 100, the.COST < 30))
    def testNot(self):
        self.assertSql('NOT (1000 > 1000)', (the.PRICE > 1000).not_)
        self.assertSql('NOT (1000 > 1000)', op.Not(the.PRICE > 1000))
    def testCase(self):
        self.assertSql(textwrap.dedent("""\
            CASE
              WHEN (1000 > 100) THEN 'EXPENSIVE'
              WHEN (1000 < 10) THEN 'CHEAP'
            END"""),
            op.case(
                ((the.PRICE > 100, 'EXPENSIVE'),
                 (the.PRICE < 10, 'CHEAP'))))
        self.assertSql(textwrap.dedent("""\
            CASE
              WHEN (1000 > 100) THEN 'EXPENSIVE'
              WHEN (1000 < 10) THEN 'CHEAP'
              ELSE 'MODERATE'
            END"""),
            op.case(
                ((the.PRICE > 100, 'EXPENSIVE'),
                 (the.PRICE < 10, 'CHEAP')),
                'MODERATE'))
    def testSwitch(self):
        self.assertSql(textwrap.dedent("""\
            CASE 'CHEAP'
              WHEN 'EXPENSIVE' THEN 'like'
              WHEN 'CHEAP' THEN 'dislike'
            END"""),
            op.switch(
              the.PRICE_TAG,
              (('EXPENSIVE', 'like'),
               ('CHEAP', 'dislike'))))
        self.assertSql(textwrap.dedent("""\
            CASE 'CHEAP'
              WHEN 'EXPENSIVE' THEN 'like'
              WHEN 'CHEAP' THEN 'dislike'
              ELSE '...'
            END"""),
            op.switch(
              the.PRICE_TAG,
              (('EXPENSIVE', 'like'),
               ('CHEAP', 'dislike')),
              '...'))
    def testNeg(self):
        self.assertSql('-(QUANTITY * VALUE)', - the.AMOUNT)
    def testPos(self):
        self.assertSql('+(QUANTITY * VALUE)', + the.AMOUNT)
    def testSummarize(self):
        self.assertSql('AAA + Bee(BBB + 1) + 1 + 2', the.A + the.B + 1 + 2)
        self.assertSql('AAA + Bee(BBB + 1) + 1 + 2', the.A + (the.B + 1) + 2)
        self.assertSql('AAA + (Bee(BBB + 1) + 1) + 2', the.A + op(the.B + 1) + 2)
    def testSub(self):
        self.assertSql('AAA - Bee(BBB + 1)', the.A - the.B)
        self.assertSql('AAA - Bee(BBB + 1) - 5', the.A - the.B - 5)
        self.assertSql('AAA - (Bee(BBB + 1) - 5)', the.A - (the.B - 5))
    def testMultiply(self):
        self.assertSql('AAA * Bee(BBB + 1) * 1 * 2', the.A * the.B * 1 * 2)
        self.assertSql('AAA * Bee(BBB + 1) * 1 * 2', the.A * (the.B * 1) * 2)
        self.assertSql('AAA * (Bee(BBB + 1) * 1) * 2', the.A * op(the.B * 1) * 2)
    def testDiv(self):
        self.assertSql('AAA / Bee(BBB + 1) / 5', the.A / the.B / 5)
        self.assertSql('AAA / (Bee(BBB + 1) / 5)', the.A / (the.B / 5))
    def testMixedMath(self):
        self.assertSql("(AAA * Bee(BBB + 1)) + ('CCC' * D)", the.A * the.B + the.C * the.D)
        self.assertSql("(AAA - Bee(BBB + 1)) * ('CCC' + D)", (the.A - the.B) * (the.C + the.D))
        self.assertSql("(AAA / Bee(BBB + 1)) + ('CCC' / D)", the.A / the.B + the.C / the.D)
        self.assertSql("(AAA - Bee(BBB + 1)) / ('CCC' + D)", (the.A - the.B) / (the.C + the.D))
    def testConcat(self):
        self.emitter.dialect.CONCAT_BY_FUNCTION = True
        self.assertSql("CONCAT(AAA, Bee(BBB + 1), '.')", op.concat(the.A, the.B, '.'))
        self.emitter.dialect.CONCAT_FUNCTION_MULTIARGS = False
        self.assertSql("CONCAT(CONCAT(AAA, Bee(BBB + 1)), '.')", op.concat(the.A, the.B, '.'))
        self.emitter.dialect.CONCAT_BY_FUNCTION = False
        self.assertSql("AAA || Bee(BBB + 1) || '.'", op.concat(the.A, the.B, '.'))
        self.emitter.dialect.CONCAT_OPERATOR = '+'
        self.assertSql("AAA + Bee(BBB + 1) + '.'", op.concat(the.A, the.B, '.'))

class TestRenameDecorator(BaseTestSql):
    def setUp(self):
        BaseTestSql.setUp(self)
        self.emitter = gen.RenameDecorator(self.emitter, dict(
            ITEM_ID = 'ItemId',
            ITEM_TYPE = 'ItemType',
            B = 'a',
            A = 'b',
            C = 'c',
            PRICE = 'Price',
            COST = 'Cost',
            FIRST = 'First',
            VMIN = 'VMin'))
        self.emitter = gen.RenameDecorator(self.emitter, dict(
            a = 'b',
            b = 'a',
            VALUE = 'Value',
            VMAX = 'VMax',
            NAME = 'Name',
            DISCOUNT = 'Discount',
            PRICE_TAG = 'PriceTag',
            AMOUNT = 'Amount'))
    def testItem(self):
        self.assertSql("ITEM_ID", the.ItemId)
    def testFunc(self):
        self.assertSql("ExecuteFunc(A, B, C)", op.ExecuteFunc(the.a, the.b, the.c))
    def testCast(self):
        self.assertSql('CAST(PRICE AS int)', op.cast(the.Price, int))
    def testComparison(self):
        self.assertSql('FIRST > SECOND', the.First > the.SECOND)
        self.assertSql('FIRST < SECOND', the.First < the.SECOND)
        self.assertSql('FIRST = SECOND', the.First == the.SECOND)
        self.assertSql('FIRST <> SECOND', the.First != the.SECOND)
        self.assertSql('FIRST >= SECOND', the.First >= the.SECOND)
        self.assertSql('FIRST <= SECOND', the.First <= the.SECOND)
    def testBetween(self):
        self.assertSql('VALUE BETWEEN VMIN AND VMAX', the.Value.between(the.VMin, the.VMax))
    def testIsNull(self):
        self.assertSql("ITEM_ID IS NULL", the.ItemId.is_null)
    def testNotNull(self):
        self.assertSql("ITEM_ID IS NOT NULL", the.ItemId.is_not_null)
    def testIsIn(self):
        self.assertSql("ITEM_TYPE IN ('A', 'B', 'C')", the.ItemType.in_(['A', 'B', 'C']))
    def testNotIn(self):
        self.assertSql("ITEM_TYPE NOT IN ('A', 'B', 'C')", the.ItemType.not_in_(['A', 'B', 'C']))
    def testLike(self):
        self.assertSql("NAME LIKE 'Sa%'", the.Name.like('Sa%'))
        self.assertSql("DISCOUNT LIKE '__!%' ESCAPE '!'", the.Discount.like('__!%', '!'))
    def testAnd(self):
        self.assertSql('(PRICE > 100) AND (COST < 30)', (the.Price > 100).and_(the.Cost < 30))
        self.assertSql('(PRICE > 100) AND (COST < 30)', op.And(the.Price > 100, the.Cost < 30))
    def testOr(self):
        self.assertSql('(PRICE > 100) OR (COST < 30)', (the.Price > 100).or_(the.Cost < 30))
        self.assertSql('(PRICE > 100) OR (COST < 30)', op.Or(the.Price > 100, the.Cost < 30))
    def testNot(self):
        self.assertSql('NOT (PRICE > 1000)', (the.Price > 1000).not_)
        self.assertSql('NOT (PRICE > 1000)', op.Not(the.Price > 1000))
    def testCase(self):
        self.assertSql(textwrap.dedent("""\
            CASE
              WHEN (PRICE > 100) THEN 'EXPENSIVE'
              WHEN (PRICE < 10) THEN 'CHEAP'
            END"""),
            op.case(
                ((the.Price > 100, 'EXPENSIVE'),
                 (the.Price < 10, 'CHEAP'))))
        self.assertSql(textwrap.dedent("""\
            CASE
              WHEN (PRICE > 100) THEN 'EXPENSIVE'
              WHEN (PRICE < 10) THEN 'CHEAP'
              ELSE 'MODERATE'
            END"""),
            op.case(
                ((the.Price > 100, 'EXPENSIVE'),
                 (the.Price < 10, 'CHEAP')),
                'MODERATE'))
    def testSwitch(self):
        self.assertSql(textwrap.dedent("""\
            CASE PRICE_TAG
              WHEN 'EXPENSIVE' THEN 'like'
              WHEN 'CHEAP' THEN 'dislike'
            END"""),
            op.switch(
              the.PriceTag,
              (('EXPENSIVE', 'like'),
               ('CHEAP', 'dislike'))))
        self.assertSql(textwrap.dedent("""\
            CASE PRICE_TAG
              WHEN 'EXPENSIVE' THEN 'like'
              WHEN 'CHEAP' THEN 'dislike'
              ELSE '...'
            END"""),
            op.switch(
              the.PriceTag,
              (('EXPENSIVE', 'like'),
               ('CHEAP', 'dislike')),
              '...'))
    def testNeg(self):
        self.assertSql('-VALUE', - the.Value)
    def testPos(self):
        self.assertSql('+VALUE', + the.Value)
    def testSummarize(self):
        self.assertSql('A + B + 1 + 2', the.a + the.b + 1 + 2)
        self.assertSql('A + B + 1 + 2', the.a + (the.b + 1) + 2)
        self.assertSql('A + (B + 1) + 2', the.a + op(the.b + 1) + 2)
    def testSub(self):
        self.assertSql('A - B', the.a - the.b)
        self.assertSql('A - B - 5', the.a - the.b - 5)
        self.assertSql('A - (B - 5)', the.a - (the.b - 5))
    def testMultiply(self):
        self.assertSql('A * B * 1 * 2', the.a * the.b * 1 * 2)
        self.assertSql('A * B * 1 * 2', the.a * (the.b * 1) * 2)
        self.assertSql('A * (B * 1) * 2', the.a * op(the.b * 1) * 2)
    def testDiv(self):
        self.assertSql('A / B / 5', the.a / the.b / 5)
        self.assertSql('A / (B / 5)', the.a / (the.b / 5))
    def testMixedMath(self):
        self.assertSql("(A * B) + (C * d)", the.a * the.b + the.c * the.d)
        self.assertSql("(A - B) * (C + d)", (the.a - the.b) * (the.c + the.d))
        self.assertSql("(A / B) + (C / d)", the.a / the.b + the.c / the.d)
        self.assertSql("(A - B) / (C + d)", (the.a - the.b) / (the.c + the.d))
    def testConcat(self):
        self.emitter.dialect.CONCAT_BY_FUNCTION = True
        self.assertSql("CONCAT(A, B, '.')", op.concat(the.a, the.b, '.'))
        self.emitter.dialect.CONCAT_FUNCTION_MULTIARGS = False
        self.assertSql("CONCAT(CONCAT(A, B), '.')", op.concat(the.a, the.b, '.'))
        self.emitter.dialect.CONCAT_BY_FUNCTION = False
        self.assertSql("A || B || '.'", op.concat(the.a, the.b, '.'))
        self.emitter.dialect.CONCAT_OPERATOR = '+'
        self.assertSql("A + B + '.'", op.concat(the.a, the.b, '.'))

class TestParamSubst(BaseTestSql):
    def setUp(self):
        BaseTestSql.setUp(self)
        self.emitter = gen.ParamSubstDecorator(self.emitter, dict(
            Param1 = the.const(1),
            Param2 = the.const('two'),
            Param3 = the.param.ParamX))
        self.emitter = gen.ParamSubstDecorator(self.emitter, dict(
            ParamTwo = the.param.Param2,
            Param4 = the.const(4)))
    def testParameter(self):
        self.assertSql(':AParam', the.param.AParam)
        self.assertSql('1', the.param.Param1)
        self.assertSql("'two'", the.param.Param2)
        self.assertSql("'two'", the.param.ParamTwo)
        self.assertSql(':ParamX', the.param.Param3)
