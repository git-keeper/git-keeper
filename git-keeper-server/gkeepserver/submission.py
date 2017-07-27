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
Provides a class for storing student submission information and running tests
on the submission.
"""

import os
from time import strftime, time
from tempfile import TemporaryDirectory

from gkeepcore.student import Student
from gkeepserver.gkeepd_logger import gkeepd_logger as logger
from gkeepcore.git_commands import git_clone, git_add_all, git_commit, git_push
from gkeepcore.system_commands import cp, sudo_chown, mkdir, rm
from gkeepcore.shell_command import run_command_in_directory
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.server_configuration import config
from gkeepserver.server_email import Email
from gkeepcore.path_utils import parse_submission_repo_path, user_home_dir


class Submission:
    """
    Stores student submission information and allows test running.
    """
    def __init__(self, student: Student, student_repo_path, tests_path,
                 reports_repo_path, faculty_username, faculty_email):
        """
        Simply assign the attributes.

        :param student: Student object containing information about the student
        :param student_repo_path: path to the student's assignment repository
        :param tests_path: path to the directory containing tests for the
         assignment
        :param reports_repo_path: path to the repository where test reports are
         stored
        :param faculty_email: email address of the faculty that owns the
         assignment
        """

        self.student = student
        self.student_repo_path = student_repo_path
        self.tests_path = tests_path
        self.reports_repo_path = reports_repo_path
        self.faculty_username = faculty_username
        self.faculty_email = faculty_email

    def run_tests(self):
        """
        Run tests on the student's submission.

        Test results are emailed to the student and placed in the reports
        repository for the assignment.

        This thread must terminate in a reasonable amount of time or it may
        prevent future tests from being run and will prevent gkeepd from
        cleanly shutting down.

        Creates a directory in the tester user's home directory in which to
        run the tests.
        """

        logger.log_debug('Running tests on {0}'.format(self.student_repo_path))

        temp_path = os.path.join(user_home_dir(config.tester_user),
                                 str(time()))
        mkdir(temp_path)

        # check out the student repo in the temp dir
        git_clone(self.student_repo_path, temp_path)

        # copy the tests - this creates a tests folder inside the temp dir
        cp(self.tests_path, temp_path, recursive=True)
        temp_tests_path = os.path.join(temp_path, 'tests')

        faculty_username, class_name, assignment_name = \
            parse_submission_repo_path(self.student_repo_path)

        temp_assignment_path = os.path.join(temp_path, assignment_name)

        # make the tester user the owner of the temporary directory
        sudo_chown(temp_path, config.tester_user, config.keeper_group,
                   recursive=True)

        # execute action.sh and capture the output
        try:
            cmd = ['sudo', '-u', config.tester_user, 'bash',
                   config.run_action_sh_file_path, temp_assignment_path]
            body = run_command_in_directory(temp_tests_path, cmd)

            # send output as email
            subject = ('[{0}] {1} submission test results'
                       .format(class_name, assignment_name))
            email_sender.enqueue(Email(self.student.email_address, subject,
                                       body))

            if self.student.username != faculty_username:
                # add the report to the reports repository

                reports_temp = TemporaryDirectory()

                # put the report file into the reports repo
                git_clone(self.reports_repo_path, reports_temp.name)

                temp_reports_repo_path = os.path.join(reports_temp.name,
                                                      'reports')

                first_last_username = self.student.get_last_first_username()

                student_report_dir_path = os.path.join(temp_reports_repo_path,
                                                       first_last_username)
                os.makedirs(student_report_dir_path, exist_ok=True)

                timestamp = strftime('%Y-%m-%d-%H:%M:%S-%Z')
                report_filename = 'report-{0}.txt'.format(timestamp)
                report_file_path = os.path.join(student_report_dir_path,
                                                report_filename)

                with open(report_file_path, 'w') as f:
                    f.write(body)

                git_add_all(temp_reports_repo_path)
                git_commit(temp_reports_repo_path, 'report submission')
                git_push(temp_reports_repo_path, dest='origin', sudo=True)

                sudo_chown(self.reports_repo_path, faculty_username,
                           config.keeper_group, recursive=True)
        except Exception as e:
            report_failure(assignment_name, self.student,
                           self.faculty_email, str(e))

        if os.path.isdir(temp_path):
            rm(temp_path, recursive=True, sudo=True)

        logger.log_debug('Done running tests on {0}'
                         .format(self.student_repo_path))


def report_failure(assignment, student, faculty_email, message):

    s_subject = ('{0}: Failed to process submission - contact instructor'
                 .format(assignment))
    s_body = ['Your submission was received, but something went wrong.',
              'This is likely your instructor\'s fault, not yours.',
              'Please contact your instructor about this error!']

    email_sender.enqueue(Email(student.email_address, s_subject, s_body))

    f_subject = 'git-keeper run_tests failure'
    f_body = ['student: {0} {1}'.format(student.first_name, student.last_name),
              'email: {0}'.format(student.email_address),
              'assignment {0}'.format(assignment),
              'further information:',
              message]

    email_sender.enqueue(Email(faculty_email, f_subject, f_body))
