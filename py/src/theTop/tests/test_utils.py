#! -*- coding: utf-8 -*-

import unittest
from .. import util

class TestSlotty(unittest.TestCase):
    class TheSlotty(object): __slots__ = ('value1', 'value2')
    def test_slotty(self):
        self.assertFalse(util.slotty(self))
        self.assertTrue(util.slotty(self.TheSlotty()))
    def test_slotty_behavior(self):
        s = self.TheSlotty()
        s.value1 = 10
        s.value2 = 20
        self.assertEqual(s.value1, 10)
        self.assertEqual(s.value2, 20)
        with self.assertRaises(AttributeError): s.value3 = 30
    def test_assert_slotty(self):
        with self.assertRaises(AssertionError): util.assert_slotty(TestSlotty)
        util.assert_slotty(self.TheSlotty)

class TestLocalFileName(unittest.TestCase):
    def test_local_filename_refclass(self):
        import os.path
        f = util.local_filename('FileName.txt', TestLocalFileName)
        self.assertTrue(f.endswith('FileName.txt'))
        self.assertIn(os.path.join('theTop', 'tests'), f)
    def test_local_filename_reffunction(self):
        import os.path
        f = util.local_filename('FileName.txt', util.slotty)
        self.assertTrue(f.endswith('FileName.txt'))
        self.assertIn('theTop', f)
        self.assertNotIn(os.path.join('theTop', 'tests'), f)
    def test_local_filename_refboundmethod(self):
        import os.path
        f = util.local_filename('FileName.txt', TestLocalFileName.test_local_filename_refboundmethod)
        self.assertTrue(f.endswith('FileName.txt'))
        self.assertIn(os.path.join('theTop', 'tests'), f)
    def test_local_filename_refunboundmethod(self):
        import os.path
        f = util.local_filename('FileName.txt', self.test_local_filename_refunboundmethod)
        self.assertTrue(f.endswith('FileName.txt'))
        self.assertIn(os.path.join('theTop', 'tests'), f)

class TestPropAttr(unittest.TestCase):
    class TheObject(object):
        mark = None
        @util.propattr
        def TheMark(self): return self.mark
    def testPropAttr(self):
        o = TestPropAttr.TheObject()
        self.assertIsNone(o.mark)
        o.mark = 10
        self.assertEqual(10, o.mark)
        self.assertEqual(10, o.TheMark)
        o.mark = 20
        self.assertEqual(20, o.mark)
        self.assertEqual(10, o.TheMark)

class TestGetSingle(unittest.TestCase):
    def testGetEmpty(self):
        with self.assertRaises(util.NotFound):
            util.get_single([])
    def testGetOne(self):
        self.assertEqual(1, util.get_single([1]))
        self.assertEqual(1, util.get_single(range(1, 2)))
    def testGetMany(self):
        with self.assertRaises(util.MoreThanOne):
            util.get_single([1, 2])
        with self.assertRaises(util.MoreThanOne):
            util.get_single(range(10))

class TestShouldNotReachHere(unittest.TestCase):
    def testShouldNotReachHear(self):
        with self.assertRaises(AssertionError): util.SHOULD_NOT_REACH_HERE()
