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

"""Provides two classes for reading from and writing to log files on the
server.

Thread-safe if the strings written to the log are <= 512 bytes.

See the gkeepcore.log_file module for more information.
"""


from gkeepclient.server_interface import server_interface, ServerInterfaceError
from gkeepcore.log_file import LogFileReader, LogFileWriter,\
    LogFileException


class ServerLogFileReader(LogFileReader):
    """Allows reading from watched log files on the server. Intended for use
    with a LogPollingThread.
    """
    def __init__(self, file_path):
        """
        :param file_path: path to the log file
        """
        self._file_path = file_path

    def get_data(self, seek_position=0) -> str:
        """Retrieve data from the log file from seek_position to the end

        :param seek_position: position to seek to before reading
        :return: string containing text from the file
        """

        try:
            data = server_interface.read_file(self._file_path, seek_position)
        except ServerInterfaceError as e:
            raise LogFileException(e)

        return data

    def get_file_path(self) -> str:
        """Getter for the log file path

        :return: the path to the log file
        """

        return self._file_path

    def get_byte_count(self) -> int:
        """Retrieve the number of bytes in the log file

        :return: number of bytes in the log file
        """

        try:
            byte_count = server_interface.get_file_byte_count(self._file_path)
        except ServerInterfaceError as e:
            raise LogFileException(e)

        return byte_count


class ServerLogFileWriter(LogFileWriter):
    """Allows writing to log files on the server."""
    def __init__(self, file_path):
        """
        :param file_path: path to the log file
        """
        self._file_path = file_path

    def _append(self, string):
        # Appends a string to the log. Should not be called directly, use the
        # inherited log() method instead.
        try:
            server_interface.append_to_file(self._file_path, string)
        except ServerInterfaceError as e:
            raise LogFileException(e)
