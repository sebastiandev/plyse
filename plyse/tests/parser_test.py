# -*- coding: utf-8 -*-

import unittest
from plyse.expressions.primitives import ParseException
from plyse.grammar import GrammarFactory
from plyse.parser import QueryParser
from plyse.term_parser import Term
from plyse.query_tree import Operand, And, Or, Not


class QueryParserTester(unittest.TestCase):

    def init_and_parse(self, input_str, fail_if_syntax_mismatch=False):
        qp = QueryParser(GrammarFactory.build_default())
        self.assert_(qp.parse(input_str))
        return qp.parse(input_str, fail_if_syntax_mismatch).query_as_tree

    def test_simple_partial_text(self):
        r = self.init_and_parse("texto")

        self.assertTrue(isinstance(r, Operand))
        self.assertEqual(r.field, "default")
        self.assertEqual(r.val, "texto")
        self.assertEqual(r.val_type, Term.PARTIAL_STRING)

    def test_simple_negated_partial_text(self):
        r = self.init_and_parse("-texto")

        self.assertTrue(isinstance(r, Not))
        for operand in r.inputs:
            self.assertEqual(operand.field, "default")
            self.assertEqual(operand.val, "texto")
            self.assertEqual(operand.val_type, Term.PARTIAL_STRING)

    def test_simple_implicit_OR_with_fields(self):
        r = self.init_and_parse('a:"test" b:otro')

        self.assertTrue(isinstance(r, Or))

        self.assertEqual(r.inputs[0].field, "a")
        self.assertEqual(r.inputs[0].val, "test")
        self.assertEqual(r.inputs[0].val_type, Term.EXACT_STRING)

        self.assertEqual(r.inputs[1].field, "b")
        self.assertEqual(r.inputs[1].val, "otro")
        self.assertEqual(r.inputs[1].val_type, Term.PARTIAL_STRING)

    def test_simple_AND_with_field(self):
        r = self.init_and_parse('a:"test" and b:otro')

        self.assertTrue(isinstance(r, And))

        self.assertEqual(r.inputs[0].field, "a")
        self.assertEqual(r.inputs[0].val, "test")
        self.assertEqual(r.inputs[0].val_type, Term.EXACT_STRING)

        self.assertEqual(r.inputs[1].field, "b")
        self.assertEqual(r.inputs[1].val, "otro")
        self.assertEqual(r.inputs[1].val_type, Term.PARTIAL_STRING)

    def test_AND_precedence(self):
        r = self.init_and_parse('a:test or b:otro + c:another')

        self.assertTrue(isinstance(r, Or))
        self.assertEqual(r.inputs[0].field, "a")
        self.assertEqual(r.inputs[0].val, "test")
        self.assertEqual(r.inputs[0].val_type, Term.PARTIAL_STRING)

        self.assertTrue(isinstance(r.inputs[1], And))

        and_op = r.inputs[1]
        self.assertEqual(and_op.inputs[0].field, "b")
        self.assertEqual(and_op.inputs[0].val, "otro")
        self.assertEqual(and_op.inputs[0].val_type, Term.PARTIAL_STRING)

        self.assertEqual(and_op.inputs[1].field, "c")
        self.assertEqual(and_op.inputs[1].val, "another")
        self.assertEqual(and_op.inputs[1].val_type, Term.PARTIAL_STRING)

    def test_parenthesis_precedence(self):
        r = self.init_and_parse('(a:test or b:otro) + c:another')

        self.assertTrue(isinstance(r, And))

        self.assertEqual(r.inputs[1].field, "c")
        self.assertEqual(r.inputs[1].val, "another")
        self.assertEqual(r.inputs[1].val_type, Term.PARTIAL_STRING)

        self.assertTrue(isinstance(r.inputs[0], Or))

        or_op = r.inputs[0]
        self.assertEqual(or_op.inputs[0].field, "a")
        self.assertEqual(or_op.inputs[0].val, "test")
        self.assertEqual(or_op.inputs[0].val_type, Term.PARTIAL_STRING)

        self.assertEqual(or_op.inputs[1].field, "b")
        self.assertEqual(or_op.inputs[1].val, "otro")
        self.assertEqual(or_op.inputs[1].val_type, Term.PARTIAL_STRING)

    def test_parenthesis_OR_field_OR_field_AND_NOT_field(self):
        r = self.init_and_parse('(a:test + b:otro) c:another d:"xx" AND -e:0')

        self.assertTrue(isinstance(r, Or))

        self.assertTrue(isinstance(r.inputs[1], And))

        and_op = r.inputs[1]
        self.assertEqual(and_op.inputs[0].field, "d")
        self.assertEqual(and_op.inputs[0].val, "xx")
        self.assertEqual(and_op.inputs[0].val_type, Term.EXACT_STRING)

        self.assertTrue(isinstance(and_op.inputs[1], Not))
        self.assertEqual(and_op.inputs[1].inputs[0].field, "e")
        self.assertEqual(and_op.inputs[1].inputs[0].val, 0)
        self.assertEqual(and_op.inputs[1].inputs[0].val_type, "int")

        self.assertTrue(isinstance(r.inputs[0], Or))

        or_op = r.inputs[0]
        self.assertTrue(isinstance(or_op.inputs[0], And))
        self.assertEqual(or_op.inputs[0].inputs[0].field, "a")
        self.assertEqual(or_op.inputs[0].inputs[0].val, "test")
        self.assertEqual(or_op.inputs[0].inputs[0].val_type, Term.PARTIAL_STRING)

        self.assertEqual(or_op.inputs[0].inputs[1].field, "b")
        self.assertEqual(or_op.inputs[0].inputs[1].val, "otro")
        self.assertEqual(or_op.inputs[0].inputs[1].val_type, Term.PARTIAL_STRING)

        self.assertEqual(or_op.inputs[1].field, "c")
        self.assertEqual(or_op.inputs[1].val, "another")
        self.assertEqual(or_op.inputs[1].val_type, Term.PARTIAL_STRING)

    def test_fail_if_syntax_mismatch(self):
        with self.assertRaises(ParseException):
            self.init_and_parse('aa*', True)

if __name__ == "__main__":
    unittest.main(verbosity=3)
