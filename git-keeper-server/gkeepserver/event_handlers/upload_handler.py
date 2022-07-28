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
Provides UploadHandler, the handler for new assignment uploads.

Event type: UPLOAD
"""

import os

from gkeepcore.git_commands import git_init_bare
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import user_from_log_path, \
    faculty_assignment_dir_path, user_gitkeeper_path
from gkeepcore.shell_command import CommandError
from gkeepcore.system_commands import chmod, sudo_chown, rm, mkdir
from gkeepcore.assignment_config import AssignmentConfig
from gkeepcore.upload_directory import UploadDirectory, UploadDirectoryError
from gkeepcore.valid_names import validate_assignment_name
from gkeepserver.assignments import AssignmentDirectory, \
    AssignmentDirectoryError, create_base_code_repo, copy_email_txt_file, \
    copy_tests_dir, setup_student_assignment, StudentAssignmentError, \
    copy_config_file
from gkeepserver.database import db
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.info_update_thread import info_updater
from gkeepserver.server_configuration import config


class UploadHandler(EventHandler):
    """Handles a new assignment uploaded by a faculty member."""

    def handle(self):
        """
        Take action after a faculty member uploads a new assignment.

        If a Docker image is specified in assignment.cfg, verifies that the
        image exists

        Copies uploaded files into the proper directory, creates bare
        repositories, and creates a repository the faculty member can use
        to
        """

        gitkeeper_path = user_gitkeeper_path(self._faculty_username)

        # path to the directory that the assignment's files will be kept in
        assignment_path = faculty_assignment_dir_path(self._class_name,
                                                      self._assignment_name,
                                                      gitkeeper_path)

        assignment_dir = AssignmentDirectory(assignment_path, check=False)

        try:
            # validate the fields in assignment.cfg file (including whether the
            # required components that support the environment are in place)
            assignment_config = \
                AssignmentConfig(os.path.join(self._upload_path,
                                              'assignment.cfg'),
                                 default_env=config.default_test_env)
            assignment_config.verify_env()

            if not db.class_is_open(self._class_name, self._faculty_username):
                raise HandlerException('{} is not open'
                                       .format(self._class_name))

            validate_assignment_name(assignment_dir.assignment_name)
            self._setup_assignment_dir(assignment_dir)
            self._setup_faculty_test_assignment(assignment_dir)

            db.insert_assignment(self._class_name, self._assignment_name,
                                 self._faculty_username)

            info_updater.enqueue_assignment_scan(self._faculty_username,
                                                 self._class_name,
                                                 self._assignment_name)

            log_gkeepd_to_faculty(self._faculty_username, 'UPLOAD_SUCCESS',
                                  self._upload_path)
            info = '{0} uploaded {1} to {2}'.format(self._faculty_username,
                                                    self._assignment_name,
                                                    self._class_name)
            gkeepd_logger.log_info(info)
        except Exception as e:
            error = '{0}'.format(str(e))
            log_gkeepd_to_faculty(self._faculty_username, 'UPLOAD_ERROR',
                                  error)
            warning = 'Faculty upload failed: {0}'.format(str(e))
            gkeepd_logger.log_warning(warning)

            # if we failed, remove the assignment directory
            try:
                rm(assignment_path, recursive=True, sudo=True)
            except CommandError:
                pass

        # delete the upload directory
        try:
            rm(self._upload_path, recursive=True, sudo=True)
        except CommandError:
            pass

    def _setup_faculty_test_assignment(self,
                                       assignment_dir: AssignmentDirectory):
        # Setup a bare repository so the faculty can test the assignment,
        # and email the faculty.

        faculty = db.get_faculty_by_username(self._faculty_username)

        # set up the faculty's test assignment and send email
        try:
            setup_student_assignment(assignment_dir, faculty, faculty.username)
        except StudentAssignmentError as e:
            raise HandlerException(str(e))

    def _setup_assignment_dir(self, assignment_dir: AssignmentDirectory):
        # Setup the directory that holds the files for the assignment.

        # Ensure all necessary files are present in the upload directory
        try:
            upload_dir = UploadDirectory(self._upload_path)
        except UploadDirectoryError as e:
            raise HandlerException(e)

        # bail if assignment directory already exists
        if os.path.isdir(assignment_dir.path):
            error = '{0} already exists'.format(self._assignment_name)
            raise HandlerException(error)

        try:
            # create the assignment directory and make it owned by keeper for
            # now
            mkdir(assignment_dir.path, sudo=True)
            sudo_chown(assignment_dir.path, config.keeper_user,
                       config.keeper_group)
        except CommandError as e:
            error = 'error creating directory: {0}'.format(str(e))
            raise HandlerException(error)

        try:
            # initialize reports repo
            mkdir(assignment_dir.reports_repo_path)
            git_init_bare(assignment_dir.reports_repo_path)
            chmod(assignment_dir.reports_repo_path, '770', recursive=True)

            # create the base code repo
            create_base_code_repo(assignment_dir, upload_dir.base_code_path)
        except GkeepException as e:
            raise HandlerException(e)

        # copy email.txt, assignment.cfg, and tests directory to assignment
        # directory
        try:
            copy_email_txt_file(assignment_dir, upload_dir.email_path)
            copy_tests_dir(assignment_dir, upload_dir.tests_path)
            copy_config_file(assignment_dir, upload_dir.config_path)
        except GkeepException as e:
            error = ('error copying assignment files: {0}'.format(str(e)))
            raise HandlerException(error)

        # set permissions on assignment directory
        try:
            chmod(assignment_dir.path, '750', sudo=True)
            sudo_chown(assignment_dir.path, self._faculty_username,
                       config.keeper_group, recursive=True)
        except CommandError as e:
            error = ('error setting permissions on {0}: {1}'
                     .format(assignment_dir.path, str(e)))
            raise HandlerException(error)

        # sanity check
        try:
            assignment_dir.check()
        except AssignmentDirectoryError as e:
            raise HandlerException(e)

    def __repr__(self):
        """
        Create a string representation of the handler for printing and logging

        :return: a string representation of the event to be handled
        """

        string = ('Upload from {0}: {1}/{2}'
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
