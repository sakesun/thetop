# ! -*- coding: utf-8 -*-

import textwrap
import unittest
from .. import structure

PLAIN_SELECT_ABC = 'SELECT a, b, c'
PRETTY_SELECT_ABC = textwrap.dedent('''\
  SELECT
    a,
    b,
    c''')

PLAIN_SELECT_ABC_FROM_WHERE = 'SELECT a, b, c FROM t WHERE (A = B) AND (C = D) AND (E = F)'
PRETTY_SELECT_ABC_FROM_WHERE = textwrap.dedent('''\
  SELECT
    a,
    b,
    c
  FROM
    t
  WHERE
    (A = B) AND
    (C = D) AND
    (E = F)''')

PLAIN_SELECT_ABC_FROM_WHERE2 = (
  'SELECT a, b, c FROM t'
  ' WHERE (A = B) AND (C = D) AND (E = F)'
  ' AND (G = (SELECT gg FROM tt))')

PRETTY_SELECT_ABC_FROM_WHERE2 = textwrap.dedent('''\
  SELECT
    a,
    b,
    c
  FROM
    t
  WHERE
    (A = B) AND
    (C = D) AND
    (E = F) AND
    (G = (
      SELECT
        gg
      FROM
        tt
    ))''')

class TestStructure(unittest.TestCase):
    def testSimpleStructure(self):
        root = structure.Roster()
        s = root.titled("SELECT").list(",")
        s.line("a")
        s.line("b")
        s.line("c")
        self.assertEqual(PLAIN_SELECT_ABC, root.plain())
        self.assertEqual(PRETTY_SELECT_ABC, root.pretty())
        s = root.titled("FROM")
        s.line("t")
        s = root.titled("WHERE").list("AND")
        s.line("(A = B)")
        s.line("(C = D)")
        s.line("(E = F)")
        self.assertEqual(PLAIN_SELECT_ABC_FROM_WHERE, root.plain())
        self.assertEqual(PRETTY_SELECT_ABC_FROM_WHERE, root.pretty())
        n = s.line()
        n.word('(G = ')
        sub = n.scope('(', ')')
        x = sub.titled('SELECT').list(',')
        x.line('gg')
        x = sub.titled('FROM')
        x.line('tt')
        n.word(')')
        self.assertEqual(PLAIN_SELECT_ABC_FROM_WHERE2, root.plain())
        self.assertEqual(PRETTY_SELECT_ABC_FROM_WHERE2, root.pretty())
    def testTagging(self):
        pass
