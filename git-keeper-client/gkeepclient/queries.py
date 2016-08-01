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
Provides functions for querying the server for information and printing the
query results.
"""


from gkeepclient.client_function_decorators import config_parsed, \
    server_interface_connected
from gkeepclient.server_interface import server_interface


@config_parsed
@server_interface_connected
def list_classes():
    """Print the names of all the classes owned by the faculty."""

    for class_name in server_interface.get_classes():
        print(class_name)


@config_parsed
@server_interface_connected
def list_assignments():
    """
    Print the names of all the assignments owned by the faculty, grouped by
    class.
    """

    for class_name in server_interface.get_classes():
        print(class_name, ':', sep='')

        for assignment_name in server_interface.get_assignments(class_name):
            print(assignment_name)

        print()


@config_parsed
@server_interface_connected
def list_students():
    """
    Print all the students in classes owned by the faculty, grouped by class.
    """

    for class_name in server_interface.get_classes():
        print(class_name, ':', sep='')

        for student in server_interface.get_students(class_name):
            print(student)

        print()
