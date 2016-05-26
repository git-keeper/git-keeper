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
from tempfile import TemporaryDirectory

from gkeepcore.log_polling import log_poller
from gkeepcore.path_utils import user_home_dir, user_log_path
from gkeepcore.system_logger import system_logger as logger
from gkeepcore.system_commands import sudo_add_user, sudo_set_password, chmod, \
    mv, sudo_chown
from gkeepserver.server_configuration import config
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.generate_password import generate_password
from gkeepserver.server_email import Email


def initialize_user_log(username):
    home_dir = user_home_dir(username)
    log_path = user_log_path(home_dir, username)

    log_notice = '# THIS FILE WAS AUTO-GENERATED, DO NOT EDIT!\n'

    with TemporaryDirectory() as temp_dir_path:
        temp_log_path = os.path.join(temp_dir_path, os.path.basename(log_path))

        with open(temp_log_path, 'w+') as f:
            f.write(log_notice)

        mv(temp_log_path, log_path, sudo=True)

    sudo_chown(log_path, username, config.keeper_group)
    chmod(log_path, '640', sudo=True)

    log_poller.watch_log_file(log_path)


def create_user(username, first_name, last_name, email_address=None,
                additional_groups=None):
    logger.log_info('Creating user {0}'.format(username))

    sudo_add_user(username, additional_groups)

    password = generate_password()
    sudo_set_password(username, password)

    initialize_user_log(username)

    if email_address is not None:
        subject = 'New git-keeper account'
        body = ('Hello {0},\n\n'
                'An account has been created for you on the '
                'git-keeper server. Here are your credentials:\n\n'
                'Username: {1}\n'
                'Password: {2}\n\n'
                'If you have any questions, please contact your instructor '
                'rather than respond to this email directly.\n\n'
                'Enjoy!'.format(first_name, username, password))

        email_sender.enqueue(Email(email_address, subject, body))
