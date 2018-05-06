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

import json
import os
from functools import wraps

from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.system_commands import user_exists
from gkeepserver.create_user import create_user, UserType
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.server_configuration import config


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

        return '{0}, {1} ({2}) <{3}>'.format(self.last_name, self.first_name,
                                             self.username, self.email_address)

def raise_if_faculty_does_not_exist(func):
    """
    Decorator for FacultyMembers class methods that should not be called if a
    certain faculty username does not exist. Raises a FacultyError if the given
    username does not exist.

    :param func: the function to decorate
    :return: the new wrapped function
    """
    @wraps(func)
    def wrapper(self, username, *args, **kwargs):
        """
        Check to see that the faculty username exists.

        :param self: reference to a FacultyMembers object
        :param username: faculty username to check
        :param args: positional arguments to pass on
        :param kwargs: keyword arguments to pass on
        :return:
        """

        if username not in self.json_dictionary:
            raise FacultyError('There is no faculty with the username {}'
                               .format(username))

        return func(self, username, *args, **kwargs)

    return wrapper


class FacultyMembers:
    """
    This class provides functionality for adding faculty members and getting
    information about existing faculty members.
    """
    def __init__(self):
        """
        Load the current stored faculty information.
        """
        if not os.path.isfile(config.faculty_json_path):
            raise FacultyError('{} does not exist'
                               .format(config.faculty_json_path))

        self.json_dictionary = None

        try:
            with open(config.faculty_json_path) as f:
                self.json_dictionary = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise FacultyError(e)

    def write_faculty_information(self):
        """
        Write the in-memory faculty information to disk.
        """
        with open(config.faculty_json_path, 'w') as f:
            json.dump(self.json_dictionary, f)

    def add_faculty(self, last_name, first_name, email_address, admin=False):
        """
        Add a faculty user.

        :param last_name: last name of the faculty member
        :param first_name: first name of the faculty member
        :param email_address: email address of the faculty member
        :param admin: True if the faculty member should be an admin
        """

        try:
            username, _ = email_address.split('@')
        except ValueError:
            raise FacultyError('{} is not an email address'
                               .format(email_address))

        faculty_dictionary = {
            'last_name': last_name,
            'first_name': first_name,
            'email_address': email_address,
            'admin': admin,
        }

        if not user_exists(username):
            gkeepd_logger.log_info('Adding faculty user {}'.format(username))

            groups = [config.keeper_group, config.faculty_group]

            create_user(username, UserType.faculty, first_name, last_name,
                        email_address=email_address, additional_groups=groups)

            gkeepd_logger.log_debug('User created')

        self.json_dictionary[username] = faculty_dictionary
        self.write_faculty_information()

    @raise_if_faculty_does_not_exist
    def promote_to_admin(self, username):
        """
        Make a faculty member an admin user.

        :param username: username of the faculty member
        """
        self.json_dictionary[username]['admin'] = True
        self.write_faculty_information()

    @raise_if_faculty_does_not_exist
    def demote_from_admin(self, username):
        """
        Make a faculty member not an admin.

        :param username: username of the faculty member
        """
        self.json_dictionary[username]['admin'] = False
        self.write_faculty_information()

    def faculty_exists(self, username) -> bool:
        """
        Check if a faculty username exists.

        :param username: username of the faculty member
        :return: True if the username exists, False otherwise
        """
        return username in self.json_dictionary

    @raise_if_faculty_does_not_exist
    def get_email(self, username) -> str:
        """
        Get the email address of a faculty member.

        :param username: username of the faculty member
        :return: the faculty's email address
        """
        return self.json_dictionary[username]['email']

    @raise_if_faculty_does_not_exist
    def get_first_name(self, username) -> str:
        """
        Get the first name of a faculty member.

        :param username: username of the faculty member
        :return: the faculty's first name
        """
        return self.json_dictionary[username]['first_name']

    @raise_if_faculty_does_not_exist
    def get_last_name(self, username) -> str:
        """
        Get the last name of a faculty member.

        :param username: username of the faculty member
        :return: the faculty's last name
        """
        return self.json_dictionary[username]['last_name']

    @raise_if_faculty_does_not_exist
    def is_admin(self, username) -> bool:
        """
        Determine if a faculty member is an admin.

        :param username: username of the faculty member
        :return: True if the faculty member is an admin, False if not
        """
        return self.json_dictionary[username]['admin']

    @raise_if_faculty_does_not_exist
    def get_faculty_object(self, username) -> Faculty:
        """
        Get a Faculty object representing the faculty member with the given
        username.

        :param username: username of the faculty member
        :return: Faculty object representing the faculty member
        """
        last_name = self.json_dictionary[username]['last_name']
        first_name = self.json_dictionary[username]['first_name']
        email_address = self.json_dictionary[username]['email_address']
        admin = self.json_dictionary[username]['admin']

        return Faculty(last_name, first_name, username, email_address, admin)

    def get_faculty_objects(self) -> list:
        """
        Get a list of Faculty objects representing all of the faculty members.

        :return: list of Faculty objects
        """

        faculty_objects = []

        for username in self.json_dictionary:
            faculty_objects.append(self.get_faculty_object(username))

        return faculty_objects
