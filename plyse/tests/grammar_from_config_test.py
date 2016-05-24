# -*- coding: utf-8 -*-
import unittest
from .grammar_test import GrammarTester
from plyse.grammar import GrammarFactory
from plyse.term_parser import Term


conf = {
    'term_parser': 'plyse.term_parser.TermParser',
    'default_fields': ['default'],
    'aliases': {},
    'operators': [ 
        {'not': {
            'implicit': False,
            'symbols': ['not', '-', '!']
        }},
        {'and': {
            'implicit': False,
            'symbols': ['and', '+', '&&']
        }},
        {'or': {
            'implicit': True,
            'symbols': ['or']
        }}
    ],
    'keywords': {
        'has': ['notifications'],
        'is': ['important']
    },
    'term': {
        'field': {
            'class': 'plyse.expressions.primitives.Field',
            'precedence': 10,
            'parse_method': 'field_parse'
        },
        'values': [
            {
                'class': 'plyse.expressions.primitives.PartialString',
                'precedence': 3,
                'parse_method': 'partial_string_parse'
            },
            {
                'class': 'plyse.expressions.primitives.QuotedString',
                'precedence': 2,
                'parse_method': 'quoted_string_parse'
            },
            {
                'class': 'plyse.expressions.primitives.Integer',
                'precedence': 4,
                'parse_method': 'integer_parse'
            },
            {
                'class': 'plyse.expressions.primitives.IntegerRange',
                'precedence': 5,
                'range_parse_method': 'range_parse',
                'item_parse_method': 'integer_parse'
            }
        ]
    }
}


class ConfigurableGrammarTester(GrammarTester):

    def _build_grammar(self):
        return GrammarFactory.build_from_conf(conf)

    def _check_field(self, term, expected_field):
        if term[Term.FIELD_TYPE] == Term.DEFAULT:
            expected_field = conf['default_fields'][0] if 'default_fields' in conf else expected_field

        elif term[Term.FIELD_TYPE] == Term.KEYWORD:
            self.assertEqual(term[Term.VAL_TYPE], Term.KEYWORD_VALUE)

        elif term[Term.FIELD_TYPE] == Term.ATTRIBUTE:
            pass

        else:
            raise Exception("Unknown Field type!")

        self.assertEqual(term[Term.FIELD], expected_field)

    def test_config_loaded(self):
        grammar = self._build_grammar()
        for keyword in conf['keywords']:
            self.assertTrue(keyword in grammar.keywords,
                            "Keyword '%s' should be defined" % keyword)

        for default_field in conf['default_fields']:
            self.assertTrue(default_field in grammar.term_parser._default_fields,
                            "Default field '%s' should be defined" % default_field)

        for alias in conf['aliases']:
            self.assertTrue(alias in grammar.term_parser.aliases,
                            "Alias '%s' should be defined" % alias)

        # order defines precedence!
        self.assertEqual(['not', 'and', 'or'], grammar.operators, "Operators are not ordered as expected")

    def test_keywords(self):
        r = self._init_and_parse('has:notifications')
        self._check_values(r, "has", 'notifications', Term.KEYWORD_VALUE)

        r = self._init_and_parse('is:important')
        self._check_values(r, "is", 'important', Term.KEYWORD_VALUE)

        r = self._init_and_parse('has:notifications + is:important')
        self._check_values(r[0], "has", "notifications", Term.KEYWORD_VALUE)
        self._check_values(r[1], expected_val="AND")
        self._check_values(r[2], "is", "important", Term.KEYWORD_VALUE)

    def test_remove_not_operator(self):
        g = self._build_grammar()

        g.remove_operator('fake')  # doesnt exists, but it should crash
        g.remove_operator('not')
        self.assertTrue('not' not in g.operators)

        r = g.parse("-name:dummy")
        self.assertEqual(r[0]['field'], "-name")  # didn't apply NOT because it was removed

    def test_remove_integer_type_then_match_as_string(self):
        g = self._build_grammar()

        g.remove_type('integer')
        self.assertTrue('integer' not in g.value_types)

        r = g.parse("number:127")
        self._check_values(r[0], 'number', '127', Term.PARTIAL_STRING)

    def test_remove_keyword_then_match_as_field(self):
        g = self._build_grammar()

        g.remove_keyword('is')
        self.assertTrue('is' not in g.keywords)

        r = g.parse("is:something")
        self._check_values(r[0], 'is', 'something', Term.PARTIAL_STRING)

if __name__ == "__main__":
    unittest.main()
