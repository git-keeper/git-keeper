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
Provides a check_system() command to be called when starting up gkeepd.

Ensures the system is in a proper state and adds new faculty accounts.

Be sure to parse the server configuration and start the system logger before
calling check_system()

"""

import os

from pkg_resources import resource_exists, resource_string

from gkeepcore.faculty import Faculty, faculty_from_csv_file
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import user_home_dir
from gkeepcore.system_commands import (CommandError, user_exists, group_exists,
                                       sudo_add_group, mode, chmod, touch,
                                       this_user, this_group, sudo_add_user,
                                       group_owner, sudo_chown)
from gkeepserver.create_user import create_user, UserType
from gkeepserver.gkeepd_logger import gkeepd_logger as gkeepd_logger
from gkeepserver.server_configuration import config


class CheckSystemError(GkeepException):
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

    check_paths_and_permissions()
    check_faculty()


def check_paths_and_permissions():
    """
    Check that all necessary files, directories, and usernames exist, and that
    everything has proper permissions.

    Fatal errors:
        * the keeper user does not exist
        * gkeepd is not being run by the keeper user
        * the keeper group does not exist
        * gkeepd is not being run by the keeper group

    Corrected scenarios:
        * the tester user does not exist
        * the faculty group does not exist
        * the faculty log directory does not exist
        * the log snapshot file does not exist
        * run_action.sh does not exist
        * permissions are wrong on the following files/directories:
            * keeper user's home directory: 750
            * gkeepd.log: 600,
            * log snapshot file: 600
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

    # create the tester user if it does not exist
    if not user_exists(config.tester_user):
        sudo_add_user(config.tester_user)

    tester_home_dir = user_home_dir(config.tester_user)

    # make the tester's home directory owned by the keeper group
    if not group_owner(tester_home_dir) == config.keeper_group:
        gkeepd_logger.log_warning('The home directory of {} must be owned by '
                                  'the group {}, changing it now'
                                  .format(config.tester_user,
                                          config.keeper_group))
        sudo_chown(tester_home_dir, config.tester_user, config.keeper_group)

    # create the faculty and student groups if they don't exist
    for group in (config.faculty_group, config.student_group):
        if not group_exists(group):
            gkeepd_logger.log_info('Group {0} does not exist, creating it now'
                                   .format(group))

            try:
                sudo_add_group(group)
            except CommandError as e:
                raise CheckSystemError(e)

    if not os.path.isfile(config.log_snapshot_file_path):
        gkeepd_logger.log_info('{0} does not exist, creating it now'
                               .format(config.log_snapshot_file_path))
        # we can create it as an empty file
        touch(config.log_snapshot_file_path)

    required_modes = {
        config.home_dir: '750',
        tester_home_dir: '770',
        config.log_file_path: '600',
        config.log_snapshot_file_path: '600',
        config.faculty_csv_path: '600',
    }

    for path, required_mode in required_modes.items():
        if not mode(path) == required_mode:
            gkeepd_logger.log_warning('Mode of {0} must be {1}, '
                                      'changing it now'
                                      .format(path, required_mode))
            chmod(path, required_mode, sudo=True)

    if not os.path.isfile(config.gitconfig_file_path):
        write_gitconfig()

    if not os.path.isfile(config.run_action_sh_file_path):
        write_run_action_sh()


def write_gitconfig():
    """
    Write .gitconfig so that the keeper user can commit to repositories
    """

    file_text = ('[user]\n\temail = {0}\n\tname = {1}\n'
                 .format(config.from_address, config.from_name))

    try:
        with open(config.gitconfig_file_path, 'w') as f:
            f.write(file_text)
    except OSError as e:
        error = 'Error writing {0}: {1}'.format(config.gitconfig_file_path, e)
        raise CheckSystemError(error)

    gkeepd_logger.log_info('Created {0}'.format(config.gitconfig_file_path))


def write_run_action_sh():
    """Write the contents of data/run_action.sh to the proper file."""

    if not resource_exists('gkeepserver', 'data/run_action.sh'):
        raise CheckSystemError('run_action.sh does not exist in the package')

    try:
        script_text = resource_string('gkeepserver', 'data/run_action.sh')
        script_text = script_text.decode()
    except Exception as e:
        raise CheckSystemError('error reading run_action.sh data: {0}'
                               .format(e))

    try:
        with open(config.run_action_sh_file_path, 'w') as f:
            f.write(script_text)
    except OSError as e:
        error = 'error writing {0}: {1}'.format(config.run_action_sh_file_path,
                                                e)
        raise CheckSystemError(error)

    sudo_chown(config.run_action_sh_file_path, config.tester_user,
               config.keeper_group)


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


def check_faculty():
    """Read faculty.csv and add any new faculty members."""

    gkeepd_logger.log_debug('Reading faculty CSV file')

    try:
        reader = LocalCSVReader(config.faculty_csv_path)
        faculty_list = faculty_from_csv_file(reader)
    except GkeepException as e:
        raise CheckSystemError(e)

    for faculty in faculty_list:
        if not user_exists(faculty.username):
            setup_faculty(faculty)
