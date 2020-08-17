# Copyright 2019 Nathan Sommer and Ben Coleman
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


"""Provides a handler for resetting student passwords."""


from gkeepcore.path_utils import user_from_log_path
from gkeepcore.system_commands import sudo_set_password
from gkeepserver.database import db
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.generate_password import generate_password
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.server_email import Email


class PasswdHandler(EventHandler):
    """Handle resetting student passwords."""

    def handle(self):
        """Handle resetting a student password."""

        try:
            email_address = db.get_email_from_username(self._username)

            student_found = False
            found_class_name = None

            class_names = db.get_faculty_class_names(self._faculty_username)
            for class_name in class_names:
                if db.student_in_class(email_address, class_name,
                                       self._faculty_username):
                    student_found = True
                    found_class_name = class_name
                    break

            if not student_found:
                error = ('No student found with username {} in any of your '
                         'classes'.format(self._username))
                raise HandlerException(error)

            student = db.get_class_student_by_username(self._username,
                                                       found_class_name,
                                                       self._faculty_username)

            password = generate_password()
            sudo_set_password(student.username, password)

            subject = 'New git-keeper password'
            body = ('Hello {},\n\n'
                    'Your git-keeper password has been reset to {}\n\n'
                    'If you have any questions, please contact your '
                    'instructor rather than responding to this email '
                    'directly.\n\n'.format(student.first_name, password))

            email_sender.enqueue(Email(student.email_address, subject, body))

            self._report_success(student.username)
        except Exception as e:
            self._report_error(str(e))

    def __repr__(self) -> str:
        """
        Build a string representation of the event.

        :return: string representation of the event
        """

        string = 'Password reset event: {0}'.format(self._payload)
        return string

    def _parse_payload(self):
        """
        Extracts the username from the payload

        Sets the following attributes:

        _faculty_username - username of the user making the request
        _username = username of the student
        """

        self._faculty_username = user_from_log_path(self._log_path)
        self._username = self._payload
