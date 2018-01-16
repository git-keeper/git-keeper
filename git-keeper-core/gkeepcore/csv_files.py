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


"""Provides two abstract base classes for reading and writing CSV files.
Allows using local and remote CSV readers and writers with the strategy
pattern.
"""

import abc

from gkeepcore.gkeep_exception import GkeepException


class CSVError(GkeepException):
    pass


class CSVReader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_rows(self):
        """Retrieve the rows from a CSV file as a list of lists"""


class CSVWriter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def write_rows(self, rows):
        """Write rows as a list of lists or tuples to a CSV file"""
