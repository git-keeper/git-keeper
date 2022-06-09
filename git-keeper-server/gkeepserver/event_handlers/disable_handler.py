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

"""
Provides DisableHandler, the handler for disabling assignments.

Event type: DISABLE
"""


from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import user_from_log_path, \
    faculty_assignment_dir_path, user_gitkeeper_path
from gkeepserver.database import db
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.info_update_thread import info_updater
from gkeepserver.server_email import Email


class DisableHandler(EventHandler):
    """Handles a request from the client to disable an assignment"""

    def handle(self):
        """
        Take action after a client requests that an assignment be disabled.

        Mark the assignment as disabled, notify the students about this via
        email, replace action.sh with a message that the assignment is
        disabled.
        """

        gitkeeper_path = user_gitkeeper_path(self._faculty_username)

        # path to the directory that the assignment's files are kept in
        assignment_path = faculty_assignment_dir_path(self._class_name,
                                                      self._assignment_name,
                                                      gitkeeper_path)

        try:
            if not db.is_published(self._class_name, self._assignment_name,
                                   self._faculty_username):
                error = ('Assignment {} is not published and cannot be '
                         'disabled.\n'
                         'Use gkeep delete to delete this assignment.'
                         .format(self._assignment_name))
                raise HandlerException(error)

            db.disable_assignment(self._class_name, self._assignment_name,
                                  self._faculty_username)

            email_subject = ('[{}] Assignment disabled: {}'
                             .format(self._class_name, self._assignment_name))
            email_body = ('Assignment {} in class {} has been disabled. '
                          'No tests will be run if you push to your '
                          'repository for this assignment.\n'
                          .format(self._assignment_name, self._class_name))
            for student in db.get_class_students(self._class_name,
                                                 self._faculty_username):
                email_sender.enqueue(Email(student.email_address,
                                           email_subject, email_body))

            info_updater.enqueue_disable_assignment(self._faculty_username,
                                                    self._class_name,
                                                    self._assignment_name)

            log_gkeepd_to_faculty(self._faculty_username, 'DISABLE_SUCCESS',
                                  '{0} {1}'.format(self._class_name,
                                                   self._assignment_name))
            info = '{0} disabled {1} from {2}'.format(self._faculty_username,
                                                      self._assignment_name,
                                                      self._class_name)
            gkeepd_logger.log_info(info)
        except GkeepException as e:
            log_gkeepd_to_faculty(self._faculty_username, 'DISABLE_ERROR',
                                  str(e))
            warning = 'Disable failed: {0}'.format(e)
            gkeepd_logger.log_warning(warning)

    def __repr__(self):
        """
        Create a string representation of the handler for printing and logging

        :return: a string representation of the event to be handled
        """

        string = ('{0} requested to disable {1} {2}'
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
            raise HandlerException('Invalid payload for DISABLE: {0}'
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
