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


"""Provides a handler for handling classes added by faculty."""


import os

from gkeepcore.csv_files import CSVError
from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import parse_faculty_class_path, user_from_log_path, \
    student_class_dir_path
from gkeepcore.shell_command import CommandError
from gkeepcore.student import students_from_csv, StudentError
from gkeepcore.system_commands import user_exists, mkdir, sudo_chown
from gkeepserver.create_user import create_user, UserType
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.server_configuration import config


class ClassAddHandler(EventHandler):
    """Handle new classes added by faculty."""

    def handle(self):
        """
        Handle adding a new class.

        Writes success or failure to the gkeepd to faculty log.

        Checks that none of the students are already in the class, creates
        non-existent student accounts, and makes directories for the class
        in each student's home directory.
        """

        # students.csv must be in place
        if not os.path.isfile(self._students_file_path):
            error = ('{0} does not exist, cannot add class'
                     .format(self._students_file_path))
            self._log_error_to_faculty(error)
            return

        # get the students from students.csv
        try:
            reader = LocalCSVReader(self._students_file_path)
            students = students_from_csv(reader)
        except (CSVError, StudentError) as e:
            self._log_error_to_faculty(str(e))
            return

        # students we need to add accounts for
        new_students = []

        # build new_students and check that existing students do not have a
        # directory for the class already
        for student in students:
            if not user_exists(student.username):
                new_students.append(student)
            else:
                class_dir_path = student_class_dir_path(student.username,
                                                        self._faculty_username,
                                                        self._class_name)
                if os.path.isdir(class_dir_path):
                    error = ('Student {0} already has a directory for class '
                             '{1}/{2}'.format(student.username,
                                              self._faculty_username,
                                              self._class_name))
                    self._log_error_to_faculty(error)
                    return

        # create new student accounts
        for student in new_students:
            create_user(student.username, UserType.student, student.first_name,
                        student.last_name, email_address=student.email_address)

        # for each student, create a directory for the class
        for student in students:
            class_dir_path = student_class_dir_path(student.username,
                                                    self._faculty_username,
                                                    self._class_name)
            try:
                mkdir(class_dir_path, sudo=True)
                sudo_chown(class_dir_path, student.username,
                           config.keeper_group)
            except CommandError as e:
                self._log_error_to_faculty(str(e))
                return

        # log success
        self._log_to_faculty('CLASS_ADDED', self._class_path)

    def __repr__(self) -> str:
        """
        Build a string representation of the event.

        :return: string representation of the event
        """

        string = 'Add class event: {0}'.format(self._payload)
        return string

    def _parse(self):
        """
        Extracts attributes from the log line.

        Raises HandlerException if the log line is not well formed.

        Sets the following attributes:

        _faculty_username - username of the faculty member
        _class_path - path to the class in the faculty's home directory
        _class_name - name of the class
        _students_file_path - path to students.csv
        """

        self._faculty_username = user_from_log_path(self._log_path)

        self._class_path = self._payload
        self._class_name = parse_faculty_class_path(self._class_path)

        if self._class_name is None:
            error = ('Malformed class path: {0}'.format(self._class_path))
            raise HandlerException(error)

        self._students_file_path = os.path.join(self._class_path,
                                                'students.csv')

    def _log_to_faculty(self, event_type, text):
        """
        Write to the gkeepd.log for the faculty member.

        :param event_type: event type
        :param text: text to write to the log
        """

        log_gkeepd_to_faculty(self._faculty_username, event_type, text)

    def _log_error_to_faculty(self, error):
        """
        Log a CLASS_ADD_ERROR message to the gkeepd.log for the faculty.

        :param error: the error message
        """

        log_text = '{0} {1}'.format(self._class_path, error)
        self._log_to_faculty('CLASS_ADD_ERROR', log_text)
