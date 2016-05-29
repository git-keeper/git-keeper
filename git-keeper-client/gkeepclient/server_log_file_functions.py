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
Provides the functions to pass to a LogFileReader in order to read

See the gkeepcore.log_file module for more information.
"""

from gkeepserver.log_polling import LogFileException
from .server_interface import server_interface, ServerInterfaceError


def byte_count_function(file_path: str) -> int:
    """
    Retrieve the number of bytes in a file on the server

    :param file_path: path to the file
    :return: number of bytes in the file

    """

    try:
        byte_count = server_interface.file_byte_count(file_path)
    except ServerInterfaceError as e:
        raise LogFileException(e)

    return byte_count


def read_bytes_function(file_path, seek_position) -> bytes:
    """
    Read from a file starting at an offset.

    :param file_path: path to the file
    :param seek_position: offset at which to start reading
    :return: data from the file as bytes
    """
    try:
        data_bytes = server_interface.read_file_bytes(file_path, seek_position)
    except ServerInterfaceError as e:
        raise LogFileException(e)

    return data_bytes
