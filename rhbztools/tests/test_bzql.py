import ddt
import testtools

import tatsu.exceptions

from rhbztools import bzql

@ddt.ddt
class TestBZQL(testtools.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestBZQL, self).__init__(*args, **kwargs)

        self.parser = bzql.parser()

    def setUp(self):
        super(TestBZQL, self).setUp()

    @ddt.data(
        ('classification == "Red Hat"',
         {'f0': 'classification', 'o0': 'equals', 'v0': 'Red Hat'}),
        ('classification == "Red Hat" and product == "Red Hat OpenStack"',
         {'f0': 'classification', 'o0': 'equals', 'v0': 'Red Hat',
          'f1': 'product', 'o1': 'equals', 'v1': 'Red Hat OpenStack'}),
        ('classification == "Red Hat" and product == "Red Hat OpenStack" and '
            'component == "openstack-nova"',
         {'f0': 'classification', 'o0': 'equals', 'v0': 'Red Hat',
          'f1': 'product', 'o1': 'equals', 'v1': 'Red Hat OpenStack',
          'f2': 'component', 'o2': 'equals', 'v2': 'openstack-nova'}),
        ('classification == "Red Hat" or product == "Red Hat OpenStack"',
         {'j_top': 'OR',
          'f0': 'classification', 'o0': 'equals', 'v0': 'Red Hat',
          'f1': 'product', 'o1': 'equals', 'v1': 'Red Hat OpenStack'}),
        ('classification == "Red Hat" or product == "Red Hat OpenStack" or '
            'component == "openstack-nova"',
         {'j_top': 'OR',
          'f0': 'classification', 'o0': 'equals', 'v0': 'Red Hat',
          'f1': 'product', 'o1': 'equals', 'v1': 'Red Hat OpenStack',
          'f2': 'component', 'o2': 'equals', 'v2': 'openstack-nova'}),
        ('classification == "Red Hat" and product == "Red Hat OpenStack" or '
            'component == "openstack-nova"',
         {'j_top': 'OR',
          'f0': 'OP',
          'f1': 'classification', 'o1': 'equals', 'v1': 'Red Hat',
          'f2': 'product', 'o2': 'equals', 'v2': 'Red Hat OpenStack',
          'f3': 'CP',
          'f4': 'component', 'o4': 'equals', 'v4': 'openstack-nova'}),
        ('classification == "Red Hat" or product == "Red Hat OpenStack" and '
            'component == "openstack-nova"',
         {'j_top': 'OR',
          'f0': 'classification', 'o0': 'equals', 'v0': 'Red Hat',
          'f1': 'OP',
          'f2': 'product', 'o2': 'equals', 'v2': 'Red Hat OpenStack',
          'f3': 'component', 'o3': 'equals', 'v3': 'openstack-nova',
          'f4': 'CP'}),
        ('classification == "Red Hat" or (product == "Red Hat OpenStack" and '
            'component == "openstack-nova")',
         {'j_top': 'OR',
          'f0': 'classification', 'o0': 'equals', 'v0': 'Red Hat',
          'f1': 'OP',
          'f2': 'product', 'o2': 'equals', 'v2': 'Red Hat OpenStack',
          'f3': 'component', 'o3': 'equals', 'v3': 'openstack-nova',
          'f4': 'CP'}),
        ('(classification == "Red Hat" or product == "Red Hat OpenStack") and '
            'component == "openstack-nova"',
         {'f0': 'OP', 'j0': 'OR',
          'f1': 'classification', 'o1': 'equals', 'v1': 'Red Hat',
          'f2': 'product', 'o2': 'equals', 'v2': 'Red Hat OpenStack',
          'f3': 'CP',
          'f4': 'component', 'o4': 'equals', 'v4': 'openstack-nova'}),
    )
    @ddt.unpack
    def test_structure(self, query, expected):
        params = self.parser(query)
        self.assertEqual(expected, params)

    @ddt.data(
        ('not classification == "Red Hat"',
         {'n0': 1, 'f0': 'classification', 'o0': 'equals', 'v0': 'Red Hat'}),
        ('not (classification == "Red Hat" and product == "Red Hat OpenStack")',
         {'f0': 'OP', 'n0': 1,
          'f1': 'classification', 'o1': 'equals', 'v1': 'Red Hat',
          'f2': 'product', 'o2': 'equals', 'v2': 'Red Hat OpenStack',
          'f3': 'CP'}),
        ('! classification == "Red Hat"',
         {'n0': 1, 'f0': 'classification', 'o0': 'equals', 'v0': 'Red Hat'}),
        ('! (classification == "Red Hat" and product == "Red Hat OpenStack")',
         {'f0': 'OP', 'n0': 1,
          'f1': 'classification', 'o1': 'equals', 'v1': 'Red Hat',
          'f2': 'product', 'o2': 'equals', 'v2': 'Red Hat OpenStack',
          'f3': 'CP'}),
    )
    @ddt.unpack
    def test_negation(self, query, expected):
        params = self.parser(query)
        self.assertEqual(expected, params)

    @ddt.data(
        ('equals', '==', '0', 0),
        ('notequals', '!=', '0', 0),
        ('anyexact', 'in', '["foo"]', 'foo'),
        ('regexp', '~', '"foo"', 'foo'),
        ('notregexp', '!~', '"foo"', 'foo'),
        ('lessthan', '<', '0', 0),
        ('lessthaneq', '<=', '0', 0),
        ('greaterthan', '>', '0', 0),
        ('greaterthaneq', '>=', '0', 0),
    )
    @ddt.unpack
    def test_specialops(self, real_op, alt_op, val, rendered_val):
        query = 'status {op} {value}'
        expected = {'f0': 'status', 'o0': real_op, 'v0': rendered_val}

        for op in (real_op, alt_op):
            params = self.parser(query.format(op=op, value=val))
            self.assertEqual(expected, params)

    @ddt.data(
        'equals',
        'notequals',
        'substring',
        'casesubstring',
        'notsubstring',
        'changedfrom',
        'changedto',
        'changedby',
        'matches',
        'notmatches',
    )
    def test_scalarops(self, op):
        query = [
            'status {op} "foo"',
            'status {op} 1',
            'status {op} 23.45',
        ]

        expected = [
            {'f0': 'status', 'o0': op, 'v0': "foo"},
            {'f0': 'status', 'o0': op, 'v0': 1},
            {'f0': 'status', 'o0': op, 'v0': 23.45},
        ]

        for (q, e) in zip(query, expected):
            params = self.parser(q.format(op=op))
            self.assertEqual(e, params)

        failquery = 'status {op} ["foo"]'.format(op=op)
        self.assertRaises(tatsu.exceptions.ParseError, self.parser, failquery)

    @ddt.data(
        'anyexact',
        'anywordssubstr',
        'allwordssubstr',
        'nowordssubstr',
        'anywords',
        'nowords',
    )
    def test_listofscalarops(self, op):
        successval = '[0, 1.2, "foo"]'
        query = 'cf_internal_whiteboard {op} {value}'
        expected = {
            'f0': 'cf_internal_whiteboard', 'o0': op, 'v0': "0, 1.2, foo"}

        params = self.parser(query.format(op=op, value=successval))
        self.assertEqual(expected, params)

        for failvalue in (0, 12.34, '"foo"'):
            self.assertRaises(tatsu.exceptions.ParseError, self.parser,
                              query.format(op=op, value=failvalue))

    @ddt.data(
        'listofbugs',
    )
    def test_listofintops(self, op):
        successval = '[0, 1, 2]'
        query = 'cf_internal_whiteboard {op} {value}'
        expected = {
            'f0': 'cf_internal_whiteboard', 'o0': op, 'v0': "0, 1, 2"}

        params = self.parser(query.format(op=op, value=successval))
        self.assertEqual(expected, params)

        for failvalue in (0, 12.34, '"foo"', '[0, 12.34]', '[0, "foo"]'):
            self.assertRaises(tatsu.exceptions.ParseError, self.parser,
                              query.format(op=op, value=failvalue))

    @ddt.data(
        # At least for now we're requiring regexps and times to be strings
        'regexp',
        'notregexp',
        'changedbefore',
        'changedafter',
    )
    def test_stringops(self, op):
        successval = '"foo"'
        query = 'status {op} {value}'

        expected = {'f0': 'status', 'o0': op, 'v0': "foo"}

        params = self.parser(query.format(op=op, value=successval))
        self.assertEqual(expected, params)

        for failval in ('0', '12.34', '["foo"]'):
            self.assertRaises(tatsu.exceptions.ParseError, self.parser,
                              query.format(op=op, value=failval))

    @ddt.data(
        'isempty',
        'isnotempty',
    )
    def test_unaryops(self, op):
        successval = ''
        query = 'status {op} {value}'

        expected = {'f0': 'status', 'o0': op}

        params = self.parser(query.format(op=op, value=successval))
        self.assertEqual(expected, params)

        for failval in ("foo", '0', '12.34', '["foo"]'):
            self.assertRaises(tatsu.exceptions.ParseError, self.parser,
                              query.format(op=op, value=failval))

    def test_compound_fieldname(self):
        query = 'flagtypes.name substring "rhos-17.0"'
        expected = {'f0': 'flagtypes.name', 'o0': 'substring',
                    'v0': 'rhos-17.0'}

        params = self.parser(query)
        self.assertEqual(expected, params)
