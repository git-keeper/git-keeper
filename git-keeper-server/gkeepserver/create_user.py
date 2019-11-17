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


"""Provides functions to create a new faculty or student user."""

import os
from enum import Enum
from shutil import which

from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import user_home_dir, user_log_path, \
    gkeepd_to_faculty_log_path
from gkeepcore.student import Student
from gkeepcore.system_commands import (sudo_add_user, sudo_set_password, chmod,
                                       sudo_chown, mkdir, make_symbolic_link)
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.generate_password import generate_password
from gkeepserver.gkeepd_logger import gkeepd_logger as logger
from gkeepserver.initialize_log import initialize_log
from gkeepserver.log_polling import log_poller
from gkeepserver.server_configuration import config
from gkeepserver.server_email import Email


class UserType(Enum):
    """Enum type for specifying faculty or student users."""
    faculty = 0
    student = 1


def initialize_user_log(username):
    """
    Create a log file for the user with the appropriate permissions and start
    watching it.

    The log starts off with a header that warns the user not to edit the file.

    The user that owns the log will have read/write permissions. The log will
    belong to the keeper group which will have read permissions.

    :param username: the user to make the log for
    """

    home_dir = user_home_dir(username)
    log_path = user_log_path(home_dir, username)

    initialize_log(log_path, username, config.keeper_group, '640')

    # start watching the file for events
    log_poller.watch_log_file(log_path)


def initialize_gkeepd_to_faculty_log(username):
    """
    Create the log file that gkeepd will write to in order to communicate with
    a faculty client.

    It will be located at ~username/gkeepd.log

    It will be owned by the keeper user and the faculty group. The keeper user
    will have read/write permissions and the faculty group will have read
    permissions.

    :param username: faculty username
    """

    home_dir = user_home_dir(username)
    log_path = gkeepd_to_faculty_log_path(home_dir)

    # this log will be owned and writable by keeper and readable by the
    # faculty's group
    initialize_log(log_path, config.keeper_user, username, '640')


def create_faculty_dirs(username: str):
    """
    Create the classes and uploads directories in a faculty member's home
    directory.

    :param username: username of the faculty member
    """

    home_dir = user_home_dir(username)
    classes_dir_path = os.path.join(home_dir, 'classes')

    mkdir(classes_dir_path, sudo=True)
    # world readable for the handouts directory
    chmod(classes_dir_path, '755', sudo=True)
    sudo_chown(classes_dir_path, username, config.keeper_group)

    uploads_dir_path = os.path.join(home_dir, 'uploads')

    mkdir(uploads_dir_path, sudo=True)
    chmod(uploads_dir_path, '750', sudo=True)
    sudo_chown(uploads_dir_path, username, config.keeper_group)


def create_git_shell_commands(username: str, command_list: list):
    """
    Create the git-shell-commands directory for a user and populate it with
    symbolic links to allowed commands.

    The user will only be able to run the listed commands from an interactive
    shell.

    :param username: username of the user
    :param command_list: list of commands that they will be able to run
    """

    home_dir = user_home_dir(username)
    git_shell_commands_path = os.path.join(home_dir, 'git-shell-commands')

    mkdir(git_shell_commands_path, sudo=True)

    for command in command_list:
        command_path = which(command)
        make_symbolic_link(command_path, git_shell_commands_path, sudo=True)


def create_user(username, user_type, first_name, last_name, email_address=None,
                additional_groups=None, shell='bash'):
    """
    Create a faculty or a student user, email them their credentials, and start
    watching their log file for events.

    A group will be created that matches the name of the user and the user
    will be placed in this group. The additional_groups parameter should only
    be used to put the user in groups beyond this default group.

    :param username: username for the new user
    :param user_type: faculty or student
    :param first_name: first name of the user
    :param last_name: last name of the user
    :param email_address: email address of the user
    :param additional_groups: groups beyond the default group to add the user
     to
    :param shell: name of the shell for the user
    """

    if username == config.faculty_group or username == config.student_group:
        error = ('{0} is not a valid username. A username may not have the '
                 'same name as the faculty or student '
                 'user groups').format(username)
        raise GkeepException(error)

    logger.log_info('Creating user {0}'.format(username))

    sudo_add_user(username, additional_groups, shell)

    password = generate_password()
    sudo_set_password(username, password)

    initialize_user_log(username)

    if user_type == UserType.faculty:
        initialize_gkeepd_to_faculty_log(username)

        create_faculty_dirs(username)

    if user_type == UserType.student:
        create_git_shell_commands(username, ['passwd'])

    # email the credentials to the user if an email address was provided
    if email_address is not None:
        subject = 'New git-keeper account'
        body = ('Hello {0},\n\n'
                'An account has been created for you on the '
                'git-keeper server. Here are your credentials:\n\n'
                'Username: {1}\n'
                'Password: {2}\n\n').format(first_name, username, password)

        # let the students know they should direct questions to their
        # instructor rather than reply to the git-keeper
        if user_type == UserType.student:
            body += ('If you have any questions, please contact your '
                     'instructor rather than responding to this email '
                     'directly.\n\n')

        body += 'Enjoy!'

        email_sender.enqueue(Email(email_address, subject, body))


def create_student_user(student: Student):
    """
    Wrapper that calls create_user() to add a new student user.

    The student is added to the student group specified in the server
    configuration, and their shell is set to git-shell.

    :param student: Student object representing the new student
    """

    groups = [config.student_group]
    create_user(student.username, UserType.student,
                student.first_name, student.last_name,
                email_address=student.email_address,
                additional_groups=groups, shell='git-shell')
