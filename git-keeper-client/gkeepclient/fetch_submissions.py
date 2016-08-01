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

from gkeepclient.client_configuration import config
from gkeepclient.client_function_decorators import config_parsed, \
    server_interface_connected, class_exists
from gkeepclient.server_interface import server_interface
from gkeepclient.text_ui import confirmation
from gkeepcore.git_commands import git_clone, is_non_bare_repo, git_head_hash, \
    git_pull
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import student_assignment_repo_path, \
    faculty_assignment_dir_path
from gkeepcore.student import Student


def clone_repo(local_repo_path, remote_url):
    """
    Clone a remote repository.

    :param local_repo_path: clone destination
    :param remote_url: git clone URL
    """

    print('Cloning {0} to {1} ... '
          .format(remote_url, local_repo_path), end='')
    sys.stdout.flush()

    try:
        git_clone(remote_url, local_repo_path)
        print('success!')
    except GkeepException as e:
        print('error cloning')


def pull_repo_if_updated(local_repo_path, remote_repo_path, remote_url):
    """
    Perform a git pull in a git repository if the remote has changed since
    the last pull.

    :param local_repo_path: path to the local repository
    :param remote_repo_path: path to the remote repostiroy
    :param remote_url: git clone URL
    """

    if not is_non_bare_repo(local_repo_path):
        print('{0} exists but is not a git repository'
              .format(local_repo_path))
        return

    # get the hash of the HEAD of the local repository
    try:
        local_head_hash = git_head_hash(local_repo_path)
    except GkeepException as e:
        print('Error reading local git repository {0}'
              .format(local_repo_path))
        return

    # get the hash of the HEAD of the remote repository
    try:
        remote_head_hash = server_interface.git_head_hash(remote_repo_path)
    except GkeepException as e:
        print('Error reading remote git repository {0}'
              .format(remote_repo_path))
        return

    # no need to pull if the hashes are the same
    if local_head_hash == remote_head_hash:
        return

    print('Pulling new content in {0} ... '.format(local_repo_path), end='')
    sys.stdout.flush()

    try:
        git_pull(local_repo_path, remote_url)
        print('success!')
    except GkeepException as e:
        print(str(e))


def build_clone_url(path):
    return ('ssh://{0}@{1}:{2}/{3}'
            .format(config.server_username, config.server_host,
                    config.server_ssh_port, path))


def fetch_student_submission(class_name: str, assignment_name: str,
                             student: Student,
                             assignment_submission_path: str):
    """
    Fetch a student's submission for an assignment.

    Clone the repo if it has not yet been cloned.

    If the repo has been cloned, check to see if the server repo has any new
    commits and pull if so.

    :param class_name: name of the class
    :param assignment_name: name of the assignment
    :param student: Student object representing the student
    :param assignment_submission_path: path to the directory containing the
     assignment's submissions
    """

    # name of the directory to store the student's submission in
    last_first_username = student.get_last_first_username()

    student_submission_path = os.path.join(assignment_submission_path,
                                           last_first_username)

    # paths on the server
    student_home_dir = server_interface.user_home_dir(student.username)
    remote_repo_path = student_assignment_repo_path(config.server_username,
                                                    class_name,
                                                    assignment_name,
                                                    student_home_dir)

    remote_git_url = build_clone_url(remote_repo_path)

    # pull if the repo already exists, clone otherwise
    if os.path.isdir(student_submission_path):
        pull_repo_if_updated(student_submission_path, remote_repo_path,
                             remote_git_url)
    else:
        clone_repo(student_submission_path, remote_git_url)


def fetch_assignment_submissions(class_name: str, assignment_name: str,
                                 class_submission_path):
    """
    Fetch submissions for a single assignment.

    Assumes the class, the assignment, and the class submission directory all
    exist.

    :param class_name: name of the class
    :param assignment_name: name of the assignment
    :param class_submission_path: path to the directory containing submissions
     for the class
    """

    print()
    print('Fetching submissions for {0} in class {1}'
          .format(assignment_name, class_name))
    print()

    assignment_submissions_path = os.path.join(class_submission_path,
                                               assignment_name, 'submissions')

    create_dir_if_non_existent(assignment_submissions_path)

    assignment_reports_path = os.path.join(class_submission_path,
                                           assignment_name, 'reports')

    remote_home_dir = server_interface.my_home_dir()
    remote_reports_path = \
        os.path.join(faculty_assignment_dir_path(class_name, assignment_name,
                                                 remote_home_dir),
                     'reports.git')

    remote_git_url = build_clone_url(remote_reports_path)

    if os.path.isdir(assignment_reports_path):
        pull_repo_if_updated(assignment_reports_path, remote_reports_path,
                             remote_git_url)
    else:
        clone_repo(assignment_reports_path, remote_git_url)

    students = server_interface.get_students(class_name)

    # fetch each student's submission
    for student in students:
        fetch_student_submission(class_name, assignment_name, student,
                                 assignment_submissions_path)


def create_dir_if_non_existent(dir_path, confirm=False):
    if not os.path.isdir(dir_path):
        if confirm:
            prompt = '{0} does not exist. Create it now?'
            if not confirmation(prompt):
                raise GkeepException('Cannot fetch submissions')
        try:
            os.makedirs(dir_path)
        except OSError as e:
            error = 'Error creating directory: {0}'.format(e)
            raise GkeepException(error)


@config_parsed
@server_interface_connected
@class_exists
def fetch_submissions(class_name: str, assignment_name: str):
    """
    Fetch student submissions for a class.

    :param class_name: name of the class to fetch assignments from
    :param assignment_name: name of an assignment to fetch, or None to fetch
     all assignments for the class
    """

    class_path = os.path.join(config.submissions_path, class_name)

    create_dir_if_non_existent(config.submissions_path, confirm=True)
    create_dir_if_non_existent(class_path)

    # build list of assignments to fetch
    if assignment_name is None:
        assignments = server_interface.get_assignments(class_name)
    else:
        if not server_interface.assignment_exists(class_name, assignment_name):
            error = ('Assignment {0} does not exist in class {1}'
                     .format(assignment_name, class_name))
            raise GkeepException(error)

        assignments = [assignment_name]

    # fetch the submissions
    for assignment_name in assignments:
        fetch_assignment_submissions(class_name, assignment_name,
                                     class_path)
