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


"""Handler for student submissions

Event type: SUBMISSION
"""


from gkeepcore.event_handler import EventHandler, HandlerException
from gkeepcore.path_utils import parse_user_log_path, \
    parse_submission_repo_path


class SubmissionHandler(EventHandler):
    """Handles a new submission from a student."""

    def handle(self):
        """Takes action after a student pushes a new submission."""

        # FIXME - ensure everything exists, set things up, and run tests
        print('Handling submission:')
        print(' Student:   ', self._student_username)
        print(' Faculty:   ', self._faculty_username)
        print(' Class:     ', self._class_name)
        print(' Assignment:', self._assignment_name)
        print(' Repo path: ', self._submission_repo_path)
        print()

    def _parse(self):
        """Extracts the student username, faculty username, class name,
         assignment name, and student submission repository from the log event.

        Attributes available after parsing:
            _student_username
            _faculty_username
            _class_name
            _assignment_name
            _submission_repo_path
        """

        self._parse_log_path()

        # the payload simply contains the submission repository path
        self._submission_repo_path = self._payload

        self._parse_repo_path()

    def _parse_log_path(self):
        """Extracts the student username from the log file path.

        Raises:
             HandlerException

        Initializes attributes:
            _student_username
        """

        self._student_username = parse_user_log_path(self._log_path)

        if self._student_username is None:
            raise HandlerException('Malformed log path: {0}'
                                   .format(self._log_path))

    def _parse_repo_path(self):
        """Extracts the faculty username, class name, and assignment name from
        the assignment path.

        Raises:
            HandlerException

        Initializes attributes:
            _faculty_username
            _class_name
            _assignment_name
        """

        assignment_info = \
            parse_submission_repo_path(self._submission_repo_path)

        if assignment_info is None:
            raise HandlerException('Malformed submission repo path: {0}'
                                   .format(self._submission_repo_path))

        self._faculty_username, self._class_name, self._assignment_name = \
            assignment_info
