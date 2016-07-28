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
Provides a class UploadDirectory for use by both the client and server to
ensure everything is in place for an assignment directory uploaded by the
client.
"""

import os

from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import path_to_list


class UploadDirectoryError(GkeepException):
    """
    Thrown by the UploadDirectory constructor if a required file or directory
    does not exist.
    """
    def __init__(self, path):
        """
        Call superclass constructor with a message indicating path does not
        exist.

        :param path: nonexistant path
        """
        Exception.__init__(self, '{0} does not exist'.format(path))


class UploadDirectory:
    """
    Stores the paths to everything in an assignment directory uploaded or to
    be uploaded by the client.

    Constructor raises UploadDirectoryError if any of the required paths do
    not exist.

    Public attributes:

        path - path to the assignment directory
        assignment_name - name of the assignment
        email_path - path to email.txt
        base_code_path - path to the base_code directory
        tests_path = path to the tests directory
        action_sh_path - path to action.sh
    """

    def __init__(self, path):
        """
        Assign attributes based on path.

        Raise ConfigDirectoryError if any required paths do not exist.

        :param path: path to the assignment directory
        """
        self.path = path
        self.email_path = os.path.join(self.path, 'email.txt')
        self.base_code_path = os.path.join(self.path, 'base_code')
        self.tests_path = os.path.join(self.path, 'tests')
        self.action_sh_path = os.path.join(self.tests_path, 'action.sh')

        # ensure all required directories exist
        for dir_path in (self.path, self.base_code_path, self.tests_path):
            if not os.path.isdir(dir_path):
                raise UploadDirectoryError(dir_path)

        # ensure all required files exist
        for file_path in (self.email_path, self.action_sh_path):
            if not os.path.isfile(file_path):
                raise UploadDirectoryError(file_path)

        self.assignment_name = path_to_list(path)[-1]
