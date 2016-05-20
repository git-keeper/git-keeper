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

"""Provides two classes for reading from and writing to local log files
over paramiko SSH connections.

Thread-safe if the strings written to the log are <= 512 bytes.
"""

import os

from gkeepcore.log_file import LogFileReader, LogFileWriter, \
    LogFileException
from gkeepcore.subprocess_commands import append_to_file, CommandError


class LocalLogFileReader(LogFileReader):
    """Allows reading from watched local log files. Intended for use
    with a LogPollingThread.
    """
    def __init__(self, file_path):
        """
        :param file_path: path to the log file
        """
        self._file_path = file_path

    def get_file_path(self):
        """Getter for the log file path

        :return: the path to the log file
        """
        return self._file_path

    def get_data(self, seek_position=0):
        """Retrieve data from the log file from seek_position to the end

        :param seek_position: position to seek to before reading
        :return: string containing text from the file
        """
        try:
            with open(self._file_path) as f:
                f.seek(seek_position)
                return f.read()
        except OSError as e:
            raise LogFileException from e

    def get_byte_count(self):
        """Retrieve the number of bytes in the log file

        :return: number of bytes in the log file
        """
        try:
            byte_count = os.path.getsize(self._file_path)
        except OSError as e:
            raise LogFileException from e

        return byte_count


class LocalLogFileWriter(LogFileWriter):
    """Allows writing to local log files"""
    def __init__(self, file_path):
        """
        :param file_path: path to the log file
        """
        self._file_path = file_path

    def _append(self, string):
        # Appends a string to the log. Should not be called directly, use the
        # inherited log() method instead.
        try:
            append_to_file(self._file_path, string)
        except CommandError as e:
            raise LogFileException from e
