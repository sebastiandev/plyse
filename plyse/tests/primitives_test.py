#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from plyse.expressions.primitives import *


class PrimitiveTester(unittest.TestCase):

    def assert_parsed_output(self, primitive, input_expected_val_dict):
        for inp, exp in iter(input_expected_val_dict.items()):
            if exp:
                output = primitive.parseString(inp)
                for n, o in enumerate(output):
                    self.assertEqual(exp[n], o)
            else:
                self.assertRaises(ParseException, primitive.parseString, inp)

    def test_base_word(self):
        bw = BaseWord("abc", 1)
        self.assertEqual(1, bw.precedence)
        self.assert_parsed_output(bw, {'abc': ['abc'], 'ad': ['a'], 'a b': ['a'], 'd': None})

    def test_simple_word(self):
        sw = SimpleWord()
        self.assert_parsed_output(sw, {'abc': ['abc'], 'ab-c': ['ab-c'], 'ab.c': ['ab.c'], 'ab_c': ['ab_c']})

        sw = SimpleWord(extra_chars=":;")
        self.assert_parsed_output(sw, {'a:b:c': ['a:b:c'], 'ab;c': ['ab;c']})

    def test_fieldname(self):
        fn = FieldName()
        self.assert_parsed_output(fn, {'abc': ['abc'], 'ab-c': ['ab-c'], 'ab_c': ['ab_c']})

        fn = FieldName(extra_chars=":")
        self.assert_parsed_output(fn, {'a:b:c': ['a:b:c']})

    def test_partial_string(self):
        ps = PartialString()
        self.assert_parsed_output(ps, {'abc': ['abc'], 'ab-c': ['ab-c'], 'ab.c': ['ab.c'], 'ab_c': ['ab_c']})

    def test_quoted_string(self):
        qs = QuotedString()
        self.assert_parsed_output(qs, {'"abc"': ['abc'], '"ab-c"': ['ab-c'], "'ab.c'": ["ab.c"], 'a': None})

    def test_phrase(self):
        ph = Phrase()
        self.assert_parsed_output(ph, {'abc': ['abc'], 'ab c': ['ab', 'c'], 'a b c': ['a', 'b', 'c']})

    def test_integer(self):
        i = Integer()
        self.assert_parsed_output(i, {'1': ['1'], '10': ['10'], '1a': ['1'], '1 a': ['1'], 'a': None})

    def test_integer_range(self):
        ir = IntegerRange()
        self.assert_parsed_output(ir, {'1..5': ['1', '..', '5'], '10..50': ['10', '..', '50'], '1': None})

        ir = IntegerRange(range_symbol='_')
        self.assert_parsed_output(ir, {'1_5': ['1', '_', '5'], '10_50': ['10', '_', '50'], '1': None})

    def test_field(self):
        f = Field()
        self.assert_parsed_output(f, {'name:test': ['name', ':'], 'age:10': ['age', ':'], 'aa': None})

        f = Field(field_separator='>')
        self.assert_parsed_output(f, {'name>test': ['name', '>'], 'age>10': ['age', '>'], 'aa': None})

    def test_multi_field(self):
        mf = Field()
        self.assert_parsed_output(mf, {'first:name:test': ['first', ':', 'name', ':'], 'age:10': ['age', ':']})

        mf = Field(field_separator='>')
        self.assert_parsed_output(mf, {'first>name>test': ['first', '>', 'name', '>'], 'age>10': ['age', '>']})

    def test_any(self):
        a = Any([Integer(), SimpleWord()])
        self.assert_parsed_output(a, {'test': ['test'], '10': ['10'], '"quoted"': None})

    def test_integer_comparisson(self):
        ic = IntegerComparison()
        self.assert_parsed_output(ic, {'<10': ['<', '10'], '<=10': ['<=', '10'], '>10': ['>', '10'], '>=10': ['>=', '10'], '">e"': None})

    def test_string_proximity(self):
        sp = StringProximity()
        self.assert_parsed_output(sp, {"'hello world'~3": ['hello world', '~', '3']})

if __name__ == '__main__':
    unittest.main()
