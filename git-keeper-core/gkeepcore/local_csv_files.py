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
Provides concrete classes for reading and writing local CSV files as well
as a function for getting rows from a local CSV file.
"""

import csv

from gkeepcore.csv_files import CSVReader, CSVWriter, CSVError


def csv_rows(file_path: str) -> list:
    """
    Retrieve rows from a local CSV file.

    :param file_path: path to the file
    :return: rows as a list of lists
    """

    try:
        with open(file_path) as f:
            rows = list(csv.reader(f))
    except csv.Error:
        raise CSVError('Error reading from {0}'.format(file_path))

    return rows


class LocalCSVReader(CSVReader):
    """Allows reading from a local CSV file."""
    def __init__(self, file_path):
        """
        :param file_path: path to the CSV file to read
        """

        try:
            with open(file_path, encoding='utf-8-sig') as f:
                self._rows = list(csv.reader(f))
        except (csv.Error, OSError):
            raise CSVError('Error reading from {0}'.format(file_path))

    def get_rows(self) -> list:
        """
        Retrieve the rows from the CSV file

        :return: list of lists representing all rows from the file
        """
        return self._rows


class LocalCSVWriter(CSVWriter):
    """Allows writing to a local CSV file."""
    def __init__(self, file_path):
        """
        :param file_path: path to the CSV file to write
        """
        self._file_path = file_path

    def write_rows(self, rows):
        """
        Write rows to the file

        :param rows: list of lists (or tuples) to write
        """
        try:
            with open(self._file_path, 'w') as f:
                writer = csv.writer(f)

                for row in rows:
                    writer.writerow(row)
        except OSError as e:
            raise CSVError('Error writing to {0}'
                           .format(self._file_path))
