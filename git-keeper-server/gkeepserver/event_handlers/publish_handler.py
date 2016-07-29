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

"""
Provides PublishHandler, the handler for publishing assignments

Event type: PUBLISH
"""

import os

from gkeepcore.csv_files import CSVError
from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import user_from_log_path, \
    faculty_assignment_dir_path, user_home_dir, class_student_csv_path
from gkeepcore.shell_command import CommandError
from gkeepcore.student import students_from_csv, StudentError, Student
from gkeepcore.system_commands import touch, sudo_chown
from gkeepserver.assignments import AssignmentDirectory, \
    AssignmentDirectoryError, setup_student_assignment, StudentAssignmentError
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.server_configuration import config


class PublishHandler(EventHandler):
    """Handles a request from the client to publish an assignment"""

    def handle(self):
        """
        Take action after a client requests that an assignment be published.

        Sets up bare repositories for the assignment for each student in the
        class.
        """

        faculty_home_dir = user_home_dir(self._faculty_username)

        # path to the directory that the assignment's files are kept in
        assignment_path = faculty_assignment_dir_path(self._class_name,
                                                      self._assignment_name,
                                                      faculty_home_dir)

        print('Handling publish:')
        print(' Faculty:        ', self._faculty_username)
        print(' Class:          ', self._class_name)
        print(' Assignment:     ', self._assignment_name)
        print(' Assignment path:', assignment_path)

        try:
            assignment_dir = AssignmentDirectory(assignment_path)
            self._ensure_not_published(assignment_dir)
            self._setup_students_assignment_repos(assignment_dir)
            self._create_published_flag(assignment_dir)

            log_gkeepd_to_faculty(self._faculty_username, 'PUBLISH_SUCCESS',
                                  '{0} {1}'.format(self._class_name,
                                                   self._assignment_name))
            info = '{0} published {1} {2}'.format(self._faculty_username,
                                                  self._assignment_name,
                                                  self._class_name)
            gkeepd_logger.log_info(info)
        except (HandlerException, AssignmentDirectoryError) as e:
            log_gkeepd_to_faculty(self._faculty_username, 'PUBLISH_ERROR',
                                  str(e))
            warning = 'Publish failed: {0}'.format(e)
            gkeepd_logger.log_warning(warning)

    def _ensure_not_published(self, assignment_dir: AssignmentDirectory):
        # Throw an exception if the assignment is already published
        if os.path.isfile(assignment_dir.published_flag_path):
            raise HandlerException('Assignment already published')

    def _create_published_flag(self, assignment_dir: AssignmentDirectory):
        # Mark the assignment as published by touching the published flag file.
        try:
            touch(assignment_dir.published_flag_path, sudo=True)
            sudo_chown(assignment_dir.published_flag_path,
                       self._faculty_username, config.keeper_group)
        except CommandError as e:
            error = 'Error flagging as published: {0}'.format(e)
            raise HandlerException(error)

    def _setup_students_assignment_repos(self,
                                         assignment_dir: AssignmentDirectory):
        # Setup bare repositories for each student in the class

        student_csv_path = class_student_csv_path(self._faculty_username,
                                                  self._class_name)

        try:
            students = students_from_csv(LocalCSVReader(student_csv_path))
        except StudentError as e:
            error = 'Error in student CSV file: {0}'.format(e)
            raise HandlerException(error)
        except CSVError as e:
            error = 'Error reading student CSV file: {0}'.format(e)
            raise HandlerException(error)

        for student in students:
            self._setup_student_assignment_repo(student, assignment_dir)

    def _setup_student_assignment_repo(self, student: Student,
                                       assignment_dir: AssignmentDirectory):
        # Setup a bare repo for a student
        try:
            setup_student_assignment(assignment_dir, student,
                                     self._faculty_username)
        except StudentAssignmentError as e:
            warning = ('Error setting up student assignment repository for '
                       '{0} {1} {2}: {3}'.format(student, self._class_name,
                                                 self._assignment_name, e))
            log_gkeepd_to_faculty(self._faculty_username, 'PUBLISH_WARNING',
                                  warning)
            gkeepd_logger.log_warning(warning)

    def __repr__(self):
        """
        Create a string representation of the handler for printing and logging

        :return: a string representation of the event to be handled
        """

        string = ('{0} requested to publish {1} {2}'
                  .format(self._faculty_username, self._class_name,
                          self._assignment_name))
        return string

    def _parse(self):
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
            raise HandlerException('Invalid payload for PUBLISH: {0}'
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
