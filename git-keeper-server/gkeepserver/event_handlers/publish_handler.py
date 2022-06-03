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
Provides PublishHandler, the handler for publishing assignments

Event type: PUBLISH
"""

import os

from gkeepcore.csv_files import CSVError
from gkeepcore.git_commands import git_add_all, git_commit
from gkeepcore.path_utils import faculty_assignment_dir_path, \
    user_gitkeeper_path
from gkeepcore.student import StudentError, Student
from gkeepcore.system_commands import touch, mkdir
from gkeepserver.assignments import AssignmentDirectory, \
    AssignmentDirectoryError, setup_student_assignment, StudentAssignmentError
from gkeepserver.database import db
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.info_update_thread import info_updater
from gkeepserver.reports import reports_clone


class PublishHandler(EventHandler):
    """Handles a request from the client to publish an assignment"""

    def handle(self):
        """
        Take action after a client requests that an assignment be published.

        Sets up bare repositories for the assignment for each student in the
        class.
        """

        gitkeeper_path = user_gitkeeper_path(self._faculty_username)

        # path to the directory that the assignment's files are kept in
        assignment_path = faculty_assignment_dir_path(self._class_name,
                                                      self._assignment_name,
                                                      gitkeeper_path)

        try:
            if not db.class_is_open(self._class_name, self._faculty_username):
                raise HandlerException(
                    '{} is not open'.format(self._class_name))

            assignment_dir = AssignmentDirectory(assignment_path)
            self._ensure_not_published()
            students = self._setup_students_assignment_repos(assignment_dir)
            self._populate_reports_repo(assignment_dir, students)

            db.set_published(self._class_name, self._assignment_name,
                             self._faculty_username)

            info_updater.enqueue_assignment_scan(self._faculty_username,
                                                 self._class_name,
                                                 self._assignment_name)

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

    def _ensure_not_published(self):
        # Throw an exception if the assignment is already published
        if db.is_published(self._class_name, self._assignment_name,
                           self._faculty_username):
            raise HandlerException('Assignment already published')

    def _populate_reports_repo(self, assignment_dir: AssignmentDirectory,
                               students: list):
        with reports_clone(assignment_dir) as temp_dir_path:
            reports_placeholder_path = os.path.join(temp_dir_path,
                                                    '.placeholder')
            touch(reports_placeholder_path)

            for student in students:
                student_report_path = \
                    os.path.join(temp_dir_path,
                                 student.get_last_first_username())
                mkdir(student_report_path)

                student_placeholder_path = os.path.join(student_report_path,
                                                        '.placeholder')
                touch(student_placeholder_path)

            git_add_all(temp_dir_path)
            git_commit(temp_dir_path, 'Initial commit')

    def _setup_students_assignment_repos(self,
                                         assignment_dir: AssignmentDirectory):
        # Setup bare repositories for each student in the class
        #
        # Return a list of Student objects

        try:
            students = db.get_class_students(self._class_name,
                                             self._faculty_username)
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
