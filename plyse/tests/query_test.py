#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from plyse.grammar import GrammarFactory
from plyse.parser import QueryParser
from plyse.query_tree import Operand, And, Operator


class QueryParserTester(unittest.TestCase):

    qp = QueryParser(GrammarFactory.build_default())

    def test_init_query(self):
        q = self.qp.parse("name:plyse")

        self.assertEqual('name:plyse', q.raw_query)
        self.assertTrue(isinstance(q.query_as_tree, Operand))
        self.assertEqual(1, len(q._stack_map))
        self.assertTrue(0 in q._stack_map)
        self.assertTrue(isinstance(q.query_from_stack(0)[0], Operand))
        self.assertEqual('name:plyse', q.query_from_stack(0)[1])
        self.assertEqual(1, len(q.terms()))
        self.assertEqual('name', q.terms()[0].field)
        self.assertEqual('plyse', q.terms()[0].val)

    def test_stack_query(self):
        q = self.qp.parse("name:plyse")
        q2 = q.stack(self.qp.parse("ask:gently"))

        # query is immutable, thus
        self.assertEqual('name:plyse', q.raw_query)
        self.assertEqual('(name:plyse) and (ask:gently)', q2.raw_query)

        self.assertTrue(And.type, q2.query_as_tree.type)
        self.assertEqual(2, len(q2._stack_map))
        self.assertTrue(0 in q2._stack_map)
        self.assertTrue(1 in q2._stack_map)

        self.assertEqual(2, len(q2.terms()))
        self.assertEqual('name', q2.terms()[0].field)
        self.assertEqual('plyse', q2.terms()[0].val)
        self.assertEqual('ask', q2.terms()[1].field)
        self.assertEqual('gently', q2.terms()[1].val)

        self.assertTrue(isinstance(q2.query_from_stack(0)[0], Operand))
        self.assertEqual('name:plyse', q.query_from_stack(0)[1])

        self.assertTrue(isinstance(q2.query_from_stack(1)[0], Operand))
        self.assertEqual('ask:gently', q2.query_from_stack(1)[1])

    def test_stack_negated_query(self):
        q = self.qp.parse("name:plyse")
        q2 = q.stack(self.qp.parse("-ask:gently"))

        # query is immutable, thus
        self.assertEqual('name:plyse', q.raw_query)
        self.assertEqual('(name:plyse) and (-ask:gently)', q2.raw_query)

        self.assertTrue(And.type, q2.query_as_tree.type)
        self.assertEqual(2, len(q2._stack_map))
        self.assertTrue(0 in q2._stack_map)
        self.assertTrue(1 in q2._stack_map)

        self.assertEqual(1, len(q2.terms(ignore_negated=True)))
        self.assertEqual('name', q2.terms()[0].field)
        self.assertEqual('plyse', q2.terms()[0].val)

        self.assertTrue(isinstance(q2.query_from_stack(0)[0], Operand))
        self.assertEqual('name:plyse', q2.query_from_stack(0)[1])

        self.assertTrue(isinstance(q2.query_from_stack(1)[0], Operator))
        self.assertEqual('-ask:gently', q2.query_from_stack(1)[1])

if __name__ == "__main__":
    unittest.main(verbosity=3)
