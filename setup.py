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

from setuptools import setup

setup(
    name = 'rhbztools',
    version = '0.1',
    packages = ['rhbztools'],
    python_requires = '>=3.7',
    install_requires = [
        'appdirs',
        'requests',
        'tatsu',
    ],
    entry_points = {
        'console_scripts': [
            'bzdevelwb = rhbztools.bzdevelwb:main',
            'bzquery = rhbztools.bzquery:main',
        ]
    },
    include_package_data=True,
    test_suite = 'rhbztools.tests.all_tests',
    tests_require = ['testtools', 'requests-mock', 'ddt'],
)
