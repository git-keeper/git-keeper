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


"""Provides 2 abstract base classes: LogFileReader and LogFileWriter"""


import abc
from time import time


class LogFileException(Exception):
    pass


class LogFileReader(metaclass=abc.ABCMeta):
    """Base class for use with a LogPollingThread"""
    def __init__(self, file_path, seek_position):
        self._file_path = file_path

        if seek_position is None:
            self._seek_position = self.get_byte_count()
        else:
            self._seek_position = seek_position

    def get_file_path(self):
        """Retrieve the path of the log file"""
        return self._file_path

    def get_seek_position(self):
        """Get the next read offset into the file"""
        return self._seek_position

    def has_new_text(self):
        """Determine if the file has grown since it was last read"""
        return self.get_byte_count() > self._seek_position

    @abc.abstractmethod
    def get_byte_count(self):
        """Retrieve the current number of bytes in the file"""

    @abc.abstractmethod
    def get_new_text(self):
        """Retrieve the data from the file, starting at seek_position"""


class LogFileWriter(metaclass=abc.ABCMeta):
    """Base class for loggers"""
    def log(self, event_type, text):
        """Log an event

        :param event_type: a string describing the event type
        :param text: the description of the event
        """
        line = '{0} {1} {2}'.format(int(time()), event_type, text)
        self._append(line)

    @abc.abstractmethod
    def _append(self, string):
        """Append the given string to the file"""
