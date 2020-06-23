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


"""Provides a handler for demoting faculty users from admin."""

from gkeepcore.path_utils import user_from_log_path
from gkeepserver.database import db
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty


class AdminDemoteHandler(EventHandler):
    """Handle demoting faculty users from admin."""

    def handle(self):
        """
        Handle demoting a faculty user from admin

        Writes success or failure to the gkeepd to faculty log.
        """

        try:
            if not db.is_admin(self._demoter_username):
                error = ('User {} is not an admin'
                         .format(self._demoter_username))
                raise HandlerException(error)

            faculty = db.get_faculty_by_email(self._email_address)

            if not db.is_admin(faculty.username):
                error = ('User with email address {} is not an admin'
                         .format(self._email_address))
                raise HandlerException(error)

            db.remove_admin(faculty.username)

            self._log_to_faculty('ADMIN_DEMOTE_SUCCESS', self._email_address)
        except Exception as e:
            self._log_error_to_faculty(str(e))
            gkeepd_logger.log_warning('Admin demotion failed: {0}'.format(e))

    def __repr__(self) -> str:
        """
        Build a string representation of the event.

        :return: string representation of the event
        """

        string = 'Admin demotion event: {0}'.format(self._payload)
        return string

    def _parse_payload(self):
        """
        Extracts the email address from the payload

        Raises HandlerException if the log line is not well formed.

        Sets the following attributes:

        _adder_username - username of the user demoting the faculty member
        _email_address - email address of faculty user to demote
        """

        self._demoter_username = user_from_log_path(self._log_path)
        self._email_address = self._payload

    def _log_to_faculty(self, event_type, text):
        """
        Write to the gkeepd.log for the faculty member.

        :param event_type: event type
        :param text: text to write to the log
        """

        log_gkeepd_to_faculty(self._faculty_username, event_type, text)

    def _log_error_to_faculty(self, error):
        """
        Log a ADMIN_DEMOTE_ERROR message to the gkeepd.log for the faculty.

        :param error: the error message
        """

        self._log_to_faculty('ADMIN_DEMOTE_ERROR', error)
