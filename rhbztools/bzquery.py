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

import argparse
import json
import logging
import yaml

from rhbztools.bugzilla import Session, AuthError, AuthRequired
from rhbztools import bzql

LOG = logging.getLogger(__name__)


class CommaListArg(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        listarg = getattr(namespace, self.dest)
        if listarg is None:
            listarg = []
            setattr(namespace, self.dest, listarg)

        listarg.extend(values.split(','))

def main():
    parser = argparse.ArgumentParser(description='Query bugzilla')
    parser.add_argument('-f', '--field', action=CommaListArg, type=str)
    parser.add_argument('-d', '--debug', action='count', default=0)
    parser.add_argument('-q', '--queryfile')
    parser.add_argument('query', type=str)
    opts = parser.parse_args()

    if opts.debug == 1:
        logging.basicConfig(level=logging.INFO)
    if opts.debug > 1:
        logging.basicConfig(level=logging.DEBUG)

    queries = {}
    if opts.queryfile is not None:
        try:
            with open(opts.queryfile, 'r') as queryfile:
                queries = yaml.safe_load(queryfile)
        except Exception as ex:
            parser.error('Unable to read queries from {path}: {msg}'.format(
                            path=parser.queryfile, msg=str(ex)))

    if opts.query in queries:
        query = queries[opts.query]
    else:
        query = opts.query

    try:
        bz = Session()
    except (AuthRequired, AuthError) as ex:
        print(ex)
        return 1

    try:
        response = bz.query(query, opts.field)
    except Exception as ex:
        print('Error fetching bugs: {msg}'.format(msg=str(ex)))
        return 1

    print(json.dumps(list(response)))
