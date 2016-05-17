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
from paramiko.client import SSHClient
from repository import Repository
from subprocess_commands import CommandError, home_dir_from_username,\
    directory_exists
from upload_assignment import copy_and_create_repo


def update_assignment_tests(class_name, local_assignment_dir):

    local_assignment_dir = os.path.expanduser(local_assignment_dir)
    local_assignment_dir = os.path.abspath(local_assignment_dir)

    assignment = os.path.basename(local_assignment_dir.rstrip('/'))

    test_code_dir = os.path.join(local_assignment_dir, 'tests')

    if not os.path.isdir(test_code_dir):
        sys.exit('{0} does not exist'.format(test_code_dir))

    action_file_path = os.path.join(test_code_dir, 'action.sh')

    if not os.path.isfile(action_file_path):
        sys.exit('No action.sh in {0}'.format(test_code_dir))

    try:
        config = GraderConfiguration(single_class_name=class_name)
    except ConfigurationError as e:
        sys.exit(e)

    try:
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(config.host, username=config.username)
    except OSError as e:
        sys.exit('Error opening SSH connection:\n{0}'.format(e))

    if class_name not in config.students_by_class:
        sys.exit('Class {0} does not exist'.format(class_name))

    test_code_repo_tempdir = TemporaryDirectory()

    try:
        test_code_repo = copy_and_create_repo(test_code_dir,
                                              test_code_repo_tempdir.name,
                                              assignment)
    except CommandError as e:
        error = 'Error copying test code repo:\n{0}'.format(e)
        sys.exit(error)

    try:
        remote_home_dir = home_dir_from_username(config.username, ssh=ssh)

    except CommandError as e:
        sys.exit('Error getting remote home dir for {0}:\n{1}'
                 .format(config.username, e))

    remote_assignment_dir = os.path.join(remote_home_dir, class_name,
                                         'assignments', assignment)

    tests_bare_repo_dir = os.path.join(remote_assignment_dir,
                                       '{0}_tests.git'.format(assignment))

    if not directory_exists(tests_bare_repo_dir, ssh=ssh):
        sys.exit('{0} does not exist on {1}'.format(tests_bare_repo_dir,
                                                    config.host))

    print('Updating test repo for assignment', assignment)

    tests_bare_repo = Repository(tests_bare_repo_dir, assignment,
                                 is_local=False, is_bare=True,
                                 remote_host=config.host,
                                 remote_user=config.username)

    try:
        test_code_repo.push(tests_bare_repo, force=True)
        print('Pushed tests to', tests_bare_repo_dir)
    except CommandError as e:
        sys.exit('Error pushing test repo:\n{0}'.format(e))

    print(assignment, 'tests updated successfully')


if __name__ == '__main__':
    main(sys.argv)
