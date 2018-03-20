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
from shutil import which

from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import user_from_log_path, student_class_dir_path, \
    user_home_dir, faculty_class_dir_path, class_student_csv_path
from gkeepcore.shell_command import CommandError
from gkeepcore.student import students_from_csv
from gkeepcore.system_commands import user_exists, mkdir, sudo_chown, cp, \
    chmod, make_symbolic_link
from gkeepcore.valid_names import validate_class_name
from gkeepserver.create_user import create_user, UserType, create_student_user
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.file_writing import write_and_install_file
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

            for student in students:
                if student.username == self._faculty_username:
                    raise HandlerException('You cannot add yourself to your '
                                           'own class')

            self._setup_class_dir()
            self._add_students_class_dirs(students)

            info_updater.enqueue_class_scan(self._faculty_username,
                                            self._class_name)

            self._log_to_faculty('CLASS_ADD_SUCCESS', self._class_name)
        except Exception as e:
            self._log_error_to_faculty(str(e))
            gkeepd_logger.log_warning('Class add failed: {0}'.format(e))

    def _setup_class_dir(self):
        # Create the class directory, copy the class CSV file to its final
        # destination, and create the class's status file

        # uploaded CSV must be in place
        if not os.path.isfile(self._uploaded_csv_path):
            error = ('{0} does not exist, cannot add class'
                     .format(self._uploaded_csv_path))
            raise HandlerException(error)

        home_dir = user_home_dir(self._faculty_username)

        faculty_class_path = faculty_class_dir_path(self._class_name, home_dir)

        # class must not already exist
        if os.path.isdir(faculty_class_path):
            error = ('class {0} already exists'.format(self._class_name))
            raise HandlerException(error)

        # create the class directory, copy the CSV, fix permissions, and
        # install the status file
        try:
            mkdir(faculty_class_path, sudo=True)
            final_csv_path = class_student_csv_path(self._class_name, home_dir)
            cp(self._uploaded_csv_path, final_csv_path, sudo=True)
            chmod(faculty_class_path, '750', sudo=True)
            sudo_chown(faculty_class_path, self._faculty_username,
                       config.keeper_group, recursive=True)
            write_and_install_file('open', 'status', faculty_class_path,
                                   self._faculty_username, config.keeper_group,
                                   '640')
        except CommandError as e:
            error = 'Error setting up class directory: {0}'.format(e)
            raise HandlerException(error)

    def _add_students_class_dirs(self, students):
        # Add class directory in students' home directories. Add student
        # accounts if necessary.

        # students we need to add accounts for
        new_students = []

        # build new_students and check that existing students do not have a
        # directory for the class already
        for student in students:
            if not user_exists(student.username):
                new_students.append(student)
            else:
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

        # create new student accounts
        for student in new_students:
            try:
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
                raise HandlerException(e)

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
