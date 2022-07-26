# Copyright 2017 Nathan Sommer
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
Provides functionality for easily pushing a solution to the server for testing.
"""

import os
from tempfile import TemporaryDirectory

from gkeepclient.client_configuration import config
from gkeepclient.client_function_decorators import config_parsed, \
    server_interface_connected, class_exists, assignment_exists
from gkeepclient.server_actions import trigger_tests
from gkeepclient.server_interface import server_interface
from gkeepcore.git_commands import git_clone_remote, git_add_all, git_commit, \
    git_push, git_unstaged_changes_exist
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.system_commands import cp, rm


@config_parsed
@server_interface_connected
@class_exists
@assignment_exists
def test_solution(class_name: str, assignment_name: str, solution_path: str):
    """
    Push a faculty solution to the server for testing.

    Creates a temporary directory into which it clones the current assignment
    repository and copies the solution directory to test. The .git folder from
    the cloned directory is copied into the solution directory, all files are
    added to the repository, the changes are committed and pushed.

    :param class_name: name of the class the assignment belongs to
    :param assignment_name: name of the assignment
    :param solution_path: path to the solution directory
    """

    if not os.path.isdir(solution_path):
        error = '{} is not a directory'.format(solution_path)
        raise GkeepException(error)

    print('Testing solution {} for assignment {} in class {}'
          .format(solution_path, assignment_name, class_name))

    solution_base_name = os.path.basename(os.path.normpath(solution_path))

    temp_dir = TemporaryDirectory()

    solution_temp_path = os.path.join(temp_dir.name, solution_base_name)

    cp(solution_path, solution_temp_path, recursive=True)

    repo_temp_path = os.path.join(temp_dir.name, 'clone')

    server_home_dir = server_interface.my_home_dir()
    server_username = config.server_username

    remote_repo_path = os.path.join(server_home_dir, server_username,
                                    class_name, assignment_name) + '.git'

    clone_url = '{}@{}:{}'.format(server_username, config.server_host,
                                  remote_repo_path)

    git_clone_remote(clone_url, repo_temp_path)

    if os.path.isdir(os.path.join(solution_temp_path, '.git')):
        rm(os.path.join(solution_temp_path, '.git'), recursive=True)

    cp(os.path.join(repo_temp_path, '.git'), solution_temp_path,
       recursive=True)

    if git_unstaged_changes_exist(solution_temp_path):
        git_add_all(solution_temp_path)
        git_commit(solution_temp_path, 'Testing')
        print('Pushing your solution using git')
        git_push(solution_temp_path, force=True)
        print('Solution pushed successfully, you should receive a report '
              'via email')
    else:
        print('Solution is up to date with remote, using gkeep trigger to '
              'trigger tests')
        trigger_tests(class_name, assignment_name, [server_username], yes=True)
        print('You should receive a report via email')
