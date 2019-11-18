import argparse
from collections import defaultdict
import logging

from bztools.bugzilla import Session, AuthError, AuthRequired
from bztools.keywords import Keywords, LineReader, InvalidKeyword

LOG = logging.getLogger(__name__)

DEV_WHITEBOARD = 'cf_devel_whiteboard'

def update_devel_whiteboard(bz, bzids, updater):
    updates = defaultdict(list)
    bugs = bz.get_bugs(bzids, fields=[DEV_WHITEBOARD])
    for bug in bugs:
        bzid = bug['id']
        dev_whiteboard = bug[DEV_WHITEBOARD]
        LOG.info('Bug {bzid} dev whiteboard: {wb}'.format(
                    bzid=bzid, wb=dev_whiteboard))

        updated = updater(dev_whiteboard)
        if updated is None:
            LOG.info('Bug {bzid} no change'.format(bzid=bzid))
            continue
        else:
            LOG.info('Bug {bzid} will update to {wb}'.format(
                        bzid=bzid, wb=updated))

        updates[updated].append(bzid)

    LOG.info('Updates: {updates}'.format(updates=updates))

    for (update, bzids) in updates.items():
        LOG.info('Updating devel_whiteboard on {bzids} to {update}'.format(
                    bzids=bzids, update=update))

        bz.update_bugs(bzids, {DEV_WHITEBOARD: update})

def main():
    parser = argparse.ArgumentParser(
        description='Update keywords in BZ Devel Whiteboard')
    parser.add_argument('-a', '--add', type=str, nargs='+')
    parser.add_argument('-r', '--remove', type=str, nargs='+')
    parser.add_argument('-k', '--keywords', type=str, required=True)
    parser.add_argument('-d', '--debug', action='count', default=0)
    parser.add_argument('bzids', type=int, nargs='+')
    opts = parser.parse_args()

    if opts.debug == 1:
        logging.basicConfig(level=logging.INFO)
    if opts.debug > 1:
        logging.basicConfig(level=logging.DEBUG)

    try:
        reader = LineReader(opts.keywords)
        keywords = Keywords(reader)
        updater = keywords.updater(opts.add, opts.remove)
    except OSError as ex:
        parser.error("Error reading keywords file: {msg}".format(msg=str(ex)))
    except InvalidKeyword as ex:
        parser.error("Invalid keyword: {word}".format(word=str(ex)))

    try:
        bz = Session()
    except (AuthRequired, AuthError) as ex:
        print(ex)
        return 1

    update_devel_whiteboard(bz, opts.bzids, updater)
