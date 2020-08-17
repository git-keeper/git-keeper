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


"""Provides a handler for adding a new class."""

from gkeepcore.path_utils import user_from_log_path
from gkeepcore.valid_names import validate_class_name
from gkeepserver.database import db
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.info_update_thread import info_updater


class ClassAddHandler(EventHandler):
    """Handle creating a new class."""

    def handle(self):
        """
        Handle creating a new class. The class will initially be empty.

        Writes success or failure to the gkeepd to faculty log.
        """

        try:
            validate_class_name(self._class_name)

            if db.class_exists(self._class_name, self._faculty_username):
                error = ('Class {} already exists. Use gkeep modify if you '
                         'would like to modify this class'
                         .format(self._class_name))
                raise HandlerException(error)

            db.insert_class(self._class_name, self._faculty_username)

            info_updater.enqueue_class_scan(self._faculty_username,
                                            self._class_name)

            self._log_to_faculty('CLASS_ADD_SUCCESS', self._class_name)
        except Exception as e:
            self._log_error_to_faculty(str(e))
            gkeepd_logger.log_warning('Class creation failed: {0}'.format(e))

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
        """

        self._faculty_username = user_from_log_path(self._log_path)
        self._class_name = self._payload

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
