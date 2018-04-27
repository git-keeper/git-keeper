# Copyright 2018 Nathan Sommer and Ben Coleman
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

from gkeepcore.system_commands import sudo_chown, chmod, mv


def write_and_install_file(contents, filename, dest_path, owner, group, mode):
    """
    Writes a file to a temporary location and then moves it to its final
    destination.

    :param contents: data to write to the file
    :param filename: name of the file to write
    :param dest_path: directory or full path to which to move the file
    :param owner: owner of the file
    :param group: group owner of the file
    :param mode: file permissions
    """

    with TemporaryDirectory() as temp_dir_path:
        temp_file_path = os.path.join(temp_dir_path, filename)

        with open(temp_file_path, 'w') as f:
            f.write(contents)

        sudo_chown(temp_file_path, owner, group)
        chmod(temp_file_path, mode, sudo=True)
        mv(temp_file_path, dest_path, sudo=True)
