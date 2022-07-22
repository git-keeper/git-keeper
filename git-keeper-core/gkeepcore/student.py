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
Provides a class for representing a student and a function for building a
list of students from a CSV file.
"""

from gkeepcore.csv_files import CSVReader
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.valid_names import validate_username, cleanup_string


class StudentError(GkeepException):
    pass


class Student:
    """
    Stores a student's attributes.

    Attributes stored:
        last_name
        first_name
        username
        email_address

    """
    def __init__(self, last_name: str, first_name: str, username: str,
                 email_address: str):
        """
        Constructor

        Simply set the attributes from the parameters.

        """
        self.last_name = last_name
        self.first_name = first_name
        self.username = username
        self.email_address = email_address

    @classmethod
    def from_csv_row(cls, csv_row: list):
        """
        Build a Student object form a CSV file row as a list.

        :param csv_row: the CSV file row as a list
        :return: a new Student object

        """

        if len(csv_row) != 3:
            raise StudentError('Not a valid student row: ' + str(csv_row))

        # remove blank spaces
        for i in range(len(csv_row)):
            csv_row[i] = csv_row[i].strip()

        last_name, first_name, email_address = csv_row

        # FIXME - need to handle email address and username mapping
        split_email = email_address.split('@')

        try:
            username, domain = split_email
        except:
            error = ('{0} does not appear to be a valid email address'
                     .format(email_address))
            raise StudentError(error)

        return cls(last_name, first_name, username, email_address)

    def __repr__(self) -> str:
        """
        Build a string representation of a student.

        Format:

            Last, First <username@example.com>

        :return: string representation of the object
        """

        return '{0}, {1} <{2}>'.format(self.last_name, self.first_name,
                                       self.email_address)

    def __eq__(self, other):
        return (self.username == other.username and
                self.email_address == other.email_address and
                self.last_name == other.last_name and
                self.first_name == other.first_name)

    def get_last_first_username(self) -> str:
        """
        Build a string of the following form:

            last_first_username

        Spaces and punctuation are stripped out of the names, NFKD
        normalization is applied, and all characters are converted to
        lowercase.

        This can be used to create directories or filenames to store student
        data.

        :return: a last_first_username string representation of a student
        """

        clean_first_name = cleanup_string(self.first_name)
        clean_last_name = cleanup_string(self.last_name)

        return '{0}_{1}_{2}'.format(clean_last_name, clean_first_name,
                                    self.username)


def students_from_csv(reader: CSVReader) -> list:
    """
    Build a list of students from a CSV file.

    Raises CSVError if there was a problem with the CSV file.

    Raises StudentError if there was a problem creating a student from a row
    in the file.

    :param reader: CSVReader object for getting rows
    :return: list of students from the file
    """

    students = []
    emails = []

    for row in reader.get_rows():
        if len(row) > 0:
            student = Student.from_csv_row(row)
            if student.email_address in emails:
                raise StudentError('{} appears more than once'.format(student.email_address))
            else:
                students.append(student)
                emails.append(student.email_address)

    return students


def student_from_username(username: str,
                          csv_reader: CSVReader) -> Student:
    """
    Build a Student object for the student with the given username from the
    given CSV reader.

    Raises StudentError or CSVError if something goes wrong.

    :param username: username of the student
    :param csv_reader: CSVReader to get the student data from
    :return: Student object with the given username
    """

    for student in students_from_csv(csv_reader):
        if student.username == username:
            return student

    raise StudentError('{0} not found'.format(username))
