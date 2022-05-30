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

from gkeepcore.git_commands import git_head_hash
from gkeepcore.path_utils import user_home_dir, faculty_assignment_dir_path, \
    student_assignment_repo_path, user_gitkeeper_path
from gkeepserver.assignments import AssignmentDirectory
from gkeepserver.database import db
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.handler_utils import log_gkeepd_to_faculty
from gkeepserver.new_submission_queue import new_submission_queue
from gkeepserver.submission import Submission


class TriggerHandler(EventHandler):
    """Handles a request from the client to trigger assignment tests."""

    def handle(self):
        """
        Take action after a client requests that tests be run for an
        assignment.
        """

        gitkeeper_path = user_gitkeeper_path(self._faculty_username)

        # path to the directory that the assignment's files are kept in
        assignment_path = faculty_assignment_dir_path(self._class_name,
                                                      self._assignment_name,
                                                      gitkeeper_path)

        try:
            assignment_dir = AssignmentDirectory(assignment_path)

            faculty_only = (len(self._student_usernames) == 1 and
                            self._faculty_username in self._student_usernames)

            is_published = db.is_published(self._class_name,
                                           self._assignment_name,
                                           self._faculty_username)
            if not is_published and not faculty_only:
                error = ('Assignment {} in class {} is not published.\n'
                         'Unpublished assignments may only be triggered for '
                         'the faculty account'
                         .format(self._assignment_name, self._class_name))
                raise HandlerException(error)

            is_disabled = db.is_disabled(self._class_name,
                                         self._assignment_name,
                                         self._faculty_username)
            if is_disabled:
                error = ('Assignment {} in class {} is disabled, and cannot '
                         'be triggered'.format(self._assignment_name,
                                               self._class_name))
                raise HandlerException(error)

            students = db.get_class_students(self._class_name,
                                             self._faculty_username)

            if len(self._student_usernames) > 0:
                students = [s for s in students
                            if s.username in self._student_usernames]

            if self._faculty_username in self._student_usernames:
                faculty = db.get_faculty_by_username(self._faculty_username)
                students.append(faculty)

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

    def _trigger_tests(self, students, assignment_dir: AssignmentDirectory):
        faculty = db.get_faculty_by_username(self._faculty_username)
        faculty_email = faculty.email_address

        # trigger tests for all requested students
        for student in students:
            home_dir = user_home_dir(student.username)
            submission_repo_path = \
                student_assignment_repo_path(self._faculty_username,
                                             self._class_name,
                                             self._assignment_name, home_dir)

            commit_hash = git_head_hash(submission_repo_path,
                                        user=student.username)

            submission = Submission(student, submission_repo_path, commit_hash,
                                    assignment_dir, self._faculty_username,
                                    faculty_email)
            new_submission_queue.put(submission)

    def __repr__(self):
        """
        Create a string representation of the handler for printing and logging

        :return: a string representation of the event to be handled
        """

        if len(self._student_usernames) > 0:
            string = ('{0} requested to trigger tests on assignment {2} in '
                      'class {1} for student(s) {3}'
                      .format(self._faculty_username, self._class_name,
                              self._assignment_name,
                              ' '.join(self._student_usernames)))
        else:
            string = ('{0} requested to trigger tests on assignment {2} in '
                      'class {1} for all students'
                      .format(self._faculty_username, self._class_name,
                              self._assignment_name))

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
        if len(payload_list) < 2:
            error = ('Invalid payload for TRIGGER: {0}'.format(self._payload))
            raise HandlerException(error)

        self._class_name = payload_list[0]
        self._assignment_name = payload_list[1]
        self._student_usernames = payload_list[2:]
