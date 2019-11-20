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
import unittest
import unittest.mock

from rhbztools import keywords

class TestLineReader(unittest.TestCase):
    FIXTURE = [
        '# Some comments',
        '#',
        '# ',
        '',
        'Line 1',
        ' ',
        'Line 2      ',
        '  ',
        '# Interspersed comment',
        '       Line 3  ',
        '',
    ]

    @unittest.mock.patch('rhbztools.keywords.open')
    def test_lines(self, mock_open):
        mock_open.side_effect = \
                unittest.mock.mock_open(read_data='\n'.join(self.FIXTURE))

        reader = keywords.LineReader('foo')
        lines = list(reader.lines())
        self.assertListEqual(lines, ['Line 1', 'Line 2', 'Line 3'])
        mock_open.assert_called_once_with('foo', 'r')

class TestKeywords(unittest.TestCase):
    KEYWORDS_FIXTURE = [
        'QENotRequired noqe',
        'BlockedHardware hardware',
        'BlockedOtherDFG otherDFG'
    ]

    def setUp(self):
        super(TestKeywords, self).setUp()

        keywords_file = unittest.mock.MagicMock()
        keywords_file.lines.return_value = iter(self.KEYWORDS_FIXTURE)

        self.keywords = keywords.Keywords(keywords_file)

    def test_all(self):
        def _run_tests(tests, add, remove):
            for before, after in tests:
                updated = self.keywords.update_string(before, add, remove)
                self.assertEqual(after, updated)

        add = ['QENotRequired']
        remove = ['BlockedHardware']
        tests = [
            ('QENotRequired', None),
            ('', 'QENotRequired'),
            ('BlockedHardware', 'QENotRequired'),
            ('qenotrequired', 'QENotRequired'),
            ('Hardware', 'QENotRequired'),
            ('BlockedOtherDFG BlockedHardware QENotRequiredFoo',
             'BlockedOtherDFG QENotRequiredFoo QENotRequired'),
        ]
        _run_tests(tests, add, remove)

        add = ['noqe']
        remove = []
        tests = [
            ('', 'QENotRequired'),
            ('qenotrequired', 'QENotRequired'),
            ('hardware', 'BlockedHardware QENotRequired'),
        ]
        _run_tests(tests, add, remove)

        add = []
        remove = ['QENotRequired']
        tests = [
            ('', None),
            ('hardware', 'BlockedHardware'),
            ('QENotRequired', ''),
            ('QEnotrequired', ''),
            ('QENotRequired hardware unrelated', 'BlockedHardware unrelated'),
        ]
        _run_tests(tests, add, remove)

        add = ['unicorns']
        with self.assertRaises(keywords.InvalidKeyword):
            self.keywords.update_string('', add, [])
