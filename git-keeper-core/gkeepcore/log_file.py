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
Provides functionality for reading and writing log files.

LogFileReader is used by log file pollers for monitoring and reading log files.

log_append_command() builds a shell command for appending to a log.

"""
from shlex import quote


class LogFileException(Exception):
    """
    Raised if anything goes wrong with the log files.
    """
    pass


class LogFileReader:
    """
    Used to create objects to be used by a LogPollingThread to read log files.

    A LogFileReader object can read local or remote files, depending on what
    functions are passed to the constructor.

    """

    def __init__(self, file_path: str, byte_count_function, read_bytes_function,
                 seek_position=None):
        """
        Constructor.

        Needs 2 functions with these signatures:
            byte_count_function(file_path: str) -> int
            read_bytes_function(file_path: str, seek_position: int) -> bytes

        This allows a LogFileReader to read local or remote files depending
        on which functions were passed in.

        :param file_path: path to the log file
        :param byte_count_function: function for getting the file's size
        :param read_bytes_function: function for reading the file as bytes
        :param seek_position: where in the file to start reading. None to go to
         the end and only read anything new
        """
        self._file_path = file_path

        self._byte_count_function = byte_count_function
        self._read_bytes_function = read_bytes_function

        if seek_position is None:
            # seek to the end
            self._seek_position = self.get_byte_count()
        else:
            self._seek_position = seek_position

    def get_file_path(self) -> str:
        """
        Get the path of the log file

        :return: path of the log file
        """
        return self._file_path

    def get_seek_position(self) -> int:
        """
        Get the next read offset into the file.

        :return: the current seek position
        """
        return self._seek_position

    def has_new_text(self) -> bool:
        """
        Determine if the file has grown since it was last read.

        :return: True if there is new text in the file to read, False otherwise
        """
        return self.get_byte_count() > self._seek_position

    def get_byte_count(self) -> int:
        """
        Get the current size of the file in bytes.

        Uses the function which was provided to the constructor.

        :return: the current size of the file in bytes
        """
        return self._byte_count_function(self._file_path)

    def get_new_text(self) -> str:
        """
        Retrieve data from the file as a string, starting at _seek_position.

        Updates _seek_position so the next read will start after this one.

        Uses the function provided to the constructor.

        :return: new text from the file
        """

        # get the data as bytes so we can accurately update the seek position
        data_bytes = self._read_bytes_function(self._file_path,
                                               self._seek_position)

        # move the seek position to the end of the file
        self._seek_position += len(data_bytes)

        # convert to a string when returning
        return data_bytes.decode('utf-8')


def log_append_command(file_path: str, item_type: str, text: str):
    """
    Create a shell command to append to a log file.

    :param file_path: path to the log file
    :param item_type: a string describing the event type
    :param text: the payload of the event
    :return: a shell command as a string which will append to the log
    """

    # keep the log line to 4KB or less to maintain write atomicity
    max_length = 4096

    time_length = 15
    type_length = len(item_type.encode())
    text_length = len(text.encode())
    spacing_length = 2

    total_length = time_length + type_length + text_length + spacing_length

    if total_length > max_length:
        diff = total_length - max_length
        text = text[:len(text) - diff - 3] + '...'

    quoted_path = quote(file_path)

    command = ('echo "$(date +%s.%N | '
               'cut -c 1-15) {0} {1}" >> {2}'.format(item_type, text,
                                                     quoted_path))

    return command
