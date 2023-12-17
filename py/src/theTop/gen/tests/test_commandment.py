#! -*- coding: utf-8 -*-

import unittest
from .. import commandment

class TestCommandmentFunctions(unittest.TestCase):
    def test_validate_boundary(self):
        with self.assertRaises(ValueError): commandment.validate_boundary('test', None, 0)
        with self.assertRaises(ValueError): commandment.validate_boundary('test', 0, None)
        with self.assertRaises(ValueError): commandment.validate_boundary('test', -1, 0)
        with self.assertRaises(ValueError): commandment.validate_boundary('test', 0, 5)
        with self.assertRaises(ValueError): commandment.validate_boundary('test', 3, 2)
        commandment.validate_boundary('test', 0, 4)
        commandment.validate_boundary('test', 1, 4)
        commandment.validate_boundary('test', 0, 3)
        commandment.validate_boundary('test', 1, 3)
        commandment.validate_boundary('test', 2, 3)
        commandment.validate_boundary('test', 0, 0)
        commandment.validate_boundary('test', 1, 1)
        commandment.validate_boundary('test', 2, 2)
        commandment.validate_boundary('test', 3, 3)
        commandment.validate_boundary('test', 4, 4)
    def test_validate_regions(self):
        text = 'this is the TEST TEST TEST'
        validregions = [(12, 16), (17, 21), (22, 26)]
        commandment.validate_regions(text, 'test', validregions)
        with self.assertRaises(ValueError):
            invalidregions = validregions[:]
            invalidregions[-1] = (22, 0)
            commandment.validate_regions('this is the TEST TEST TEST', 'test', invalidregions)
    def test_crossovering(self):
        self.assertFalse(commandment.crossovering(3, 7, 3, 7)) # match region
        self.assertFalse(commandment.crossovering(3, 17, 3, 7)) # inner region
        self.assertFalse(commandment.crossovering(3, 17, 8, 17)) # inner region
        self.assertFalse(commandment.crossovering(3, 17, 8, 12)) # inner region
        self.assertFalse(commandment.crossovering(3, 7, 3, 17)) # outer region
        self.assertFalse(commandment.crossovering(8, 17, 3, 17)) # outer region
        self.assertFalse(commandment.crossovering(8, 12, 3, 17)) # outer region
        self.assertTrue(commandment.crossovering(3, 17, 8, 18))
        self.assertTrue(commandment.crossovering(7, 25, 3, 9))
    def test_validate_tags(self):
        text = 'this is the TEST TEST TEST'
        validregions = [(12, 16), (17, 21), (22, 26)]
        commandment.validate_tags(text, {
            'A': validregions[0:1],
            'B': validregions[1:]})
        with self.assertRaises(ValueError):
            commandment.validate_tags(text, {
                'A': validregions[0:1],
                'B': validregions[1:],
                'C': [(3, 18)]})

class TestCommand(unittest.TestCase):
    TEST_REGIONS = [(12, 16), (18, 22), (28, 32)]
    TEMPLATE = commandment.Commandment('this is the TEST, TEST, and TEST', {
        'test1': TEST_REGIONS[0:1],
        'test2': TEST_REGIONS[1:2],
        'test3': TEST_REGIONS[2:3],
        'test1 + test2': [(TEST_REGIONS[0][0], TEST_REGIONS[1][1])],
        'test2 & test3': TEST_REGIONS[1:3] })
    instance = None
    def setUp(self): self.instance = self.TEMPLATE.clone()
    def tearDown(self): self.instance = None
    def check_template(self, c):
        self.assertEqual(5, len(c))
        self.assertNotIn('xxx', c)
        self.assertIn('test1', c)
        self.assertIn('test2', c)
        self.assertIn('test3', c)
        self.assertIn('test1 + test2', c)
        self.assertIn('test2 & test3', c)
        self.assertEqual(c['test1'], 'TEST')
        self.assertEqual(c['test2'], 'TEST')
        self.assertEqual(c['test3'], 'TEST')
        self.assertEqual(c['test1 + test2'], 'TEST, TEST')
        self.assertEqual(c['test2 & test3'], 'TEST')
    def test_setting(self):
        self.check_template(self.TEMPLATE)
        self.check_template(self.instance)
        self.instance['test1'] = 'THE_FIRST'
        self.assertEqual(5, len(self.instance))
        self.assertEqual(self.instance['test1'], 'THE_FIRST')
        self.assertEqual(self.instance['test2'], 'TEST')
        self.assertEqual(self.instance['test3'], 'TEST')
        self.assertEqual(self.instance['test1 + test2'], 'THE_FIRST, TEST')
        self.assertEqual(self.instance['test2 & test3'], 'TEST')
        self.assertEqual(self.instance.text, 'this is the THE_FIRST, TEST, and TEST')
        self.check_template(self.TEMPLATE)
        with self.assertRaises(ValueError): self.instance['test2'] = 'xx'
        with self.assertRaises(ValueError): self.instance['test3'] = 'xx'
        self.instance['test2 & test3'] = '2 & 3'
        self.assertEqual(5, len(self.instance))
        self.assertEqual(self.instance['test1'], 'THE_FIRST')
        self.assertEqual(self.instance['test2'], '2 & 3')
        self.assertEqual(self.instance['test3'], '2 & 3')
        self.assertEqual(self.instance['test1 + test2'], 'THE_FIRST, 2 & 3')
        self.assertEqual(self.instance['test2 & test3'], '2 & 3')
        self.assertEqual(self.instance.text, 'this is the THE_FIRST, 2 & 3, and 2 & 3')
        self.check_template(self.TEMPLATE)
        self.instance['test1 + test2'] = 'THE_FIRST + THE_SECOND'
        self.assertEqual(3, len(self.instance))
        self.assertNotIn('test1', self.instance)
        self.assertNotIn('test2', self.instance)
        self.assertIn('test3', self.instance)
        self.assertIn('test1 + test2', self.instance)
        self.assertIn('test2 & test3', self.instance)
        self.assertEqual(self.instance['test3'], '2 & 3')
        self.assertEqual(self.instance['test1 + test2'], 'THE_FIRST + THE_SECOND')
        self.assertEqual(self.instance['test2 & test3'], '2 & 3')
        self.assertEqual(self.instance.text, 'this is the THE_FIRST + THE_SECOND, and 2 & 3')
        self.check_template(self.TEMPLATE)
    def test_revise(self):
        self.check_template(self.TEMPLATE)
        self.check_template(self.instance)
        self.instance.revise({
            'test1': 'THE_FIRST',
            'test1 + test2': '1st + 2nd',
            'test2 & test3': '2 & 3'
            }),
        self.assertEqual(self.instance.text, 'this is the 1st + 2nd, and 2 & 3')
        self.check_template(self.TEMPLATE)
