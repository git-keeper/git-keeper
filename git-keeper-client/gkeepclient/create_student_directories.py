#!/usr/bin/env python3

# Copyright 2016 Nathan Sommer and Ben Coleman
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

import os
import sys

from configuration import GraderConfiguration, ConfigurationError
from subprocess_commands import directory_exists


def create_student_directories(class_name, parent_dir):

    if not directory_exists(parent_dir):
        try:
            os.makedirs(parent_dir)
        except OSError as e:
            sys.exit('Error creating{0}:\n{1}'.format(parent_dir, e))

    try:
        config = GraderConfiguration(single_class_name=class_name)
    except ConfigurationError as e:
        sys.exit(e)

    if class_name not in config.students_by_class:
        sys.exit('class {0} does not exist'.format(class_name))

    for student in config.students_by_class[class_name]:
        path = os.path.join(parent_dir, student.get_last_first_username())

        if directory_exists(path):
            print('{0} already exists, skipping'.format(path))
            continue

        try:
            os.makedirs(path)
        except OSError as e:
            print('Error creating {0}:\n{1}'.format(path, e))
