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
from tempfile import TemporaryDirectory

from pkg_resources import resource_exists, resource_string, ResolutionError, \
    ExtractionError

from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import user_home_dir, user_log_path, \
    gkeepd_to_faculty_log_path, user_gitkeeper_path
from gkeepcore.student import Student
from gkeepcore.system_commands import sudo_add_user, sudo_set_password, \
    chmod, sudo_chown, mkdir, make_symbolic_link, mv, sudo_set_shell, \
    sudo_add_user_to_groups, get_all_users
from gkeepserver.database import db
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.faculty import Faculty
from gkeepserver.generate_password import generate_password
from gkeepserver.gkeepd_logger import gkeepd_logger as logger, gkeepd_logger
from gkeepserver.initialize_log import initialize_log
from gkeepserver.log_polling import log_poller
from gkeepserver.server_configuration import config
from gkeepserver.server_email import Email, EmailPriority


class UserType(Enum):
    """Enum type for specifying faculty or student users."""
    faculty = 0
    student = 1


class NewUserAction(Enum):
    """
    Enum type for indicating whether a username exists in the system and/or
    database
    """
    NEW_USER_NEW_DB = 0
    NEW_DB_ROLE = 1


def initialize_user_log(username):
    """
    Create a log file for the user with the appropriate permissions and start
    watching it.

    The log starts off with a header that warns the user not to edit the file.

    The user that owns the log will have read/write permissions. The log will
    belong to the keeper group which will have read permissions.

    :param username: the user to make the log for
    """

    gitkeeper_path = user_gitkeeper_path(username)
    log_path = user_log_path(gitkeeper_path, username)

    if not os.path.isfile(log_path):
        initialize_log(log_path, username, config.keeper_group, '640')

    # start watching the file for events
    log_poller.watch_log_file(log_path)


def initialize_gkeepd_to_faculty_log(username):
    """
    Create the log file that gkeepd will write to in order to communicate with
    a faculty client.

    It will be located at <.gitkeeper path>/gkeepd.log

    It will be owned by the keeper user and the faculty group. The keeper user
    will have read/write permissions and the faculty group will have read
    permissions.

    :param username: faculty username
    """

    gitkeeper_path = user_gitkeeper_path(username)
    log_path = gkeepd_to_faculty_log_path(gitkeeper_path)

    # this log will be owned and writable by keeper and readable by the
    # faculty's group
    initialize_log(log_path, config.keeper_user, username, '640')


def create_faculty_dirs(username: str):
    """
    Create the classes and uploads directories in a faculty member's .gitkeeper
    directory.

    :param username: username of the faculty member
    """

    gitkeeper_path = user_gitkeeper_path(username)
    classes_dir_path = os.path.join(gitkeeper_path, 'classes')

    if not os.path.isdir(classes_dir_path):
        mkdir(classes_dir_path, sudo=True)

    # world readable for the handouts directory
    chmod(classes_dir_path, '755', sudo=True)
    sudo_chown(classes_dir_path, username, config.keeper_group)

    uploads_dir_path = os.path.join(gitkeeper_path, 'uploads')

    if not os.path.isdir(uploads_dir_path):
        mkdir(uploads_dir_path, sudo=True)

    chmod(uploads_dir_path, '750', sudo=True)
    sudo_chown(uploads_dir_path, username, config.keeper_group)


def write_git_shell_command_script(script, dest_path, username):
    script_data_path = 'data/{}'.format(script)

    if not resource_exists('gkeepserver', script_data_path):
        raise GkeepException('Data sript {} does not exist'
                             .format(script_data_path))

    try:
        script_text = resource_string('gkeepserver', script_data_path)
        script_text = script_text.decode()
    except (ResolutionError, ExtractionError, UnicodeDecodeError):
        raise GkeepException('error reading {} script data'.format(script))

    script_tempdir = TemporaryDirectory()
    temp_script_path = os.path.join(script_tempdir.name, script)

    try:
        with open(temp_script_path, 'w') as f:
            f.write(script_text)
    except OSError as e:
        error = 'error writing {}: {}'.format(temp_script_path, str(e))
        raise GkeepException(error)

    mv(temp_script_path, dest_path, sudo=True)
    sudo_chown(dest_path, username, config.keeper_group)
    chmod(dest_path, '750', sudo=True)


def setup_git_shell_commands_directory(username: str, command_list: list):
    """
    Create the git-shell-commands directory for a user, populate it with
    symbolic links to allowed commands, and write custom scripts to allow
    ssh-copy-id.

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

    for script in ('exec', 'add_ssh_id', 'exit'):
        dest_path = os.path.join(git_shell_commands_path, script)
        write_git_shell_command_script(script, dest_path, username)


def create_gitkeeper_directory(username):
    """
    Create a user's .gitkeeper directory.

    :param username: username of the user
    """

    gitkeeper_path = user_gitkeeper_path(username)

    if not os.path.isdir(gitkeeper_path):
        mkdir(gitkeeper_path, sudo=True)

    # read/write for user and keeper
    chmod(gitkeeper_path, '770', sudo=True)
    sudo_chown(gitkeeper_path, username, config.keeper_group)


def create_user(username, additional_groups=None, shell='bash'):
    """
    Create a new user on the system.

    :param username:
    :param additional_groups:
    :param shell:
    :return:
    """
    sudo_add_user(username, additional_groups, shell)

    password = generate_password()
    sudo_set_password(username, password)

    return password


def setup_user(username, user_type, first_name, last_name, action,
               email_address=None, additional_groups=None, shell='bash'):
    """
    Setup a faculty or a student user, email them their credentials, and start
    watching their log file for events.

    A new user is created if there is not yet a student or faculty account
    that exists with the provided username.

    A group will be created that matches the name of the user and the user
    will be placed in this group. The additional_groups parameter should only
    be used to put the user in groups beyond this default group.

    :param username: username for the new user
    :param user_type: faculty or student
    :param first_name: first name of the user
    :param last_name: last name of the user
    :param action: a NewUserAction instance indicating the action to perform
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

    logger.log_info('Setting up user {0}'.format(username))

    if action == NewUserAction.NEW_USER_NEW_DB:
        password = create_user(username, additional_groups, shell)
    else:
        sudo_set_shell(username, shell)
        if additional_groups is not None:
            sudo_add_user_to_groups(username, additional_groups)
        password = None

    create_gitkeeper_directory(username)
    initialize_user_log(username)

    if user_type == UserType.faculty:
        initialize_gkeepd_to_faculty_log(username)
        create_faculty_dirs(username)

        if action == NewUserAction.NEW_DB_ROLE and email_address is not None:
            email_about_faculty_role(email_address, first_name, username)

    if user_type == UserType.student:
        setup_git_shell_commands_directory(username, ['passwd'])

    # email the credentials to the user if an email address was provided
    # and a new user was just created
    if email_address is not None and password is not None:
        email_new_user(email_address, first_name, username, password,
                       user_type)


def email_about_faculty_role(email_address, first_name, username):
    """
    Send an email to a user that was a student and is now faculty.

    :param email_address: email address of the user
    :param first_name: first name of the user
    """

    subject = 'git-keeper faculty account'
    body = ('Hello {},\n\n'
            'Your git-keeper account "{}" on {} is now a faculty account and '
            'you may now create classes and assignments. Your credentials are '
            'unchanged.\n\n'
            'Enjoy!\n'.format(first_name, username, config.hostname))

    email_sender.enqueue(Email(email_address, subject, body))


def email_new_user(email_address, first_name, username, password, user_type):
    """
    Send an email containing a password to a new user.

    :param email_address: email address of the user
    :param first_name: first name of the user
    :param username: username of the user
    :param password: password of the user
    :param user_type: UserType.student or UserType.faculty
    """
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

    body += 'Enjoy!\n'

    if user_type == UserType.student:
        email_priority = EmailPriority.LOW
    else:
        email_priority = EmailPriority.NORMAL

    email_sender.enqueue(Email(email_address, subject, body,
                               priority=email_priority))


def setup_student_user(student: Student, action: NewUserAction):
    """
    Wrapper that calls setup_user() to add a new student user.

    The student is added to the student group specified in the server
    configuration, and their shell is set to git-shell.

    :param student: Student object representing the new student
    :param action: a NewUserAction instance indicating the status of
     the username on the host and in the db
    """

    groups = [config.student_group]
    setup_user(student.username, UserType.student,
               student.first_name, student.last_name, action,
               email_address=student.email_address,
               additional_groups=groups, shell='git-shell')


def add_faculty(last_name, first_name, email_address, admin=False):
    """
    Add a faculty user, or make an existing user a faculty user.

    :param last_name: last name of the faculty member
    :param first_name: first name of the faculty member
    :param email_address: email address of the faculty member
    :param admin: True if the faculty member should be an admin
    """

    try:
        email_username, email_domain = email_address.split('@')
    except ValueError:
        error = ('{} is not a valid email address'
                 .format(email_address))
        raise GkeepException(error)

    if db.email_exists(email_address):
        username = db.get_username_from_email(email_address)
        if db.faculty_username_exists(username):
            error = ('A faculty user with email {} already exists'
                     .format(email_address))
            raise GkeepException(error)
        elif db.student_username_exists(username):
            action = NewUserAction.NEW_DB_ROLE
        else:
            error = ('Database inconsistency: a user exists with the '
                     'email {}, but is not registered as faculty or '
                     'student').format(email_address)
            raise GkeepException(error)
    else:
        action = NewUserAction.NEW_USER_NEW_DB

    exists_in_db = (action == NewUserAction.NEW_DB_ROLE)

    existing_users = get_all_users()
    faculty = db.insert_faculty(Faculty(last_name, first_name, '',
                                        email_address, admin), existing_users,
                                user_exists=exists_in_db)

    gkeepd_logger.log_info('Setting up faculty user with email {}'
                           .format(email_address))

    groups = [config.keeper_group, config.faculty_group]

    setup_user(faculty.username, UserType.faculty, first_name, last_name,
               action, email_address=email_address, additional_groups=groups)
    gkeepd_logger.log_debug('Set up faculty user {}'.format(faculty.username))

    return faculty
