#!/usr/bin/python
# -*- coding: utf-8 -*-

from .term_parser import TermParserFactory
from .expressions.primitives import PrimitiveFactory, ParserElement, operatorPrecedence, opAssoc
from .expressions.operators import *
from .expressions.terms import *


class GrammarError(Exception):
    pass


class GrammarFactory(object):

    @staticmethod
    def build(term, parser, operators, keywords=None):
        return Grammar(term=term, operators=operators, term_parser=parser, keywords=keywords)

    @staticmethod
    def build_default(term_parser=None):
        t_parser = term_parser or TermParserFactory.build_default()
        operators = [Operator("not", ['!', '-', 'not']), Operator('and', ['+', 'and']), Operator('or', ['or'], True)]
        term = TermFactory.build_default_term(t_parser)

        return Grammar(operators=operators, term=term, keywords=[], term_parser=t_parser)

    @staticmethod
    def build_from_conf(conf):
        operators = []
        keywords = {}

        term_parser = TermParserFactory.build_from_conf(conf['term_parser'])

        if 'operators' in conf:
            for op_def in conf['operators']:
                key = list(op_def.keys())[0]
                op_ = list(op_def.values())[0]
                operators.append(Operator(key, op_['symbols'], op_['implicit']))

        if 'term' in conf:
            field = PrimitiveFactory.build_from_conf(conf['term']['field'], term_parser)
            values = [PrimitiveFactory.build_from_conf(v, term_parser) for v in conf['term']['values']]

            term = TermFactory.build_term(field, values, term_parser.term_parse)
        else:
            term = TermFactory.build_default_term(term_parser)

        if 'keywords' in conf:
            keywords = [KeywordTerm(keyword_name=key, possible_values=values, parse_method=term_parser.keyword_parse)
                        for key, values in iter(conf['keywords'].items())]

        return Grammar(operators=operators, term=term, keywords=keywords, term_parser=term_parser)


class Grammar(object):

    def __init__(self, operators, term, keywords, term_parser):
        self._term_parser = term_parser
        self._operators = operators
        self._keywords = keywords
        self._term = term
        self._grammar_parser = self._build_grammar()

    def _build_grammar(self):
        ParserElement.enablePackrat()

        precedence_list = []

        for op in self._operators:
            if op.name == 'not':
                op_def = Optional(op) if op.implicit else op
                op_def = (op_def.setParseAction(lambda: "NOT"), 1, opAssoc.RIGHT)
            elif op.name == 'and':
                op_def = Optional(op) if op.implicit else op
                op_def = (op_def.setParseAction(lambda: "AND"), 2, opAssoc.LEFT)
            elif op.name == 'or':
                op_def = Optional(op) if op.implicit else op
                op_def = (op_def.setParseAction(lambda: "OR"), 2, opAssoc.LEFT)
            else:
                op_def = None

            precedence_list.append(op_def)

        # The expression has to combine operators with terms and/or keywords
        # Keywords have higher precedence over terms
        expression_elem = concatenate((self._keywords if self._keywords else []) + [self._term])
        expression = operatorPrecedence(expression_elem, precedence_list)

        return expression.parseString

    def _update_grammar(self, term=None, operators=None, keywords=None):
        self._term = term if term else self._term
        self._operators = operators if operators else self._operators
        self._keywords = keywords if keywords else self._keywords
        self._grammar_parser = self._build_grammar()

    @property
    def term_parser(self):
        return self._term_parser

    @property
    def keywords(self):
        return [k.name for k in self._keywords]

    @property
    def value_types(self):
        return [{'type': v.name, 'precedence': v.precedence} for v in self._term.values]

    @property
    def field_type(self):
        return self._term.field.name

    @property
    def operators(self):
        return [op.name for op in self._operators]

    def add_keyword(self, keyword):
        if not isinstance(keyword, KeywordTerm):
            raise GrammarError("Keyword types should be plyse.expressions.terms.Keyword")

        if keyword.name in self.keywords:
            raise GrammarError("Grammar already has a keyword with the same name")

        self._update_grammar(keywords=self._keywords + [keyword])
        return self

    def add_value_type(self, value):
        if not isinstance(value, ParserElement):
            raise GrammarError("Value types should be PyParsing ParserElements or plyse.expressions.primitives.BaseType")

        new_term = TermFactory.build_term(self._term.field, self._term.values + [value], *self._term.parseAction)
        self._update_grammar(new_term)
        return self

    def remove_type(self, type_name):
        new_term_values = filter(lambda x: x.name != type_name, self._term.values)
        new_term = TermFactory.build_term(self._term.field, new_term_values, *self._term.parseAction)
        self._update_grammar(term=new_term)
        return self

    def remove_operator(self, operator_name):
        self._update_grammar(operators=list(filter(lambda x: x.name != operator_name, self._operators)))
        return self

    def remove_keyword(self, keyword_name):
        self._update_grammar(keywords=list(filter(lambda x: x.name != keyword_name, self._keywords)))
        return self

    def parse(self, input_string, fail_if_syntax_mismatch=False):
        return self._grammar_parser(input_string, parseAll=fail_if_syntax_mismatch)
