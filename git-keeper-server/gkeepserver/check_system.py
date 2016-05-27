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


"""
Provides a check_system() command to be called when starting up gkeepd.

Ensures the system is in a proper state and adds new faculty accounts.

Be sure to parse the server configuration and start the system logger before
calling check_system()

"""


import csv
import os

from gkeepcore.path_utils import user_home_dir
from gkeepserver.create_user import create_user, UserType
from gkeepserver.server_configuration import config
from gkeepcore.faculty import Faculty, FacultyError
from gkeepcore.system_commands import (CommandError, user_exists, group_exists,
                                       sudo_add_group, mode, chmod, mkdir,
                                       touch, sudo_chown, this_user,
                                       this_group)
from gkeepcore.system_logger import system_logger as gkeepd_logger


class CheckSystemError(Exception):
    """Raised for fatal errors."""
    pass


def check_system():
    """
    Check the state of the system and ensure that everything is in place so the
    server can run correctly.

    This is the only function from this module that should be called
    externally.

    Raises a CheckSystemError exception for fatal errors.

    Only call this once.
    """

    check_keeper_paths_and_permissions()
    check_faculty()


def check_keeper_paths_and_permissions():
    """
    Check that all necessary files, directories, and usernames exist, and that
    everything has proper permissions.

    Fatal errors:
        * the keeper user does not exist
        * gkeepd is not being run by the keeper user
        * the keeper group does not exist
        * gkeepd is not being run by the keeper group

    Corrected scenarios:
        * the faculty group does not exist
        * the faculty log directory does not exist
        * the log snapshot file does not exist
        * permissions are wrong on the following files/directories:
            * keeper user's home directory: 750
            * gkeepd.log: 600,
            * log snapshot file: 600
            * faculty log directory: 750
            * faculty.csv: 600

    Raises a CheckSystemError exception on fatal errors.

    """

    if not user_exists(config.keeper_user):
        raise CheckSystemError('User {0} does not exist'
                               .format(config.keeper_user))

    if this_user() != config.keeper_user:
        raise CheckSystemError('gkeepd must be running as user {0}'
                               .format(config.keeper_user))

    if not group_exists(config.keeper_group):
        raise CheckSystemError('Group {0} does not exist'
                               .format(config.keeper_group))

    if this_group() != config.keeper_group:
        raise CheckSystemError('gkeepd must be running as group {0}'
                               .format(config.keeper_group))

    # below are non-fatal conditions that can be corrected

    if not group_exists(config.faculty_group):
        gkeepd_logger.log_info('Group {0} does not exist, creating it now'
                               .format(config.faculty_group))

        try:
            sudo_add_group(config.faculty_group)
        except CommandError as e:
            raise CheckSystemError(e)

    if not os.path.isdir(config.faculty_log_dir_path):
        gkeepd_logger.log_info('{0} does not exist, creating it now'
                               .format(config.faculty_log_dir_path))

        mkdir(config.faculty_log_dir_path)

    if not os.path.isfile(config.log_snapshot_file_path):
        gkeepd_logger.log_info('{0} does not exist, creating it now'
                               .format(config.log_snapshot_file_path))
        # we can create it as an empty file
        touch(config.log_snapshot_file_path)

    required_modes = {
        config.home_dir: '750',
        config.log_file_path: '600',
        config.log_snapshot_file_path: '600',
        config.faculty_log_dir_path: '750',
        config.faculty_csv_path: '600',
    }

    for path, required_mode in required_modes.items():
        if not mode(path) == required_mode:
            gkeepd_logger.log_warning('Mode of {0} must be {1}, '
                                      'changing it now'
                                      .format(path, required_mode))
            chmod(path, required_mode)


def create_keeper_faculty_event_log(faculty: Faculty):
    """
    Create a log for the faculty member to read from.

    gkeepd writes events to this log to communicate to the faculty's client.

    Log is located at <keeper home dir>/faculty_logs/<faculty username>.log

    Log will contain a notice that it should not be edited.

    keeper user has read/write permissions, keeper group has read permissions.

    :param faculty: Faculty object representing the faculty member
    """

    log_filename = '{0}.log'.format(faculty.username)
    log_path = os.path.join(config.home_dir, 'faculty_logs', log_filename)

    log_notice = '# THIS FILE WAS AUTO-GENERATED, DO NOT EDIT!\n'

    with open(log_path, 'w+') as f:
        f.write(log_notice)

    chmod(log_path, '640')


def setup_faculty(faculty: Faculty):
    """
    Create a faculty user and set up the home directory and logging.

    :param faculty: Faculty object representing the faculty member
    """

    gkeepd_logger.log_info('New faculty: {0}'.format(faculty))

    # in addition to the faculty's default group, the faculty needs to be in
    # the keeper group and the faculty group
    groups = [config.keeper_group, config.faculty_group]

    create_user(faculty.username, UserType.faculty, faculty.first_name,
                faculty.last_name, email_address=faculty.email_address,
                additional_groups=groups)

    gkeepd_logger.log_debug('User created')

    home_dir = user_home_dir(faculty.username)
    git_keeper_dir_path = os.path.join(home_dir, 'git-keeper')

    mkdir(git_keeper_dir_path, sudo=True)
    # world readable for the handouts directory
    chmod(git_keeper_dir_path, '755', sudo=True)
    sudo_chown(git_keeper_dir_path, faculty.username, config.keeper_group)

    gkeepd_logger.log_debug('git-keeper directory created')

    create_keeper_faculty_event_log(faculty)


def check_faculty():
    """Read faculty.csv and add any new faculty members."""

    faculty_list = []

    gkeepd_logger.log_debug('Reading faculty CSV file')

    with open(config.faculty_csv_path) as f:
        reader = csv.reader(f)

        for row in reader:
            try:
                faculty_list.append(Faculty.from_csv_row(row))
            except FacultyError:
                raise CheckSystemError

    for faculty in faculty_list:
        if not user_exists(faculty.username):
            setup_faculty(faculty)


