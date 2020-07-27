# Copyright 2016, 2017 Nathan Sommer and Ben Coleman
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
Provides fetch_submissions() for fetching student submissions from the server.
"""

import json
import os
import sys

from gkeepclient.client_configuration import config
from gkeepclient.client_function_decorators import config_parsed, \
    server_interface_connected, class_exists
from gkeepclient.server_interface import server_interface
from gkeepclient.server_response_poller import ServerResponsePoller, \
    ServerResponseType
from gkeepclient.text_ui import confirmation
from gkeepcore.git_commands import is_non_bare_repo, git_head_hash, \
    git_pull, git_clone_remote
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import student_assignment_repo_path
from gkeepcore.faculty_class_info import FacultyClassInfo


class FetchedHashCache:
    """
    Provides functionality to manage a cache of git commit hashes for fetched
    assignment submissions.

    The cache file is stored at <assignment_fetch_path>/.hash_cache
    """
    def __init__(self, fetched_assignment_path):
        """
        Initialize the cache dictionary and load the existing cache if it
        exists.

        :param fetched_assignment_path: path to where the assignment is fetched
        """
        self.cache_path = os.path.join(fetched_assignment_path, '.hash_cache')

        self.hashes = {}

        if os.path.isfile(self.cache_path):
            try:
                with open(self.cache_path) as f:
                    self.hashes = json.load(f)
            except Exception as e:
                print('Error loading hash cache from {}'
                      .format(self.cache_path))

    def get_hash(self, path):
        """
        Get the git head hash for a repository.

        :param path: path to the repository
        :return: has of the head commit of the repository
        """
        return self.hashes[path]

    def set_hash(self, path, hash):
        """
        Set the hash of a repository in the cache.

        :param path: path to the repository
        :param hash: git head hash of the repository
        """
        self.hashes[path] = hash

    def write_cache(self):
        """
        Write the cache to the cache file.
        """
        with open(self.cache_path, 'w') as f:
            json.dump(self.hashes, f)

    def is_cached(self, local_repo_path):
        """
        Determine if a repository's hash is cached.

        :param local_repo_path: path to the repository
        :return: True if the hash is cached, False otherwise
        """
        return local_repo_path in self.hashes


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
        git_clone_remote(remote_url, local_repo_path)
        print('success!')
    except GkeepException as e:
        print('error cloning: {0}'.format(e))


def pull_repo_if_updated(local_repo_path, remote_url, remote_head_hash,
                         hash_cache: FetchedHashCache):
    """
    Perform a git pull in a git repository if the remote has changed since
    the last pull.

    :param local_repo_path: path to the local repository
    :param remote_url: git clone URL
    :param remote_head_hash: has of the HEAD commit of the remote repository
    :param hash_cache: cache of git commit hashes of local repositories
    """

    if not is_non_bare_repo(local_repo_path):
        print('{0} exists but is not a git repository'
              .format(local_repo_path))
        return

    if hash_cache.is_cached(local_repo_path):
        local_head_hash = hash_cache.get_hash(local_repo_path)
    else:
        # get the hash of the HEAD of the local repository
        try:
            local_head_hash = git_head_hash(local_repo_path)
            hash_cache.set_hash(local_repo_path, local_head_hash)
        except GkeepException as e:
            print('Error reading local git repository {0}: {1}'
                  .format(local_repo_path, e))
            return

    # no need to pull if the hashes are the same
    if local_head_hash == remote_head_hash:
        return

    print('Pulling new content in {0} ... '.format(local_repo_path), end='')
    sys.stdout.flush()

    try:
        git_pull(local_repo_path, remote_url)
        hash_cache.set_hash(local_repo_path, remote_head_hash)
        print('success!')
    except GkeepException as e:
        print(str(e))


def build_clone_url(path):
    """
    Build a git clone URL with the following form:

    ssh://<username>@<hostname>:<port number>/<path>

    The username, hostname, and port number come from the configuration file,
    which needs to be parsed.

    :param path: path to the repository on the server
    :return:
    """
    return ('ssh://{0}@{1}:{2}/{3}'
            .format(config.server_username, config.server_host,
                    config.server_ssh_port, path))


def fetch_student_submission(class_name: str, assignment_name: str,
                             assignment_submission_path: str,
                             remote_head_hash: str, remote_repo_path: str,
                             last_first_username: str,
                             hash_cache: FetchedHashCache):
    """
    Fetch a student's submission for an assignment.

    Clone the repo if it has not yet been cloned.

    If the repo has been cloned, check to see if the server repo has any new
    commits and pull if so.

    :param class_name: name of the class
    :param assignment_name: name of the assignment
    :param assignment_submission_path: path to the directory containing the
     assignment's submissions
    :param remote_head_hash: hash of the remote repo's HEAD commit
    :param remote_repo_path: path to the student's remote assignment repo
    :param last_first_username: <last name>_<first name>_<username> for student
    :param hash_cache: cache of git commit hashes of local repositories
    """

    student_submission_path = os.path.join(assignment_submission_path,
                                           last_first_username)

    remote_git_url = build_clone_url(remote_repo_path)

    # pull if the repo already exists, clone otherwise
    if os.path.isdir(student_submission_path):
        pull_repo_if_updated(student_submission_path, remote_git_url,
                             remote_head_hash, hash_cache)
    else:
        clone_repo(student_submission_path, remote_git_url)
        hash_cache.set_hash(student_submission_path, remote_head_hash)


def fetch_assignment_submissions(class_name: str, assignment_name: str,
                                 class_submission_path: str,
                                 info: FacultyClassInfo):
    """
    Fetch submissions for a single assignment.

    Assumes the class, the assignment, and the class submission directory all
    exist.

    :param class_name: name of the class
    :param assignment_name: name of the assignment
    :param class_submission_path: path to the directory containing submissions
     for the class
    :param info: info dictionary
    """

    print()
    print('Fetching submissions for {0} in class {1}'
          .format(assignment_name, class_name))
    print()

    assignment_path = os.path.join(class_submission_path, assignment_name)
    assignment_submissions_path = os.path.join(assignment_path, 'submissions')

    create_dir_if_non_existent(assignment_submissions_path)

    assignment_reports_path = os.path.join(assignment_path, 'reports')

    hash_cache = FetchedHashCache(assignment_path)

    remote_reports_path = info.reports_path(class_name, assignment_name)
    remote_reports_hash = info.reports_hash(class_name, assignment_name)

    remote_git_url = build_clone_url(remote_reports_path)

    if os.path.isdir(assignment_reports_path):
        pull_repo_if_updated(assignment_reports_path, remote_git_url,
                             remote_reports_hash, hash_cache)
    else:
        clone_repo(assignment_reports_path, remote_git_url)

    # fetch each student's submission

    for username in info.student_list(class_name):
        remote_head_hash = info.student_assignment_hash(class_name, assignment_name, username)
        remote_repo_path = info.student_assignment_path(class_name, assignment_name, username)

        last_first_username = info.student_last_first_username(class_name, username)

        fetch_student_submission(class_name, assignment_name,
                                 assignment_submissions_path, remote_head_hash,
                                 remote_repo_path, last_first_username,
                                 hash_cache)

    hash_cache.write_cache()


def create_dir_if_non_existent(dir_path, confirm=False):
    """
    Create a directory if it does not exist. Optionally ask for confirmation
    before creating.

    :param dir_path: path to the directory
    :param confirm: if True, user confirmation is required before creating
    """
    if not os.path.isdir(dir_path):
        if confirm:
            prompt = '{0} does not exist. Create it now?'.format(dir_path)
            if not confirmation(prompt):
                raise GkeepException('Cannot fetch submissions')
        try:
            os.makedirs(dir_path)
        except OSError as e:
            error = 'Error creating directory: {0}'.format(e)
            raise GkeepException(error)


@config_parsed
def build_dest_path(destination_path, class_name):
    """
    Build the path that submissions will be fetched to.

    If destination_path is not None, then it will be expanded as necessary.

    If destination_path is None and submissions_path is defined in the
    configuration, then the destination path will be:
       submissions_path/class_name

    If destination_path is None and submissions_path is not defined in the
    configuration, then the destination path will be the current working
    directory.

    :param destination_path: the path given on the command line, or None
    :param class_name: name of the class to fetch
    :return: the path to fetch into
    """

    if destination_path is None:
        if config.submissions_path is None:
            print('No destination path specified, fetching to the current '
                  'working directory')
            destination_path = os.getcwd()
        else:
            destination_path = os.path.join(config.submissions_path,
                                            class_name)
    else:
        destination_path = os.path.expanduser(destination_path)
        destination_path = os.path.abspath(destination_path)

    return destination_path


@config_parsed
@server_interface_connected
@class_exists
def fetch_submissions(class_name: str, assignment_name: str,
                      destination_path: str):
    """
    Fetch student submissions for a class.

    :param class_name: name of the class to fetch assignments from
    :param assignment_name: name of an assignment to fetch, or None to fetch
     all assignments for the class
    :param destination_path: directory in which to fetch the assignment
    """

    info = server_interface.get_info()

    create_dir_if_non_existent(destination_path, confirm=True)

    assignments_to_fetch = []

    if assignment_name == 'all':
        for assignment_name in info.assignment_list(class_name):
            published = info.is_published(class_name, assignment_name)
            disabled = info.is_disabled(class_name, assignment_name)
            if published and not disabled:
                assignments_to_fetch.append(assignment_name)
    else:
        if assignment_name not in info.assignment_list(class_name):
            error = ('Assignment {0} does not exist in class {1}'
                     .format(assignment_name, class_name))
            raise GkeepException(error)
        elif not info.is_published(class_name, assignment_name):
            error = ('Assignment {0} in class {1} is not published'
                     .format(assignment_name, class_name))
            raise GkeepException(error)
        elif info.is_disabled(class_name, assignment_name):
            error = ('Assignment {0} in class {1} is disabled'
                     .format(assignment_name, class_name))
            raise GkeepException(error)

        assignments_to_fetch.append(assignment_name)

    for assignment_name in assignments_to_fetch:
        fetch_assignment_submissions(class_name, assignment_name,
                                     destination_path, info)
