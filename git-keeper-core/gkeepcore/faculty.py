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


class FacultyError(Exception):
    pass


class Faculty:
    def __init__(self, last_name, first_name, username, email_address):
        self.last_name = last_name
        self.first_name = first_name
        self.username = username
        self.email_address = email_address

    @classmethod
    def from_csv_row(cls, csv_row):
        if len(csv_row) != 3:
            raise FacultyError('Not a valid faculty row: ' + str(csv_row))

        last_name, first_name, email_address = csv_row

        username, domain = email_address.split('@')

        return cls(last_name, first_name, username, email_address)

    def __repr__(self):
        return '{0}, {1} ({2}) <{3}>'.format(self.last_name, self.first_name,
                                             self.username, self.email_address)

