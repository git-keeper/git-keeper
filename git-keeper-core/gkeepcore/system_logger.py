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


import abc


class SystemLogger(metaclass=abc.ABCMeta):
    def __init__(self):
        self._log_file_path = None
        self._writer = None

    @abc.abstractmethod
    def initialize(self, log_file_path: str):
        """
        Store the log file path and initialize the writer.

        The writer must have a method with the following signature:
                log(log_item_type, text)

        The abstract class LogFileWriter was designed for this.
        """

    def _cleanup_and_log(self, log_item_type: str, text: str):
        text = text.replace('\n', ' ')
        self._writer.log(log_item_type, text)

    def log_info(self, text: str):
        self._cleanup_and_log('INFO', text)

    def log_warning(self, text: str):
        self._cleanup_and_log('WARNING', text)

    def log_error(self, text: str):
        self._cleanup_and_log('ERROR', text)
