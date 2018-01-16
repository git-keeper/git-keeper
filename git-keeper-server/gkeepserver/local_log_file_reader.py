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
Provides a LogFileReader subclass LocalLogFileReader for reading from log
files on the local machine.

See the gkeepcore.log_file module for more information.
"""

import os

from gkeepcore.log_file import LogFileException, LogFileReader


class LocalLogFileReader(LogFileReader):
    """Provides functionality for reading from local log files."""

    def get_byte_count(self) -> int:
        """
        Get the current size of the file in bytes

        Raises LogFileException.

        :return: number of bytes in the file
        """

        try:
            byte_count = os.path.getsize(self._file_path)
        except OSError as e:
            raise LogFileException(e)

        return byte_count

    def _read_bytes(self) -> bytes:
        """
        Retrieve data as bytes from the file from _seek_position to the end

        :return: data from the file as bytes
        """

        try:
            with open(self._file_path, 'rb') as f:
                f.seek(self._seek_position)
                data_bytes = f.read()
        except OSError as e:
            raise LogFileException(e)

        return data_bytes
