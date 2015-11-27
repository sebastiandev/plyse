#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from plyse.grammar import GrammarFactory
from plyse.term_parser import Term


class GrammarTester(unittest.TestCase):

    def _build_grammar(self):
        return GrammarFactory.build_default()

    def _init_and_parse(self, input_str):
        g = self._build_grammar()
        self.assert_(g.parse(input_str, True))
        return g.parse(input_str, True)[0]

    def _check_field(self, term, expected_field):
        self.assertEqual(term['field'], expected_field)

    def _check_values(self, term, expected_field=None, expected_val=None, expected_val_type=None):
        if not expected_field and not expected_val_type:
            self.assertEqual(term, expected_val)
        else:
            self._check_field(term, expected_field)
            self.assertEqual(term['val'], expected_val)
            self.assertEqual(term['val_type'], expected_val_type)

    def test_simple_partial_text(self):
        r = self._init_and_parse("texto")

        self._check_values(r, "default", "texto", Term.PARTIAL_STRING)

    def test_simple_negated_partial_text(self):
        r = self._init_and_parse("-texto")

        self._check_values(r[0], expected_val="NOT")
        self._check_values(r[1], "default", "texto", Term.PARTIAL_STRING)

    def test_simple_field_partial_text_value(self):
        r = self._init_and_parse("a:test")

        self._check_values(r, "a", "test", Term.PARTIAL_STRING)

    def test_simple_field_with_underscore_partial_text_value(self):
        r = self._init_and_parse("a_b:test")

        self._check_values(r, "a_b", "test", Term.PARTIAL_STRING)

    def test_simple_field_with_dash_partial_text_value(self):
        r = self._init_and_parse("a-b:test")

        self._check_values(r, "a-b", "test", Term.PARTIAL_STRING)

    def test_simple_negated_field_partial_text_value(self):
        r = self._init_and_parse("-a:test")

        self._check_values(r[0], expected_val="NOT")
        self._check_values(r[1], "a", "test", Term.PARTIAL_STRING)

    def test_simple_field_exact_text_value(self):
        r = self._init_and_parse('a:"test"')

        self._check_values(r, "a", "test", Term.EXACT_STRING)

    def test_simple_field_exact_int_range_value(self):
        r = self._init_and_parse('a:1..4')

        self._check_values(r, "a", [1, 4], Term.RANGE % "int")

    def test_simple_field_exact_int_value(self):
        r = self._init_and_parse('age:30')

        self._check_values(r, "age", 30, Term.INT)

    def test_use_point_as_part_of_text(self):
        r = self._init_and_parse('"something.else"')
        self._check_values(r, "default", "something.else", Term.EXACT_STRING)

        r = self._init_and_parse('something.else')
        self._check_values(r, "default", "something.else", Term.PARTIAL_STRING)

    def test_use_underscore_as_part_of_text(self):
        r = self._init_and_parse('"something_else"')
        self._check_values(r, "default", "something_else", Term.EXACT_STRING)

        r = self._init_and_parse('something_else')
        self._check_values(r, "default", "something_else", Term.PARTIAL_STRING)

    def test_use_not_as_part_of_text(self):
        r = self._init_and_parse('"something-else"')
        self._check_values(r, "default", "something-else", Term.EXACT_STRING)

        r = self._init_and_parse('something-else')
        self._check_values(r, "default", "something-else", Term.PARTIAL_STRING)

    def test_use_not_as_part_of_partial_text(self):
        r = self._init_and_parse('"something-*"')

        self._check_values(r, "default", "something-*", Term.PARTIAL_STRING)

    def test_use_colon_as_part_of_text(self):
        r = self._init_and_parse('"something:else"')

        self._check_values(r, "default", "something:else", Term.EXACT_STRING)

    def test_use_colon_as_part_of_partial_text(self):
        r = self._init_and_parse('"something:*"')

        self._check_values(r, "default", "something:*", Term.PARTIAL_STRING)

    def test_simple_implicit_OR_with_fields(self):
        r = self._init_and_parse('a:"test" b:otro')

        self._check_values(r[0], "a", "test", Term.EXACT_STRING)
        self._check_values(r[1], expected_val="OR")
        self._check_values(r[2], "b", "otro", Term.PARTIAL_STRING)

    def test_simple_OR_with_text_field(self):
        r = self._init_and_parse('"test" or b:otro')

        self._check_values(r[0], "default", "test", Term.EXACT_STRING)
        self._check_values(r[1], expected_val="OR")
        self._check_values(r[2], "b", "otro", Term.PARTIAL_STRING)

    def test_simple_AND_with_field(self):
        r = self._init_and_parse('a:"test" and b:otro')

        self._check_values(r[0], "a", "test", Term.EXACT_STRING)
        self._check_values(r[1], expected_val="AND")
        self._check_values(r[2], "b", "otro", Term.PARTIAL_STRING)

    def test_simple_AND_as_plus_with_field(self):
        r = self._init_and_parse('a:"test" + b:otro')

        self._check_values(r[0], "a", "test", Term.EXACT_STRING)
        self._check_values(r[1], expected_val="AND")
        self._check_values(r[2], "b", "otro", Term.PARTIAL_STRING)

    def test_AND_precedence(self):
        r = self._init_and_parse('a:test or b:otro + c:another')

        self._check_values(r[0], "a", "test", Term.PARTIAL_STRING)
        self._check_values(r[1], expected_val="OR")

        # Right operand of OR is a nested AND
        self._check_values(r[2][0], "b", "otro", Term.PARTIAL_STRING)
        self._check_values(r[2][1], expected_val="AND")
        self._check_values(r[2][2], "c", "another", Term.PARTIAL_STRING)

    def test_parenthesis_precedence(self):
        r = self._init_and_parse('(a:test or b:otro) + c:another')

        self._check_values(r[0][0], "a", "test", Term.PARTIAL_STRING)
        self._check_values(r[0][1], expected_val="OR")
        self._check_values(r[0][2], "b", "otro", Term.PARTIAL_STRING)

        self._check_values(r[1], expected_val="AND")
        self._check_values(r[2], "c", "another", Term.PARTIAL_STRING)

    def test_parenthesis_precedence_with_implicit_OR(self):
        r = self._init_and_parse('(a:test b:otro) + c:another')

        self._check_values(r[0][0], "a", "test", Term.PARTIAL_STRING)
        self._check_values(r[0][1], expected_val="OR")
        self._check_values(r[0][2], "b", "otro", Term.PARTIAL_STRING)

        self._check_values(r[1], expected_val="AND")
        self._check_values(r[2], "c", "another", Term.PARTIAL_STRING)

    def test_parenthesis_OR_field_OR_field_AND_NOT_field(self):
        r = self._init_and_parse('(a:test + b:otro) c:another d:"xx" AND -e:0')

        self._check_values(r[0][0], "a", "test", Term.PARTIAL_STRING)
        self._check_values(r[0][1], expected_val="AND")
        self._check_values(r[0][2], "b", "otro", Term.PARTIAL_STRING)

        self._check_values(r[1], expected_val="OR")
        self._check_values(r[2], "c", "another", Term.PARTIAL_STRING)

        self._check_values(r[3], expected_val="OR")

        self._check_values(r[4][0], "d", "xx", Term.EXACT_STRING)
        self._check_values(r[4][1], expected_val="AND")
        self._check_values(r[4][2][0], expected_val="NOT")
        self._check_values(r[4][2][1], "e", 0, Term.INT)

if __name__ == '__main__':
    unittest.main()
