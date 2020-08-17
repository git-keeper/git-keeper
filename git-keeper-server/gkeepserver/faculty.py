# Copyright 2016, 2018 Nathan Sommer and Ben Coleman
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
Provides a class for representing a faculty member, and a class for working
with all faculty members.
"""

from gkeepcore.gkeep_exception import GkeepException


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
        admin

    """
    def __init__(self, last_name: str, first_name: str, username: str,
                 email_address: str, admin: bool):
        """
        Constructor.

        Simply set the attributes from the parameters.

        """
        self.last_name = last_name
        self.first_name = first_name
        self.username = username
        self.email_address = email_address
        self.admin = admin

    def __repr__(self):
        """
        Build a string representation of a faculty member.

        Format::
            Last, First (username) <username@email.com>

        :return: string representation of the ojbect
        """

        repr = '{0}, {1} ({2}) <{3}>'.format(self.last_name, self.first_name,
                                             self.username, self.email_address)
        if self.admin:
            repr += ' (admin)'

        return repr

    def __eq__(self, other):
        """
        Test equality of two Faculty objects.

        :param other: the other Faculty object
        :return: True if equal, False if not
        """

        return (self.last_name == other.last_name and
                self.first_name == other.first_name and
                self.username == other.username and
                self.email_address == other.email_address and
                self.admin == other.admin)
