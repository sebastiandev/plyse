#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from plyse.expressions.terms import *
from plyse.expressions.primitives import *


class TermsTester(unittest.TestCase):

    def assert_parsed_output(self, primitive, input_list):
        for inp in input_list:
            output = primitive.parseString(inp)[0]
            for o in output:
                self.assertIn(o, inp)

    def test_term(self):
        t = TermFactory.build_term(Field(), [Integer(), QuotedString(), PartialString()])
        self.assert_parsed_output(t, ["name:tester", "age:30", "nickname:'test'", "freetext"])

    def test_keyword(self):
        k = KeywordTerm("has", ["message", "comment", "notification"])

        output = k.parseString("has:message")
        self.assertEqual("has", output[0])
        self.assertEqual("message", output[2])

        output = k.parseString("has:comment")
        self.assertEqual("has", output[0])
        self.assertEqual("comment", output[2])

        output = k.parseString("has:notification")
        self.assertEqual("has", output[0])
        self.assertEqual("notification", output[2])

        output = k.parseString("has:10")
        self.assertEqual("has", output[0])
        self.assertEqual("10", output[2])

        self.assertRaises(ParseException, k.parseString, "freetext")

        k = KeywordTerm("has", ["message", "comment", "notification"], allow_other_values=False)
        self.assertRaises(ParseException, k.parseString, "has:10")

if __name__ == '__main__':
    unittest.main()

