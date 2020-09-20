# -*- coding: utf-8 -*-
from pyparsing import Optional, Group, Literal, CaselessKeyword, And, OneOrMore

from .primitives import SimpleWord, Field, PartialString, QuotedString, Integer, IntegerRange, concatenate


class TermFactory(object):

    @staticmethod
    def build_term(field, values, parse_method=None):
        ordered_values = [val for val in sorted(values, key=lambda v: v.precedence, reverse=True)]
        return Term(field, ordered_values, parse_method)

    @staticmethod
    def build_default_term(parser):
        values = [IntegerRange(range_parse_method=parser.range_parse, item_parse_method=parser.integer_parse),
                  Integer(parse_method=parser.integer_parse),
                  PartialString(parse_method=parser.partial_string_parse),
                  QuotedString(parse_method=parser.quoted_string_parse)]

        return Term(Field(parse_method=parser.field_parse), values, parse_method=parser.term_parse)


class Term(Group):

    def __init__(self, field, values, parse_method=None):
        super(Term, self).__init__(Optional(field) + concatenate(values, operator="LONGEST_OR"))

        self.field = field
        self.values = values

        if parse_method:
            self.setParseAction(parse_method)


class KeywordTerm(And):

    def __init__(self, keyword_name, possible_values, separator=':', parse_method=None, allow_other_values=True):

        _values = concatenate(possible_values, operator="LONGEST_OR", class_to_embed_elem=CaselessKeyword)

        if allow_other_values:
            _values ^= SimpleWord()

        super(KeywordTerm, self).__init__([CaselessKeyword(keyword_name) + Literal(separator) + _values])

        self.name = keyword_name
        self.values = possible_values

        if parse_method:
            self.setParseAction(parse_method)
