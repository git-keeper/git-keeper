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
    def __init__(self, file_path, seek_position=None):
        """
        :param file_path: path to the log file
        :param seek_position: offset to start reading from
        """

        LogFileReader.__init__(self, file_path, seek_position)

    def get_new_text(self) -> str:
        """Retrieve new text from the log file and update the seek position.

        :return: string containing new text from the file
        """

        try:
            data_bytes = server_interface.read_file_bytes(self._file_path,
                                                          self._seek_position)
        except ServerInterfaceError as e:
            raise LogFileException(e)

        self._seek_position += len(data_bytes)

        return data_bytes.decode('utf-8')

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
