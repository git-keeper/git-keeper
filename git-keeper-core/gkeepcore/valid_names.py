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
Provides functions for checking to see if names of classes and assignments
are valid.
"""
import re
import string
import unicodedata

from gkeepcore.gkeep_exception import GkeepException


def validate_assignment_name(assignment_name: str):
    """
    Check that an assignment name is valid. If it is, do nothing. If not, raise
    a GkeepException.

    :param assignment_name: name of the assignment
    """
    blacklist = ['all']

    if assignment_name in blacklist:
        error = ('"{0}" is not an allowed assignment name'
                 .format(assignment_name))
        raise GkeepException(error)

    validate_assignment_or_class_name_characters(assignment_name)


def validate_class_name(class_name: str):
    """
    Check that a class name is valid. If it is, do nothing. If not, raise
    a GkeepException.

    :param class_name: name of the class
    """
    validate_assignment_or_class_name_characters(class_name)


def validate_assignment_or_class_name_characters(name: str):
    """
    Check that an assignment or class name contains only valid characters. If
    it does, do nothing. If not, raise a GkeepException.

    :param name: name of the assignment or class
    """
    valid_characters = string.ascii_letters + string.digits + '_-'

    for character in name:
        if character not in valid_characters:
            error = ('Assignment and class names may only contain ASCII '
                     'letters, digits, -, and _')
            raise GkeepException(error)


def validate_username(username: str):
    """
    Check that the provided string is a valid Linux username. Raises a
    GkeepException if it is not.

    :param username: username to validate
    """

    if not re.match(r'^[a-z][_\-.a-z0-9]*$', username):
        raise GkeepException('{} is not a valid username'.format(username))

    if len(username) > 32:
        raise GkeepException('The username {} is too long'.format(username))


def cleanup_string(dirty_string: str, is_username=False):
    """
    Clean up a string for use as a username or part of a file or directory
    name.

    Spaces and punctuation are stripped string, NFKD normalization is applied,
    and all characters are converted to lowercase.

    :param dirty_string: string to clean up
    :param is_username: True if the string is to be used as a username
    :return: clean string
    """

    s = unicodedata.normalize('NFKD', dirty_string).encode('ascii', 'ignore')
    s = s.decode('utf-8')
    s = str(re.sub(r'[^\w\s-]', '', s).strip().lower())
    s = str(re.sub(r'[-\s]+', '-', s))

    if is_username:
        if s[0] not in string.ascii_letters:
            s = 'a' + s
        if len(s) > 31:
            s = s[:31]

    return s
