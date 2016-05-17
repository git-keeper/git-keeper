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
from tempfile import TemporaryDirectory

from configuration import GraderConfiguration, ConfigurationError
from repository import Repository, copy_and_create_repo
from subprocess_commands import directory_exists, touch, CommandError,\
    chmod_world_writable_recursive, home_dir_from_username, scp_file

from student import Student


def upload_assignment(class_name, grader_project):

    grader_project_path = os.path.dirname(sys.argv[0])
    post_update_path = os.path.join(grader_project_path, 'post-update')

    local_assignment_dir = os.path.expanduser(grader_project)
    local_assignment_dir = os.path.abspath(local_assignment_dir)

    assignment = os.path.basename(local_assignment_dir.rstrip('/'))

    base_code_dir = os.path.join(local_assignment_dir, 'base_code')
    test_code_dir = os.path.join(local_assignment_dir, 'tests')

    if not os.path.isdir(base_code_dir):
        sys.exit('{0} does not exist'.format(base_code_dir))

    if not os.path.isdir(test_code_dir):
        sys.exit('{0} does not exist'.format(test_code_dir))

    action_file_path = os.path.join(test_code_dir, 'action.sh')

    if not os.path.isfile(action_file_path):
        sys.exit('No action.sh in {0}'.format(test_code_dir))

    email_file_path = os.path.join(local_assignment_dir, 'email.txt')

    if not os.path.isfile(email_file_path):
        sys.exit('{0} does not exist'.format(email_file_path))

    try:
        config = GraderConfiguration(single_class_name=class_name)
    except ConfigurationError as e:
        sys.exit(e)

    if class_name not in config.students_by_class:
        sys.exit('Class {0} does not exist'.format(class_name))

    base_code_repo_tempdir = TemporaryDirectory()

    try:
        base_code_repo = copy_and_create_repo(base_code_dir,
                                              base_code_repo_tempdir.name,
                                              assignment, 'created assignment')
    except CommandError as e:
        error = 'Error copying base code repo:\n{0}'.format(e)
        sys.exit(error)

    test_code_repo_tempdir = TemporaryDirectory()

    try:
        test_code_repo = copy_and_create_repo(test_code_dir,
                                              test_code_repo_tempdir.name,
                                              assignment)
    except CommandError as e:
        error = 'Error copying test code repo:\n{0}'.format(e)
        sys.exit(error)

    try:
        remote_home_dir = home_dir_from_username(config.username,
                                                 config.username,
                                                 config.host)
    except CommandError as e:
        sys.exit('Error getting remote home dir for {0}:\n{1}'
                 .format(config.username, e))

    remote_assignment_dir = os.path.join(remote_home_dir, class_name,
                                         'assignments', assignment)

    tests_bare_repo_dir = os.path.join(remote_assignment_dir,
                                       '{0}_tests.git'.format(assignment))
    reports_bare_repo_dir = os.path.join(remote_assignment_dir,
                                         '{0}_reports.git'.format(assignment))

    if directory_exists(tests_bare_repo_dir, config.username, config.host):
        sys.exit('{0} already exists on {1}'.format(tests_bare_repo_dir,
                                                    config.host))
    if directory_exists(reports_bare_repo_dir, config.username, config.host):
        sys.exit('{0} already exists on {1}'.format(reports_bare_repo_dir,
                                                    config.host))

    print('Uploading assignment', assignment)

    reports_repo_tempdir = TemporaryDirectory()
    reports_repo_dir = reports_repo_tempdir.name

    reports_repo = Repository(reports_repo_dir, assignment)
    reports_repo.init()

    for student in config.students_by_class[class_name]:
        assert isinstance(student, Student)
        bare_repo_dir = student.get_bare_repo_dir(class_name, assignment)
        if directory_exists(bare_repo_dir, config.username, config.host):
            sys.exit('{0} already exists on {1}'.format(bare_repo_dir,
                                                        config.host))
        student_repo = Repository(bare_repo_dir, assignment,
                                  is_local=False, is_bare=True,
                                  remote_user=config.username,
                                  remote_host=config.host,
                                  student_username=student.username)
        try:
            student_repo.init()
            student_repo.add_update_flag_hook(post_update_path)
            base_code_repo.push(student_repo)
            chmod_world_writable_recursive(student_repo.path,
                                           remote_user=config.username,
                                           remote_host=config.host)
            print('Pushed base code to', bare_repo_dir)
        except CommandError as e:
            sys.exit('Error creating {0} on {1}:\n{2}'.format(bare_repo_dir,
                                                              config.host, e))

        student_report_dir = os.path.join(reports_repo_dir,
                                          student.get_last_first_username())
        os.makedirs(student_report_dir)
        placeholder_path = os.path.join(student_report_dir, '.placeholder')
        touch(placeholder_path)

    reports_bare_repo = Repository(reports_bare_repo_dir, assignment,
                                   is_local=False, is_bare=True,
                                   remote_user=config.username,
                                   remote_host=config.host)

    try:
        reports_repo.add_all_and_commit('added student directories')
        reports_bare_repo.init()
        reports_repo.push(reports_bare_repo)
        print('Created reports repository in', reports_bare_repo_dir)
    except CommandError as e:
        sys.exit('Error creating reports repository:\n{0}'.format(e))

    tests_bare_repo = Repository(tests_bare_repo_dir, assignment,
                                 is_local=False, is_bare=True,
                                 remote_user=config.username,
                                 remote_host=config.host)

    try:
        tests_bare_repo.init()
        test_code_repo.push(tests_bare_repo)
        print('Pushed tests to', tests_bare_repo_dir)
    except CommandError as e:
        sys.exit('Error creating {0} on {1}\n{2}'.format(tests_bare_repo_dir,
                                                         test_code_dir, e))

    scp_file(email_file_path, config.username, config.host,
             remote_assignment_dir)

    print(assignment, 'uploaded successfully')
    print('Reports repo clone URL:', reports_bare_repo.url)
