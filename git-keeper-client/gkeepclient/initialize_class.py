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
from subprocess_commands import CommandError, directory_exists, \
    create_directory, scp_file, home_dir_from_username


def initialize_class(class_name):
    try:
        config = GraderConfiguration(single_class_name=class_name)
    except ConfigurationError as e:
        sys.exit('Config error: {0}'.format(e))

    if class_name not in config.students_by_class:
        sys.exit('No student CSV file for {0}'.format(class_name))

    try:
        home_dir = home_dir_from_username(config.username, config.username,
                                          config.host)
    except CommandError as e:
        sys.exit('Error getting remote home dir for {0}:\n{1}'
                 .format(config.username, e))

    class_path = os.path.join(home_dir, class_name)

    if directory_exists(class_path, config.username, config.host):
        sys.exit('{0} already exists'.format(class_path))

    print('Initializing class', class_name, 'on', config.host)

    assignments_path = os.path.join(class_path, 'assignments')

    for dir_path in [class_path, assignments_path]:
        if directory_exists(dir_path, config.username, config.host):
            sys.exit('{0} already exists'.format(dir_path))
        try:
            create_directory(dir_path, config.username, config.host)
        except CommandError as e:
            sys.exit('Error creating {0}: {1}'.format(dir_path, e))

        print('Created', dir_path)

    try:
        remote_home_dir = home_dir_from_username(config.username,
                                                 config.username,
                                                 config.host)
        remote_config_dir = os.path.join(remote_home_dir, '.config/grader')

        scp_file(config.students_csv_filenames_by_class[class_name],
                 config.username, config.host, remote_config_dir)
    except CommandError as e:
        sys.exit('Error copying student file:\n{0}'.format(e))

    print('Copied', config.students_csv_filenames_by_class[class_name], 'to',
          class_path, 'on', config.host)

    print('Class', class_name, 'initialized on', config.host)
    print()
    print('Next, run populate_students.py on', config.host)
