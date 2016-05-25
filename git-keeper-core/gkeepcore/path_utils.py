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


"""Utility functions for extracting information from paths."""


import os


def path_to_list(path: str) -> list:
    """Constructs a list containing each element of a path.

    Example:

      /an/example/path -> ['an', 'example', 'path']

    :param path: the path to convert
    :return: a list containing each path element
    """

    elements = []

    # remove any slashes from the beginning and the end of the path
    path = path.strip('/')

    # continually split the path, which splits the last element in the path
    # from the rest
    while path != '':
        path, basename = os.path.split(path)
        elements.insert(0, basename)

    return elements


def user_home_dir(username):
    """Get a user's home directory on the local machine.

    :param username: the user to get the home directory of
    :return: the user's home directory

    """

    tilde_home_dir = '~{0}'.format(username)

    return os.path.expanduser(tilde_home_dir)


def user_log_path(home_dir: str, username: str):
    """Builds a log file path of this form:

    ~<username>/git-keeper-<username>.log
    """

    filename = '{0}.log'.format(username)

    return os.path.join(home_dir, filename)


def user_from_log_path(path: str) -> str:
    """Extracts the username from a faculty or student log file.

    :param path: path of the log file
    :return: the username or None if the path is malformed
    """

    # we're parsing a path that ends with this:
    # <username>/git-keeper-<username>.log

    path_list = path_to_list(path)

    if len(path_list) < 2:
        return None

    # the information we want is in the last 2 elements of the list
    username, log_filename = path_list[-2:]

    expected_filename = username + '.log'

    if log_filename != expected_filename:
        return None

    return username


def parse_submission_repo_path(path) -> (str, str, str):
    """
    Extracts student username, faculty username, class name, and assignment
    name from a submission repository.

    :param path: path to the submission repository
    :return: a tuple containing the student username, faculty username, class
     name, and assignment name, or None if the path is malformed
    """

    # we're parsing a path which ends with this:
    # <student>/<faculty>/<class>/<assignment>.git

    path_list = path_to_list(path)

    if len(path_list) < 4:
        return None

    # the information we want is in the last 3 elements of the list
    faculty_username, class_name, repo_name = path_list[-3:]

    # repo name must end with .git and must be more than just .git
    if not repo_name.endswith('.git') or repo_name == '.git':
        return None

    # strip the last 4 characters off the repo name to get the assignment name
    assignment_name = repo_name[:-4]

    return faculty_username, class_name, assignment_name


def parse_faculty_assignment_path(path) -> (str, str):
    """Extracts the class name and assignment name from a path to a faculty
    assignment directory
    :param path: path to the assignment directory
    :return: a tuple containing the class name and the assignment name, or
             None if the path is malformed
    """

    # we're parsing a path that ends with this:
    # <class>/<assignment>

    path_list = path_to_list(path)

    if len(path_list) < 2:
        return None

    # the information we want is in the last 2 elements of the list
    class_name, assignment_name = path_list[-2:]

    return class_name, assignment_name


def get_log_path_from_username(username: str) -> str:
    """Creates the path to the log file for the given student or faculty
    username.

    :param username: the user who owns the log
    :return: the path to the log
    """
    
    filename = '{0}.log'.format(username)
    home_dir = user_home_dir(username)

    log_path = os.path.join(home_dir, filename)

    return log_path
