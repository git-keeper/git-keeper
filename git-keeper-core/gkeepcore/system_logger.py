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


from enum import IntEnum

from gkeepcore.log_file import LogFileWriter


class LogLevel(IntEnum):
    NONE = -1
    ERROR = 0
    WARNING = 1
    INFO = 2
    DEBUG = 3


class SystemLogger:
    def __init__(self, log_append_function):
        self._log_file_path = None
        self._writer = None
        self._log_level = None

        self._log_append_function = log_append_function

    def initialize(self, log_file_path: str, log_level=LogLevel.DEBUG):
        self._log_file_path = log_file_path
        self._writer = LogFileWriter(log_file_path, self._log_append_function)
        self._log_level = log_level

    def _cleanup_and_log(self, log_level, text: str):
        if self._log_level >= log_level:
            text = text.replace('\n', ' ')
            self._writer.log(log_level.name, text)

    def log_debug(self, text: str):
        self._cleanup_and_log(LogLevel.DEBUG, text)

    def log_info(self, text: str):
        self._cleanup_and_log(LogLevel.INFO, text)

    def log_warning(self, text: str):
        self._cleanup_and_log(LogLevel.WARNING, text)

    def log_error(self, text: str):
        self._cleanup_and_log(LogLevel.ERROR, text)
