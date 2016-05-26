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


import csv
import os

from gkeepserver.server_configuration import config
from gkeepcore.faculty import Faculty, FacultyError
from gkeepcore.system_commands import (CommandError, user_exists, group_exists,
                                       sudo_add_group, mode, chmod, mkdir,
                                       sudo_add_user, sudo_set_password, touch)
from gkeepcore.system_logger import system_logger as gkeepd_logger
from gkeepserver.generate_password import generate_password
from gkeepserver.server_email import Email
from gkeepserver.email_sender_thread import email_sender


class CheckSystemError(Exception):
    pass


def check_keeper_permissions():
    if not user_exists(config.keeper_user):
        raise CheckSystemError('User {0} does not exist'
                               .format(config.keeper_user))

    if not group_exists(config.keeper_group):
        raise CheckSystemError('Group {0} does not exist'
                               .format(config.keeper_group))

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


def add_faculty(faculty: Faculty):
    gkeepd_logger.log_info('Creating user {0}'.format(faculty.username))

    groups = [config.faculty_group, config.keeper_group]

    sudo_add_user(faculty.username, groups)

    password = generate_password()

    sudo_set_password(faculty.username, password)

    subject = 'New git-keeper account'
    body = ('Hello {0}\n\nAn account has been created for you on the '
            'git-keeper server. Here are your credentials:\n\n'
            'Username: {1}\n'
            'Password: {2}\n\n'
            'Enjoy!'.format(faculty.first_name, faculty.username, password))

    email_sender.enqueue(Email(faculty.email_address, subject, body))


def check_system():
    check_keeper_permissions()

    faculty_list = []

    gkeepd_logger.log_debug('Reading faculty CSV file')

    with open(config.faculty_csv_path) as f:
        reader = csv.reader(f)

        for row in reader:
            faculty_list.append(Faculty.from_csv_row(row))

    new_faculty_list = []

    for faculty in faculty_list:
        if not user_exists(faculty.username):
            gkeepd_logger.log_info('New faculty: {0}'.format(faculty))
            add_faculty(faculty)
