# Copyright 2016 Nathan Sommer and Ben Coleman
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


"""Handler for new assignment uploads.

Event type: UPLOAD
"""

from gkeepcore.path_utils import user_from_log_path, \
    parse_faculty_assignment_path
from gkeepserver.event_handler import EventHandler, HandlerException


class UploadHandler(EventHandler):
    """Handles a new assignment uploaded by a faculty member."""

    def handle(self):
        """Take action after a faculty member uploads a new assignment."""

        # FIXME - ensure everything exists, create bare repos, email prof
        print('Handling upload:')
        print(' Faculty:   ', self._faculty_username)
        print(' Class:     ', self._class_name)
        print(' Assignment:', self._assignment_name)
        print(' Path:      ', self._assignment_path)

    def _parse(self):
        """
        Extract the faculty username, class name, assignment name, and
        assignment path from the log event.

        Attributes available after parsing:
            _faculty_username
            _class_name
            _assignment_name
            _assignment_path
        """

        self._parse_log_path()

        # the log payload simply contains the assignment path
        self._assignment_path = self._payload

        self._parse_assignment_path()

    def _parse_log_path(self):
        """
        Extract the faculty username from the log file path.

        Raises:
             HandlerException

        Initializes attributes:
            _faculty_username
        """

        self._faculty_username = user_from_log_path(self._log_path)

        if self._faculty_username is None:
            raise HandlerException('Malformed log path: {0}'
                                   .format(self._log_path))

    def _parse_assignment_path(self):
        """
        Extract the class name and assignment name from the assignment path.

        Raises:
            HandlerException

        Initializes attributes:
            _class_name
            _assignment_name
        """

        assignment_info = parse_faculty_assignment_path(self._assignment_path)

        if assignment_info is None:
            raise HandlerException('Malformed assignment path: {0}'
                                   .format(self._assignment_path))

        self._class_name, self._assignment_name = assignment_info
