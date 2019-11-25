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

import ddt
import fixtures
import json
import requests_mock
from urllib.parse import urlencode
import testtools
import types
from unittest import mock

from rhbztools import bugzilla

@ddt.ddt
class TestCreds(testtools.TestCase):
    def setUp(self):
        super(TestCreds, self).setUp()

        f = fixtures.MockPatch('rhbztools.bugzilla.open')
        self.mock_open = self.useFixture(f).mock

        # This testcase should never try to hit real bugzilla
        self.useFixture(fixtures.MockPatch('rhbztools.bugzilla.requests'))

    def test_no_auth_file(self):
        self.mock_open.side_effect = FileNotFoundError
        self.assertRaises(bugzilla.AuthRequired, bugzilla.Session)

    @ddt.data(
        # Invalid json
        '{',
        # Missing api key
        '{"login": "user@example.com"}',
        # Unknown field
        '{"login": "user@example.com", "api_key": "12345", "foo": "bar"}',
    )
    def test_auth_invalid_creds(self, auth_data):
        self.mock_open.side_effect = mock.mock_open(read_data=auth_data)
        self.assertRaises(bugzilla.AuthError, bugzilla.Session)


class _CredentialFileFixture(fixtures.Fixture):
    def setUp(self):
        super(_CredentialFileFixture, self).setUp()

        self.fake_creds = {'login': 'user@example.com',
                           'api_key': 'fake_api_key'}

        mock_open = mock.mock_open(read_data=json.dumps(self.fake_creds))
        f = fixtures.MonkeyPatch('rhbztools.bugzilla.open', mock_open)
        self.useFixture(f)


@requests_mock.Mocker()
class TestSessionValidation(testtools.TestCase):
    def setUp(self):
        super(TestSessionValidation, self).setUp()
        f = self.useFixture(_CredentialFileFixture())
        self.fake_creds = f.fake_creds

    def test_validate_ok(self, req):
        response = {'result': True}
        req.get('https://bugzilla.redhat.com/rest/valid_login?' +
                urlencode(self.fake_creds), text=json.dumps(response))

        bugzilla.Session()

    def test_validate_invalid_login(self, req):
        # Returned for a correct api_key and incorrect login
        response = {'result': False}
        req.get('https://bugzilla.redhat.com/rest/valid_login?' +
                urlencode(self.fake_creds), text=json.dumps(response))

        self.assertRaises(bugzilla.AuthRequired, bugzilla.Session)

    def test_validate_invalid_api_key(self, req):
        # Returned for an incorrect_api_key
        response = {
            'documentation': 'https://bugzilla.redhat.com/docs/en/html/api/index.html',
            'error': True,
            'code': 306,
            'message': ('The API key you specified is invalid. Please check '
                        'that you typed it correctly.')
        }
        req.get('https://bugzilla.redhat.com/rest/valid_login?' +
                urlencode(self.fake_creds), text=json.dumps(response))

        ex = self.assertRaises(bugzilla.AuthRequired, bugzilla.Session)
        self.assertEqual(response['message'], ex.args[0])


class TestSession(testtools.TestCase):
    def setUp(self):
        super(TestSession, self).setUp()

        f = self.useFixture(_CredentialFileFixture())
        self.fake_creds = f.fake_creds

        self.req = requests_mock.Mocker()
        self.addCleanup(self.req.stop)
        m = self.req.start()

        valid_login_response = {'result': True}
        self.req.get('https://bugzilla.redhat.com/rest/valid_login?' +
                     urlencode(self.fake_creds),
                     text=json.dumps(valid_login_response))

    def _find_req_for_path(self, path):
        return next((req for req in self.req.request_history
                     if req.path == path), None)

    def _assert_query_match(self, query, qs):
        self.assertListEqual(sorted(query.keys()), sorted(qs.keys()))

        for key, value in query.items():
            if not isinstance(value, list):
                value = [value]

            self.assertListEqual(list(value), list(qs[key]))

    def test_bugs_single(self):
        query = dict(id='12345', **self.fake_creds)
        expected_url = ('https://bugzilla.redhat.com/rest/bug?' +
                        urlencode(query))
        self.req.get(expected_url, text=json.dumps({'bugs': ['fake_bug']}))

        session = bugzilla.Session()
        r = session.get_bug(12345)

        req = self._find_req_for_path('/rest/bug')
        self.assertIsNotNone(req)
        self._assert_query_match(query, req.qs)
        self.assertIsInstance(r, types.GeneratorType)
        self.assertListEqual(['fake_bug'], list(r))

    def test_bugs_multiple(self):
        query = dict(id='1,2,3,4,5', **self.fake_creds)
        expected_url = ('https://bugzilla.redhat.com/rest/bug?' +
                        urlencode(query))
        self.req.get(expected_url, text=json.dumps({'bugs': ['fake_bug']}))

        session = bugzilla.Session()
        r = session.get_bugs([1, 2, 3, 4, 5])

        req = self._find_req_for_path('/rest/bug')
        self.assertIsNotNone(req)
        self._assert_query_match(query, req.qs)
        self.assertIsInstance(r, types.GeneratorType)
        self.assertListEqual(['fake_bug'], list(r))

    def test_bugs_include_fields(self):
        query = dict(id='1,2,3,4,5',
                     include_fields='cf_internal_whiteboard,id',
                     **self.fake_creds)
        expected_url = ('https://bugzilla.redhat.com/rest/bug?' +
                        urlencode(query))
        self.req.get(expected_url, text=json.dumps({'bugs': ['fake_bug']}))

        session = bugzilla.Session()
        r = session.get_bugs([1, 2, 3, 4, 5], fields=['cf_internal_whiteboard'])

        bug_req = next((req for req in self.req.request_history
                        if req.path == '/rest/bug'))
        self._assert_query_match(query, bug_req.qs)
        self.assertIsInstance(r, types.GeneratorType)
        self.assertListEqual(['fake_bug'], list(r))

    # NOTE(mdbooth): This tests the multiple bugs version of PUT, which RHBZ
    # doesn't seem to support
    def _test_update_bug_single(self):
        self.req.put('https://bugzilla.redhat.com/rest/bug',
                     text=json.dumps('fake_response'))
        session = bugzilla.Session()
        r = session.update_bug('12345', {'cf_internal_whiteboard': 'test'})

        bug_req = next((req for req in self.req.request_history
                        if req.path == '/rest/bug'))
        self.assertDictEqual(
                {'cf_internal_whiteboard': 'test', 'ids': [12345]},
                bug_req.json())
        self.assertEqual(r, 'fake_response')

    # NOTE(mdbooth): This tests the multiple bugs version of PUT, which RHBZ
    # doesn't seem to support
    def _test_update_bug_multiple(self):
        self.req.put('https://bugzilla.redhat.com/rest/bug',
                     text=json.dumps('fake_response'))
        session = bugzilla.Session()
        r = session.update_bugs([1, 2, 3, 4, 5],
                                {'cf_internal_whiteboard': 'test'})

        bug_req = next((req for req in self.req.request_history
                        if req.path == '/rest/bug'))
        self.assertDictEqual(
                {'cf_internal_whiteboard': 'test', 'ids': [1, 2, 3, 4, 5]},
                bug_req.json())
        self.assertEqual(r, 'fake_response')

    def test_update_bug_single(self):
        self.req.put('https://bugzilla.redhat.com/rest/bug/12345',
                        text=json.dumps('fake_response'))
        session = bugzilla.Session()
        r = session.update_bug('12345', {'cf_internal_whiteboard': 'test'})

        bug_req = next((req for req in self.req.request_history
                        if req.path == '/rest/bug/12345'))
        self.assertDictEqual(
                {'cf_internal_whiteboard': 'test'},
                bug_req.json())
        self.assertEqual(r, 'fake_response')
