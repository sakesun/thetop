#! -*- coding: utf-8 -*-

import unittest
from theTop.model import models
from theTop.model import the, T, op

class Test_defined_labels(unittest.TestCase):
    def test_regular(self):
        labels = models.defined_labels(
            ('A', 'B', 'C'),
            models.deflist(Z=7, B=6, X=5))
        self.assertEqual(labels, ('A', 'B', 'C', 'X', 'Z'))

class Test_renamed_labels(unittest.TestCase):
    def test_regular(self):
        dic = dict(A='AA', C='CC')
        labels = models.renamed_labels(('A', 'B', 'C'), dic)
        self.assertEqual(labels, ('AA', 'B', 'CC'))
        assert(2, len(dic))
        assert('AA', dic['A'])
        assert('CC', dic['C'])
    def test_duplicated(self):
        with self.assertRaises(KeyError):
            models.renamed_labels(('A', 'B', 'C'), dict(A='X', C='X'))
    def test_illegals(self):
        with self.assertRaises(KeyError):
            models.renamed_labels(('A', 'B', 'C'), dict(A='X', bad='A'))

class Test_deflist(unittest.TestCase):
    def test_deflist_list(self):
        d = models.deflist(('B', 20), ('A', 10), ('C', 30))
        self.assertEqual(
            [('B', 20), ('A', 10), ('C', 30)],
            [(k, v.constant) for (k,v) in d])
    def test_deflist_mixed(self):
        with self.assertRaises(ValueError):
            models.deflist(('B', 20), ('A', 10), ('B', 30), X=100)
    def test_deflist_list_duplicated(self):
        with self.assertRaises(KeyError):
            models.deflist(('B', 20), ('A', 10), ('B', 30))
    def test_deflist_dict(self):
        d = models.deflist(B=20, A=10, C=30)
        self.assertEqual(
            [('A', 10), ('B', 20), ('C', 30)],
            [(k, v.constant) for (k,v) in d])

class Test_setlist(unittest.TestCase):
    def test_regular(self):
        s = models.setlist(('B', 20), ('A', 10), ('C', 30))
        self.assertEqual(
            [('B', 20), ('A', 10), ('C', 30)],
            [(k, v.constant) for (k,v) in s])
    def test_empty(self):
        with self.assertRaises(ValueError): models.setlist()
    def test_mixed(self):
        with self.assertRaises(ValueError): models.setlist('A', 'B', A=10, B=20)
    def test_duplicated(self):
        with self.assertRaises(KeyError): models.setlist('A', 'B', 'A')

class TestParamCollector(unittest.TestCase):
    def assertParam(self, params, m):
        self.assertSetEqual(
            set(params),
            models.params(m))
    def test_ParamCollector(self):
        t = T['T']
        self.assertParam([], t)
        t = t.where(the.ID == the.param.A)
        self.assertParam(['A'], t)
        t = t.where(the.NAME == the.param.A)
        self.assertParam(['A'], t)
        t = t.where(the.ADDRESS == the.param.B)
        self.assertParam(['A', 'B'], t)
        t = t.assign(A='XX')
        self.assertParam(['B'], t)
        t = t.define(NEW_ID = the.param.C)
        self.assertParam(['B', 'C'], t)
        u = t.updatingall('X', 'Y', 'Z')
        self.assertParam(['B', 'C', 'X', 'Y', 'Z'], u)
        t2 = T['T2'].where(the.GROUP == the.param['GRP'])
        self.assertParam(['GRP'], t2)
        self.assertParam(
            ['B', 'C', 'GRP'],
            t.innerjoin(t2.where(the.ID == the.host.ID)))
        self.assertParam(
            ['B', 'C', 'K','GRP'],
            t.define(X = (t2.where(the.ID == the.host.ID) * the.param.K)))

class TestParamCollectorWithDecorator(TestParamCollector):
    def assertParam(self, params, m):
        emitter = models.CollectParamEmitter()
        collector = models.EmitterDecorator(emitter)
        m.emit(collector)
        self.assertSetEqual(
            set(params),
            emitter.params)
