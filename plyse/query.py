#!/usr/bin/python
# -*- coding: utf-8 -*-
from .query_tree import OperatorFactory, And, Or
from copy import deepcopy


class QueryError(Exception):
    pass


class Query(object):
    """
    Query represents the parsed user query. It allows to operate on a higher level
    combining query objects to build stacked or combined queries, as well as to retrieve
    queries from complex combined/stacked queries and all the terms conforming the query.

    Query is Immutable, every operation that modifies the state returns a new Query object

    """
    def __init__(self, query_tree, raw_query=None):
        self._raw_query = raw_query
        self._query_tree = deepcopy(query_tree)

        original_tuple = (deepcopy(query_tree), deepcopy(raw_query))
        self._stack_map = {0: original_tuple}
        self._combine_map = {0: original_tuple}

    def _mix_query(self, query, operator):
        q, raw = query.query_as_tree, query.raw_query

        new_root = OperatorFactory.create(operator)
        new_root.add_input(self._query_tree)
        new_root.add_input(deepcopy(q))

        new_root_raw = None
        if self._raw_query and raw:
            new_root_raw = "(%s) %s (%s)" % (self._raw_query, new_root.type, raw)

        return q, raw, new_root, new_root_raw

    def stack(self, query):
        q, raw, new_root, new_root_raw = self._mix_query(query, And.type)

        result = Query(new_root, new_root_raw)
        result._combine_map.update(self._combine_map)  # Keep the combined history from current query
        result._stack_map.update(self._stack_map)  # Keep the stack history and append the new one to the dict
        result._stack_map[len(self._stack_map)] = (deepcopy(q), deepcopy(raw))

        return result

    def combine(self, query):
        q, raw, new_root, new_root_raw = self._mix_query(query, Or.type)

        result = Query(new_root, new_root_raw)
        result._stack_map.update(self._stack_map)  # Keep the stack history from current query
        result._combine_map.update(self._combine_map)  # Keep the combine history and append the new one to the dict
        result._combine_map[len(self._combine_map)] = (deepcopy(q), deepcopy(raw))

        return result

    @property
    def query_as_tree(self):
        return self._query_tree

    @property
    def raw_query(self):
        return self._raw_query

    def terms(self, ignore_negated=False):
        return self._query_tree.leaves(ignore_negated)

    def query_from_stack(self, level):
        """
        Get the stacked query at level :level

        :param level: stack level or layer (position in the stack)
        :return: tuple (query_tree, raw_query)
        """
        return self._stack_map[level]
