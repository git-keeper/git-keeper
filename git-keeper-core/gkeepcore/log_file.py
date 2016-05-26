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
Provides 2 classes for log files: LogFileReader and LogFileWriter

"""


class LogFileException(Exception):
    pass


class LogFileReader:
    """Base class for use with a LogPollingThread"""
    def __init__(self, file_path: str, byte_count_function, read_bytes_function,
                 seek_position=None):
        self._file_path = file_path

        self._byte_count_function = byte_count_function
        self._read_bytes_function = read_bytes_function

        if seek_position is None:
            self._seek_position = self.get_byte_count()
        else:
            self._seek_position = seek_position

    def get_file_path(self) -> str:
        """Retrieve the path of the log file"""
        return self._file_path

    def get_seek_position(self) -> int:
        """Get the next read offset into the file"""
        return self._seek_position

    def has_new_text(self) -> bool:
        """Determine if the file has grown since it was last read"""
        return self.get_byte_count() > self._seek_position

    def get_byte_count(self) -> int:
        return self._byte_count_function(self._file_path)

    def get_new_text(self) -> str:
        """Retrieve the data from the file, starting at seek_position"""

        data_bytes = self._read_bytes_function(self._file_path,
                                               self._seek_position)

        self._seek_position += len(data_bytes)

        return data_bytes.decode('utf-8')


class LogFileWriter:
    def __init__(self, file_path: str, log_append_function):
        self._file_path = file_path
        self._log_append_function = log_append_function

    def log(self, event_type, text):
        """Log an event

        :param event_type: a string describing the event type
        :param text: the description of the event
        """

        self._log_append_function(self._file_path, event_type, text)
