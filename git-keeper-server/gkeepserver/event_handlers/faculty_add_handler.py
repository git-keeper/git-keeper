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


"""Provides a handler for adding faculty users."""

import json

from gkeepcore.path_utils import user_from_log_path
from gkeepserver.database import db
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.user_setup import add_faculty
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.info_update_thread import info_updater


class FacultyAddHandler(EventHandler):
    """Handle adding new faculty members."""

    def handle(self):
        """
        Handle adding a new faculty member.

        Writes success or failure to the gkeepd to faculty log.
        """

        try:
            if not db.is_admin(self._adder_username):
                error = 'User {} is not an admin'.format(self._adder_username)
                raise HandlerException(error)

            try:
                _, _ = self._email_address.split('@')
            except ValueError:
                raise HandlerException('{} is not an email address'
                                       .format(self._email_address))

            faculty = add_faculty(self._last_name, self._first_name,
                                  self._email_address, self._admin)

            info_updater.enqueue_full_scan(faculty.username)

            self._log_to_faculty('FACULTY_ADD_SUCCESS', self._adder_username)
        except Exception as e:
            self._log_error_to_faculty(str(e))
            gkeepd_logger.log_warning('Faculty add failed: {0}'.format(e))

    def __repr__(self) -> str:
        """
        Build a string representation of the event.

        :return: string representation of the event
        """

        string = 'Add faculty event: {0}'.format(self._payload)
        return string

    def _parse_payload(self):
        """
        Extracts the faculty info from the payload

        Raises HandlerException if the log line is not well formed.

        Sets the following attributes:

        _adder_username - username of the user adding the faculty member
        _last_name - last name of the new faculty member
        _first_name - first name of the new faculty member
        _email_address - email address of the new faculty member
        _admin - whether or not the new user should be an admin
        """

        self._adder_username = user_from_log_path(self._log_path)

        try:
            faculty_dictionary = json.loads(self._payload)
        except json.JSONDecodeError:
            raise HandlerException('Payload is not valid JSON')

        for required_field in ('last_name', 'first_name', 'email_address',
                               'admin'):
            if required_field not in faculty_dictionary:
                raise HandlerException('Missing required field {}'
                                       .format(required_field))

        self._last_name = faculty_dictionary['last_name']
        self._first_name = faculty_dictionary['first_name']
        self._email_address = faculty_dictionary['email_address']
        self._admin = faculty_dictionary['admin']

    def _log_to_faculty(self, event_type, text):
        """
        Write to the gkeepd.log for the faculty member.

        :param event_type: event type
        :param text: text to write to the log
        """

        log_gkeepd_to_faculty(self._faculty_username, event_type, text)

    def _log_error_to_faculty(self, error):
        """
        Log a FACULTY_ADD_ERROR message to the gkeepd.log for the faculty.

        :param error: the error message
        """

        self._log_to_faculty('FACULTY_ADD_ERROR', error)
