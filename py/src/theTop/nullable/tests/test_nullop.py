#! -*- coding: utf-8 -*-

import unittest
from .. import nullop

IronPythonOnly = unittest.skipIf(not hasattr(nullop, 'DBNull'), 'For IronPython only')

if hasattr(nullop, 'DBNull'): dbnull = getattr(nullop, 'DBNull').Value

class TestIsNull(unittest.TestCase):
    def testNoneIsNull(self):
        self.assertTrue(nullop.isnull(None))
    @IronPythonOnly
    def testDBNullIsNull(self):
        self.assertTrue(nullop.isnull(dbnull))
    def testZeroIsNotNull(self):
        self.assertFalse(nullop.isnull(0))
    def testEmptyStringIsNotNull(self):
        self.assertFalse(nullop.isnull(''))
    def testOneIsNotNull(self):
        self.assertFalse(nullop.isnull(1))
    def testHelloIsNotNull(self):
        self.assertFalse(nullop.isnull('hello'))
    def testEmptyTupleIsNotNull(self):
        self.assertFalse(nullop.isnull(()))
    def testEmptyListIsNotNull(self):
        self.assertFalse(nullop.isnull([]))
    def testEmptyDictIsNotNull(self):
        self.assertFalse(nullop.isnull({}))

class TestAccept(unittest.TestCase):
    def testNoneIsNotAccepted(self):
        self.assertFalse(nullop.accept(None))
    @IronPythonOnly
    def testDBNullIsNotAccepted(self):
        self.assertFalse(nullop.accept(dbnull))
    def testZeroIsNotAccepted(self):
        self.assertFalse(nullop.accept(0))
    def testEmptyStringIsNotAccepted(self):
        self.assertFalse(nullop.accept(''))
    def testOneIsAccepted(self):
        self.assertTrue(nullop.accept(1))
    def testHelloIsAccepted(self):
        self.assertTrue(nullop.accept('hello'))
    def testEmptyTupleIsNotAccepted(self):
        self.assertFalse(nullop.accept(()))
    def testEmptyListIsNotAccepted(self):
        self.assertFalse(nullop.accept([]))
    def testEmptyDictIsNotAccepted(self):
        self.assertFalse(nullop.accept({}))

class TestNullMember(unittest.TestCase):
    def setUp(self):
        self.empty = []
        self.allfalse = [0, False, '']
        self.alltrue = [1, 2, 3, 4, 5]
        self.alltrue_someunknown = [1, 2, None, 4, 5]
        self.allfalse_someunknown = [0, False, None, '']
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
class TestNullMemberIronPython(TestNullMember):
    def setUp(self):
        TestNullMember.setUp(self)
        self.alltrue_someunknown = [
            (dbnull if x is None else x)
            for x in self.alltrue_someunknown]
        self.allfalse_someunknown = [
            (dbnull if x is None else x)
            for x in self.allfalse_someunknown]

class TestOperators(unittest.TestCase):
    def assertNull(self, v): self.assertTrue(nullop.isnull(v))
    def testNeg(self):
        self.assertNull(nullop.neg(None))
        self.assertEqual(0, nullop.neg(0))
        self.assertEqual(-1, nullop.neg(1))
        self.assertEqual(1, nullop.neg(-1))
    @IronPythonOnly
    def testNeg_IronPython(self):
        self.assertNull(nullop.neg(dbnull))
    def testPos(self):
        self.assertNull(nullop.pos(None))
        self.assertEqual(0, nullop.pos(0))
        self.assertEqual(1, nullop.pos(1))
        self.assertEqual(-1, nullop.pos(-1))
    @IronPythonOnly
    def testPos_IronPython(self):
        self.assertNull(nullop.pos(dbnull))
    def testSummarize(self):
        self.assertNull(nullop.summarize(1, 2, None, 4))
        self.assertEqual(10, nullop.summarize(1, 2, 3, 4))
    @IronPythonOnly
    def testSummarize_IronPython(self):
        self.assertNull(nullop.summarize(1, dbnull, 3, 4))
    def testSub(self):
        self.assertNull(nullop.sub(1, None))
        self.assertEqual(1, nullop.sub(1, 0))
        self.assertEqual(0, nullop.sub(1, 1))
        self.assertEqual(-1, nullop.sub(1, 2))
    @IronPythonOnly
    def testSub_IronPython(self):
        self.assertNull(nullop.sub(dbnull, 1))
    def testMultiply(self):
        self.assertNull(nullop.multiply(1, None, 3, 4))
        self.assertEqual(24, nullop.multiply(1, 2, 3, 4))
    @IronPythonOnly
    def testMultiply_IronPython(self):
        self.assertNull(nullop.multiply(1, 2, dbnull, 4))
    def testTrueDiv(self):
        self.assertNull(nullop.truediv(25, None))
        self.assertEqual(5.5, nullop.truediv(33, 6))
    @IronPythonOnly
    def testTrueDiv_IronPython(self):
        self.assertNull(nullop.truediv(dbnull, 4))
    def testFloorDiv(self):
        self.assertNull(nullop.floordiv(25, None))
        self.assertEqual(5, nullop.floordiv(33, 6))
    @IronPythonOnly
    def testFloorDiv_IronPython(self):
        self.assertNull(nullop.floordiv(dbnull, 4))
    def testConcat(self):
        self.assertNull(nullop.concat('a', 'b', None, 'd'))
        self.assertEqual('abcd', nullop.concat('a', 'b', 'c', 'd'))
    @IronPythonOnly
    def testConcat_IronPython(self):
        self.assertNull(nullop.concat('a', dbnull, 'c', 'd'))
    def testIn(self):
        S = [1, None, 3, 4, None, 6, 7]
        self.assertNull(nullop.isin(2, S))
        self.assertNull(nullop.isin(None, [1, 2, 3]))
        self.assertTrue(nullop.isin(4, S))
    @IronPythonOnly
    def testIn_IronPython(self):
        S = [1, None, 3, 4, dbnull, 6, 7]
        self.assertNull(nullop.isin(2, S))
        self.assertNull(nullop.isin(None, [1, 2, 3]))
        self.assertNull(nullop.isin(dbnull, [1, 2, 3]))
        self.assertTrue(nullop.isin(4, S))
    def testNotIn(self):
        S = [1, None, 3, 4, None, 6, 7]
        self.assertNull(nullop.notin(2, S))
    @IronPythonOnly
    def testNotIn_IronPython(self):
        S = [1, None, 3, 4, dbnull, 6, 7]
        self.assertNull(nullop.notin(2, S))
    def testLessThan(self):
        self.assertNull(nullop.lt(None, None))
        self.assertNull(nullop.lt(1, None))
        self.assertTrue(nullop.lt(1, 3))
        self.assertFalse(nullop.lt(3, 1))
        self.assertFalse(nullop.lt(2, 2))
    @IronPythonOnly
    def testLessThanIronPython(self):
        self.assertNull(nullop.lt(dbnull, dbnull))
        self.assertNull(nullop.lt(dbnull, 0))
    def testLessThanOrEqual(self):
        self.assertNull(nullop.le(None, None))
        self.assertNull(nullop.le(1, None))
        self.assertTrue(nullop.le(1, 3))
        self.assertFalse(nullop.le(3, 1))
        self.assertTrue(nullop.le(2, 2))
    @IronPythonOnly
    def testLessThanOrEqual_IronPython(self):
        self.assertNull(nullop.le(dbnull, dbnull))
        self.assertNull(nullop.le(dbnull, 0))
    def testEqual(self):
        self.assertNull(nullop.eq(None, None))
        self.assertNull(nullop.eq(1, None))
        self.assertFalse(nullop.eq(1, 3))
        self.assertFalse(nullop.eq(3, 1))
        self.assertTrue(nullop.eq(2, 2))
    @IronPythonOnly
    def testEqual_IronPython(self):
        self.assertNull(nullop.eq(dbnull, dbnull))
        self.assertNull(nullop.eq(dbnull, 0))
    def testNotEqual(self):
        self.assertNull(nullop.ne(None, None))
        self.assertNull(nullop.ne(1, None))
        self.assertTrue(nullop.ne(1, 3))
        self.assertTrue(nullop.ne(3, 1))
        self.assertFalse(nullop.ne(2, 2))
    @IronPythonOnly
    def testNotEqual_IronPython(self):
        self.assertNull(nullop.ne(dbnull, dbnull))
        self.assertNull(nullop.ne(dbnull, 0))
    def testGreaterThanOrEqual(self):
        self.assertNull(nullop.ge(None, None))
        self.assertNull(nullop.ge(1, None))
        self.assertFalse(nullop.ge(1, 3))
        self.assertTrue(nullop.ge(3, 1))
        self.assertTrue(nullop.ge(2, 2))
    @IronPythonOnly
    def testGreaterThanOrEqual_IronPython(self):
        self.assertNull(nullop.ge(dbnull, dbnull))
        self.assertNull(nullop.ge(dbnull, 0))
    def testGreaterThan(self):
        self.assertNull(nullop.gt(None, None))
        self.assertNull(nullop.gt(1, None))
        self.assertFalse(nullop.gt(1, 3))
        self.assertTrue(nullop.gt(3, 1))
        self.assertFalse(nullop.gt(2, 2))
    @IronPythonOnly
    def testGreaterThan_IronPython(self):
        self.assertNull(nullop.gt(dbnull, dbnull))
        self.assertNull(nullop.gt(dbnull, 0))
    def testLike(self):
        self.assertTrue(nullop.REGEX_SPECIALS[0] == "\\")
        self.assertNotIn("%", nullop.REGEX_SPECIALS)
        self.assertNotIn("_", nullop.REGEX_SPECIALS)
        self.assertNull(nullop.like(None, None))
        self.assertNull(nullop.like("hello", None))
        self.assertTrue(nullop.like("hello", "hell%"))
        self.assertFalse(nullop.like("hello", "ha%"))
        self.assertTrue(nullop.like("a * b", "a *%"))
        self.assertFalse(nullop.like("hello", "he%", "e"))
        self.assertTrue(nullop.like("h%llo", "he%llo", "e"))
        self.assertTrue(nullop.like("h%llo_", "he%lloe_", "e"))
        self.assertTrue(nullop.like("hello", "%llo", "e"))
        self.assertTrue(nullop.like("\\.^$*+?{}[]()<>|", "\\.^$*+?{}[]()<>|"))
    @IronPythonOnly
    def testLike_IronPython(self):
        self.assertNull(nullop.like(dbnull, dbnull))
        self.assertNull(nullop.like(dbnull, 'hell%'))
    def testBetween(self):
        self.assertNull(nullop.between(4, None, 9))
        self.assertTrue(nullop.between(1, 1, 9))
        self.assertTrue(nullop.between(9, 1, 9))
        self.assertFalse(nullop.between(0, 1, 9))
        self.assertFalse(nullop.between(10, 1, 9))
    @IronPythonOnly
    def testBetween_IronPython(self):
        self.assertNull(nullop.between(None, dbnull, None))
        self.assertNull(nullop.between(2, 1, dbnull))
    def testAnd(self):
        self.assertNull(nullop.And(True, True, None, True))
        self.assertNull(nullop.And(None, None))
        self.assertTrue(nullop.And(True, True))
        self.assertTrue(nullop.And())
        self.assertFalse(nullop.And(False))
        self.assertTrue(nullop.And(True))
        self.assertFalse(nullop.And(None, False))
    @IronPythonOnly
    def testAnd_IronPython(self):
        self.assertNull(nullop.And(dbnull, dbnull))
        self.assertNull(nullop.And(True, dbnull, True, True))
        self.assertFalse(nullop.And(dbnull, True, False))
    def testOr(self):
        self.assertNull(nullop.Or(False, False, None, False))
        self.assertNull(nullop.Or(None, None))
        self.assertFalse(nullop.Or(False, False))
        self.assertFalse(nullop.Or())
        self.assertFalse(nullop.Or(False))
        self.assertTrue(nullop.Or(True))
        self.assertTrue(nullop.Or(None, True))
    @IronPythonOnly
    def testOr_IronPython(self):
        self.assertNull(nullop.Or(False, dbnull, False, False))
        self.assertNull(nullop.Or(dbnull, dbnull))
        self.assertTrue(nullop.Or(dbnull, True, False))
    def testNot(self):
        self.assertNull(nullop.Not(None))
        self.assertFalse(nullop.Not(True))
        self.assertTrue(nullop.Not(False))
    @IronPythonOnly
    def testNot_IronPythonOnly(self):
        self.assertNull(nullop.Not(dbnull))
    def testPow(self):
        self.assertNull(nullop.pow(2, None))
        self.assertEqual(8, nullop.pow(2, 3))
    @IronPythonOnly
    def testPow_IronPython(self):
        self.assertNull(nullop.pow(dbnull, 3))
        self.assertNull(nullop.pow(None, dbnull))
    def testMod(self):
        self.assertNull(nullop.mod(25, None))
        self.assertEqual(1, nullop.mod(25, 8))
    @IronPythonOnly
    def testMod_IronPython(self):
        self.assertNull(nullop.mod(dbnull, 3))
        self.assertNull(nullop.mod(None, dbnull))
    def testConcat2(self):
        self.assertEqual('ab', nullop.concat2('a', 'b'))
        self.assertNull(nullop.concat2('a', None))
        self.assertNull(nullop.concat2(None, 'b'))
        self.assertNull(nullop.concat2(None, None))
    @IronPythonOnly
    def testConcat2_IronPython(self):
        self.assertNull(nullop.concat2('a', dbnull))
        self.assertNull(nullop.concat2(dbnull, 'b'))
        self.assertNull(nullop.concat2(None, dbnull))
        self.assertNull(nullop.concat2(dbnull, dbnull))
    def testUcase(self):
        self.assertNull(nullop.ucase(None))
        self.assertEqual('A', nullop.ucase('a'))
    @IronPythonOnly
    def testUcase_IronPython(self):
        self.assertNull(nullop.ucase(dbnull))
    def testLcase(self):
        self.assertNull(nullop.lcase(None))
        self.assertEqual('a', nullop.lcase('A'))
    @IronPythonOnly
    def testLcase_IronPython(self):
        self.assertNull(nullop.lcase(dbnull))
    def testReplace(self):
        self.assertNull(nullop.replace(None, None, None))
        self.assertNull(nullop.replace('hello', 'llo', None))
        self.assertNull(nullop.replace('hello', None, 'lix'))
        self.assertEqual('helix', nullop.replace('hello', 'llo' ,'lix'))
    @IronPythonOnly
    def testReplace_IronPython(self):
        self.assertNull(nullop.replace(dbnull, dbnull, dbnull))
        self.assertNull(nullop.replace(dbnull, 'llo', 'lix'))
    def testLtrim(self):
        self.assertNull(nullop.ltrim(None))
        self.assertEqual('A', nullop.ltrim('   A'))
        self.assertEqual('A  ', nullop.ltrim('   A  '))
    @IronPythonOnly
    def testLtrim_IronPython(self):
        self.assertNull(nullop.ltrim(dbnull))
    def testRtrim(self):
        self.assertNull(nullop.rtrim(None))
        self.assertEqual('A', nullop.rtrim('A  '))
        self.assertEqual('   A', nullop.rtrim('   A  '))
    @IronPythonOnly
    def testRtrim_IronPython(self):
        self.assertNull(nullop.rtrim(dbnull))
    def testTrim(self):
        self.assertNull(nullop.trim(None))
        self.assertEqual('A', nullop.trim('   A  '))
    @IronPythonOnly
    def testTrim_IronPython(self):
        self.assertNull(nullop.trim(dbnull))
    def testCast(self):
        self.assertEqual(3, nullop.cast('3', 'int'))
        self.assertEqual(3, nullop.cast('3', int))
    @IronPythonOnly
    def testCast_IronPython(self):
        self.assertNull(nullop.cast(dbnull, 'int'))
        self.assertNull(nullop.cast(dbnull, int))
    def test_aggregate_summary(self):
        self.assertNull(nullop.aggregate_summary([]))
        self.assertNull(nullop.aggregate_summary([None, None, None]))
        self.assertEqual(7, nullop.aggregate_summary([0, 1, 2, None, 4]))
        self.assertEqual(10, nullop.aggregate_summary([0, 1, 2, 3, 4]))
    @IronPythonOnly
    def test_aggregate_summary_IronPython(self):
        self.assertNull(nullop.aggregate_summary([dbnull, None, dbnull]))
        self.assertEqual(7, nullop.aggregate_summary([0, 1, 2, dbnull, 4]))
    def test_aggregate_summaries(self):
        (r1, r2, r3) = nullop.aggregate_summaries(3, [])
        self.assertNull(r1)
        self.assertNull(r2)
        self.assertNull(r3)
        (r1, r2, r3) = nullop.aggregate_summaries(3, [
            (   0,    3, None),
            (   5,    8, None),
            (None,    2, None),
            (   3, None, None) ] )
        self.assertEqual(8, r1)
        self.assertEqual(13, r2)
        self.assertNull(r3)
    @IronPythonOnly
    def test_aggregate_summaries_IronPython(self):
        (r1, r2, r3) = nullop.aggregate_summaries(3, [])
        self.assertNull(r1)
        self.assertNull(r2)
        self.assertNull(r3)
        (r1, r2, r3) = nullop.aggregate_summaries(3, [
            (   0,            3, dbnull),
            (   5,            8, dbnull),
            (None,            2,         None),
            (   3, dbnull, dbnull) ] )
        self.assertEqual(8, r1)
        self.assertEqual(13, r2)
        self.assertNull(r3)
    def test_aggregate_minimum(self):
        self.assertNull(nullop.aggregate_minimum([]))
        self.assertNull(nullop.aggregate_minimum([None, None, None]))
        self.assertEqual(0, nullop.aggregate_minimum([0, 1, 2, None, 4]))
        self.assertEqual(0, nullop.aggregate_minimum([0, 1, 2, 3, 4]))
    @IronPythonOnly
    def test_aggregate_minimum_IronPython(self):
        self.assertNull(nullop.aggregate_minimum([dbnull, None, dbnull]))
        self.assertEqual(0, nullop.aggregate_minimum([0, 1, 2, dbnull, 4]))
    def test_aggregate_minimums(self):
        (r1, r2, r3) = nullop.aggregate_minimums(3, [])
        self.assertNull(r1)
        self.assertNull(r2)
        self.assertNull(r3)
        (r1, r2, r3) = nullop.aggregate_minimums(3, [
            (   0,    3, None),
            (   5,    8, None),
            (None,    2, None),
            (   3, None, None) ] )
        self.assertEqual(0, r1)
        self.assertEqual(2, r2)
        self.assertNull(r3)
    @IronPythonOnly
    def test_aggregate_minimums_IronPython(self):
        (r1, r2, r3) = nullop.aggregate_minimums(3, [])
        self.assertNull(r1)
        self.assertNull(r2)
        self.assertNull(r3)
        (r1, r2, r3) = nullop.aggregate_minimums(3, [
            (   0,      3, dbnull),
            (   5,      8, dbnull),
            (None,      2,   None),
            (   3, dbnull, dbnull) ] )
        self.assertEqual(0, r1)
        self.assertEqual(2, r2)
        self.assertNull(r3)
    def test_aggregate_maximum(self):
        self.assertNull(nullop.aggregate_maximum([]))
        self.assertNull(nullop.aggregate_maximum([None, None, None]))
        self.assertEqual(4, nullop.aggregate_maximum([0, 1, 2, None, 4]))
        self.assertEqual(4, nullop.aggregate_maximum([0, 1, 2, 3, 4]))
    @IronPythonOnly
    def test_aggregate_maximum_IronPython(self):
        self.assertNull(nullop.aggregate_maximum([dbnull, None, dbnull]))
        self.assertEqual(4, nullop.aggregate_maximum([0, 1, 2, dbnull, 4]))
    def test_aggregate_maximums(self):
        (r1, r2, r3) = nullop.aggregate_maximums(3, [])
        self.assertNull(r1)
        self.assertNull(r2)
        self.assertNull(r3)
        (r1, r2, r3) = nullop.aggregate_maximums(3, [
            (   0,    3, None),
            (   5,    8, None),
            (None,    2, None),
            (   3, None, None) ] )
        self.assertEqual(5, r1)
        self.assertEqual(8, r2)
        self.assertNull(r3)
    @IronPythonOnly
    def test_aggregate_maximums_IronPython(self):
        (r1, r2, r3) = nullop.aggregate_maximums(3, [])
        self.assertNull(r1)
        self.assertNull(r2)
        self.assertNull(r3)
        (r1, r2, r3) = nullop.aggregate_maximums(3, [
            (   0,      3, dbnull),
            (   5,      8, dbnull),
            (None,      2,   None),
            (   3, dbnull, dbnull) ] )
        self.assertEqual(5, r1)
        self.assertEqual(8, r2)
        self.assertNull(r3)
    def test_aggregate_count(self):
        self.assertEqual(0, nullop.aggregate_count([None, None, None]))
        self.assertEqual(3, nullop.aggregate_count([None, 1, 2, None, 5]))
    @IronPythonOnly
    def test_aggregate_count_IronPython(self):
        self.assertEqual(0, nullop.aggregate_count([dbnull, dbnull, dbnull]))
        self.assertEqual(3, nullop.aggregate_count([dbnull, 1, 2, dbnull, 5]))
    def test_aggregate_counts(self):
        (r1, r2, r3) = nullop.aggregate_counts(3, [])
        self.assertEqual(0, r1)
        self.assertEqual(0, r2)
        self.assertEqual(0, r3)
        (r1, r2, r3) = nullop.aggregate_counts(3, [
            (   0,    3, None),
            (   5, None, None),
            (None,    2, None),
            (   3, None, None) ] )
        self.assertEqual(3, r1)
        self.assertEqual(2, r2)
        self.assertEqual(0, r3)
    @IronPythonOnly
    def test_aggregate_counts_IronPython(self):
        (r1, r2, r3) = nullop.aggregate_counts(3, [])
        self.assertEqual(0, r1)
        self.assertEqual(0, r2)
        self.assertEqual(0, r3)
        (r1, r2, r3) = nullop.aggregate_maximums(3, [
            (   0,      3, dbnull),
            (   5,   None, dbnull),
            (None,      2,   None),
            (   3, dbnull, dbnull) ] )
        self.assertEqual(5, r1)
        self.assertEqual(8, r2)
        self.assertEqual(0, r3)

class TestDictWithLimit(unittest.TestCase):
    def test_dict_with_limit(self):
        dic = {}
        limit = 5
        def assert_joined_keys(s): self.assertEqual(s, ''.join(dic.keys()))
        nullop._add_to_dict_with_limit(dic, limit, 'q', 0); assert_joined_keys('q')
        nullop._add_to_dict_with_limit(dic, limit, 'w', 1); assert_joined_keys('qw')
        nullop._add_to_dict_with_limit(dic, limit, 'e', 2); assert_joined_keys('qwe')
        nullop._add_to_dict_with_limit(dic, limit, 'r', 3); assert_joined_keys('qwer')
        nullop._add_to_dict_with_limit(dic, limit, 't', 4); assert_joined_keys('qwert')
        nullop._add_to_dict_with_limit(dic, limit, 'y', 5); assert_joined_keys('werty')
        nullop._add_to_dict_with_limit(dic, limit, 'u', 6); assert_joined_keys('ertyu')
        nullop._add_to_dict_with_limit(dic, limit, 'i', 7); assert_joined_keys('rtyui')
