# Copyright 2022 Nathan Sommer and Ben Coleman
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


"""Provides a handler for checking the state of the server"""

import json

from gkeepcore.assignment_config import verify_firejail_installed, verify_docker_installed
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import user_from_log_path
from gkeepserver.database import db
from gkeepserver.event_handler import EventHandler
from gkeepserver.server_configuration import config
from gkeepserver.version import __version__


class CheckHandler(EventHandler):
    """Handle checking server status"""

    def handle(self):
        try:
            verify_firejail_installed()
            firejail_installed = True
        except GkeepException:
            firejail_installed = False

        try:
            verify_docker_installed()
            docker_installed = True
        except GkeepException:
            docker_installed = False

        try:
            data = {
                'version': __version__,
                'uptime': config.uptime(),
                'firejail_installed': firejail_installed,
                'docker_installed': docker_installed,
                'is_admin': db.is_admin(self._faculty_username),
                'default_test_env': config.default_test_env.value,
                'use_html': config.use_html,
                'tests_timeout': config.tests_timeout,
                'tests_memory_limit': config.tests_memory_limit,
            }

            self._report_success(json.dumps(data))
        except Exception as e:
            self._report_error(e)

    def __repr__(self) -> str:
        """
        Build a string representation of the event.

        :return: string representation of the event
        """

        string = 'Check event from {0}'.format(self._faculty_username)
        return string

    def _parse_payload(self):
        """
        Extracts the faculty username from the payload

        Sets the following attributes:

        _faculty_username - username of the user making the request
        """

        self._faculty_username = user_from_log_path(self._log_path)
