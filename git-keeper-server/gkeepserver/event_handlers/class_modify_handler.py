# Copyright 2016, 2017, 2018 Nathan Sommer and Ben Coleman
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


"""Provides a handler for modifying class enrollments."""

import os

from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import user_from_log_path, \
    student_class_dir_path, user_home_dir, faculty_class_dir_path, \
    class_student_csv_path
from gkeepcore.shell_command import CommandError
from gkeepcore.student import students_from_csv, Student
from gkeepcore.system_commands import user_exists, mkdir, sudo_chown, cp, chmod
from gkeepserver.assignments import get_class_assignment_dirs, \
    setup_student_assignment, StudentAssignmentError
from gkeepserver.create_user import create_user, UserType, create_student_user
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.info_update_thread import info_updater
from gkeepserver.server_configuration import config


class ClassModifyHandler(EventHandler):
    """Handle class enrollments modified by the faculty."""

    def handle(self):
        """
        Handle modifying an existing class's enrollment.

        Writes success or failure to the gkeepd to faculty log.

        Removing a student simply changes students.csv and removes the class
        directory from the student's home directory.

        Adding a student changes students.csv, creates a directory for the
        class in the student's home directory, and adds all current assignments
        for the class.
        """

        home_dir = user_home_dir(self._faculty_username)

        try:
            new_students_reader = LocalCSVReader(self._uploaded_csv_path)
            new_students_by_username = {}
            for student in students_from_csv(new_students_reader):
                if student.username == self._faculty_username:
                    raise HandlerException('You cannot add yourself to your '
                                           'own class')
                new_students_by_username[student.username] = student

            old_students_path = class_student_csv_path(self._class_name,
                                                       home_dir)
            old_students_reader = LocalCSVReader(old_students_path)
            old_students_by_username = {}
            for student in students_from_csv(old_students_reader):
                old_students_by_username[student.username] = student

            self._copy_csv_to_class_dir()
            self._add_class_students(old_students_by_username,
                                     new_students_by_username)

            info_updater.enqueue_class_scan(self._faculty_username,
                                            self._class_name)

            self._log_to_faculty('CLASS_MODIFY_SUCCESS', self._class_name)
        except Exception as e:
            self._log_error_to_faculty(str(e))
            gkeepd_logger.log_warning('Class modify failed: {0}'.format(e))

    def _copy_csv_to_class_dir(self):
        # copy the CSV file to its final destination

        # uploaded CSV must be in place
        if not os.path.isfile(self._uploaded_csv_path):
            error = ('{0} does not exist, cannot modify class'
                     .format(self._uploaded_csv_path))
            raise HandlerException(error)

        home_dir = user_home_dir(self._faculty_username)

        faculty_class_path = faculty_class_dir_path(self._class_name, home_dir)

        # copy the CSV and fix permissions
        try:
            final_csv_path = class_student_csv_path(self._class_name, home_dir)
            cp(self._uploaded_csv_path, final_csv_path, sudo=True)
            chmod(faculty_class_path, '750', sudo=True)
            sudo_chown(faculty_class_path, self._faculty_username,
                       config.keeper_group, recursive=True)
        except CommandError as e:
            error = 'Error copying class CSV: {0}'.format(e)
            raise HandlerException(error)

    def _add_class_students(self, old_students_by_username: dict,
                            new_students_by_username: dict):
        # create sets so we can take the set difference
        old_usernames = set([username
                             for username in old_students_by_username])
        new_usernames = set([username
                             for username in new_students_by_username])

        # add students
        for username in new_usernames - old_usernames:
            self._add_class_student(new_students_by_username[username])

    def _add_class_student(self, student: Student):
        # Add the student user if it does not already exist, create the class
        # directory, and add all assignments.

        # add the user if necessary
        if not user_exists(student.username):
            try:
                create_student_user(student)
            except Exception as e:
                error = 'Error adding user {0}: {1}'.format(student.username,
                                                            e)
                raise HandlerException(error)

        home_dir = user_home_dir(student.username)

        class_dir_path = student_class_dir_path(self._faculty_username,
                                                self._class_name, home_dir)
        # create the class directory
        try:
            mkdir(class_dir_path, sudo=True)
            sudo_chown(class_dir_path, student.username,
                       config.keeper_group)
        except Exception as e:
            warning = ('Error creating student class directory for {0} '
                       'in class {1}: {2}'.format(student, self._class_name,
                                                  e))
            self._log_warning_to_faculty(warning)
            gkeepd_logger.log_warning(warning)

        # add all assignments
        for assignment_dir in get_class_assignment_dirs(self._faculty_username,
                                                        self._class_name):
            # do not setup the assignment if it is not yet published
            if not assignment_dir.is_published():
                continue

            try:
                setup_student_assignment(assignment_dir, student,
                                         self._faculty_username)
            except StudentAssignmentError as e:
                warning = ('Error setting up student assignment repository '
                           'for {0} {1} {2}: {3}'
                           .format(student, self._class_name,
                                   assignment_dir.assignment_name, e))
                self._log_warning_to_faculty(warning)
                gkeepd_logger.log_warning(warning)

    def __repr__(self) -> str:
        """
        Build a string representation of the event.

        :return: string representation of the event
        """

        string = 'Modify class event: {0}'.format(self._payload)
        return string

    def _parse_payload(self):
        """
        Extracts attributes from the log line.

        Raises HandlerException if the log line is not well formed.

        Sets the following attributes:

        _faculty_username - username of the faculty member
        _class_name - name of the class
        _uploaded_csv_path - path to CSV file uploaded by the faculty
        """

        self._faculty_username = user_from_log_path(self._log_path)

        try:
            self._class_name, self._uploaded_csv_path =\
                self._payload.split(' ')
        except ValueError:
            error = ('Payload must look like <class name> <uploaded CSV path> '
                     ' not {0}'.format(self._payload))
            raise HandlerException(error)

    def _log_to_faculty(self, event_type, text):
        """
        Write to the gkeepd.log for the faculty member.

        :param event_type: event type
        :param text: text to write to the log
        """

        log_gkeepd_to_faculty(self._faculty_username, event_type, text)

    def _log_error_to_faculty(self, error):
        """
        Log a CLASS_MODIFY_ERROR message to the gkeepd.log for the faculty.

        :param error: the error message
        """

        self._log_to_faculty('CLASS_MODIFY_ERROR', error)

    def _log_warning_to_faculty(self, warning):
        """
        Log a CLASS_MODIFY_WARNING message to the gkeepd.log for the faculty.

        :param warning: the warning message
        """

        self._log_to_faculty('CLASS_MODIFY_WARNING', warning)
