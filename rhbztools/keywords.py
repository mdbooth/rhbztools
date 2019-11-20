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

import re

class LineReader:
    # Lines to ignore
    IGNORE_RE = [re.compile(r) for r in (r'^#', r'^\s*$')]

    def __init__(self, path):
        super(LineReader, self).__init__()
        self.path = path

    def lines(self):
        with open(self.path, 'r') as f:
            for line in f:
                if any((r.match(line) for r in self.IGNORE_RE)):
                    continue

                yield line.strip()


class InvalidKeyword(Exception):
    pass


class Keywords:
    def __init__(self, keywords):
        super(Keywords, self).__init__()

        # A map of lower case constant keywords to their correct
        # spelling and capitalisations
        self.constants = {}

        for line in keywords.lines():
            words = line.split()
            keyword = words.pop(0)
            self._add_constant(keyword, words)

    def _add_constant(self, keyword, typos=None):
        if typos is None:
            typos = []

        self.constants[keyword.lower()] = keyword
        for typo in typos:
            self.constants[typo.lower()] = keyword

    def _to_canon(self, word):
        return self.constants.get(word.lower())

    def _to_canon_set(self, word_list):
        canon_set = set()
        for word in word_list:
            canon_word = self._to_canon(word)
            if canon_word is None:
                raise InvalidKeyword(word)
            canon_set.add(canon_word)

        return canon_set

    def updater(self, add=None, remove=None):
        add_set = set() if add is None else self._to_canon_set(add)
        remove_set = set() if remove is None else self._to_canon_set(remove)

        def _updater(orig):
            updated = False
            output = []

            for word in orig.split():
                canon_word = self._to_canon(word)

                # Ignore unrecognised words
                if canon_word is None:
                    output.append(word)
                    continue

                if canon_word in remove_set:
                    updated = True
                    continue

                if canon_word in add_set:
                    add_set.remove(canon_word)
                    output.append(canon_word)
                    updated = updated or (word != canon_word)
                    continue

                output.append(canon_word)
                updated = updated or (word != canon_word)

            for word in add_set:
                updated = True
                output.append(word)

            if not updated:
                return None

            return ' '.join(output)

        return _updater

    def update_string(self, orig, add=None, remove=None):
        updater = self.updater(add, remove)
        return updater(orig)
