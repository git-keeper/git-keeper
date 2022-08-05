# Copyright 2016, 2017, 2018, 2020 Nathan Sommer and Ben Coleman
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


"""Provides a handler for adding students to a class."""

import os

from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import user_from_log_path, student_class_dir_path, \
    user_home_dir
from gkeepcore.shell_command import CommandError
from gkeepcore.student import students_from_csv, Student
from gkeepcore.system_commands import mkdir, sudo_chown, get_all_users
from gkeepserver.assignments import get_class_assignment_dirs, \
    setup_student_assignment, student_assignment_exists, StudentAssignmentError
from gkeepserver.user_setup import setup_student_user, NewUserAction
from gkeepserver.database import db, DatabaseException
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.info_update_thread import info_updater
from gkeepserver.server_configuration import config


class StudentsAddHandler(EventHandler):
    """Handle adding students to a class."""

    def handle(self):
        """
        Handle adding students to a class.

        Writes success or failure to the gkeepd to faculty log.

        Checks that none of the students are already in the class, creates
        non-existent student accounts, and adds assignment repositories if
        necessary.
        """

        try:
            reader = LocalCSVReader(self._uploaded_csv_path)
            students = students_from_csv(reader)
            faculty = db.get_faculty_by_username(self._faculty_username)

            for student in students:
                if student.email_address == faculty.email_address:
                    raise HandlerException('You cannot add yourself to your '
                                           'own class')

                if db.student_in_class(student.email_address, self._class_name,
                                       self._faculty_username):
                    error = ('Student {} is already in class {}'
                             .format(student.email_address, self._class_name))
                    raise HandlerException(error)

            self._setup_and_add_students(students)

            info_updater.enqueue_class_scan(self._faculty_username,
                                            self._class_name)

            self._log_to_faculty('STUDENTS_ADD_SUCCESS', self._class_name)
        except Exception as e:
            self._log_error_to_faculty(str(e))
            gkeepd_logger.log_warning('Students add failed: {0}'.format(e))

    def _setup_and_add_students(self, students):
        # Add class directory in students' home directories. Add student
        # accounts if necessary.

        # will be a list of (student, action) tuples, associating new student
        # users with the appropriate action to take
        student_actions = []

        # associate each new student user with an action
        for student in students:
            if db.email_exists(student.email_address):
                # email is in the database, but the username may not match
                # the email username
                student.username = \
                    db.get_username_from_email(student.email_address)
                if (db.faculty_username_exists(student.username) and
                        not db.student_username_exists(student.username)):
                    # email is associated with a faculty account, but not yet
                    # a student account
                    student_actions.append((student,
                                            NewUserAction.NEW_DB_ROLE))
            else:
                student_actions.append((student,
                                        NewUserAction.NEW_USER_NEW_DB))

        existing_users = get_all_users()

        # take actions as determined in the loop above
        for student, action in student_actions:
            if action == NewUserAction.NEW_DB_ROLE:
                try:
                    db.insert_student(student, existing_users,
                                      user_exists=True)
                except Exception as e:
                    error = ('Error adding faculty user with email {} '
                             'as a student: {}'.format(student.email_address, e))
                    raise HandlerException(error)
            else:
                try:
                    db.insert_student(student, existing_users)
                    setup_student_user(student, action)
                except Exception as e:
                    error = ('Error adding student with email {0}: {1}'
                             .format(student.email_address, e))
                    raise HandlerException(error)

        for student in students:
            home_dir = user_home_dir(student.username)
            class_dir_path = student_class_dir_path(self._faculty_username,
                                                    self._class_name,
                                                    home_dir)

            if not os.path.isdir(class_dir_path):
                self._add_new_student(student, class_dir_path)
            else:
                self._activate_existing_student(student, class_dir_path)

        published_assignment_dirs = []

        for assignment_dir in get_class_assignment_dirs(self._faculty_username,
                                                        self._class_name):
            if db.is_published(self._class_name,
                               assignment_dir.assignment_name,
                               self._faculty_username):
                published_assignment_dirs.append(assignment_dir)

        for assignment_dir in published_assignment_dirs:
            for student in students:
                if not student_assignment_exists(assignment_dir, student,
                                                 self._faculty_username):
                    try:
                        setup_student_assignment(assignment_dir, student,
                                                 self._faculty_username)
                    except StudentAssignmentError as e:
                        warning = (
                            'Error setting up student assignment repository '
                            'for {0} {1} {2}: {3}'
                            .format(student, self._class_name,
                                    assignment_dir.assignment_name, e)
                        )
                        self._log_warning_to_faculty(warning)
                        gkeepd_logger.log_warning(warning)

    def _add_new_student(self, student: Student, class_dir_path: str):
        try:
            mkdir(class_dir_path, sudo=True)
            sudo_chown(class_dir_path, student.username,
                       config.keeper_group)
        except CommandError as e:
            warning = ('Error creating student class directory for '
                       'student {0} in class {1}: {2}'
                       .format(student.email_address, self._class_name,
                               e))
            self._log_warning_to_faculty(warning)
            gkeepd_logger.log_warning(warning)

        try:
            db.add_student_to_class(self._class_name, student,
                                    self._faculty_username)
        except DatabaseException as e:
            warning = ('Error adding student {} in the database: {}'
                       .format(student.email_address, e))
            self._log_warning_to_faculty(warning)
            gkeepd_logger.log_warning(warning)

    def _activate_existing_student(self, student: Student,
                                   class_dir_path: str):
        try:
            db.activate_student_in_class(self._class_name,
                                         student.email_address,
                                         self._faculty_username)
        except DatabaseException as e:
            warning = ('Error activating student {} in the database: '
                       '{}'.format(student.email_address, e))
            self._log_warning_to_faculty(warning)
            gkeepd_logger.log_warning(warning)

    def __repr__(self) -> str:
        """
        Build a string representation of the event.

        :return: string representation of the event
        """

        string = 'Add students event: {0}'.format(self._payload)
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
        Log a STUDENTS_ADD_ERROR message to the gkeepd.log for the faculty.

        :param error: the error message
        """

        self._log_to_faculty('STUDENTS_ADD_ERROR', error)

    def _log_warning_to_faculty(self, warning):
        """
        Log a STUDENTS_MODIFY_WARNING message to the gkeepd.log for the faculty.

        :param warning: the warning message
        """

        self._log_to_faculty('STUDENTS_ADD_WARNING', warning)
