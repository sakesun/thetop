#! -*- coding: utf-8 -*-

import unittest
from ... import util
from .. import nullop
from .. import foldop

IronPythonOnly = unittest.skipIf(not hasattr(nullop, 'DBNull'), 'For IronPython only')
if hasattr(nullop, 'DBNull'): dbnull = getattr(nullop, 'DBNull').Value

fold = foldop.fold
Fold = foldop.Fold

class FoldOpTestCase(unittest.TestCase):
    def assertFoldTrue(self, x):
        self.assertTrue(isinstance(x, Fold))
        self.assertTrue(x.inner)
    def assertFoldFalse(self, x):
        self.assertTrue(isinstance(x, Fold))
        self.assertFalse(x.inner)
    def assertFoldNull(self, x):
        self.assertTrue(isinstance(x, Fold))
        self.assertNull(x.inner)
    def assertFoldEqual(self, a, b):
        self.assertTrue(isinstance(b, Fold))
        self.assertEqual(a, b)

class TestFoldOpIsNull(FoldOpTestCase):
    def testNoneIsNull(self):
        self.assertFoldTrue(foldop.isnull(None))
    @IronPythonOnly
    def testDBNullIsNull(self):
        self.assertFoldTrue(foldop.isnull(dbnull))
    def testZeroIsNotNull(self):
        self.assertFoldFalse(foldop.isnull(0))
    def testEmptyStringIsNotNull(self):
        self.assertFoldFalse(foldop.isnull(''))
    def testOneIsNotNull(self):
        self.assertFoldFalse(foldop.isnull(1))
    def testHelloIsNotNull(self):
        self.assertFoldFalse(foldop.isnull('hello'))

class TestFoldOpAccept(FoldOpTestCase):
    def testNoneIsNotAccepted(self):
        self.assertFoldFalse(foldop.accept(None))
    @IronPythonOnly
    def testDBNullIsNotAccepted(self):
        self.assertFoldFalse(foldop.accept(dbnull))
    def testZeroIsNotAccepted(self):
        self.assertFoldFalse(foldop.accept(0))
    def testEmptyStringIsNotAccepted(self):
        self.assertFoldFalse(foldop.accept(''))
    def testOneIsAccepted(self):
        self.assertFoldTrue(foldop.accept(1))
    def testHelloIsAccepted(self):
        self.assertFoldTrue(foldop.accept('hello'))

class TestFoldOpNullMember(FoldOpTestCase):
    def setUp(self):
        self.empty = []
        self.allfalse = [0, False, '']
        self.alltrue = [1, 2, 3, 4, 5]
        self.alltrue_someunknown = [1, 2, None, 4, 5]
        self.allfalse_someunknown = [0, False, None, '']
    def testAny(self):
        self.assertFoldFalse(foldop.Any(self.empty))
        self.assertFoldFalse(foldop.Any(self.allfalse))
        self.assertFoldTrue(foldop.Any(self.alltrue))
        self.assertFoldTrue(foldop.Any(self.alltrue_someunknown))
        self.assertFoldFalse(foldop.Any(self.allfalse_someunknown))
    def testAll(self):
        self.assertFoldTrue(foldop.All(self.empty)) # all(empty) is true !
        self.assertFoldFalse(foldop.All(self.allfalse))
        self.assertFoldTrue(foldop.All(self.alltrue))
        self.assertFoldFalse(foldop.All(self.alltrue_someunknown))
        self.assertFoldFalse(foldop.All(self.allfalse_someunknown))

@IronPythonOnly
class TestFoldOpNullMemberIronPython(TestFoldOpNullMember):
    def setUp(self):
        TestFoldOpNullMember.setUp(self)
        self.alltrue_someunknown = [
            (dbnull if x is None else x)
            for x in self.alltrue_someunknown]
        self.allfalse_someunknown = [
            (dbnull if x is None else x)
            for x in self.allfalse_someunknown]

class TestFoldOpOperators(FoldOpTestCase):
    def assertNull(self, v): self.assertFoldTrue(foldop.isnull(v))
    def testNeg(self):
        self.assertFoldNull(foldop.neg(None))
        self.assertFoldEqual(0, foldop.neg(0))
        self.assertFoldEqual(-1, foldop.neg(1))
        self.assertFoldEqual(1, foldop.neg(-1))
    @IronPythonOnly
    def testNeg_IronPython(self):
        self.assertFoldNull(foldop.neg(dbnull))
    def testPos(self):
        self.assertFoldNull(foldop.pos(None))
        self.assertFoldEqual(0, foldop.pos(0))
        self.assertFoldEqual(1, foldop.pos(1))
        self.assertFoldEqual(-1, foldop.pos(-1))
    @IronPythonOnly
    def testPos_IronPython(self):
        self.assertFoldNull(foldop.pos(dbnull))
    def testSummarize(self):
        self.assertFoldNull(foldop.summarize(1, 2, None, 4))
        self.assertFoldEqual(10, foldop.summarize(1, 2, 3, 4))
    @IronPythonOnly
    def testSummarize_IronPython(self):
        self.assertFoldNull(foldop.summarize(1, dbnull, 3, 4))
    def testSub(self):
        self.assertFoldNull(foldop.sub(1, None))
        self.assertFoldEqual(1, foldop.sub(1, 0))
        self.assertFoldEqual(0, foldop.sub(1, 1))
        self.assertFoldEqual(-1, foldop.sub(1, 2))
    @IronPythonOnly
    def testSub_IronPython(self):
        self.assertFoldNull(foldop.sub(dbnull, 1))
    def testMultiply(self):
        self.assertFoldNull(foldop.multiply(1, None, 3, 4))
        self.assertFoldEqual(24, foldop.multiply(1, 2, 3, 4))
    @IronPythonOnly
    def testMultiply_IronPython(self):
        self.assertFoldNull(foldop.multiply(1, 2, dbnull, 4))
    def testTrueDiv(self):
        self.assertFoldNull(foldop.truediv(25, None))
        self.assertFoldEqual(5.5, foldop.truediv(33, 6))
    @IronPythonOnly
    def testTrueDiv_IronPython(self):
        self.assertFoldNull(foldop.truediv(dbnull, 4))
    def testFloorDiv(self):
        self.assertFoldNull(foldop.floordiv(25, None))
        self.assertFoldEqual(5, foldop.floordiv(33, 6))
    @IronPythonOnly
    def testFloorDiv_IronPython(self):
        self.assertFoldNull(foldop.floordiv(dbnull, 4))
    def testConcat(self):
        self.assertFoldNull(foldop.concat('a', 'b', None, 'd'))
        self.assertFoldEqual('abcd', foldop.concat('a', 'b', 'c', 'd'))
    @IronPythonOnly
    def testConcat_IronPython(self):
        self.assertFoldNull(foldop.concat('a', dbnull, 'c', 'd'))
    def testIn(self):
        S = [1, None, 3, 4, None, 6, 7]
        self.assertFoldNull(foldop.isin(2, S))
        self.assertFoldNull(foldop.isin(None, [1, 2, 3]))
        self.assertFoldTrue(foldop.isin(4, S))
    @IronPythonOnly
    def testIn_IronPython(self):
        S = [1, None, 3, 4, dbnull, 6, 7]
        self.assertFoldNull(foldop.isin(2, S))
        self.assertFoldNull(foldop.isin(None, [1, 2, 3]))
        self.assertFoldNull(foldop.isin(dbnull, [1, 2, 3]))
        self.assertFoldTrue(foldop.isin(4, S))
    def testNotIn(self):
        S = [1, None, 3, 4, None, 6, 7]
        self.assertFoldNull(foldop.notin(2, S))
    @IronPythonOnly
    def testNotIn_IronPython(self):
        S = [1, None, 3, 4, dbnull, 6, 7]
        self.assertFoldNull(foldop.notin(2, S))
    def testLessThan(self):
        self.assertFoldNull(foldop.lt(None, None))
        self.assertFoldNull(foldop.lt(1, None))
        self.assertFoldTrue(foldop.lt(1, 3))
        self.assertFoldFalse(foldop.lt(3, 1))
        self.assertFoldFalse(foldop.lt(2, 2))
    @IronPythonOnly
    def testLessThanIronPython(self):
        self.assertFoldNull(foldop.lt(dbnull, dbnull))
        self.assertFoldNull(foldop.lt(dbnull, 0))
    def testLessThanOrEqual(self):
        self.assertFoldNull(foldop.le(None, None))
        self.assertFoldNull(foldop.le(1, None))
        self.assertFoldTrue(foldop.le(1, 3))
        self.assertFoldFalse(foldop.le(3, 1))
        self.assertFoldTrue(foldop.le(2, 2))
    @IronPythonOnly
    def testLessThanOrEqual_IronPython(self):
        self.assertFoldNull(foldop.le(dbnull, dbnull))
        self.assertFoldNull(foldop.le(dbnull, 0))
    def testEqual(self):
        self.assertFoldNull(foldop.eq(None, None))
        self.assertFoldNull(foldop.eq(1, None))
        self.assertFoldFalse(foldop.eq(1, 3))
        self.assertFoldFalse(foldop.eq(3, 1))
        self.assertFoldTrue(foldop.eq(2, 2))
    @IronPythonOnly
    def testEqual_IronPython(self):
        self.assertFoldNull(foldop.eq(dbnull, dbnull))
        self.assertFoldNull(foldop.eq(dbnull, 0))
    def testNotEqual(self):
        self.assertFoldNull(foldop.ne(None, None))
        self.assertFoldNull(foldop.ne(1, None))
        self.assertFoldTrue(foldop.ne(1, 3))
        self.assertFoldTrue(foldop.ne(3, 1))
        self.assertFoldFalse(foldop.ne(2, 2))
    @IronPythonOnly
    def testNotEqual_IronPython(self):
        self.assertFoldNull(foldop.ne(dbnull, dbnull))
        self.assertFoldNull(foldop.ne(dbnull, 0))
    def testGreaterThanOrEqual(self):
        self.assertFoldNull(foldop.ge(None, None))
        self.assertFoldNull(foldop.ge(1, None))
        self.assertFoldFalse(foldop.ge(1, 3))
        self.assertFoldTrue(foldop.ge(3, 1))
        self.assertFoldTrue(foldop.ge(2, 2))
    @IronPythonOnly
    def testGreaterThanOrEqual_IronPython(self):
        self.assertFoldNull(foldop.ge(dbnull, dbnull))
        self.assertFoldNull(foldop.ge(dbnull, 0))
    def testGreaterThan(self):
        self.assertFoldNull(foldop.gt(None, None))
        self.assertFoldNull(foldop.gt(1, None))
        self.assertFoldFalse(foldop.gt(1, 3))
        self.assertFoldTrue(foldop.gt(3, 1))
        self.assertFoldFalse(foldop.gt(2, 2))
    @IronPythonOnly
    def testGreaterThan_IronPython(self):
        self.assertFoldNull(foldop.gt(dbnull, dbnull))
        self.assertFoldNull(foldop.gt(dbnull, 0))
    def testLike(self):
        self.assertTrue(nullop.REGEX_SPECIALS[0] == "\\")
        self.assertNotIn("%", nullop.REGEX_SPECIALS)
        self.assertNotIn("_", nullop.REGEX_SPECIALS)
        self.assertFoldNull(foldop.like(None, None))
        self.assertFoldNull(foldop.like("hello", None))
        self.assertFoldTrue(foldop.like("hello", "hell%"))
        self.assertFoldFalse(foldop.like("hello", "ha%"))
        self.assertFoldTrue(foldop.like("a * b", "a *%"))
        self.assertFoldFalse(foldop.like("hello", "he%", "e"))
        self.assertFoldTrue(foldop.like("h%llo", "he%llo", "e"))
        self.assertFoldTrue(foldop.like("h%llo_", "he%lloe_", "e"))
        self.assertFoldTrue(foldop.like("hello", "%llo", "e"))
        self.assertFoldTrue(foldop.like("\\.^$*+?{}[]()<>|", "\\.^$*+?{}[]()<>|"))
    @IronPythonOnly
    def testLike_IronPython(self):
        self.assertFoldNull(foldop.like(dbnull, dbnull))
        self.assertFoldNull(foldop.like(dbnull, 'hell%'))
    def testBetween(self):
        self.assertFoldNull(foldop.between(4, None, 9))
        self.assertFoldTrue(foldop.between(1, 1, 9))
        self.assertFoldTrue(foldop.between(9, 1, 9))
        self.assertFoldFalse(foldop.between(0, 1, 9))
        self.assertFoldFalse(foldop.between(10, 1, 9))
    @IronPythonOnly
    def testBetween_IronPython(self):
        self.assertFoldNull(foldop.between(None, dbnull, None))
        self.assertFoldNull(foldop.between(2, 1, dbnull))
    def testAnd(self):
        self.assertFoldNull(foldop.And(True, True, None, True))
        self.assertFoldNull(foldop.And(None, None))
        self.assertFoldTrue(foldop.And(True, True))
        self.assertFoldTrue(foldop.And())
        self.assertFoldFalse(foldop.And(False))
        self.assertFoldTrue(foldop.And(True))
        self.assertFoldFalse(foldop.And(None, False))
    @IronPythonOnly
    def testAnd_IronPython(self):
        self.assertFoldNull(foldop.And(dbnull, dbnull))
        self.assertFoldNull(foldop.And(True, dbnull, True, True))
        self.assertFoldFalse(foldop.And(dbnull, True, False))
    def testOr(self):
        self.assertFoldNull(foldop.Or(False, False, None, False))
        self.assertFoldNull(foldop.Or(None, None))
        self.assertFoldFalse(foldop.Or(False, False))
        self.assertFoldFalse(foldop.Or())
        self.assertFoldFalse(foldop.Or(False))
        self.assertFoldTrue(foldop.Or(True))
        self.assertFoldTrue(foldop.Or(None, True))
    @IronPythonOnly
    def testOr_IronPython(self):
        self.assertFoldNull(foldop.Or(False, dbnull, False, False))
        self.assertFoldNull(foldop.Or(dbnull, dbnull))
        self.assertFoldTrue(foldop.Or(dbnull, True, False))
    def testNot(self):
        self.assertFoldNull(foldop.Not(None))
        self.assertFoldFalse(foldop.Not(True))
        self.assertFoldTrue(foldop.Not(False))
    @IronPythonOnly
    def testNot_IronPythonOnly(self):
        self.assertFoldNull(foldop.Not(dbnull))
    def testPow(self):
        self.assertFoldNull(foldop.pow(2, None))
        self.assertFoldEqual(8, foldop.pow(2, 3))
    @IronPythonOnly
    def testPow_IronPython(self):
        self.assertFoldNull(foldop.pow(dbnull, 3))
        self.assertFoldNull(foldop.pow(None, dbnull))
    def testMod(self):
        self.assertFoldNull(foldop.mod(25, None))
        self.assertFoldEqual(1, foldop.mod(25, 8))
    @IronPythonOnly
    def testMod_IronPython(self):
        self.assertFoldNull(foldop.mod(dbnull, 3))
        self.assertFoldNull(foldop.mod(None, dbnull))
    def testConcat2(self):
        self.assertFoldEqual('ab', foldop.concat2('a', 'b'))
        self.assertFoldNull(foldop.concat2('a', None))
        self.assertFoldNull(foldop.concat2(None, 'b'))
        self.assertFoldNull(foldop.concat2(None, None))
    @IronPythonOnly
    def testConcat2_IronPython(self):
        self.assertFoldNull(foldop.concat2('a', dbnull))
        self.assertFoldNull(foldop.concat2(dbnull, 'b'))
        self.assertFoldNull(foldop.concat2(None, dbnull))
        self.assertFoldNull(foldop.concat2(dbnull, dbnull))
    def testUcase(self):
        self.assertFoldNull(foldop.ucase(None))
        self.assertFoldEqual('A', foldop.ucase('a'))
    @IronPythonOnly
    def testUcase_IronPython(self):
        self.assertFoldNull(foldop.ucase(dbnull))
    def testLcase(self):
        self.assertFoldNull(foldop.lcase(None))
        self.assertFoldEqual('a', foldop.lcase('A'))
    @IronPythonOnly
    def testLcase_IronPython(self):
        self.assertFoldNull(foldop.lcase(dbnull))
    def testReplace(self):
        self.assertFoldNull(foldop.replace(None, None, None))
        self.assertFoldNull(foldop.replace('hello', 'llo', None))
        self.assertFoldNull(foldop.replace('hello', None, 'lix'))
        self.assertFoldEqual('helix', foldop.replace('hello', 'llo' ,'lix'))
    @IronPythonOnly
    def testReplace_IronPython(self):
        self.assertFoldNull(foldop.replace(dbnull, dbnull, dbnull))
        self.assertFoldNull(foldop.replace(dbnull, 'llo', 'lix'))
    def testLtrim(self):
        self.assertFoldNull(foldop.ltrim(None))
        self.assertFoldEqual('A', foldop.ltrim('   A'))
        self.assertFoldEqual('A  ', foldop.ltrim('   A  '))
    @IronPythonOnly
    def testLtrim_IronPython(self):
        self.assertFoldNull(foldop.ltrim(dbnull))
    def testRtrim(self):
        self.assertFoldNull(foldop.rtrim(None))
        self.assertFoldEqual('A', foldop.rtrim('A  '))
        self.assertFoldEqual('   A', foldop.rtrim('   A  '))
    @IronPythonOnly
    def testRtrim_IronPython(self):
        self.assertFoldNull(foldop.rtrim(dbnull))
    def testTrim(self):
        self.assertFoldNull(foldop.trim(None))
        self.assertFoldEqual('A', foldop.trim('   A  '))
    @IronPythonOnly
    def testTrim_IronPython(self):
        self.assertFoldNull(foldop.trim(dbnull))
    def testCast(self):
        self.assertFoldEqual(3, foldop.cast('3', 'int'))
        self.assertFoldEqual(3, foldop.cast('3', int))
    @IronPythonOnly
    def testCast_IronPython(self):
        self.assertFoldNull(foldop.cast(dbnull, 'int'))
        self.assertFoldNull(foldop.cast(dbnull, int))
    def test_aggregate_summary(self):
        self.assertFoldNull(foldop.aggregate_summary([]))
        self.assertFoldNull(foldop.aggregate_summary([None, None, None]))
        self.assertFoldEqual(7, foldop.aggregate_summary([0, 1, 2, None, 4]))
        self.assertFoldEqual(10, foldop.aggregate_summary([0, 1, 2, 3, 4]))
    @IronPythonOnly
    def test_aggregate_summary_IronPython(self):
        self.assertFoldNull(foldop.aggregate_summary([dbnull, None, dbnull]))
        self.assertFoldEqual(7, foldop.aggregate_summary([0, 1, 2, dbnull, 4]))
    def test_aggregate_summaries(self):
        (r1, r2, r3) = foldop.aggregate_summaries(3, [])
        self.assertFoldNull(r1)
        self.assertFoldNull(r2)
        self.assertFoldNull(r3)
        (r1, r2, r3) = foldop.aggregate_summaries(3, [
            (   0,    3, None),
            (   5,    8, None),
            (None,    2, None),
            (   3, None, None) ] )
        self.assertFoldEqual(8, r1)
        self.assertFoldEqual(13, r2)
        self.assertFoldNull(r3)
    @IronPythonOnly
    def test_aggregate_summaries_IronPython(self):
        (r1, r2, r3) = foldop.aggregate_summaries(3, [])
        self.assertFoldNull(r1)
        self.assertFoldNull(r2)
        self.assertFoldNull(r3)
        (r1, r2, r3) = foldop.aggregate_summaries(3, [
            (   0,      3, dbnull),
            (   5,      8, dbnull),
            (None,      2,   None),
            (   3, dbnull, dbnull) ] )
        self.assertFoldEqual(8, r1)
        self.assertFoldEqual(13, r2)
        self.assertFoldNull(r3)
    def test_aggregate_minimum(self):
        self.assertFoldNull(foldop.aggregate_minimum([]))
        self.assertFoldNull(foldop.aggregate_minimum([None, None, None]))
        self.assertFoldEqual(0, foldop.aggregate_minimum([0, 1, 2, None, 4]))
        self.assertFoldEqual(0, foldop.aggregate_minimum([0, 1, 2, 3, 4]))
    @IronPythonOnly
    def test_aggregate_minimum_IronPython(self):
        self.assertFoldNull(foldop.aggregate_minimum([dbnull, None, dbnull]))
        self.assertFoldEqual(0, foldop.aggregate_minimum([0, 1, 2, dbnull, 4]))
    def test_aggregate_minimums(self):
        (r1, r2, r3) = foldop.aggregate_minimums(3, [])
        self.assertFoldNull(r1)
        self.assertFoldNull(r2)
        self.assertFoldNull(r3)
        (r1, r2, r3) = foldop.aggregate_minimums(3, [
            (   0,    3, None),
            (   5,    8, None),
            (None,    2, None),
            (   3, None, None) ] )
        self.assertFoldEqual(0, r1)
        self.assertFoldEqual(2, r2)
        self.assertFoldNull(r3)
    @IronPythonOnly
    def test_aggregate_minimums_IronPython(self):
        (r1, r2, r3) = foldop.aggregate_minimums(3, [])
        self.assertFoldNull(r1)
        self.assertFoldNull(r2)
        self.assertFoldNull(r3)
        (r1, r2, r3) = foldop.aggregate_minimums(3, [
            (   0,      3, dbnull),
            (   5,      8, dbnull),
            (None,      2,   None),
            (   3, dbnull, dbnull) ] )
        self.assertFoldEqual(0, r1)
        self.assertFoldEqual(2, r2)
        self.assertFoldNull(r3)
    def test_aggregate_maximum(self):
        self.assertFoldNull(foldop.aggregate_maximum([]))
        self.assertFoldNull(foldop.aggregate_maximum([None, None, None]))
        self.assertFoldEqual(4, foldop.aggregate_maximum([0, 1, 2, None, 4]))
        self.assertFoldEqual(4, foldop.aggregate_maximum([0, 1, 2, 3, 4]))
    @IronPythonOnly
    def test_aggregate_maximum_IronPython(self):
        self.assertFoldNull(foldop.aggregate_maximum([dbnull, None, dbnull]))
        self.assertFoldEqual(4, foldop.aggregate_maximum([0, 1, 2, dbnull, 4]))
    def test_aggregate_maximums(self):
        (r1, r2, r3) = foldop.aggregate_maximums(3, [])
        self.assertFoldNull(r1)
        self.assertFoldNull(r2)
        self.assertFoldNull(r3)
        (r1, r2, r3) = foldop.aggregate_maximums(3, [
            (   0,    3, None),
            (   5,    8, None),
            (None,    2, None),
            (   3, None, None) ] )
        self.assertFoldEqual(5, r1)
        self.assertFoldEqual(8, r2)
        self.assertFoldNull(r3)
    @IronPythonOnly
    def test_aggregate_maximums_IronPython(self):
        (r1, r2, r3) = foldop.aggregate_maximums(3, [])
        self.assertFoldNull(r1)
        self.assertFoldNull(r2)
        self.assertFoldNull(r3)
        (r1, r2, r3) = foldop.aggregate_maximums(3, [
            (   0,      3, dbnull),
            (   5,      8, dbnull),
            (None,      2,   None),
            (   3, dbnull, dbnull) ] )
        self.assertFoldEqual(5, r1)
        self.assertFoldEqual(8, r2)
        self.assertFoldNull(r3)
    def test_aggregate_count(self):
        self.assertFoldEqual(0, foldop.aggregate_count([None, None, None]))
        self.assertFoldEqual(3, foldop.aggregate_count([None, 1, 2, None, 5]))
    @IronPythonOnly
    def test_aggregate_count_IronPython(self):
        self.assertFoldEqual(0, foldop.aggregate_count([dbnull, dbnull, dbnull]))
        self.assertFoldEqual(3, foldop.aggregate_count([dbnull, 1, 2, dbnull, 5]))
    def test_aggregate_counts(self):
        (r1, r2, r3) = foldop.aggregate_counts(3, [])
        self.assertFoldEqual(0, r1)
        self.assertFoldEqual(0, r2)
        self.assertFoldEqual(0, r3)
        (r1, r2, r3) = foldop.aggregate_counts(3, [
            (   0,    3, None),
            (   5, None, None),
            (None,    2, None),
            (   3, None, None) ] )
        self.assertFoldEqual(3, r1)
        self.assertFoldEqual(2, r2)
        self.assertFoldEqual(0, r3)
    @IronPythonOnly
    def test_aggregate_counts_IronPython(self):
        (r1, r2, r3) = foldop.aggregate_maximums(3, [])
        self.assertFoldEqual(0, r1)
        self.assertFoldEqual(0, r2)
        self.assertFoldEqual(0, r3)
        (r1, r2, r3) = foldop.aggregate_maximums(3, [
            (   0,      3, dbnull),
            (   5,   None, dbnull),
            (None,      2,   None),
            (   3, dbnull, dbnull) ] )
        self.assertFoldEqual(5, r1)
        self.assertFoldEqual(8, r2)
        self.assertFoldEqual(0, r3)

class TestFoldIsNull(unittest.TestCase):
    def testFoldIsSlotty(self):
        self.assertTrue(util.slotty(Fold))
    def testNoneIsNull(self):
        self.assertTrue(fold(None).is_null)
    @IronPythonOnly
    def testDBNullIsNull(self):
        self.assertTrue(fold(dbnull).is_null)
    def testZeroIsNotNull(self):
        self.assertFalse(fold(0).is_null)
        self.assertFalse(fold(0).isnull())
        self.assertTrue(fold(0).is_not_null)
        self.assertTrue(fold(0).notnull())
    def testEmptyStringIsNotNull(self):
        self.assertFalse(fold('').is_null)
        self.assertFalse(fold('').isnull())
        self.assertTrue(fold('').is_not_null)
        self.assertTrue(fold('').notnull())
    def testOneIsNotNull(self):
        self.assertFalse(fold(1).is_null)
        self.assertFalse(fold(1).isnull())
        self.assertTrue(fold(1).is_not_null)
        self.assertTrue(fold(1).notnull())
    def testHelloIsNotNull(self):
        self.assertFalse(nullop.isnull(fold('hello')))

class TestFoldAccept(unittest.TestCase):
    def testNoneIsNotAccepted(self):
        self.assertFalse(fold(None))
    @IronPythonOnly
    def testDBNullIsNotAccepted(self):
        self.assertFalse(fold(dbnull))
    def testZeroIsNotAccepted(self):
        self.assertFalse(fold(0))
    def testEmptyStringIsNotAccepted(self):
        self.assertFalse(fold(''))
    def testOneIsAccepted(self):
        self.assertTrue(fold(1))
    def testHelloIsAccepted(self):
        self.assertTrue(fold('hello'))

class TestFoldNullMember(unittest.TestCase):
    def getnull(self): return None
    def setUp(self):
        self.empty = fold([])
        self.allfalse = fold([0, False, ''])
        self.alltrue = fold([1, 2, 3, 4, 5])
        self.alltrue_someunknown = fold([1, 2, self.getnull(), 4, 5])
        self.allfalse_someunknown = fold([0, False, self.getnull(), ''])
    def testAny(self):
        self.assertFalse(nullop.Any(self.empty))
        self.assertFalse(nullop.Any(self.allfalse))
        self.assertTrue(nullop.Any(self.alltrue))
        self.assertTrue(nullop.Any(self.alltrue_someunknown))
        self.assertFalse(nullop.Any(self.allfalse_someunknown))
    def testAll(self):
        self.assertTrue(nullop.All(self.empty)) # all(empty) is true !
        self.assertFalse(nullop.All(self.allfalse))
        self.assertTrue(nullop.All(self.alltrue))
        self.assertFalse(nullop.All(self.alltrue_someunknown))
        self.assertFalse(nullop.All(self.allfalse_someunknown))

@IronPythonOnly
class TestFoldNullMemberIronPython(TestFoldNullMember):
    def getnull(self): return dbnull

class TestFoldOperators(unittest.TestCase):
    def assertNull(self, v): self.assertTrue(v.is_null)
    def testNeg(self):
        self.assertNull(- fold(None))
        self.assertEqual(0, - fold(0))
        self.assertEqual(-1, - fold(1))
        self.assertEqual(1, - fold(-1))
    @IronPythonOnly
    def testNeg_IronPython(self):
        self.assertNull(- fold(dbnull))
    def testPos(self):
        self.assertNull(+ fold(None))
        self.assertEqual(0, + fold(0))
        self.assertEqual(1, + fold(1))
        self.assertEqual(-1, + fold(-1))
    @IronPythonOnly
    def testPos_IronPython(self):
        self.assertNull(+ fold(dbnull))
    def testSummarize(self):
        self.assertNull(fold(1) + fold(2) + fold(None) + fold(4))
        self.assertNull(sum(fold([1, 2, None, 4])))
        self.assertEqual(10, fold(1) + fold(2) + fold(3) + fold(4))
        self.assertEqual(10, sum(fold([1, 2, 3, 4])))
    @IronPythonOnly
    def testSummarize_IronPython(self):
        self.assertNull(fold(1) + fold(2) + fold(dbnull) + fold(4))
        self.assertNull(sum(fold([1, 2, dbnull, 4])))
    def testSub(self):
        self.assertNull(fold(1) - fold(None))
        self.assertEqual(1, fold(1) - fold(0))
        self.assertEqual(0, fold(1) - fold(1))
        self.assertEqual(-1, fold(1) - fold(2))
    @IronPythonOnly
    def testSub_IronPython(self):
        self.assertNull(fold(dbnull) - fold(1))
    def testMultiply(self):
        self.assertNull(fold(1) * fold(None) * fold(3) * fold(4))
        self.assertEqual(24, fold(1) * fold(2) * fold(3) * fold(4))
    @IronPythonOnly
    def testMultiply_IronPython(self):
        self.assertNull(fold(1) * fold(2) * fold(dbnull))
    def testFloorDiv(self):
        self.assertNull(fold(25) // fold(None))
        self.assertEqual(5, fold(33) // fold(6))
    @IronPythonOnly
    def testFloorDiv_IronPython(self):
        self.assertNull(fold(25) // fold(dbnull))
    def testTrueDiv(self):
        self.assertNull(fold(25) / fold(None))
        self.assertEqual(5.5, fold(33) / fold(6))
    @IronPythonOnly
    def testTrueDiv_IronPython(self):
        self.assertNull(fold(25) / fold(dbnull))
    def testConcat(self):
        self.assertNull(fold('a').append('b').append(fold(None)).append('d'))
        self.assertEqual('abcd', fold('a').append('b').append('c').append(fold('d')))
        self.assertEqual('dbac', fold('a').prepend('b').append('c').prepend(fold('d')))
        self.assertEqual('abcd', 'a' + fold('b') + 'c' + fold('d'))
    @IronPythonOnly
    def testConcat_IronPython(self):
        self.assertNull(nullop.concat('a', dbnull, fold('c'), fold('d')))
    def testIn(self):
        S = [1, None, 3, 4, None, fold(6), 7]
        self.assertNull(fold(2).in_(*S))
        self.assertNull(fold(None).in_(1, 2, 3))
        self.assertTrue(fold(4).in_(*S))
    @IronPythonOnly
    def testIn_IronPython(self):
        S = [1, None, 3, 4, dbnull, fold(6), 7]
        self.assertNull(fold(2).in_(*S))
        self.assertNull(fold(None).in_(1, 2, 3))
        self.assertTrue(fold(4).in_(*S))
    def testNotIn(self):
        S = [1, None, 3, 4, None, fold(6), 7]
        self.assertNull(fold(2).not_in_(*S))
    @IronPythonOnly
    def testNotIn_IronPython(self):
        S = [1, None, 3, 4, dbnull, fold(6), 7]
        self.assertNull(fold(2).not_in_(*S))
    def testLessThan(self):
        self.assertNull(fold(None) < None)
        self.assertNull(1 < fold(None))
        self.assertTrue(fold(1) < fold(3))
        self.assertFalse(fold(3) < 1)
        self.assertFalse(2 < fold(2))
    @IronPythonOnly
    def testLessThanIronPython(self):
        self.assertNull(fold(dbnull) < None)
        self.assertNull(fold(dbnull) < 0)
    def testLessThanOrEqual(self):
        self.assertNull(fold(None) <= None)
        self.assertNull(1 <= fold(None))
        self.assertTrue(fold(1) <= fold(3))
        self.assertFalse(fold(3) <= 1)
        self.assertTrue(2 <= fold(2))
    @IronPythonOnly
    def testLessThanOrEqual_IronPython(self):
        self.assertNull(fold(dbnull) <= None)
        self.assertNull(fold(dbnull) <= 0)
    def testEqual(self):
        self.assertNull(fold(None) == None)
        self.assertNull(1 == fold(None))
        self.assertFalse(fold(1) == fold(3))
        self.assertFalse(fold(3) == 1)
        self.assertTrue(2 == fold(2))
    @IronPythonOnly
    def testEqual_IronPython(self):
        self.assertNull(fold(dbnull) == None)
        self.assertNull(fold(dbnull) == 0)
    def testNotEqual(self):
        self.assertNull(fold(None) != None)
        self.assertNull(1 != fold(None))
        self.assertTrue(fold(1) != fold(3))
        self.assertTrue(fold(3) != 1)
        self.assertFalse(2 != fold(2))
    @IronPythonOnly
    def testNotEqual_IronPython(self):
        self.assertNull(fold(dbnull) != None)
        self.assertNull(fold(dbnull) != 0)
    def testGreaterThanOrEqual(self):
        self.assertNull(fold(None) >= None)
        self.assertNull(1 >= fold(None))
        self.assertFalse(fold(1) >= fold(3))
        self.assertTrue(fold(3) >= 1)
        self.assertTrue(2 >= fold(2))
    @IronPythonOnly
    def testGreaterThanOrEqual_IronPython(self):
        self.assertNull(fold(dbnull) >= None)
        self.assertNull(fold(dbnull) >= 0)
    def testGreaterThan(self):
        self.assertNull(fold(None) > None)
        self.assertNull(1 > fold(None))
        self.assertFalse(fold(1) > fold(3))
        self.assertTrue(fold(3) > 1)
        self.assertFalse(2 > fold(2))
    @IronPythonOnly
    def testGreaterThan_IronPython(self):
        self.assertNull(fold(dbnull) > None)
        self.assertNull(fold(dbnull) > 0)
    def testLike(self):
        self.assertNull(fold(None).like(None))
        self.assertNull(fold('hello').like(None))
        self.assertTrue(fold('hello').like('hell_'))
        self.assertTrue(fold('hello').like('he%'))
        self.assertFalse(fold('hello').like('hello_'))
        self.assertTrue(fold('hello').like('hello%'))
        self.assertFalse(fold('hello').like('ho%'))
        self.assertFalse(fold('hello').like('he%', 'e'))
        self.assertTrue(fold('h%llo').like('he%llo', 'e'))
        self.assertTrue(fold('h%llo_').like('he%lloe_', 'e'))
        self.assertTrue(fold('hello').like('%llo', 'e'))
        self.assertTrue(fold('\\.^$*+?{}[]()<>|').like('\\.^$*+?{}[]()<>|'))
    @IronPythonOnly
    def testLike_IronPython(self):
        self.assertNull(fold(dbnull).like(dbnull))
        self.assertNull(fold(dbnull.like('hell%')))
    def testBetween(self):
        self.assertNull(fold(4).between(None, 9))
        self.assertNull(fold(None).between(1, 9))
        self.assertTrue(fold(1).between(1, 9))
        self.assertFalse(fold(0).between(1, 9))
        self.assertFalse(fold(10).between(1, 9))
    @IronPythonOnly
    def testBetween_IronPython(self):
        self.assertNull(fold(4).between(dbnull, 9))
        self.assertNull(fold(dbnull).between(1, 9))
    def testAnd(self):
        self.assertNull(fold(True).and_(True).and_(None).and_(True))
        self.assertNull(fold(None).and_(None))
        self.assertTrue(fold(True).and_(fold(True)))
        self.assertFalse(fold(None).and_(False))
    @IronPythonOnly
    def testAnd_IronPython(self):
        self.assertNull(fold(True).and_(True).and_(dbnull).and_(True))
        self.assertNull(fold(dbnull).and_(dbnull))
        self.assertFalse(fold(dbnull).and_(False))
    def testOr(self):
        self.assertNull(fold(False).or_(False).or_(None).or_(False))
        self.assertNull(fold(None).or_(None))
        self.assertFalse(fold(False).or_(fold(False)))
        self.assertTrue(fold(None).or_(True))
    @IronPythonOnly
    def testOr_IronPython(self):
        self.assertNull(fold(False).and_(False).and_(dbnull).and_(False))
        self.assertNull(fold(dbnull).and_(dbnull))
        self.assertTrue(fold(dbnull).and_(True))
    def testNot(self):
        self.assertNull(fold(None).not_)
        self.assertFalse(fold(True).not_)
        self.assertTrue(fold(False).not_)
    @IronPythonOnly
    def testNot_IronPythonOnly(self):
        self.assertNull(fold(dbnull).not_)
    def testPow(self):
        self.assertNull(fold(2) ** None)
        self.assertNull(fold(None) ** 3)
        self.assertEqual(8, fold(2) ** 3)
        self.assertEqual(9, 3 ** fold(2))
    @IronPythonOnly
    def testPow_IronPython(self):
        self.assertNull(fold(2) ** dbnull)
        self.assertNull(fold(dbnull) ** 3)
    def testMod(self):
        self.assertNull(fold(25) % None)
        self.assertNull(None % fold(8))
        self.assertEqual(1, fold(25) % 8)
        self.assertEqual(1, 25 % fold(8))
    @IronPythonOnly
    def testMod_IronPython(self):
        self.assertNull(fold(25) % dbnull)
        self.assertNull(dbnull % fold(8))
    def testConcat2(self):
        self.assertEqual('ab', fold('a') + fold('b'))
        self.assertEqual('ab', fold('a') + 'b')
        self.assertEqual('ab', 'a' + fold('b'))
        self.assertNull(fold(None) + fold('b'))
        self.assertNull(fold('a') + fold(None))
        self.assertNull(None + fold('b'))
        self.assertNull(fold('a') + None)
    @IronPythonOnly
    def testConcat2_IronPython(self):
        self.assertNull(fold(dbnull) + fold('b'))
        self.assertNull(fold('a') + fold(dbnull))
        self.assertNull(dbnull + fold('b'))
        self.assertNull(fold('a') + dbnull)
    def testUcase(self):
        self.assertNull(fold(None).upper())
        self.assertEqual('A', fold('a').upper())
    @IronPythonOnly
    def testUcase_IronPython(self):
        self.assertNull(fold(dbnull).upper())
    def testLcase(self):
        self.assertNull(fold(None).lower())
        self.assertEqual('a', fold('A').lower())
    @IronPythonOnly
    def testLcase_IronPython(self):
        self.assertNull(fold(dbnull).lower())
    def testReplace(self):
        self.assertNull(fold(None).replace(None, None))
        self.assertNull(fold('hello').replace('llo', None))
        self.assertNull(fold('hello').replace('llo', None))
        self.assertEqual('helix', (fold('hello').replace('llo', 'lix')))
    @IronPythonOnly
    def testReplace_IronPython(self):
        self.assertNull(fold(dbnull).replace(dbnull, dbnull))
        self.assertNull(fold('hello').replace('llo', dbnull))
        self.assertNull(fold('hello').replace('llo', dbnull))
    def testLtrim(self):
        self.assertNull(fold(None).lstrip())
        self.assertEqual('A', fold('    A').lstrip())
        self.assertEqual('A   ', fold('  A   ').lstrip())
    @IronPythonOnly
    def testLtrim_IronPython(self):
        self.assertNull(fold(dbnull).lstrip())
    def testRtrim(self):
        self.assertNull(fold(None).rstrip())
        self.assertEqual('A', fold('A    ').rstrip())
        self.assertEqual('   A', fold('   A  ').rstrip())
    @IronPythonOnly
    def testRtrim_IronPython(self):
        self.assertNull(fold(dbnull))
    def testTrim(self):
        self.assertNull(fold(None).strip())
        self.assertEqual('A', fold('  A   ').strip())
    @IronPythonOnly
    def testTrim_IronPython(self):
        self.assertNull(fold(dbnull).strip())
    def testCast(self):
        self.assertNull(fold(None).cast(int))
        self.assertNull(fold(None).cast('int'))
        self.assertEqual(3, fold('3').cast(int))
        self.assertEqual(3, fold('3').cast('int'))
    @IronPythonOnly
    def testCast_IronPython(self):
        self.assertNull(fold(dbnull).cast(int))
        self.assertNull(fold(dbnull).cast('int'))
    def test_aggregate_summary(self):
        self.assertNull(fold(nullop.aggregate_summary([])))
        self.assertNull(fold(nullop.aggregate_summary(fold([None, None, None]))))
        self.assertEqual(7, nullop.aggregate_summary(fold([0, 1, 2, None, 4])))
        self.assertEqual(10, nullop.aggregate_summary(fold([0, 1, 2, 3, 4])))
    @IronPythonOnly
    def test_aggregate_summary_IronPython(self):
        self.assertNull(fold(nullop.aggregate_summary(fold([dbnull, dbnull, None]))))
        self.assertEqual(7, nullop.aggregate_summary(fold([0, 1, 2, dbnull, 4])))
    def test_aggregate_summaries(self):
        items = fold([ (   0,    3, None),
                       (   5,    8, None),
                       (None,    2, None),
                       (   3, None, None) ] )
        (r1, r2, r3) = fold(nullop.aggregate_summaries(3, items))
        self.assertEqual(8, r1)
        self.assertEqual(13, r2)
        self.assertNull(r3)
    @IronPythonOnly
    def test_aggregate_summaries_IronPython(self):
        items = fold([ (   0,      3, dbnull),
                       (   5,      8, dbnull),
                       (None,      2,   None),
                       (   3, dbnull, dbnull) ] )
        (r1, r2, r3) = fold(nullop.aggregate_summaries(3, items))
        self.assertEqual(8, r1)
        self.assertEqual(13, r2)
        self.assertNull(r3)
    def test_aggregate_minimum(self):
        self.assertNull(fold(nullop.aggregate_minimum(fold([None, None, None]))))
        self.assertEqual(0, fold(nullop.aggregate_minimum(fold([0, 1, 2, None, 4]))))
        self.assertEqual(0, fold(nullop.aggregate_minimum(fold([0, 1, 2, 3, 4]))))
    @IronPythonOnly
    def test_aggregate_minimum_IronPython(self):
        self.assertNull(fold(nullop.aggregate_minimum(fold([dbnull, None, dbnull]))))
        self.assertEqual(0, fold(nullop.aggregate_minimum(fold([0, 1, 2, dbnull, 4]))))
    def test_aggregate_minimums(self):
        items = fold([ (   0,    3, None),
                       (   5,    8, None),
                       (None,    2, None),
                       (   3, None, None) ])
        (r1, r2, r3) = fold(nullop.aggregate_minimums(3, items))
        self.assertEqual(0, r1)
        self.assertEqual(2, r2)
        self.assertNull(r3)
    @IronPythonOnly
    def test_aggregate_minimums_IronPython(self):
        items = fold([ (   0,      3, dbnull),
                       (   5,      8, dbnull),
                       (None,      2,   None),
                       (   3, dbnull, dbnull) ])
        (r1, r2, r3) = fold(nullop.aggregate_minimums(3,  items))
        self.assertEqual(0, r1)
        self.assertEqual(2, r2)
        self.assertNull(r3)
    def test_aggregate_maximum(self):
        self.assertNull(fold(nullop.aggregate_maximum(fold([None, None, None]))))
        self.assertEqual(4, fold(nullop.aggregate_maximum(fold([0, 1, 2, None, 4]))))
        self.assertEqual(4, fold(nullop.aggregate_maximum(fold([0, 1, 2, 3, 4]))))
    @IronPythonOnly
    def test_aggregate_maximum_IronPython(self):
        self.assertNull(fold(nullop.aggregate_maximum(fold([dbnull, None, dbnull]))))
        self.assertEqual(4, fold(nullop.aggregate_maximum(fold([0, 1, 2, dbnull, 4]))))
    def test_aggregate_maximums(self):
        items = fold([ (   0,    3, None),
                       (   5,    8, None),
                       (None,    2, None),
                       (   3, None, None) ])
        (r1, r2, r3) = fold(nullop.aggregate_maximums(3, items))
        self.assertEqual(5, r1)
        self.assertEqual(8, r2)
        self.assertNull(r3)
    @IronPythonOnly
    def test_aggregate_maximums_IronPython(self):
        items = fold([ (   0,      3, dbnull),
                       (   5,      8, dbnull),
                       (None,      2, dbnull),
                       (   3, dbnull, dbnull) ])
        (r1, r2, r3) = nullop.aggregate_maximums(3, items)
        self.assertEqual(5, r1)
        self.assertEqual(8, r2)
        self.assertNull(r3)
    def test_aggregate_count(self):
        self.assertEqual(0, fold(nullop.aggregate_count(fold([None, None, None]))))
        self.assertEqual(3, fold(nullop.aggregate_count(fold([None, 1, 2, None, 5]))))
    @IronPythonOnly
    def test_aggregate_count_IronPython(self):
        self.assertEqual(0, fold(nullop.aggregate_count(fold([dbnull, dbnull, dbnull]))))
        self.assertEqual(3, fold(nullop.aggregate_count(fold([dbnull, 1, 2, dbnull, 5]))))
    def test_aggregate_counts(self):
        items = fold([ (   0,    3, None),
                       (   5, None, None),
                       (None,    2, None),
                       (   3, None, None) ])
        (r1, r2, r3) = fold(nullop.aggregate_counts(3, items))
        self.assertEqual(3, r1)
        self.assertEqual(2, r2)
        self.assertEqual(0, r3)
    @IronPythonOnly
    def test_aggregate_counts_IronPython(self):
        items = fold([ (   0,      3, dbnull),
                       (   5,   None, dbnull),
                       (None,      2,   None),
                       (   3, dbnull, dbnull) ])
        (r1, r2, r3) = fold(nullop.aggregate_counts(3, items))
        self.assertEqual(3, r1)
        self.assertEqual(2, r2)
        self.assertEqual(0, r3)
