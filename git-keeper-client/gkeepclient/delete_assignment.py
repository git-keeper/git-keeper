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
from time import strftime

from configuration import GraderConfiguration, ConfigurationError
from repository import Repository
from subprocess_commands import move_directory, CommandError, directory_exists,\
    create_directory


def trash_dest(trash_dir, source_path, timestamp, username=None):
    if username is not None:
        basename = '{0}-{1}-{2}'.format(timestamp,
                                        os.path.basename(source_path),
                                        username)
    else:
        basename = '{0}-{1}'.format(timestamp,
                                        os.path.basename(source_path))

    return os.path.join(trash_dir, basename)


def delete_assignment(class_name, assignment):

    timestamp = strftime('%Y-%m-%d-%H:%M:%S-%Z')

    try:
        config = GraderConfiguration(single_class_name=class_name)
    except ConfigurationError as e:
        sys.exit(e)

    if class_name not in config.students_by_class:
        sys.exit('class {0} does not exist'.format(class_name))

    if assignment not in config.get_assignments(class_name):
        sys.exit('assignment {0} not in class {1}'.format(assignment,
                                                          class_name))

    paths_source_dest = []

    grader_assignment_path = os.path.join(config.home_dir, class_name,
                                          'assignments', assignment)

    if not directory_exists(grader_assignment_path, ssh=config.ssh):
        sys.exit('{0} does not exist'.format(grader_assignment_path))

    trash_dir = os.path.join(config.home_dir, class_name, 'trash')

    if not directory_exists(trash_dir):
        create_directory(trash_dir, ssh=config.ssh)

    grader_assignment_dest = trash_dest(trash_dir, grader_assignment_path,
                                        timestamp)

    paths_source_dest.append((grader_assignment_path, grader_assignment_dest))

    for student in config.students_by_class[class_name]:
        student_repos = student.get_class_repositories(class_name)

        for repo in student_repos:
            assert isinstance(repo, Repository)
            if repo.assignment == assignment:
                student_source = repo.path
                student_dest = trash_dest(trash_dir, repo.path, timestamp,
                                          student.username)
                paths_source_dest.append((student_source, student_dest))

    print('These directories will be moved to the trash:')
    for source, dest in paths_source_dest:
        print('{0} -> {1}'.format(source, dest))

    answer = input('Proceed? Type yes to continue: ')

    answer = answer.strip()

    if answer.lower() != 'yes':
        sys.exit('Aborting')

    for source, dest in paths_source_dest:
        assert assignment in source
        try:
            move_directory(source, dest, ssh=config.ssh)
            print('moved {0}'.format(source))
        except CommandError as e:
            print('Error moving {0} to {1}:\n{2}'.format(source, dest, e))

