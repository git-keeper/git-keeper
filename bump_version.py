#!/usr/bin/env python3
#
# Copyright 2018 Nathan Sommer and Ben Coleman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
This script writes a new version number to the version.py files in all three
of the main packages.

Before running this script, place the new version number in the file named
VERSION.

The version string must have the form MAJOR.MINOR.PATCH as detailed in Semantic
Versioning 2.0:  https://semver.org/
"""


import argparse
import os

from distutils.version import StrictVersion

import sys


package_paths = (
    'git-keeper-client/gkeepclient',
    'git-keeper-core/gkeepcore',
    'git-keeper-server/gkeepserver',
)


def main():
    if not os.path.isfile('VERSION'):
        sys.exit('VERSION does not exist')

    version = None

    try:
        with open('VERSION') as f:
            version = f.read().strip()
    except OSError as e:
        error = 'Error reading VERSION: {}'.format(e)
        sys.exit(error)

    try:
        strict_version = StrictVersion(version)
    except ValueError:
        sys.exit('{} is not a valid version string'.format(version))

    print('Updating version to', version)

    file_text = \
'''# This file was generated automatically and should not be edited manually.
# Instead, edit the VERSION file in the top level directory of the git-keeper
# project and then run bump_version.py.

__version__ = '{}'
'''.format(version)

    for package_path in package_paths:
        version_file_path = os.path.join(package_path, 'version.py')

        try:
            with open(version_file_path, 'w') as f:
                f.write(file_text)
            print('Wrote', version_file_path)
        except OSError as e:
            error = 'Error opening {}: {}'.format(version_file_path, e)
            sys.exit(error)

    print('Version updated successfully')


if __name__ == '__main__':
    main()
