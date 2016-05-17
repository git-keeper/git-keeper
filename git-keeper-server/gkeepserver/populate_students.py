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

# This script is to be run on the grading server AFTER initialize_class.py has
# been run

import os
import sys

from configuration import GraderConfiguration, ConfigurationError
from subprocess_commands import CommandError, user_exists, create_user,\
    home_dir_from_username, chown, create_directory, chmod, directory_exists

from student import Student


def y_or_n(prompt):
    user_input = ''
    while user_input != 'y' and user_input != 'n':
        user_input = input(prompt)
        user_input = user_input.strip().lower()

    return user_input == 'y'


def populate_students(class_name):

    try:
        config = GraderConfiguration(on_grading_server=True)
    except ConfigurationError as e:
        sys.exit('Config error: {0}'.format(e))

    home_dir = home_dir_from_username(config.username)

    grader_class_path = os.path.join(home_dir, class_name)

    if not directory_exists(grader_class_path):
        sys.exit('{0} does not exist.\nClass appears to be uninitialized.'
                 .format(grader_class_path))

    print('Creating student directories for class', class_name)

    students = config.students_by_class[class_name]

    if len(students) == 0:
        sys.exit('No students found for class {0}'.format(class_name))

    create_users = False
    for student in students:
        assert isinstance(student, Student)
        if not user_exists(student.username):
            if not create_users:
                print('User', student.username, 'does not exist')
                if y_or_n('Create nonexistent users? (y/n) '):
                    create_users = True
            if create_users:
                try:
                    create_user(student.username)
                    home_dir = home_dir_from_username(student.username)
                    chown(home_dir, student.username, config.group)
                    chmod(home_dir, '770', sudo=True)
                    print('Created user', student.username)
                except CommandError as e:
                    sys.exit('Error creating user {0}:\n{1}'
                             .format(student.username, e))
            else:
                sys.exit('Not creating users, exiting')

        home_dir = home_dir_from_username(student.username)

        student_class_path = os.path.join(home_dir, class_name)

        if directory_exists(student_class_path):
            print('{0} already exists, skipping'.format(student_class_path))
            continue

        try:
            create_directory(student_class_path)
            chmod(student_class_path, '775')
            print('Created', student_class_path)
        except OSError as e:
            error = 'Error creating {0}: {1}'.format(student_class_path, e)
            sys.exit(error)

    print('Student directories created successfully')
    print('You may now start the grader daemon')
