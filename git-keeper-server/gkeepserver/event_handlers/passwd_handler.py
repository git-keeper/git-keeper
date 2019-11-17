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
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.generate_password import generate_password
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.server_email import Email
from gkeepserver.students_and_classes import get_student_from_username


class PasswdHandler(EventHandler):
    """Handle resetting student passwords."""

    def handle(self):
        """Handle resetting a student password."""

        try:
            student = get_student_from_username(self._faculty_username,
                                                self._username)

            if student is None:
                error = 'No student found with username {}'\
                        .format(self._username)
                raise HandlerException(error)

            password = generate_password()
            sudo_set_password(student.username, password)

            subject = 'New git-keeper password'
            body = ('Hello {},\n\n'
                    'Your git-keeper password has been reset to {}\n\n'
                    'If you have any questions, please contact your '
                    'instructor rather than responding to this email '
                    'directly.\n\n'.format(student.username, password))

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
