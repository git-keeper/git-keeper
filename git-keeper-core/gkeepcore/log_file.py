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
It is an abstract class, different concrete classes allow reading from local
or remote logs.

log_append_command() builds a shell command for appending to a log.

"""

import abc
import re
from shlex import quote

from gkeepcore.gkeep_exception import GkeepException

# keep the log line to 4KB or less to maintain write atomicity
MAX_LOG_LINE_LENGTH = 4096


class LogFileException(GkeepException):
    """
    Raised if anything goes wrong with the log files.
    """
    pass


class LogEvent:
    """
    Stores the timestamp, event type, and payload from a log line.
    """
    def __init__(self, log_line: str):
        """
        Parse the log line and store the components as attributes.

        A log line should look like this:
            <timestamp> <event type> <payload>

        Raises a LogFileException if the line does not parse correctly.

        :param log_line: line from a log file
        """
        match = re.match('(\d+.\d+) (\w+) (.*)', log_line)

        if match is None:
            error = ('Log line does not look like an event: {0}'
                     .format(log_line))
            raise LogFileException(error)

        self.timestamp, self.event_type, self.payload = match.groups()

        try:
            self.timestamp = float(self.timestamp)
        except ValueError:
            raise LogFileException('{0} is not a valid timestamp'
                                   .format(self.timestamp))

    @classmethod
    def from_values(cls, timestamp: float, event_type: str, payload: str):
        """
        Create a LogEvent from the values that are usually parsed from a log
        line rather than the line itself.

        :param timestamp: floating point timestamp
        :param event_type: type of the event
        :param payload: payload of the event
        :return: LogEvent object
        """

        log_line = '{0} {1} {2}'.format(str(timestamp), event_type, payload)

        return cls(log_line)


class LogFileReader(metaclass=abc.ABCMeta):
    """
    Base class for creating objects to be used by a LogPollingThread to read
    log files.
    """

    def __init__(self, file_path: str, seek_position=None):
        """
        Initialize attributes.

        :param file_path: path to the log file
        :param seek_position: where in the file to start reading. None to go to
         the end and only read anything new
        """
        self._file_path = file_path

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

    def has_new_lines(self) -> bool:
        """
        Determine if the file has grown since it was last read.

        :return: True if there is new text in the file to read, False otherwise
        """
        return self.get_byte_count() > self._seek_position

    def get_new_lines(self) -> list:
        """
        Retrieve lines from the file starting at _seek_position.

        Updates _seek_position so the next read will start after this one.

        Uses the function provided to the constructor.

        :return: a list of strings representing each new line
        """

        if not self.has_new_lines():
            return []

        # get the data as bytes so we can accurately update the seek position
        data_bytes = self._read_bytes()

        # move the seek position to the end of the file
        self._seek_position += len(data_bytes)

        # convert to a string
        data_string = data_bytes.decode('utf-8')

        # split on newlines and return the list
        return data_string.strip().split('\n')

    def get_new_events(self) -> list:
        """
        Like get_new_lines() but parses the lines and returns a list of
        LogEvent objects instead.

        Raises LogFileException if anything goes wrong.

        :return: a list of LogEvent objects
        """

        events = []

        for line in self.get_new_lines():
            events.append(LogEvent(line))

        return events

    @abc.abstractmethod
    def get_byte_count(self) -> int:
        """
        Get the current size of the file in bytes.

        :return: the current size of the file in bytes
        """

    @abc.abstractmethod
    def _read_bytes(self) -> bytes:
        """
        Retrieve data as bytes from the file from _seek_position to the end

        :return: data from the file as bytes
        """


def log_append_command(file_path: str, item_type: str, text: str,
                       human_readable=False):
    """
    Create a shell command which will append data to a log file.

    After the command is run, a string of the following form will be appended
    to the log file:

    <timestamp> <item type> <text>

    If the text contains any newline characters they will each be replaced by
    two spaces, so that the logged item is on a single line.

    The date command line utility is used to generate the timestamp. The
    system running gkeepd must have a date utility that supports nanosecond
    precision with the %N format specifier, such as GNU's date.

    If human_readable is True, the following format will be used:

        date -u +%Y-%m-%d-%H:%M:%S.%N

    If human_readable is False, the following format will be used:

        date -u +%s.%N

    The 5 least significant digits of the timestamp are truncated. The text
    will be truncated if the total length of the line is longer than
    MAX_LOG_LINE_LENGTH.

    :param file_path: path to the log file
    :param item_type: a string describing the event type
    :param text: the payload of the event
    :param human_readable: If True, the timestamp will be a human-readable
      timestamp, otherwise it will use epoch time
    :return: a shell command as a string which will append to the log
    """

    text = text.replace('\n', '  ')
    text = text.replace('"', '\\"')

    if human_readable:
        timestamp_format = '%Y-%m-%d-%H:%M:%S.%N'
        time_length = 24
    else:
        timestamp_format = '%s.%N'
        time_length = 15

    type_length = len(item_type.encode())
    text_length = len(text.encode())
    spacing_length = 2

    total_length = time_length + type_length + text_length + spacing_length

    if total_length > MAX_LOG_LINE_LENGTH:
        # truncate the text and append '...' to indicate that it was truncated
        diff = total_length - MAX_LOG_LINE_LENGTH
        text = text[:len(text) - diff - 3] + '...'

    quoted_path = quote(file_path)

    command = ('echo "$(date -u +{3} | '
               'cut -c 1-{4}) {0} {1}" >> {2}'.format(item_type, text,
                                                      quoted_path,
                                                      timestamp_format,
                                                      time_length))

    return command
