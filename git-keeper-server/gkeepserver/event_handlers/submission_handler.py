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
Handler for student submissions.

Event type: SUBMISSION
"""

from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.path_utils import user_from_log_path, \
    parse_submission_repo_path
from gkeepcore.path_utils import user_home_dir, class_student_csv_path, \
    faculty_assignment_dir_path
from gkeepcore.student import student_from_username
from gkeepserver.assignments import AssignmentDirectory
from gkeepserver.event_handler import EventHandler, HandlerException
from gkeepserver.faculty import FacultyMembers
from gkeepserver.new_submission_queue import new_submission_queue
from gkeepserver.server_configuration import config
from gkeepserver.submission import Submission


class SubmissionHandler(EventHandler):
    """Handles a new submission from a student."""

    def handle(self):
        """Take action after a student pushes a new submission."""

        print('Handling submission:')
        print(' Student:    ', self._student_username)
        print(' Faculty:    ', self._faculty_username)
        print(' Class:      ', self._class_name)
        print(' Assignment: ', self._assignment_name)
        print(' Repo path:  ', self._submission_repo_path)
        print(' Commit hash:', self._commit_hash)
        print()

        # We need to create a submission object to put in the
        # new_submission_queue.  This requires a Student object and
        # paths to student repo, tests (not a repo), and reports repo.

        # The AssignmentDirectory object can provide the paths we need
        faculty_home_dir = user_home_dir(self._faculty_username)

        faculty = FacultyMembers().get_faculty_object(self._faculty_username)
        faculty_email = faculty.email_address

        assignment_path = faculty_assignment_dir_path(self._class_name,
                                                      self._assignment_name,
                                                      faculty_home_dir)
        assignment_directory = AssignmentDirectory(assignment_path)

        reader = LocalCSVReader(class_student_csv_path(self._class_name,
                                                       faculty_home_dir))

        # if the student is the facutly testing the assignment, use the
        # faculty as the student
        if self._student_username == self._faculty_username:
            student = faculty
        # otherwise build the Student from the csv for the class
        else:
            student = student_from_username(self._student_username, reader)

        submission = Submission(student, self._submission_repo_path,
                                self._commit_hash, assignment_directory,
                                self._faculty_username, faculty_email)

        new_submission_queue.put(submission)

    def __repr__(self) -> str:
        """
        Create a string representation of the object for printing and
        logging

        :return: a string representation of the event to be handled
        """

        string = ('Submission event from {0} for assignment {1}/{2}/{3}'
                  .format(self._student_username, self._faculty_username,
                          self._class_name, self._assignment_name))

        return string

    def _parse_payload(self):
        """
        Extract the student username, faculty username, class name,
        assignment name, and student submission repository from the log event.

        Attributes available after parsing:
            _student_username
            _faculty_username
            _class_name
            _assignment_name
            _submission_repo_path
        """

        self._parse_log_path()

        # the payload contains the submission repository path and the hash of
        # the commit of the submission
        self._submission_repo_path, self._commit_hash = self._payload.split()

        self._parse_repo_path()

    def _parse_log_path(self):
        """
        Extract the student username from the log file path.

        Raises:
             HandlerException

        Initializes attributes:
            _student_username
        """

        self._student_username = user_from_log_path(self._log_path)

        if self._student_username is None:
            raise HandlerException('Malformed log path: {0}'
                                   .format(self._log_path))

    def _parse_repo_path(self):
        """
        Extract the faculty username, class name, and assignment name from
        the assignment path.

        Raises:
            HandlerException

        Initializes attributes:
            _faculty_username
            _class_name
            _assignment_name
        """

        assignment_info = \
            parse_submission_repo_path(self._submission_repo_path)

        if assignment_info is None:
            raise HandlerException('Malformed submission repo path: {0}'
                                   .format(self._submission_repo_path))

        self._faculty_username, self._class_name, self._assignment_name = \
            assignment_info
