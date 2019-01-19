#!/usr/bin/python
# -*- coding: utf-8 -*-
from copy import deepcopy
from .query_tree import Operator, OperatorFactory, Operand, And, Or, Not
from .query import Query
from .term_parser import Term


class QueryParserError(Exception):
    pass


class QueryParser(object):

    def __init__(self, grammar):
        self._grammar = grammar

    def parse(self, query_string, fail_if_syntax_mismatch=False):
        """
        Runs the query through the grammar and transforms the results into a boolean
        tree of operators and operands. Will raise ParseExceptopm if fail_if_syntax_mismatch
        is set and the full input can't be parsed.

        Grammar parse result should be a concatenation of lists where the elements/leafs
        are :class:Term 's representing the properties of each defined grammar element
        matched in the query string
        """
        return Query(
            self.parse_elements(self._grammar.parse(query_string, fail_if_syntax_mismatch)),
            raw_query=query_string
        )

    def parse_elements(self, elements, stack=None):
        if not elements:
            return deepcopy(stack.pop()) if stack else None

        stack = [] if not stack else stack

        e = elements[0]
        if type(e) is str and e.lower() in [And.type, Or.type, Not.type]:
            op = OperatorFactory.create(e)

            if op.has_left_operand():
                op.add_input(stack.pop())

            stack.append(op)
        else:
            if isinstance(e, dict):
                operand = Operand(**e)

            else:
                operand = self.parse_elements(e)

            if len(stack) == 0:
                stack.append(operand)

            elif isinstance(stack[-1], Operator) or isinstance(stack[-1], Operand):
                    current_elem = stack.pop().add_input(operand)

                    # 'Not' operator only works on the right element, if there was a previous operator
                    # the stack would be have 2 elements, so the new operand is added to the current operator
                    # (Not operator) and then the Not operator is added as an input to the previous operator
                    # finishing the cicle and leaving the stack with only one element (an operator)
                    if stack:
                        current_elem = stack.pop().add_input(current_elem)

                    stack.append(current_elem)

            else:
                msg = """The previous element of an operand should be None or another Operand.
                      The inputted parse result is invalid! Type '{type}', Stack: {stack}"""
                raise QueryParserError(msg.format(type=type(stack[-1]), stack=stack))

        return self.parse_elements(elements[1:], stack)

    def stringify(self, query):
        """
        Converts a query into its original string representation (like reversing the original parsing)

        :param query: :class:Query representing the original query string
        :return: string
        """
        s = self._do_stringify(query.query_as_tree)
        return s[1:-1] if s.startswith('(') else s

    def _do_stringify(self, node):
        if node.is_leaf:
            s = self._leaf_to_string(Term(**node))

        elif node.type is Not.type:
            s = Not.type + " " + self._do_stringify(node.children[0])

        else:
            s = "(%s %s %s)" % (self._do_stringify(node.children[0]), node.type, self._do_stringify(node.children[1]))

        return s

    def _leaf_to_string(self, term):
        if type(term.field) is list:
            s = str(term.value)
        else:
            # We are reverting the query to string, we have the already aliased fields and we want the original ones
            aliases = {v: k for k, v in iter(self._grammar.term_parser.aliases.items())}
            field = aliases[term.field] if term.field in aliases else term.field
            value = "%s..%s" % (term.value[0], term.value[1]) if type(term.value) is list else term.value
            s = "%s:%s" % (field, value)

        return s
