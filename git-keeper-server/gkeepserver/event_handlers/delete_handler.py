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
from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import user_from_log_path, \
    faculty_assignment_dir_path, user_home_dir, class_student_csv_path
from gkeepcore.student import students_from_csv
from gkeepcore.system_commands import rm
from gkeepserver.assignments import AssignmentDirectory, \
    remove_student_assignment
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.faculty import FacultyMembers
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.info_update_thread import info_updater
from gkeepserver.server_configuration import config


class DeleteHandler(EventHandler):
    """Handles a request from the client to delete an assignment"""

    def handle(self):
        """
        Take action after a client requests that an assignment be deleted.

        Delete the assignment directory, the faculty test repo, and all
        student repos for the assignment.
        """

        faculty_home_dir = user_home_dir(self._faculty_username)

        # path to the directory that the assignment's files are kept in
        assignment_path = faculty_assignment_dir_path(self._class_name,
                                                      self._assignment_name,
                                                      faculty_home_dir)

        print('Handling delete:')
        print(' Faculty:        ', self._faculty_username)
        print(' Class:          ', self._class_name)
        print(' Assignment:     ', self._assignment_name)
        print(' Assignment path:', assignment_path)

        try:
            assignment_dir = AssignmentDirectory(assignment_path)

            self._delete_assignment(assignment_dir)

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

    def _delete_assignment(self, assignment_dir: AssignmentDirectory):
        # Delete the assignment bare repos for the students and the faculty,
        # as well as the assignment directory itself.

        home_dir = user_home_dir(self._faculty_username)

        assignment_name = assignment_dir.assignment_name

        reader = LocalCSVReader(class_student_csv_path(self._class_name,
                                                       home_dir))
        students_with_assignment = []

        faculty = FacultyMembers().get_faculty_object(self._faculty_username)

        students_with_assignment.append(faculty)

        if assignment_dir.is_published():
            for student in students_from_csv(reader):
                students_with_assignment.append(student)

        # delete each student's repository and the faculty test repository
        for student in students_with_assignment:
            try:
                remove_student_assignment(assignment_dir, student,
                                          self._faculty_username)
            except GkeepException as e:
                gkeepd_logger.log_warning('Could not remove {0} for {1}: {2}'
                                          .format(assignment_name,
                                                  student.username, e))

        # delete the assignment directory
        rm(assignment_dir.path, recursive=True, sudo=True)

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
