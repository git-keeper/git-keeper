# Copyright 2020 Nathan Sommer and Ben Coleman
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


"""Provides a handler for removing students from a class."""


from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import user_from_log_path
from gkeepcore.student import students_from_csv
from gkeepserver.database import db, DatabaseException
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.info_update_thread import info_updater


class StudentsRemoveHandler(EventHandler):
    """Handle removing students from a class."""

    def handle(self):
        """
        Handle removing students from a class.

        Writes success or failure to the gkeepd to faculty log.

        Students that are removed will be marked as deactivated.
        """

        try:
            reader = LocalCSVReader(self._uploaded_csv_path)
            students = students_from_csv(reader)

            for student in students:
                if db.student_inactive_in_class(student.email_address,
                                                self._class_name,
                                                self._faculty_username):
                    error = ('Student {} is already inactive in class {}'
                             .format(student.email_address, self._class_name))
                    raise HandlerException(error)

                if not db.student_in_class(student.email_address,
                                           self._class_name,
                                           self._faculty_username):
                    error = ('Student {} is not in class {}'
                             .format(student.email_address, self._class_name))
                    raise HandlerException(error)

            self._disable_students(students)

            info_updater.enqueue_class_scan(self._faculty_username,
                                            self._class_name)

            self._log_to_faculty('STUDENTS_REMOVE_SUCCESS', self._class_name)
        except Exception as e:
            self._log_error_to_faculty(str(e))
            gkeepd_logger.log_warning('Removing students failed: {0}'.format(e))

    def _disable_students(self, students):
        for student in students:
            try:
                db.deactivate_student_in_class(self._class_name,
                                               student.email_address,
                                               self._faculty_username)
            except DatabaseException as e:
                error = ('Error deactivating student {} in class {}: {}'
                         .format(student.email_address, self._class_name, e))
                raise HandlerException(error)

    def __repr__(self) -> str:
        """
        Build a string representation of the event.

        :return: string representation of the event
        """

        string = 'Remove students event: {0}'.format(self._payload)
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
        Log a STUDENTS_REMOVE_ERROR message to the gkeepd.log for the faculty.

        :param error: the error message
        """

        self._log_to_faculty('STUDENTS_REMOVE_ERROR', error)


    def _log_warning_to_faculty(self, warning):
        """
        Log a STUDENTS_REMOVE_WARNING message to the gkeepd.log for the faculty.

        :param warning: the warning message
        """

        self._log_to_faculty('STUDENTS_REMOVE_WARNING', warning)
