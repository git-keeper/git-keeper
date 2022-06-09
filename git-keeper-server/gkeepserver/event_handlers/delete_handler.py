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

"""
Provides DeleteHandler, the handler for deleting assignments.

Event type: DELETE
"""


from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import user_from_log_path, \
    faculty_assignment_dir_path, user_gitkeeper_path
from gkeepcore.system_commands import rm
from gkeepserver.assignments import AssignmentDirectory, \
    remove_student_assignment
from gkeepserver.database import db
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.info_update_thread import info_updater


class DeleteHandler(EventHandler):
    """Handles a request from the client to delete an assignment"""

    def handle(self):
        """
        Take action after a client requests that an assignment be deleted.

        Delete the assignment directory, the faculty test repo, and all
        student repos for the assignment.
        """

        gitkeeper_path = user_gitkeeper_path(self._faculty_username)

        # path to the directory that the assignment's files are kept in
        assignment_path = faculty_assignment_dir_path(self._class_name,
                                                      self._assignment_name,
                                                      gitkeeper_path)

        try:
            if db.is_published(self._class_name, self._assignment_name,
                               self._faculty_username):
                error = ('Assignment {} is published and cannot be deleted.\n'
                         'Use gkeep disable to disable this assignment.'
                         .format(self._assignment_name))
                raise HandlerException(error)

            assignment_dir = AssignmentDirectory(assignment_path)

            # remove the faculty's "student" repo used for testing
            faculty = db.get_faculty_by_username(self._faculty_username)
            remove_student_assignment(assignment_dir, faculty,
                                      self._faculty_username)

            rm(assignment_dir.path, recursive=True, sudo=True)

            db.remove_assignment(self._class_name, self._assignment_name,
                                 self._faculty_username)

            info_updater.enqueue_delete_assignment(self._faculty_username,
                                                   self._class_name,
                                                   self._assignment_name)

            log_gkeepd_to_faculty(self._faculty_username, 'DELETE_SUCCESS',
                                  '{0} {1}'.format(self._class_name,
                                                   self._assignment_name))
            info = '{0} deleted {1} from {2}'.format(self._faculty_username,
                                                     self._assignment_name,
                                                     self._class_name)
            gkeepd_logger.log_info(info)
        except GkeepException as e:
            log_gkeepd_to_faculty(self._faculty_username, 'DELETE_ERROR',
                                  str(e))
            warning = 'Delete failed: {0}'.format(e)
            gkeepd_logger.log_warning(warning)

    def __repr__(self):
        """
        Create a string representation of the handler for printing and logging

        :return: a string representation of the event to be handled
        """

        string = ('{0} requested to delete {1} {2}'
                  .format(self._faculty_username, self._class_name,
                          self._assignment_name))
        return string

    def _parse_payload(self):
        """
        Extract the faculty username, class name, and assignment name from the
        log event.

        Attributes available after parsing:
            _faculty_username
            _class_name
            _assignment_name
        """

        self._parse_log_path()

        try:
            self._class_name, self._assignment_name = self._payload.split(' ')
        except ValueError:
            raise HandlerException('Invalid payload for DELETE: {0}'
                                   .format(self._payload))

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
