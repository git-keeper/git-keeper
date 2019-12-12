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
Provides a class for representing a faculty member.

"""

from gkeepcore.csv_files import CSVReader
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.valid_names import validate_username


class FacultyError(GkeepException):
    pass


class Faculty:
    """
    Stores a faculty member's attributes.

    Attributes stored::
        last_name
        first_name
        username
        email_address

    """
    def __init__(self, last_name: str, first_name: str, username: str,
                 email_address: str):
        """
        Constructor.

        Simply set the attributes from the parameters.

        """
        self.last_name = last_name
        self.first_name = first_name
        self.username = username
        self.email_address = email_address

    @classmethod
    def from_csv_row(cls, csv_row: list):
        """
        Build a Faculty object from a CSV file row as a list

        :param csv_row: the CSV file row as a list
        :return: a new Faculty object

        """

        if len(csv_row) != 3:
            raise FacultyError('Not a valid faculty row: {0}'
                               .format(str(csv_row)))

        # remove blank spaces
        for i in range(len(csv_row)):
            csv_row[i] = csv_row[i].strip()

        last_name, first_name, email_address = csv_row

        # the faculty's username is their email address username
        try:
            username, domain = email_address.split('@')
        except ValueError:
            raise FacultyError('Not a valid email address: {0}'
                               .format(email_address))

        validate_username(username)

        return cls(last_name, first_name, username, email_address)

    def __repr__(self):
        """
        Build a string representation of a faculty member.

        Format::
            Last, First (username) <username@email.com>

        :return: string representation of the ojbect
        """

        return '{0}, {1} ({2}) <{3}>'.format(self.last_name, self.first_name,
                                             self.username, self.email_address)


def faculty_from_csv_file(csv_reader: CSVReader):
    """
    Build a list of Faculty from a CSV file reader.

    Raises FacultyError on a malformed row.

    :param csv_reader: the CSV reader
    :return: list of Faculty objects
    """
    faculty = []

    try:
        for row in csv_reader.get_rows():
            # skip blank lines
            if len(row) > 0:
                faculty.append(Faculty.from_csv_row(row))
    except GkeepException as e:
        raise FacultyError(e)

    return faculty


def faculty_from_username(username: str,
                          csv_reader: CSVReader) -> Faculty:
    """
    Build a Faculty object for the faculty with the given username from the
    given CSV reader.

    Raises FacultyError or CSVError if something goes wrong.

    :param username: username of the faculty
    :param csv_reader: CSVReader to get the faculty data from
    :return: Faculty object with the given username
    """

    for faculty in faculty_from_csv_file(csv_reader):
        if faculty.username == username:
            return faculty

    raise FacultyError('{0} not found'.format(username))
