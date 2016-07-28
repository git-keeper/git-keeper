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
import os

from gkeepcore.path_utils import parse_faculty_assignment_path


class AssignmentDirectoryError(Exception):
    def __init__(self, path):
        Exception.__init__(self, '{0} does not exist'.format(path))


class AssignmentDirectory:
    """
    Stores the paths to everything in an assignment directory on the server.

    Constructor raises AssignmentDirectoryError if any of the required paths do
    not exist.

    Public attributes:

        path - path to the assignment directory
        published_flag_path - path to published flag
        class_name - name of the class
        assignment_name - name of the assignment
        email_path - path to email.txt
        base_code_repo_path - path to the base code repository
        reports_repo_path - path to the reports repository
        tests_path - path to the tests directory
        action_sh_path - path to action.sh
    """

    def __init__(self, path, check=True):
        """
        Assign attributes based on path.

        Raises AssignmentDirectoryError if check is True and any required
        paths do not exist.

        :param path: path to the assignment directory
        :param check: whether or not to check if everything exists
        """
        self.path = path
        self.published_flag_path = os.path.join(self.path, 'published')
        self.email_path = os.path.join(self.path, 'email.txt')
        self.base_code_repo_path = os.path.join(self.path, 'base_code.git')
        self.reports_repo_path = os.path.join(self.path, 'reports.git')
        self.tests_path = os.path.join(self.path, 'tests')
        self.action_sh_path = os.path.join(self.tests_path, 'action.sh')

        path_info = parse_faculty_assignment_path(path)

        if path_info is None:
            self.class_name = None
            self.assignment_name = None
        else:
            self.class_name, self.assignment_name = path_info

        if check:
            self.check()

    def check(self):
        """
        Ensure everything is in place in the assignment directory.

        Raise AssignmentDirectoryError if check fails.
        """

        if self.class_name is None or self.assignment_name is None:
            error = '{0} is not a valid assignment path'.format(self.path)
            raise AssignmentDirectoryError(error)

        # ensure all required directories exist
        for dir_path in (self.path, self.base_code_repo_path,
                         self.reports_repo_path, self.tests_path):
            if not os.path.isdir(dir_path):
                raise AssignmentDirectoryError(dir_path)

        # ensure all required files exist
        for file_path in (self.email_path, self.action_sh_path):
            if not os.path.isfile(file_path):
                raise AssignmentDirectoryError(file_path)
