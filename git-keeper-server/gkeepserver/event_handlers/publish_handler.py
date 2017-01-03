# Copyright 2016, 2017 Nathan Sommer and Ben Coleman
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
from tempfile import TemporaryDirectory

from gkeepcore.csv_files import CSVError
from gkeepcore.git_commands import git_init, git_push, git_add_all, git_commit
from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import user_from_log_path, \
    faculty_assignment_dir_path, user_home_dir, class_student_csv_path
from gkeepcore.shell_command import CommandError
from gkeepcore.student import students_from_csv, StudentError, Student
from gkeepcore.system_commands import touch, sudo_chown, mkdir
from gkeepserver.assignments import AssignmentDirectory, \
    AssignmentDirectoryError, setup_student_assignment, StudentAssignmentError
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.info_refresh_thread import info_refresher
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
            students = self._setup_students_assignment_repos(assignment_dir)
            self._populate_reports_repo(assignment_dir, students)
            self._create_published_flag(assignment_dir)

            info_refresher.enqueue(self._faculty_username)

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

    def _populate_reports_repo(self, assignment_dir: AssignmentDirectory,
                               students: list):
        temp_dir = TemporaryDirectory()

        temp_dir_path = temp_dir.name

        git_init(temp_dir_path)

        for student in students:
            student_report_path = \
                os.path.join(temp_dir_path, student.get_last_first_username())
            mkdir(student_report_path)

            placeholder_path = os.path.join(student_report_path,
                                            '.placeholder')
            touch(placeholder_path)

        git_add_all(temp_dir_path)
        git_commit(temp_dir_path, 'Initial commit')
        git_push(temp_dir_path, dest=assignment_dir.reports_repo_path,
                 sudo=True)
        sudo_chown(assignment_dir.reports_repo_path, self._faculty_username,
                   config.keeper_group, recursive=True)

    def _setup_students_assignment_repos(self,
                                         assignment_dir: AssignmentDirectory):
        # Setup bare repositories for each student in the class
        #
        # Return a list of Student objects

        home_dir = user_home_dir(self._faculty_username)

        student_csv_path = class_student_csv_path(self._class_name, home_dir)

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

        return students

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

        gkeepd_logger.log_debug('Set up assignment {0} for {1}'
                                .format(assignment_dir.assignment_name,
                                        student.username))

    def __repr__(self):
        """
        Create a string representation of the handler for printing and logging

        :return: a string representation of the event to be handled
        """

        string = ('{0} requested to publish {1} {2}'
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
            raise HandlerException('Invalid payload for PUBLISH: {0}'
                                   .format(self._payload))
