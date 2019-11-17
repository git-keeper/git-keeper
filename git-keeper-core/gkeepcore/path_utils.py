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


"""Utility functions for extracting information from paths."""


import os


def path_to_list(path: str) -> list:
    """
    Construct a list containing each element of a path.

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


def path_to_assignment_name(path: str) -> str:
    """
    Extract an assignment name from a path. This simply returns the last
    element in a path, and does not ensure that the name is a valid assignment
    name.

    If given an empty string, the empty string is returned.

    :param path: assignment path
    :return: name of the assignment
    """

    path_components = path_to_list(path)

    if len(path_components) == 0:
        return ''
    else:
        return path_components[-1]


def user_home_dir(username):
    """
    Get a user's home directory on the local machine.

    :param username: the user to get the home directory of
    :return: the user's home directory

    """

    tilde_home_dir = '~{0}'.format(username)

    return os.path.expanduser(tilde_home_dir)


def user_log_path(home_dir: str, username: str):
    """
    Build a log file path of this form:

    ~<username>/<username>.log
    """

    filename = '{0}.log'.format(username)

    return os.path.join(home_dir, filename)


def gkeepd_to_faculty_log_path(faculty_home_dir: str):
    """
    Build the path to the log that the server used to communicate with the
    faculty member.

    :param faculty_home_dir: home directory of the faculty account
    :return: path to gkeepd's log for that faculty member
    """

    return os.path.join(faculty_home_dir, 'gkeepd.log')


def user_from_log_path(path: str) -> str:
    """
    Extract the username from a faculty or student log file.

    :param path: path of the log file
    :return: the username or None if the path is malformed
    """

    # we're parsing a path that ends with this:
    # <username>/<username>.log

    path_list = path_to_list(path)

    if len(path_list) < 2:
        return None

    # the information we want is in the last 2 elements of the list
    username, log_filename = path_list[-2:]

    expected_filename = username + '.log'

    if log_filename != expected_filename:
        return None

    return username


def parse_submission_repo_path(path) -> (str, str, str, str):
    """
    Extract student username, faculty username, class name, and assignment
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
    """
    Extract the class name and assignment name from a path to a faculty
    assignment directory.

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


def parse_faculty_class_path(path) -> str:
    """
    Extract the class name from a path to a faculty class directory.

    :param path: path to the class directory
    :return: the class name
    """

    # we're parsing a path that ends with this:
    # classes/<class name>

    path_list = path_to_list(path)

    if len(path_list) < 2:
        return None

    classes, class_name = path_list[-2:]

    if classes != 'classes':
        return None

    return class_name


def faculty_upload_dir_path(home_dir: str) -> str:
    """
    Build the path to the faculty's upload directory on the server.

    :param home_dir: faculty's home directory
    :return: upload directory path
    """

    return os.path.join(home_dir, 'uploads')


def faculty_classes_dir_path(home_dir: str):
    """
    Build the path to a faculty member's directory for storing classes.

    :param home_dir: home directory of the faculty member.
    :return: path to the classes directory
    """

    return os.path.join(home_dir, 'classes')


def faculty_class_dir_path(class_name: str, home_dir: str):
    """
    Build the path to a faculty member's class directory on the server.

    :param class_name: name of the class
    :param home_dir: home directory of the faculty member.
    :return: path to the class directory
    """

    return os.path.join(faculty_classes_dir_path(home_dir), class_name)


def faculty_class_status_path(class_name: str, home_dir: str):
    """
    Build the path to a class's status file on the server.

    :param class_name: name of the class
    :param home_dir: home directory of the faculty member
    :return: path to the class's status file
    """

    return os.path.join(faculty_class_dir_path(class_name, home_dir),
                        'status')


def faculty_info_path(home_dir: str):
    """
    Build the path to a faculty member's info directory.

    :param home_dir: home directory of the faculty member
    :return: path to the info directory
    """

    return os.path.join(home_dir, 'info')


def assignment_published_file_path(class_name: str, assignment_name: str,
                                   home_dir: str):
    """
    Build the path to an assignment's published flag file.

    :param class_name: name of the class
    :param assignment_name: name of the assignment
    :param home_dir: home dir of the faculty
    :return: path to the published flag file
    """

    assignment_path = faculty_assignment_dir_path(class_name, assignment_name,
                                                  home_dir)
    return os.path.join(assignment_path, 'published')


def faculty_assignment_dir_path(class_name: str, assignment_name: str,
                                home_dir: str,):
    """
    Build the path to a faculty member's assignment directory on the server.

    :param class_name: name of the class
    :param assignment_name: name of the assignment
    :param home_dir: home directory of the faculty member.
    """

    return os.path.join(faculty_class_dir_path(class_name, home_dir),
                        assignment_name)


def log_path_from_username(username: str) -> str:
    """
    Create the path to the log file for the given student or faculty
    username.

    Use only if you are looking for the log path on the local machine.

    :param username: the user who owns the log
    :return: the path to the log
    """

    filename = '{0}.log'.format(username)
    home_dir = user_home_dir(username)

    log_path = os.path.join(home_dir, filename)

    return log_path


def class_student_csv_path(class_name: str, home_dir: str) -> str:
    """
    Build a path to the CSV file of students for a class.

    :param class_name: name of the class
    :param home_dir: home directory of the faculty
    :return: path to the CSV file
    """

    class_path = faculty_class_dir_path(class_name, home_dir)

    return os.path.join(class_path, 'students.csv')


def student_class_dir_path(faculty_username, class_name, home_dir) -> str:
    """
    Build a path to a student's directory for a class.

    :param faculty_username: username of the faculty
    :param class_name: name of the class
    :param home_dir: home directory of the student
    :return: path to the class directory
    """

    return os.path.join(home_dir, faculty_username, class_name)


def student_assignment_repo_path(faculty_username: str, class_name: str,
                                 assignment_name: str, home_dir: str) -> str:
    """
    Build a path to a student's repository for an assignment.

    :param faculty_username: username of the faculty who owns the class
    :param class_name: name of the class
    :param assignment_name: name of the assignment
    :param home_dir: home directory of the student
    :return: path to the assignment repository
    """
    return os.path.join(student_class_dir_path(faculty_username, class_name,
                                               home_dir),
                        assignment_name + '.git')
