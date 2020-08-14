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


"""Provides a handler for modifying student names in a class."""


from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import user_from_log_path
from gkeepcore.student import students_from_csv
from gkeepserver.database import db
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.info_update_thread import info_updater


class StudentsModifyHandler(EventHandler):
    """Handle student names modified by the faculty."""

    def handle(self):
        """
        Handle modifying student names.

        Writes success or failure to the gkeepd to faculty log.
        """

        try:
            reader = LocalCSVReader(self._uploaded_csv_path)

            students = students_from_csv(reader)

            for student in students:
                if not db.student_in_class(student.email_address,
                                           self._class_name,
                                           self._faculty_username):
                    error = ('No student with email {} in class {}'
                             .format(student.email_address, self._class_name))
                    raise HandlerException(error)

            for student in students:
                db.change_student_name(student, self._class_name,
                                       self._faculty_username)

            info_updater.enqueue_class_scan(self._faculty_username,
                                            self._class_name)

            self._log_to_faculty('STUDENTS_MODIFY_SUCCESS', self._class_name)
        except Exception as e:
            self._log_error_to_faculty(str(e))
            gkeepd_logger.log_warning('Renaming students failed: {0}'.format(e))

    def __repr__(self) -> str:
        """
        Build a string representation of the event.

        :return: string representation of the event
        """

        string = 'Students modify event: {0}'.format(self._payload)
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

        self._log_to_faculty('STUDENTS_MODIFY_ERROR', error)

    def _log_warning_to_faculty(self, warning):
        """
        Log a CLASS_MODIFY_WARNING message to the gkeepd.log for the faculty.

        :param warning: the warning message
        """

        self._log_to_faculty('STUDENTS_MODIFY_WARNING', warning)
