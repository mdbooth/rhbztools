import appdirs
import dataclasses
import json
import os.path
import requests

class AuthRequired(Exception):
    pass

class AuthError(Exception):
    pass

@dataclasses.dataclass(frozen=True)
class _Credentials:
    login: str
    api_key: str

class Session:
    def _auth_file(self):
        return os.path.join(appdirs.user_config_dir('rhbugzilla'), 'auth')

    @staticmethod
    def _read_auth(auth_file):
        try:
            with open(auth_file, 'r') as f:
                authdata = json.load(f)
            return _Credentials(**authdata)
        except FileNotFoundError:
            raise AuthRequired('Not logged in: {file} does not exist'
                                .format(file=auth_file))
        except json.decoder.JSONDecodeError as ex:
            msg = 'Error in authentication file {path}:\n{msg}'.format(
                    path=auth_file, msg=ex.msg)
            raise AuthError(msg)
        except TypeError:
            msg = ('Missing or extraneous data in authentication file '
                   '{path}'.format(path=auth_file))
            raise AuthError(msg)

    def _method(self, func, path, params=None, body=None):
        if params is None:
            params = {}
        params.update(dataclasses.asdict(self.creds))

        uri = 'https://bugzilla.redhat.com/rest/' + '/'.join(path)
        kwargs = {'params': params}
        if body is not None:
            kwargs['json'] = body

        return func(uri, **kwargs).json()

    def _get(self, path, params=None):
        return self._method(requests.get, path,
                            params=params)

    def _put(self, path, body, params=None):
        return self._method(requests.put, path,
                            params=params, body=body)

    def _validate_creds(self):
        resp = self._get(['valid_login'])

        if resp.get('error'):
            raise AuthRequired(resp.get('message'))

        if not resp.get('result'):
            raise AuthRequired('Invalid login details')

    def __init__(self):
        auth_file = self._auth_file()

        self.creds = self._read_auth(auth_file)
        self._validate_creds()

    def get_bug(self, bzid, fields=None):
        return self.get_bugs([bzid], fields=fields)

    def get_bugs(self, bzids, fields=None):
        params = {'id': ','.join((str(bzid) for bzid in bzids))}
        params.update(dataclasses.asdict(self.creds))
        if fields is not None:
            params['include_fields'] = ','.join(fields + ['id'])

        return self._get(['bug'], params)['bugs']

    def update_bug(self, bzid, values):
        return self._put(['bug', str(bzid)], body=values)

    def update_bugs(self, bzids, values):
        # NOTE(mdbooth): Upstream Buzilla documentation[1] suggests we can do
        # this in a single PUT call for multiple bugs. This would be more
        # efficient, but it fails with:
        #   A REST API resource was not found for 'PUT /bug'
        # It's possible RH Bugzilla is too old.
        # [1] https://bugzilla.readthedocs.io/en/latest/api/core/v1/bug.html#update-bug
        #body = {'ids': [int(bzid) for bzid in bzids]}
        #body.update(values)
        #return self._put(['bug'], body=body)

        for bzid in bzids:
            self.update_bug(bzid, values)
