# -*- coding: utf-8 -*-
from pyparsing import Literal, CaselessKeyword, MatchFirst
from .primitives import concatenate


class Operator(MatchFirst):

    def __init__(self, name, symbols, implicit=False):
        symbols_ = [Literal(s) if len(s) == 1 else CaselessKeyword(s) for s in symbols]
        super(Operator, self).__init__(concatenate(symbols_, operator='OR'))

        self.name = name
        self.implicit = implicit
