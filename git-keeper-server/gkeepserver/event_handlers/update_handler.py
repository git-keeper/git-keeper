# Copyright 2016, 2018 Nathan Sommer and Ben Coleman
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
Provides UpdateHandler, the handler for updating assignments.

Event type: UPDATE
"""

import os

from gkeepcore.assignment_config import AssignmentConfig
from gkeepserver.directory_locks import directory_locks
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import user_from_log_path, \
    faculty_assignment_dir_path, user_gitkeeper_path
from gkeepcore.system_commands import sudo_chown, rm
from gkeepcore.upload_directory import UploadDirectory
from gkeepserver.assignments import AssignmentDirectory, \
    create_base_code_repo, copy_email_txt_file, \
    copy_tests_dir, remove_student_assignment, setup_student_assignment, \
    StudentAssignmentError, copy_config_file
from gkeepserver.database import db
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.server_configuration import config


class UpdateHandler(EventHandler):
    """Handles an update to an assignment."""

    def handle(self):
        """
        Take action after a faculty member updates an assignment.

        If the assignment is unpublished, any part of the assignment may be
        updated. If the assignment has been published, only the tests may be
        updated.
        """

        gitkeeper_path = user_gitkeeper_path(self._faculty_username)

        # path to the directory that the assignment's files are kept in on
        # the server
        assignment_path = faculty_assignment_dir_path(self._class_name,
                                                      self._assignment_name,
                                                      gitkeeper_path)

        if db.is_disabled(self._class_name, self._assignment_name,
                          self._faculty_username):
            error = ('Assignment {} in class {} is disabled and '
                     'cannot be updated'
                     .format(self._assignment_name, self._class_name))
            raise HandlerException(error)

        with directory_locks.get_lock(assignment_path):
            self._perform_update(assignment_path)

    def _perform_update(self, assignment_path):
        assignment_dir = None

        try:
            assignment_dir = AssignmentDirectory(assignment_path)

            # take over ownership of the assignment directory temporarily
            sudo_chown(assignment_dir.path, config.keeper_user,
                       config.keeper_group, recursive=True)

            upload_dir = UploadDirectory(self._upload_path, check=False)

            # validate the fields in assignment.cfg file (including whether
            # the required components that support the environment are in
            # place)
            if os.path.isfile(upload_dir.config_path):
                assignment_config = \
                    AssignmentConfig(os.path.join(self._upload_path,
                                                  'assignment.cfg'),
                                     config.default_test_env)
                assignment_config.verify_env()

            self._update_items(assignment_dir, upload_dir)
            self._replace_faculty_test_assignment(assignment_dir)

            log_gkeepd_to_faculty(self._faculty_username, 'UPDATE_SUCCESS',
                                  self._upload_path)
            info = '{0} updated {1} in {2}'.format(self._faculty_username,
                                                   self._assignment_name,
                                                   self._class_name)
            gkeepd_logger.log_info(info)
        except GkeepException as e:
            error = '{0}'.format(str(e))
            log_gkeepd_to_faculty(self._faculty_username, 'UPDATE_ERROR',
                                  error)
            warning = 'Faculty update failed: {0}'.format(str(e))
            gkeepd_logger.log_warning(warning)

        # return ownership to faculty and delete the upload directory
        try:
            sudo_chown(assignment_dir.path, self._faculty_username,
                       config.keeper_group, recursive=True)
            rm(self._upload_path, recursive=True, sudo=True)
        except Exception:
            pass

    def _replace_faculty_test_assignment(self,
                                         assignment_dir: AssignmentDirectory):
        # Remove and re-setup the bare repository so the faculty can test the
        # assignment, and email the faculty.

        faculty = db.get_faculty_by_username(self._faculty_username)

        # remove existing test assignment and setup the new test assignment
        try:
            remove_student_assignment(assignment_dir, faculty,
                                      faculty.username)
            setup_student_assignment(assignment_dir, faculty, faculty.username)
        except StudentAssignmentError as e:
            raise HandlerException(str(e))

    def _update_items(self, assignment_dir: AssignmentDirectory,
                      upload_dir: UploadDirectory):
        # Update the directory that holds the files for the assignment.

        published = db.is_published(self._class_name, self._assignment_name,
                                    self._faculty_username)

        if os.path.isdir(upload_dir.base_code_path) and not published:
            rm(assignment_dir.base_code_repo_path, recursive=True)
            create_base_code_repo(assignment_dir, upload_dir.base_code_path)

        if os.path.isfile(upload_dir.email_path) and not published:
            rm(assignment_dir.email_path)
            copy_email_txt_file(assignment_dir, upload_dir.email_path)

        if os.path.isdir(upload_dir.tests_path):
            if upload_dir.action_script is None:
                error = 'No action script in tests directory'
                raise GkeepException(error)

            rm(assignment_dir.tests_path, recursive=True)
            copy_tests_dir(assignment_dir, upload_dir.tests_path)

        if os.path.isfile(upload_dir.config_path):
            rm(assignment_dir.config_path)
            copy_config_file(assignment_dir, upload_dir.config_path)

        # sanity check
        assignment_dir.check()

    def __repr__(self):
        """
        Create a string representation of the handler for printing and logging

        :return: a string representation of the event to be handled
        """

        string = ('Update from {0}: {1}/{2}'
                  .format(self._faculty_username, self._class_name,
                          self._assignment_name))

        return string

    def _parse_payload(self):
        """
        Extract the faculty username, class name, assignment name, and
        assignment path from the log event.

        Attributes available after parsing:
            _faculty_username
            _class_name
            _assignment_name
            _upload_path
        """

        self._faculty_username = user_from_log_path(self._log_path)

        if self._faculty_username is None:
            raise HandlerException('Malformed log path: {0}'
                                   .format(self._log_path))

        try:
            self._class_name, self._assignment_name, self._upload_path = \
                self._payload.split(' ')
        except ValueError:
            error = ('Expected <class name> <assignment name> <upload path> '
                     'not {0}'.format(self._payload))
            raise HandlerException(error)
