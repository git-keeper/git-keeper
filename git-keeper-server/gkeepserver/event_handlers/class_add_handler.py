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


"""Provides a handler for handling classes added by faculty."""

import os

from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import user_from_log_path, student_class_dir_path, \
    user_home_dir
from gkeepcore.shell_command import CommandError
from gkeepcore.student import students_from_csv
from gkeepcore.system_commands import user_exists, mkdir, sudo_chown
from gkeepcore.valid_names import validate_class_name
from gkeepserver.create_user import create_student_user
from gkeepserver.database import db, DatabaseException
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.info_update_thread import info_updater
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

        try:
            validate_class_name(self._class_name)
            reader = LocalCSVReader(self._uploaded_csv_path)
            students = students_from_csv(reader)
            faculty = db.get_faculty_by_username(self._faculty_username)

            for student in students:
                if student.email_address == faculty.email_address:
                    raise HandlerException('You cannot add yourself to your '
                                           'own class')

            db.insert_class(self._class_name, self._faculty_username)

            self._setup_and_add_students(students)

            info_updater.enqueue_class_scan(self._faculty_username,
                                            self._class_name)

            self._log_to_faculty('CLASS_ADD_SUCCESS', self._class_name)
        except Exception as e:
            self._log_error_to_faculty(str(e))
            gkeepd_logger.log_warning('Class add failed: {0}'.format(e))

    def _setup_and_add_students(self, students):
        # Add class directory in students' home directories. Add student
        # accounts if necessary.

        # students we need to add accounts for
        new_students = []

        # build new_students and check that existing students do not have a
        # directory for the class already
        for student in students:
            try:
                # update the Student object from the database, in case the
                # student's username is not the email username
                student = db.get_student_by_email(student.email_address)
                home_dir = user_home_dir(student.username)
                class_dir_path = student_class_dir_path(self._faculty_username,
                                                        self._class_name,
                                                        home_dir)
                if os.path.isdir(class_dir_path):
                    error = ('Student {0} already has a directory for class '
                             '{1}/{2}'.format(student.username,
                                              self._faculty_username,
                                              self._class_name))
                    raise HandlerException(error)
            except DatabaseException:
                new_students.append(student)

        # create new student accounts
        for student in new_students:
            try:
                student.username = db.insert_student(student)
                if not user_exists(student.username):
                    create_student_user(student)
            except Exception as e:
                error = 'Error adding user {0}: {1}'.format(student.username,
                                                            e)
                raise HandlerException(error)

        # for each student, create a directory for the class
        for student in students:
            home_dir = user_home_dir(student.username)

            class_dir_path = student_class_dir_path(self._faculty_username,
                                                    self._class_name,
                                                    home_dir)
            try:
                mkdir(class_dir_path, sudo=True)
                sudo_chown(class_dir_path, student.username,
                           config.keeper_group)
            except CommandError as e:
                warning = ('Error creating student class directory for {0} '
                           'in class {1}: {2}'.format(student,
                                                      self._class_name,
                                                      e))
                self._log_warning_to_faculty(warning)
                gkeepd_logger.log_warning(warning)

        for student in students:
            db.add_student_to_class(self._class_name, student.username,
                                    self._faculty_username)

    def __repr__(self) -> str:
        """
        Build a string representation of the event.

        :return: string representation of the event
        """

        string = 'Add class event: {0}'.format(self._payload)
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
        Log a CLASS_ADD_ERROR message to the gkeepd.log for the faculty.

        :param error: the error message
        """

        self._log_to_faculty('CLASS_ADD_ERROR', error)


    def _log_warning_to_faculty(self, warning):
        """
        Log a CLASS_MODIFY_WARNING message to the gkeepd.log for the faculty.

        :param warning: the warning message
        """

        self._log_to_faculty('CLASS_ADD_WARNING', warning)
