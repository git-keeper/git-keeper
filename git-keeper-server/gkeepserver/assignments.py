# Copyright 2016, 2018 Nathan Sommer and Ben Coleman
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


"""Provides functionality related to assignments on the server."""


import os
from tempfile import TemporaryDirectory

from gkeepcore.action_scripts import get_action_script_and_interpreter
from gkeepcore.assignment_config import AssignmentConfig
from gkeepcore.student import Student
from pkg_resources import resource_exists, resource_string, ResolutionError, \
    ExtractionError

from gkeepcore.git_commands import git_init_bare, git_init, git_add_all, \
    git_commit, git_push, git_config
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import parse_faculty_assignment_path, \
    user_home_dir, faculty_class_dir_path, student_assignment_repo_path, \
    student_class_dir_path, faculty_assignment_dir_path, user_gitkeeper_path
from gkeepcore.shell_command import CommandError
from gkeepcore.system_commands import cp, chmod, mkdir, sudo_chown, rm
from gkeepserver.database import db
from gkeepserver.directory_locks import directory_locks
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.server_configuration import config
from gkeepserver.server_email import Email, EmailException, EmailPriority


class StudentAssignmentError(GkeepException):
    """Raised if anything goes wrong with a student assignment."""
    pass


class AssignmentDirectoryError(GkeepException):
    """
    Raised if any of the required items in the assignment directory do not
    exist.
    """
    def __init__(self, path):
        Exception.__init__(self, '{0} does not exist'.format(path))


class AssignmentDirectory:
    """
    Stores the paths to everything in an assignment directory on the server.

    Constructor raises AssignmentDirectoryError if any of the required paths do
    not exist.

    Public attributes:

        path - path to the assignment directory
        class_name - name of the class
        assignment_name - name of the assignment
        email_path - path to email.txt
        base_code_repo_path - path to the base code repository
        reports_repo_path - path to the reports repository
        tests_path - path to the tests directory
        config_path - path to assignment.cfg (if present)
    """

    def __init__(self, path, check=True):
        """
        Assign attributes based on path.

        Raises AssignmentDirectoryError if check is True and any required
        paths do not exist.

        :param path: path to the assignment directory
        :param check: whether or not to check if everything exists
        """
        self.path = path
        self.email_path = os.path.join(self.path, 'email.txt')
        self.base_code_repo_path = os.path.join(self.path, 'base_code.git')
        self.reports_repo_path = os.path.join(self.path, 'reports.git')
        self.tests_path = os.path.join(self.path, 'tests')
        self.config_path = os.path.join(self.path, 'assignment.cfg')

        self.action_script, self.action_script_interpreter = \
            get_action_script_and_interpreter(self.tests_path)

        path_info = parse_faculty_assignment_path(path)

        if path_info is None:
            self.faculty_username = None
            self.class_name = None
            self.assignment_name = None
        else:
            self.faculty_username, self.class_name, self.assignment_name = \
                path_info

        if check:
            self.check()

    def check(self):
        """
        Ensure everything is in place in the assignment directory.

        Raise AssignmentDirectoryError if check fails.
        """

        with directory_locks.get_lock(self.path):
            if self.class_name is None or self.assignment_name is None:
                error = '{0} is not a valid assignment path'.format(self.path)
                raise AssignmentDirectoryError(error)

            # ensure all required directories exist
            for dir_path in (self.path, self.base_code_repo_path,
                             self.reports_repo_path, self.tests_path):
                if not os.path.isdir(dir_path):
                    raise AssignmentDirectoryError(dir_path)

            # ensure email.txt exists
            if not os.path.isfile(self.email_path):
                raise AssignmentDirectoryError(self.email_path)

            # ensure there is an action script
            self.action_script, self.action_script_interpreter = \
                get_action_script_and_interpreter(self.tests_path)
            if self.action_script is None:
                raise AssignmentDirectoryError('action script')

    def get_config(self):
        """
        Returns an AssignmentConfig object representing the data from
        assignment.cfg.

        :return: AssignmentConfig object for the assignment
        """

        return AssignmentConfig(self.config_path,
                                default_env=config.default_test_env)


def get_assignment_dir(faculty_username: str, class_name: str,
                       assignment_name: str) -> AssignmentDirectory:
    """
    Build and return an AssignmentDirectory object for an assignment.

    :param faculty_username: faculty that owns the assignment
    :param class_name: name of the class that the assignment belongs to
    :param assignment_name: name of the assignment
    :return: an AssignmentDirectory object representing the assignment's
     directory
    """

    assignment_path = \
        faculty_assignment_dir_path(class_name, assignment_name,
                                    user_gitkeeper_path(faculty_username))

    return AssignmentDirectory(assignment_path)


def get_class_assignment_paths(faculty_username: str, class_name: str,
                               include_inactive=False) -> list:
    """
    Get a list of all the paths for all the assignment directories for a class.

    :param faculty_username: faculty who owns the class
    :param class_name: name of the class
    :param include_inactive: if True, inactive assignments will be included
    :return: list of AssignmentDirectory objects
    """
    class_path = faculty_class_dir_path(class_name,
                                        user_gitkeeper_path(faculty_username))

    assignment_paths = []

    if not os.path.isdir(class_path):
        return assignment_paths

    for assignment in db.get_class_assignments(class_name, faculty_username,
                                               include_inactive):
        path = os.path.join(class_path, assignment.name)
        assignment_paths.append(path)

    return assignment_paths


def get_class_assignment_dirs(faculty_username: str, class_name: str,
                              include_inactive=False) -> list:
    """
    Get all the valid assignment directories from a class, as a list of
    AssignmentDirectory objects.

    :param faculty_username: faculty who owns the class
    :param class_name: name of the class
    :param include_inactive: if True, inactive assignments will be included
    :return: list of AssignmentDirectory objects
    """
    class_path = faculty_class_dir_path(class_name,
                                        user_gitkeeper_path(faculty_username))

    assignment_dirs = []

    if not os.path.isdir(class_path):
        return assignment_dirs

    for assignment in db.get_class_assignments(class_name, faculty_username,
                                               include_inactive):
        path = os.path.join(class_path, assignment.name)

        try:
            assignment_dir = AssignmentDirectory(path)
            assignment_dirs.append(assignment_dir)
        except AssignmentDirectoryError:
            pass

    return assignment_dirs


def create_base_code_repo(assignment_dir: AssignmentDirectory,
                          base_code_path: str):
    """
    Create a bare repository in an assignment directory which contains the
    base code for an assignment, a post-receive hook script for triggering
    tests, and a pre-receive hook for ensuring the students only push to
    the one existing branch. The repository is configured to reject destructive
    pushes.

    Raises an AssignmentDirectoryError if anything goes wrong.

    :param assignment_dir: AssignmentDir object representing the assignment
     directory
    :param base_code_path: path to the directory which contains the base code
    """

    # temporary directory in which to create a git repository from
    # base_code
    base_code_tempdir = TemporaryDirectory()

    # copy base_code to the temporary directory
    try:
        cp(base_code_path, base_code_tempdir.name, recursive=True)
    except CommandError as e:
        error = ('Error copying base code to a temporary directory: {0}'
                 .format(str(e)))
        raise AssignmentDirectoryError(error)

    base_code_temp_path = os.path.join(base_code_tempdir.name,
                                       'base_code')

    try:
        # initialize bare repository
        mkdir(assignment_dir.base_code_repo_path)
        git_init_bare(assignment_dir.base_code_repo_path)

        # initialize base code repository in upload directory
        git_init(base_code_temp_path)
        git_add_all(base_code_temp_path)
        git_commit(base_code_temp_path, 'Initial commit')

        # push base code into bare repo
        git_push(base_code_temp_path,
                 assignment_dir.base_code_repo_path)

        # put the git hook scripts in place
        hook_script_names = ('pre-receive', 'post-receive')
        for script_name in hook_script_names:
            script_path = os.path.join(assignment_dir.base_code_repo_path,
                                       'hooks', script_name)
            write_git_hook_script(script_name, script_path)
            chmod(script_path, '750')

        # configure the repository so that it will not accept destructive
        # pushes
        git_config(assignment_dir.base_code_repo_path,
                   ('receive.denyNonFastForwards', 'true'))

    except GkeepException as e:
        error = 'error building base code repository: {0}'.format(str(e))
        raise AssignmentDirectoryError(error)


def copy_email_txt_file(assignment_dir: AssignmentDirectory,
                        email_txt_path: str):
    """
    Copy email.txt into an assignment directory.

    :param assignment_dir: AssignmentDirectory to copy into
    :param email_txt_path: path to email.txt
    """
    cp(email_txt_path, assignment_dir.path, sudo=True)


def copy_config_file(assignment_dir: AssignmentDirectory, config_path: str):
    """
    Copy assignment.cfg into an assignment directory

    :param assignment_dir: AssignmentDirectory to copy into
    :param config_path: path to assignment.cfg
    """
    cp(config_path, assignment_dir.path, sudo=True)


def copy_tests_dir(assignment_dir: AssignmentDirectory, tests_path: str):
    """
    Copy tests folder into an assignment directory.

    :param assignment_dir: AssignmentDirectory to copy into
    :param tests_path: path to tests directory
    """
    cp(tests_path, assignment_dir.tests_path, recursive=True, sudo=True)


def remove_student_assignment(assignment_dir: AssignmentDirectory,
                              student, faculty_username: str):
    """
    Remove a student's bare repository for an assignment.

    :param assignment_dir: object representing the faculty's assignment
     directory
    :param student: Student object representing the student
    :param faculty_username: username of the faculty who owns the class
    """

    student_home_dir = user_home_dir(student.username)

    # path to the student's bare repository for this assignment
    assignment_repo_path = \
        student_assignment_repo_path(faculty_username,
                                     assignment_dir.class_name,
                                     assignment_dir.assignment_name,
                                     student_home_dir)

    # the repo should exist
    if not os.path.isdir(assignment_repo_path):
        error = '{0} does not exist'.format(assignment_repo_path)
        raise StudentAssignmentError(error)

    # remove the directory
    try:
        rm(assignment_repo_path, recursive=True, sudo=True)
    except CommandError as e:
        raise StudentAssignmentError(e)


def student_assignment_exists(assignment_dir: AssignmentDirectory,
                              student: Student, faculty_username: str):
    """
    Determine if an assignment repository exists for a student.

    :param assignment_dir: AssignmentDirectory object representing the
     assignment
    :param student: Student object representing the student
    :param faculty_username: username of the faculty that owns the class
    :return: True if a repo exists, False if not
    """

    home_dir = user_home_dir(student.username)

    assignment_repo_path = \
        student_assignment_repo_path(faculty_username,
                                     assignment_dir.class_name,
                                     assignment_dir.assignment_name, home_dir)

    return os.path.isdir(assignment_repo_path)


def setup_student_assignment(assignment_dir: AssignmentDirectory,
                             student, faculty_username: str):
    """
    Setup the bare repository that a student will clone and push to for an
    assignment and email the student.

    Raises StudentAssignmentError if anything goes wrong.

    :param assignment_dir: object representing the directory
    :param student: Student object representing the student
    :param faculty_username: username of the faculty who owns the class
    """

    home_dir = user_home_dir(student.username)

    # path to the student's directory containing the class that this assignment
    # belongs to
    class_path = student_class_dir_path(faculty_username,
                                        assignment_dir.class_name, home_dir)

    # path to the student's bare repository for this assignment
    assignment_repo_path = \
        student_assignment_repo_path(faculty_username,
                                     assignment_dir.class_name,
                                     assignment_dir.assignment_name, home_dir)

    # the repo should not already exist
    if os.path.isdir(assignment_repo_path):
        error = '{0} already exists'.format(assignment_repo_path)
        raise StudentAssignmentError(error)

    # make the class directory if it does not exist
    if not os.path.isdir(class_path):
        try:
            mkdir(class_path, sudo=True)
            sudo_chown(class_path, student.username, config.keeper_group)
        except OSError as e:
            error = 'error creating {0}: {1}'.format(assignment_repo_path,
                                                     str(e))
            raise StudentAssignmentError(error)

    # copy the base code repo from the faculty's home directory
    try:
        cp(assignment_dir.base_code_repo_path, assignment_repo_path,
           recursive=True, sudo=True)
    except GkeepException as e:
        error = ('error copying {0} to {1}: {2}'
                 .format(assignment_dir.base_code_repo_path,
                         assignment_repo_path, str(e)))
        raise StudentAssignmentError(error)

    # set permissions on the assignment repo
    try:
        chmod(assignment_repo_path, '750', sudo=True)
        sudo_chown(assignment_repo_path, student.username,
                   config.keeper_group, recursive=True)
    except CommandError as e:
        error = ('error setting permissions on {0}: {1}'
                 .format(assignment_repo_path, str(e)))
        raise StudentAssignmentError(error)

    assignment_config = assignment_dir.get_config()

    email_subject = (assignment_config.announcement_subject
                     .format(class_name=assignment_dir.class_name,
                             assignment_name=assignment_dir.assignment_name))

    # build the clone URL for the assignment
    clone_url = '{0}@{1}:{2}'.format(student.username,
                                     config.hostname,
                                     assignment_repo_path)

    # read email.txt to get the customizable part of the email body
    try:
        with open(assignment_dir.email_path) as f:
            email_body = f.read()
    except OSError as e:
        error = 'error reading {0}: {1}'.format(assignment_dir.email_path,
                                                str(e))
        raise StudentAssignmentError(error)

    # clone URL followed by email.txt contents
    email_body = 'Clone URL:\n{0}\n\n{1}'.format(clone_url, email_body)

    if student.username != faculty_username:
        priority = EmailPriority.LOW
    else:
        priority = EmailPriority.HIGH

    # build the email
    try:
        email = Email(student.email_address, email_subject, email_body,
                      priority=priority)
    except EmailException as e:
        raise StudentAssignmentError(e)

    # enqueue the email for sending
    email_sender.enqueue(email)


def write_git_hook_script(script_name: str, dest_path: str):
    """
    Write the contents of one of the git hook scripts into its appropriate
    location.

    This will overwrite an existing file.

    Raises PostReceiveScriptError on any errors.

    :param script_name: name of the hook script to write
    :param dest_path: path to write to
    """

    script_data_path = 'data/{}'.format(script_name)

    if not resource_exists('gkeepserver', script_data_path):
        raise StudentAssignmentError('{} script does not exist'
                                     .format(script_name))

    try:
        script_text = resource_string('gkeepserver', script_data_path)
        script_text = script_text.decode()
    except (ResolutionError, ExtractionError, UnicodeDecodeError):
        raise StudentAssignmentError('error reading {} script data'
                                     .format(script_name))

    try:
        with open(dest_path, 'w') as f:
            f.write(script_text)
    except OSError as e:
        error = 'error writing {0}: {1}'.format(dest_path, str(e))
        raise StudentAssignmentError(error)
