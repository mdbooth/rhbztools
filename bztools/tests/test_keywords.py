import contextlib
import unittest
import unittest.mock

from bztools import keywords

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

    @unittest.mock.patch('bztools.keywords.open')
    def test_lines(self, mock_open):
        mock_open.side_effect = \
                unittest.mock.mock_open(read_data='\n'.join(self.FIXTURE))

        reader = keywords._LineReader('foo')
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
