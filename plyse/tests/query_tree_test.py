#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from plyse.query_tree import Operand, And, Or, Not, NotOperatorError


class QueryTreeTester(unittest.TestCase):

    def setUp(self):
        self.o1 = {'field': 'dummy', 'field_type': 'string', 'val': 'test', 'val_type': 'string'}
        self.o2 = {'field': 'dummy', 'field_type': 'string', 'val': 'test', 'val_type': 'string'}

    def test_operand_node(self):
        o = Operand(**self.o1)
        self.assertTrue(o.is_leaf)
        self.assertEqual([], o.children)
        self.assertEqual(self.o1, o.leaves()[0])

    def assert_node(self, op):
        self.assertTrue(not op.is_leaf)

        if op.type == Not.type:
            self.assertEqual(1, len(op.inputs))
            self.assertEqual(self.o1, op.children[0])
            self.assertRaises(NotOperatorError, op.add_input, Operand(**self.o1))

        else:
            self.assertEqual(2, len(op.inputs))

            self.assertEqual(self.o1, op.children[0])
            self.assertEqual(self.o2, op.children[1])

            op.add_input(Operand(**self.o1))
            self.assertEqual(3, len(op.leaves()))
            self.assertEqual(Operand, type(op.children[0]))
            self.assertEqual(type(op), type(op.children[1]))

    def test_or_operator_node(self):
        o1 = Operand(**self.o1)
        o2 = Operand(**self.o2)
        or_op = Or([o1, o2])

        self.assert_node(or_op)

    def test_and_operator_node(self):
        o1 = Operand(**self.o1)
        o2 = Operand(**self.o2)
        and_op = And([o1, o2])

        self.assert_node(and_op)

    def test_not_operator_node(self):
        o1 = Operand(**self.o1)
        not_op = Not([o1])

        self.assert_node(not_op)

if __name__ == '__main__':
    unittest.main()
