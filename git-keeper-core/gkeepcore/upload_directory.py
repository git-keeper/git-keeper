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
Provides a class UploadDirectory for use by both the client and server to
ensure everything is in place for an assignment directory uploaded by the
client.
"""

import os

from gkeepcore.action_scripts import get_action_script_and_interpreter
from gkeepcore.assignment_config import AssignmentConfig
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import path_to_assignment_name


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
        action_script_path - path to action script
        action_script_interpreter - name of interpreter to run action script
        assignment_config_path - path to assignment.cfg (if present)
    """

    def __init__(self, path, check=True):
        """
        Assign attributes based on path.

        Raise ConfigDirectoryError if any required paths do not exist.  Also
        if assignment.cfg is present, this exception is raised if there
        is an error in the file.

        :param path: path to the assignment directory
        :param check: if True, raise an exception if any files or directories
         do not exist
        """
        self.path = path
        self.email_path = os.path.join(self.path, 'email.txt')
        self.base_code_path = os.path.join(self.path, 'base_code')
        self.tests_path = os.path.join(self.path, 'tests')
        self.config_path = os.path.join(self.path, 'assignment.cfg')

        self.assignment_name = path_to_assignment_name(self.path)

        self.action_script, self.action_script_interpreter = \
            get_action_script_and_interpreter(self.tests_path)

        if self.action_script is not None:
            self.action_script_path = os.path.join(self.tests_path,
                                                   self.action_script)
        else:
            self.action_script_path = None

        if check:
            self.action_script, self.action_script_interpreter = \
                get_action_script_and_interpreter(self.tests_path)

            if self.action_script is None:
                raise UploadDirectoryError('action script')

            # ensure all required directories exist
            for dir_path in (self.path, self.base_code_path, self.tests_path):
                if not os.path.isdir(dir_path):
                    raise UploadDirectoryError(dir_path)

            # ensure email.txt exists
            if not os.path.isfile(self.email_path):
                raise UploadDirectoryError(self.email_path)

            # Verify that the appropriate fields are present in assignment.cfg
            # if it exists.
            if os.path.exists(self.config_path):
                AssignmentConfig(self.config_path)
