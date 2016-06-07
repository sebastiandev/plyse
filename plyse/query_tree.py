#!/usr/bin/python
# -*- coding: utf-8 -*-
from copy import deepcopy


class TreeNode(dict):

    def __init__(self, *args, **kwargs):
        super(TreeNode, self).__init__(*args, **kwargs)

    @property
    def is_leaf(self):
        raise NotImplementedError()

    @property
    def children(self, *args, **kwargs):
        """
        Returns all the child nodes from the itself

        :return children as list of TreeNodes
        """

        raise NotImplementedError()

    def leaves(self, *args, **kwargs):
        """
        Returns all leaves from the current node

        :return a list of leaves
        """
        raise NotImplementedError()

    def traverse(self, node_callback=lambda node: node, leaf_callback=lambda node: node):
        """
        Traverse the tree and for each node or leaf calls the corresponding callback
        """
        raise NotImplementedError()


class Operand(TreeNode):

    def __init__(self, *args, **kwargs):
        super(Operand, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("Operand doesn't have an attribute named '%s'" % name)

    def __setattr__(self, name, val):
        self[name] = val

    @property
    def is_leaf(self):
        return True

    @property
    def children(self, *args, **kwargs):
        return []

    def leaves(self, *args, **kwargs):
        return [self]


class OperatorFactoryError(Exception):
    pass


class OperatorFactory(object):

    @staticmethod
    def create(op_type):
        if op_type.lower() == Or.type:
            return Or()
        elif op_type.lower() == And.type:
            return And()
        elif op_type.lower() == Not.type:
            return Not()
        else:
            raise OperatorFactoryError("Cannot create an operator of type '%s'" % op_type)


class Operator(TreeNode):
    type = "base_operator"

    def __init__(self, operands=None, *args, **kwargs):
        super(Operator, self).__init__(*args, **kwargs)
        self._operands = [] if not operands else operands

    def has_left_operand(self):
        raise Exception("Not implemented!")

    def has_right_operand(self):
        raise Exception("Not implemented!")

    def add_input(self, operand):
        # An operator can have only two inputs (binary tree). If another gets added then it creates a new operator
        # of the same type with inputs as the last element and the one wanted to be added. The result is a left input
        # operand and a right input operator, with the last element and the new one as inputs
        if len(self._operands) == 2:
            op = self.__class__([self._operands.pop(1), operand])
            self._operands.append(op)
        else:
            self._operands.append(operand)

        return self

    @property
    def is_leaf(self):
        return False

    @property
    def children(self, *args, **kwargs):
        return self.inputs

    @property
    def inputs(self):
        return self._operands

    def leaves(self, ignore_negated=False, *args, **kwargs):
        leaves = []
        self.traverse(ignore_negated=ignore_negated, leaf_callback=lambda leaf: leaves.append(leaf))
        return leaves

    def traverse(self, node_callback=lambda node: node, leaf_callback=lambda leaf: leaf, ignore_negated=False):
        def _do_traverse(operand):
            if operand.is_leaf:
                leaf_callback(operand)

            elif isinstance(operand, Not) and ignore_negated:
                pass

            else:
                node_callback(operand)
                _do_traverse(operand.inputs[0])

                if len(operand.inputs) > 1:
                    _do_traverse(operand.inputs[1])

        return _do_traverse(self)

    def __str__(self):
        return "[TreeNode] '{op}' operator with {children} children ".format(op=self.type.upper(), children=len(self.children))

    def __repr__(self):
        return self.__str__()


class And(Operator):
    type = "and"

    def has_left_operand(self):
        return True

    def has_right_operand(self):
        return True


class Or(Operator):
    type = "or"

    def has_left_operand(self):
        return True

    def has_right_operand(self):
        return True


class NotOperatorError(Exception):
    pass


class Not(Operator):
    type = "not"

    def has_left_operand(self):
        return False

    def has_right_operand(self):
        return True

    def add_input(self, operand):
        if not self._operands:
            self._operands.append(operand)
        else:
            raise NotOperatorError("Cannot add more than one input to Not Operator")

        return self
