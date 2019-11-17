# Copyright 2018 Nathan Sommer and Ben Coleman
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

"""
Provides ClassStatusHandler, the handler for changing a class's status.

Possible statuses are 'open' and 'closed'.

Event type: CLASS_STATUS
"""

from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import user_home_dir, faculty_class_dir_path

from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.file_writing import write_and_install_file
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.info_update_thread import info_updater
from gkeepserver.server_configuration import config


class ClassStatusHandler(EventHandler):
    """Handles a request from the client to change the status of a class."""

    def handle(self):
        """
        Take action after a client requests that a class's status be changed.

        The contents of a class's status file is updated.
        """

        if self._status not in ('open', 'closed'):
            raise HandlerException('Invalid status for CLASS_STATUS: {}'
                                   .format(self._status))

        faculty_home_dir = user_home_dir(self._faculty_username)
        class_path = faculty_class_dir_path(self._class_name, faculty_home_dir)

        print('Handling class status:')
        print(' Faculty:', self._faculty_username)
        print(' Class:  ', self._class_name)
        print(' Status: ', self._status)

        try:
            write_and_install_file(self._status, 'status', class_path,
                                   self._faculty_username, config.keeper_group,
                                   '640')

            info_updater.enqueue_class_scan(self._faculty_username,
                                            self._class_name)

            log_gkeepd_to_faculty(self._faculty_username,
                                  'CLASS_STATUS_SUCCESS',
                                  '{0} {1}'.format(self._class_name,
                                                   self._status))
            info = ('{0} changed status of {1} to {2}'
                    .format(self._faculty_username, self._class_name,
                            self._status))
            gkeepd_logger.log_info(info)
        except (HandlerException, GkeepException) as e:
            log_gkeepd_to_faculty(self._faculty_username, 'CLASS_STATUS_ERROR',
                                  str(e))
            warning = 'Class status update failed: {0}'.format(e)
            gkeepd_logger.log_warning(warning)

    def __repr__(self):
        """
        Create a string representation of the handler for printing and logging

        :return: a string representation of the event to be handled
        """

        string = ('{0} requested to change status of {1} to {2}'
                  .format(self._faculty_username, self._class_name,
                          self._status))
        return string

    def _parse_payload(self):
        """
        Extract the faculty username, class name, and status from the log
        event.

        Attributes available after parsing:
            _faculty_username
            _class_name
            _status
        """

        self._parse_log_path()

        try:
            self._class_name, self._status = self._payload.split(' ')
        except ValueError:
            raise HandlerException('Invalid payload for CLASS_STATUS: {0}'
                                   .format(self._payload))
