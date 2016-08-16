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
Provides a LogFileReader subclass ServerLogFileReader for reading from log
files on the server.

See the gkeepcore.log_file module for more information.
"""

from gkeepcore.log_file import LogFileException, LogFileReader
from .server_interface import server_interface, ServerInterfaceError


class ServerLogFileReader(LogFileReader):
    """
    Provides functionality for reading from server log files.

    server_interface must be connected to the server before use.
    """
    def get_byte_count(self) -> int:
        """
        Retrieve the size of the file in bytes.

        Raises LogFileException

        :return: number of bytes in the file
        """

        try:
            byte_count = server_interface.file_byte_count(self._file_path)
        except ServerInterfaceError as e:
            raise LogFileException(e)

        return byte_count

    def _read_bytes(self) -> bytes:
        """
        Retrieve data as bytes from the file from _seek_position to the end

        Raises LogFileException

        :return: data from the file as bytes
        """

        try:
            data_bytes = server_interface.read_file_bytes(self._file_path,
                                                          self._seek_position)
        except ServerInterfaceError as e:
            raise LogFileException(e)

        return data_bytes
