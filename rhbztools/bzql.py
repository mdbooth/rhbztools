# Copyright 2019 Red Hat, Inc
#
# This file is part of rhbztools.
#
# rhbztools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rhbztools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rhbztools.  If not, see <https://www.gnu.org/licenses/>.

import contextlib
import os.path

import tatsu
from tatsu.walkers import NodeWalker


class BZQLWalker(NodeWalker):
    def __init__(self):
        super(BZQLWalker, self).__init__()

        self.n = 0
        self.params = {}

        self.aliased_ops = {
            '=': 'equals',
            '!=': 'notequals',
            'in': 'anyexact',
            '~': 'regexp',
            '!~': 'notregexp',
            '<': 'lessthan',
            '<=': 'lessthaneq',
            '>': 'greaterthan',
            '>=': 'greaterthaneq',
            'contains': 'casesubstring',
        }

        self.aliased_query_fields = {
            'devel_whiteboard': 'cf_devel_whiteboard',
            'fixed_in': 'cf_fixed_in',
            'flags': 'flagtypes.name',
            'internal_whiteboard': 'cf_internal_whiteboard',
            'pm_score': 'cf_pm_score',
            'qa_whiteboard': 'cf_qa_whiteboard',
            'status': 'bug_status',
            'zstream_target_release': 'cf_zstream_target_release',
        }

    def _set(self, key, value, n=None):
        if n is None:
            n = self.n
        if n < 0:
            n = '_top'

        self.params['{key}{n}'.format(key=key, n=n)] = value

    def walk_object(self, node, negate=False):
        return node

    def walk_OrGroup(self, node):
        # Ignore or group with a single member
        if len(node.ast) == 1:
            return self.walk(node.ast[0])

        self._set('j', 'OR', n=self.n - 1)
        for e in node.ast:
            self.walk(e, parent_is_or=True)

    def walk_AndGroup(self, node, parent_is_or=False):
        def _andgroup():
            for e in node.ast:
                self.walk(e)

        # Populated and group beneath an or group needs an implicit subgroup
        if parent_is_or and len(node.ast) > 1:
            with self._subgroup():
                _andgroup()
        else:
            _andgroup()

    @contextlib.contextmanager
    def _subgroup(self, negate=False):
        self._set('f', 'OP')
        if negate:
            self._set('n', 1)

        self.n += 1

        yield

        self._set('f', 'CP')
        self.n += 1

    def walk_Negatable(self, node):
        negated = node.negate is not None
        return self.walk(node.negatable, negate=negated)

    def walk_SubGroup(self, node, negate=False):
        with self._subgroup(negate):
            self.walk(node.ast)

    def walk_OpExpression(self, node, negate=False):
        op = self.aliased_ops.get(node.op)
        if op is None:
            op = node.op

        field = self.aliased_query_fields.get(node.field)
        if field is None:
            field = node.field

        self._set('f', field)
        self._set('o', op)
        if negate:
            self._set('n', 1)

        if node.value is not None:
            value = self.walk(node.value)
            self._set('v', value)

        self.n += 1

    def walk_String(self, node):
        return str(node.scalar)

    def walk_Float(self, node):
        return float(node.scalar)

    def walk_Int(self, node):
        return int(node.scalar)

    def walk_List(self, node):
        return ", ".join((i.scalar for i in node.list))

def parser():
    ebnf_path = os.path.join(os.path.dirname(__file__), 'bzql.ebnf')
    with open(ebnf_path, 'r') as ebnf:
        grammar = ebnf.read()

    parser = tatsu.compile(grammar, asmodel=True)

    def _parse(query):
        model = parser.parse(query)
        walker = BZQLWalker()
        walker.walk(model)
        return walker.params

    return _parse
