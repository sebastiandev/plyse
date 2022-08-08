# -*- coding: utf-8 -*-
from pyparsing import (Literal, Word, MatchFirst, CaselessKeyword, Regex, QuotedString as QString,
                       Suppress, Optional, Group, FollowedBy, Combine,
                       operatorPrecedence, opAssoc, ParseException,
                       ParserElement, alphanums, And, OneOrMore, delimitedList)

from ..util import load_module


class PrimitiveFactoryError(Exception):
    pass


class PrimitiveFactory(object):

    @staticmethod
    def build_from_conf(conf, parser):
        _cls = load_module(conf['class'])

        _kwargs = {}
        if not (set(conf.keys() - ['class']) <= set(_cls.__init__.__code__.co_varnames[1:])):
            extra_parameters = set(conf.keys()) - (set(conf.keys()) & set(_cls.__init__.__code__.co_varnames[1:]))
            raise PrimitiveFactoryError(
                'Invalid primitive definition: configuration for class {} has extra parameters'.format(
                    _cls.__name__, extra_parameters))

        for var in _cls.__init__.__code__.co_varnames[1:]:
            if var not in conf:
                continue

            if var.endswith('parse_method'):
                try:
                    _kwargs[var] = getattr(parser, conf[var])
                except AttributeError:
                    raise PrimitiveFactoryError(
                        'Invalid Primitive definition. Parser {} does not have a method {}'.format(parser, conf[var]))

                continue

            _kwargs[var] = conf[var]
        return _cls(**_kwargs)


def concatenate(elems, operator='OR', class_to_embed_elem=None):
    """
    Receives a list of elements to be concatenated, to generate a type
    MatchFirst from pyParsing. Order is important given that it matches with the
    one found first

    :param elems: list of elements to concatenate
    :param operator: type of operator to concatenate with
    :param class_to_embed_elem: class to use to initialize each element in the list
    :return: MatchFirst object representing the optional matching with any of the elements in the list
    """
    combined_elems = class_to_embed_elem(elems[0]) if class_to_embed_elem else elems[0]

    for e in elems[1:]:
        elem_to_concat = class_to_embed_elem(e) if class_to_embed_elem else e

        if operator == 'OR':
            combined_elems = combined_elems | elem_to_concat

        elif operator == 'AND':
            combined_elems = combined_elems & elem_to_concat

        elif operator == 'LONGEST_OR':  # OR that matches the longest expression
            combined_elems = combined_elems ^ elem_to_concat

    return combined_elems


class BaseType(object):

    name = 'base'

    def __init__(self, precedence):
        self.precedence = precedence


class BaseWord(Word, BaseType):

    name = 'base_word'

    def __init__(self, chars, precendece):
        Word.__init__(self, chars)
        BaseType.__init__(self, precendece)


class SimpleWord(BaseWord):

    name = 'simple_word'

    def __init__(self, parse_method=None, extra_chars=None, precedence=0):
        extra_chars = extra_chars if extra_chars else ''
        extra_chars += '_.-'
        super(SimpleWord, self).__init__(alphanums+extra_chars, precedence)

        self.addParseAction(lambda t: t[0].replace('\\\\', chr(127)).replace('\\', '').replace(chr(127), '\\'))

        if parse_method:
            self.addParseAction(parse_method)


class FieldName(BaseWord):

    name = 'field_name'

    def __init__(self, parse_method=None, extra_chars=None, precedence=0):
        extra_chars = extra_chars if extra_chars else ''
        extra_chars += '_-'

        super(FieldName, self).__init__(alphanums+extra_chars, precedence)

        if parse_method:
            self.addParseAction(parse_method)


class PartialString(SimpleWord):

    name = 'partial_string'

    def __init__(self, parse_method=None, precedence=3):
        super(PartialString, self).__init__(parse_method, precedence=precedence)


class QuotedString(MatchFirst, BaseType):

    name = 'quoted_string'

    def __init__(self, parse_method=None, precedence=2):
        MatchFirst.__init__(self, [QString('"'), QString("'")])
        BaseType.__init__(self, precedence)

        if parse_method:
            self.addParseAction(parse_method)


class Phrase(OneOrMore, BaseType):

    name = 'phrase'

    def __init__(self, parse_method=None, precedence=2):
        OneOrMore.__init__(self, SimpleWord()+Optional(OneOrMore(Regex(r'[\b|\s]'))))
        BaseType.__init__(self, precedence)

        if parse_method:
            self.addParseAction(parse_method)


class Any(MatchFirst, BaseType):

    name = 'any'

    def __init__(self, elems, precedence=4):
        MatchFirst.__init__(self, concatenate(elems))
        BaseType.__init__(self, precedence)


class Integer(Regex, BaseType):

    name = 'integer'

    def __init__(self, parse_method=None, precedence=6):
        Regex.__init__(self, r"\d+")
        BaseType.__init__(self, precedence)

        if parse_method:
            self.addParseAction(parse_method)


class Container(And, BaseType):

    name = 'container'

    def __init__(self,
                 parse_method=None,
                 int_parse_method=None,
                 part_str_parse_method=None,
                 qstr_parse_method=None,
                 delim=',',
                 precedence=8):
        value = Integer(int_parse_method) ^ PartialString(part_str_parse_method) ^ QuotedString(qstr_parse_method)
        And.__init__(
            self,
            [
                Suppress(Literal('['))
                + Group(delimitedList(value, delim=delim) + Optional(Suppress(Literal(delim))))
                + Suppress(Literal(']'))
            ],
        )
        BaseType.__init__(self, precedence)

        if parse_method:
            self.addParseAction(parse_method)


class IntegerComparison(And, BaseType):

    name = 'integer_comparison'

    def __init__(self, parse_method=None, precedence=9):
        gt_lt_e = Literal('<') ^ Literal("<=") ^ Literal('>') ^ Literal(">=")
        And.__init__(self, [gt_lt_e + Integer()])
        BaseType.__init__(self, precedence)

        if parse_method:
            self.addParseAction(parse_method)


class IntegerRange(And, BaseType):

    name = 'integer_range'

    def __init__(self, range_parse_method=None, item_parse_method=None, range_symbol='..', precedence=10):
        And.__init__(self, [Integer(item_parse_method) + Literal(range_symbol) + Integer(item_parse_method)])
        BaseType.__init__(self, precedence)

        if range_parse_method:
            self.addParseAction(range_parse_method)


class Field(And, BaseType):

    name = 'field'

    def __init__(self, parse_method=None, field_separator=':', precedence=11):
        And.__init__(self, [FieldName() + Literal(field_separator)])
        BaseType.__init__(self, precedence)

        if parse_method:
            self.addParseAction(parse_method)


class MultiField(OneOrMore, BaseType):

    name = 'multi_field'

    def __init__(self, parse_method=None, field_separator=':', precedence=12):
        OneOrMore.__init__(self, Field(field_separator=field_separator))
        BaseType.__init__(self, precedence)

        if parse_method:
            self.addParseAction(parse_method)


class StringProximity(And, BaseType):

    name = 'string_proximity'

    def __init__(self, parse_method=None, precedence=11):
        And.__init__(self, [QuotedString() + Literal('~') + Integer()])
        BaseType.__init__(self, precedence)

        if parse_method:
            self.addParseAction(parse_method)
