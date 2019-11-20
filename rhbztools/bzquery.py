import argparse
import json
import logging

from rhbztools.bugzilla import Session, AuthError, AuthRequired
from rhbztools import bzql

LOG = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Query bugzilla')
    parser.add_argument('-f', '--field', action='append', type=str)
    parser.add_argument('-d', '--debug', action='count', default=0)
    parser.add_argument('query', type=str)
    opts = parser.parse_args()

    if opts.debug == 1:
        logging.basicConfig(level=logging.INFO)
    if opts.debug > 1:
        logging.basicConfig(level=logging.DEBUG)

    try:
        bz = Session()
    except (AuthRequired, AuthError) as ex:
        print(ex)
        return 1

    try:
        response = bz.query(opts.query, opts.field)
    except Exception as ex:
        print('Error fetching bugs: {msg}'.format(msg=str(ex)))
        return 1

    print(json.dumps(response))
