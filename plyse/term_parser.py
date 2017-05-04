#!/usr/bin/python
# -*- coding: utf-8 -*-
from .util import load_module


class TermParserFactory(object):

    @staticmethod
    def build_from_conf(conf):
        args = {k: conf[k] for k in ['default_fields', 'aliases', 'integer_as_string'] if k in conf}

        return TermParser(**args) if not 'class' in conf else load_module(conf['class'])(**args)

    @staticmethod
    def build_default():
        return TermParser()


class TermParser(object):

    """
    Parse and build a term from the grammar matches. A Term represents a query component that can have a specific field
    to look for, or a default one, a field type, the value required for that field and the type of value.

    TermParser defines methods to be used in combination with :class:Grammar as the callbacks for the pyparsing
    setParseAction method.

    Callback parameters are always:
      - matched string from query string
      - position of the match
      - pyparsing token list

    """

    def __init__(self, default_fields=['default'], aliases=None, integer_as_string=False):
        self._default_fields = default_fields
        self._field_name_aliases = aliases if aliases else {}
        self._integers_as_string = integer_as_string

    def _build_field_data(self, field_values, field_type):
        return {Term.FIELD: field_values, Term.FIELD_TYPE: field_type}

    def _build_value_data(self, value, value_type):
        return {Term.VAL: value, Term.VAL_TYPE: value_type}

    def _build_term_with_default_fields(self, value_dict):
        default_fields = self._default_fields[0] if len(self._default_fields) == 1 else self._default_fields
        r = self._build_field_data(default_fields, Term.DEFAULT)

        r.update(value_dict)

        return r

    @property
    def aliases(self):
        return self._field_name_aliases

    def term_parse(self, string, location, tokens):
        """
        Term parse receives a list with the components of a query term, the fields to look for and the desired value.
        Those components are expanded by field_parse and integer_parse r whatever value is matched, to a dictionary
        specifying the field_type and field_value as well as value_type and value. Thus, tokens[0] contains one element
        for the field data, and another for the value data. If there's only one item, it means no field was specified only
        a value, and so we treat it as a default field which can be configured to be expanded to several fields.

        If tokens[0] has 2 elements:
            > tokens[0][0]: field dict
            > tokens[0][1]: value dict

        If tokens[0] has 1 element:
            > tokens[0][0]: value dict
        """
        if tokens:
            if len(tokens[0]) == 1:  # If there was no field specified, use the default
                r = self._build_term_with_default_fields(tokens[0][0])
            else:
                r = tokens[0][0]
                r.update(tokens[0][1])

            return Term(**r)

    def keyword_parse(self, string=None, location=None, tokens=None):
        """
        Keywords are defined externally and so values are restricted to the ones accepted/defined. They are treated as
        strings always and so the parsing method receives a token list with <keyword>, <separator>, <value>

            > ej: has:notification => token list would be ['has', ':', 'notification']
        """
        if tokens:
            fields = [f for f in "".join(tokens).split(":") if f]
            output = self._build_field_data(fields[0], Term.KEYWORD)
            output.update(self._build_value_data(fields[1], Term.KEYWORD_VALUE))

            return output

    def field_parse(self, string, location, tokens):
        """
        Fields are whatever comes before a separator and they are usually use for attribute/property matching. The value
        of a field is parsed separately form the field name and it depends on the definition of the grammar and the
        accepted/supported values. Thus this method receives a token list with <field name> <separator>.

        If combined or nested fields are allowed, the pattern would be:
            <field name> <separator> <field name> <separator> ...

            > ej: address:zip:ABC1234 => token list would be ['address', ':', 'zip']
        """
        if tokens:
            fields = [f for f in "".join(tokens).split(":") if f]
            t = fields if len(fields) > 1 else fields[0]

            field_value = self._field_name_aliases.get(t, t)

            return self._build_field_data(field_value, Term.ATTRIBUTE)

    def integer_parse(self, string, location, tokens):
        if tokens:
            r = self._build_value_data(int(tokens[0]), Term.INT)

            if self._integers_as_string:
                r[Term.VAL_TYPE] = Term.PARTIAL_STRING
                r[Term.VAL] = str(r[Term.VAL])

            return r

    def integer_comparison_parse(self, string, location, tokens):
        if tokens:
            val = int(tokens[1]) if not self._integers_as_string else tokens[1]

            for symbol, value_type in [('<', Term.LOWER_THAN), ('<=', Term.LOWER_EQUAL_THAN),
                                       ('>', Term.GREATER_THAN), ('>=', Term.GREATER_EQUAL_THAN)]:
                if tokens[0] == symbol:
                    return self._build_value_data(val, value_type)

            raise Exception("Invalid comparison symbol!")  # should never get here since pyparsing would fail before

    def quoted_string_parse(self, string, location, tokens):
        if tokens:
            return self._build_value_data(tokens[0], Term.EXACT_STRING if '*' not in tokens[0] else Term.PARTIAL_STRING)

    def partial_string_parse(self, string, location, tokens):
        if tokens:
            return self._build_value_data(tokens[0], Term.PARTIAL_STRING)

    def range_parse(self, string, location, tokens):
        if tokens:
            return self._build_value_data([tokens[0][Term.VAL], tokens[2][Term.VAL]],
                                          Term.RANGE % tokens[0][Term.VAL_TYPE])


class Term(dict):

    # value types
    RANGE = "%s_range"
    INT = 'int'
    EXACT_STRING = 'exact_string'
    PARTIAL_STRING = 'partial_string'
    KEYWORD_VALUE = 'keyword_value'
    GREATER_THAN = 'greater_than'
    GREATER_EQUAL_THAN = 'greater_equal_than'
    LOWER_THAN = 'lower_than'
    LOWER_EQUAL_THAN = 'lower_equal_than'

    # field types
    KEYWORD = 'keyword'
    DEFAULT = 'default'
    ATTRIBUTE = 'attribute'

    # term keys
    FIELD = 'field'
    FIELD_TYPE = 'field_type'
    VAL = 'val'
    VAL_TYPE = 'val_type'

    def __getattr__(self, key):
        if key in self:
            return self[key]
        else:
            raise AttributeError("Term doesn't have attribute '%s'" % key)

    @property
    def field(self):
        return self[self.FIELD] if self.FIELD in self else None

    @property
    def field_type(self):
        return self[self.FIELD_TYPE] if self.FIELD_TYPE in self else None

    @property
    def value(self):
        return self[self.VAL] if self.VAL in self else None

    @property
    def value_type(self):
        return self[self.VAL_TYPE] if self.VAL_TYPE in self else None
