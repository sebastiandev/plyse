#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from plyse.grammar import GrammarFactory
from plyse.term_parser import TermParserFactory, Term
from plyse.expressions.primitives import IntegerComparison


class TermParserTester(unittest.TestCase):

    def _init_and_parse(self, input_str):
        conf = {
            'class': 'plyse.term_parser.TermParser',
            'default_fields': ['name', 'description'],
            'aliases': {
                'id': '__id__',
                'type': '__type__'
            },
            'integer_as_string': False
        }

        term_parser = TermParserFactory.build_from_conf(conf)
        g = GrammarFactory.build_default(term_parser)
        g.add_value_type(IntegerComparison(term_parser.integer_comparison_parse))
        self.assertTrue(g.parse(input_str, True))

        return g.parse(input_str, True)[0]

    def _check_values(self, term, expected_field=None, expected_val=None, expected_val_type=None):
        if not expected_field and not expected_val_type:
            self.assertEqual(term, expected_val)
        else:
            self.assertEqual(term['field'], expected_field)
            self.assertEqual(term['val'], expected_val)
            self.assertEqual(term['val_type'], expected_val_type)

    def test_default_field_partial_text(self):
        r = self._init_and_parse("texto")
        self._check_values(r, ['name', 'description'], "texto", Term.PARTIAL_STRING)

    def test_default_field_partial_text_with_wildcard(self):
        r = self._init_and_parse("'texto*'")
        self._check_values(r, ['name', 'description'], "texto*", Term.PARTIAL_STRING)

    def test_default_field_exact_text(self):
        r = self._init_and_parse("'texto'")
        self._check_values(r, ['name', 'description'], "texto", Term.EXACT_STRING)

    def test_aliased_field_partial_text(self):
        r = self._init_and_parse("id:xxx")
        self._check_values(r, '__id__', "xxx", Term.PARTIAL_STRING)

    def test_aliased_field_partial_text_with_wildcard(self):
        r = self._init_and_parse("id:'xxx*'")
        self._check_values(r, '__id__', "xxx*", Term.PARTIAL_STRING)

    def test_aliased_field_exact_text(self):
        r = self._init_and_parse("id:'xxx'")
        self._check_values(r, '__id__', "xxx", Term.EXACT_STRING)

    def test_aliased_field_int(self):
        r = self._init_and_parse("id:00")
        self._check_values(r, '__id__', 00, Term.INT)

    def test_field_int_range(self):
        r = self._init_and_parse("age:18..30")
        self._check_values(r, 'age', [18, 30], Term.RANGE % 'int')

    def test_field_int_comparisson(self):
        r = self._init_and_parse("age:>18")
        self._check_values(r, 'age', 18, Term.GREATER_THAN)

        r = self._init_and_parse("age:>=18")
        self._check_values(r, 'age', 18, Term.GREATER_EQUAL_THAN)

        r = self._init_and_parse("age:<18")
        self._check_values(r, 'age', 18, Term.LOWER_THAN)

        r = self._init_and_parse("age:<=18")
        self._check_values(r, 'age', 18, Term.LOWER_EQUAL_THAN)

if __name__ == '__main__':
    unittest.main()
