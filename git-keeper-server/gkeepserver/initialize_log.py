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
Provides the function intialize_log() for creating a log file with a header
that warns against editing the file.
"""

import os
from tempfile import TemporaryDirectory

from gkeepcore.system_commands import mv, sudo_chown, chmod


def initialize_log(log_path, user_owner, group_owner, mode):
    """
    Create a log file with a header that warns against editing the file.

    The file might need to be in a directory that the keeper user does not own,
    so it is first created in a temporary directory and then moved into place.

    :param log_path: path to the log file
    :param user_owner: user that owns the file
    :param group_owner: group that owns the file
    :param mode: permissions for the file
    """

    # the starting contents of the log file
    log_notice = '# THIS FILE WAS AUTO-GENERATED, DO NOT EDIT!\n'

    # create the log file in a temporary directory since we don't have
    # permission to write directly to the user's log.
    with TemporaryDirectory() as temp_dir_path:
        temp_log_path = os.path.join(temp_dir_path, os.path.basename(log_path))

        with open(temp_log_path, 'w+') as f:
            f.write(log_notice)

        # move the log into place after writing
        mv(temp_log_path, log_path, sudo=True)

    # fix permissions and ownership
    sudo_chown(log_path, user_owner, group_owner)
    chmod(log_path, mode, sudo=True)
