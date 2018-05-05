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
Provides TriggerHandler, the handler for triggering assignment tests

Event type: TRIGGER
"""
from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import user_home_dir, faculty_assignment_dir_path, \
    user_log_path, student_assignment_repo_path
from gkeepserver.assignments import AssignmentDirectory
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.faculty import FacultyMembers
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.new_submission_queue import new_submission_queue
from gkeepserver.server_configuration import config
from gkeepserver.students_and_classes import get_class_students
from gkeepserver.submission import Submission


class TriggerHandler(EventHandler):
    """Handles a request from the client to trigger assignment tests."""

    def handle(self):
        """
        Take action after a client requests that tests be run for an
        assignment.
        """

        faculty_home_dir = user_home_dir(self._faculty_username)

        # path to the directory that the assignment's files are kept in
        assignment_path = faculty_assignment_dir_path(self._class_name,
                                                      self._assignment_name,
                                                      faculty_home_dir)

        print('Handling trigger:')
        print(' Faculty:        ', self._faculty_username)
        print(' Class:          ', self._class_name)
        print(' Assignment:     ', self._assignment_name)
        print(' Students:       ', self._student_usernames)

        try:
            assignment_dir = AssignmentDirectory(assignment_path)
            self._ensure_published(assignment_dir)
            students = get_class_students(self._faculty_username,
                                          self._class_name)

            students = [s for s in students
                        if s.username in self._student_usernames]

            self._trigger_tests(students, assignment_dir)

            log_gkeepd_to_faculty(self._faculty_username, 'TRIGGER_SUCCESS',
                                  '{0} {1}'.format(self._class_name,
                                                   self._assignment_name))
            info = ('{0} triggered tests on {1} for students {2}'
                    .format(self._faculty_username, self._assignment_name,
                            ' '.join(self._student_usernames)))
            gkeepd_logger.log_info(info)
        except Exception as e:
            log_gkeepd_to_faculty(self._faculty_username, 'TRIGGER_ERROR',
                                  str(e))
            warning = 'Trigger failed: {0}'.format(e)
            gkeepd_logger.log_warning(warning)

    def _ensure_published(self, assignment_dir: AssignmentDirectory):
        # Throw an exception if the assignment is not published
        if not assignment_dir.is_published():
            raise HandlerException('Assignment is not published')

    def _trigger_tests(self, students, assignment_dir: AssignmentDirectory):
        faculty = FacultyMembers().get_faculty_object(self._faculty_username)
        faculty_email = faculty.email_address

        # trigger tests for all requested students
        for student in students:
            home_dir = user_home_dir(student.username)
            log_path = user_log_path(home_dir, student.username)
            submission_repo_path = \
                student_assignment_repo_path(self._faculty_username,
                                             self._class_name,
                                             self._assignment_name, home_dir)

            submission = Submission(student, submission_repo_path,
                                    assignment_dir, self._faculty_username,
                                    faculty_email)
            new_submission_queue.put(submission)

    def __repr__(self):
        """
        Create a string representation of the handler for printing and logging

        :return: a string representation of the event to be handled
        """

        string = ('{0} requested to trigger tests on {1} for student(s) {2}'
                  .format(self._faculty_username, self._class_name,
                          self._assignment_name,
                          ' '.join(self._student_usernames)))

        return string

    def _parse_payload(self):
        """
        Extract the faculty username, class name, assignment name, and list of
        student usernames from the log event.

        Attributes available after parsing:
            _faculty_username
            _class_name
            _assignment_name
            _student_usernames
        """

        self._parse_log_path()

        payload_list = self._payload.split(' ')

        # there must be a class name and assignment name, and at least one
        # student username
        if len(payload_list) < 3:
            error = ('Invalid payload for TRIGGER: {0}'.format(self._payload))
            raise HandlerException(error)

        self._class_name = payload_list[0]
        self._assignment_name = payload_list[1]
        self._student_usernames = payload_list[2:]
