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
Provides a class for storing student submission information and running tests
on the submission.
"""

import os
from time import strftime
from tempfile import TemporaryDirectory

from gkeepcore.student import Student
from gkeepserver.gkeepd_logger import gkeepd_logger as logger
from gkeepcore.git_commands import git_clone, git_add_all, git_commit, git_push
from gkeepcore.system_commands import cp
from gkeepcore.shell_command import run_command, run_command_in_directory, CommandError
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.server_email import Email
from gkeepcore.path_utils import parse_submission_repo_path


class Submission:
    """
    Stores student submission information and allows test running.
    """
    def __init__(self, student: Student, student_repo_path, tests_path,
                 reports_repo_path, faculty_email):
        """
        Simply assign the attributes.

        :param student: Student object containing information about the student
        :param student_repo_path: path to the student's assignment repository
        :param tests_repo_path: path to the repository containing tests for the
         assignment
        :param reports_repo_path: path to the repository where test reports are
         stored
        """

        self.student = student
        self.student_repo_path = student_repo_path
        self.tests_path = tests_path
        self.reports_repo_path = reports_repo_path
        self.faculty_email = faculty_email

    def run_tests(self):
        """
        Run tests on the student's submission.

        This thread must terminate in a reasonable amount of time or it may
        prevent future tests from being run and will prevent gkeepd from
        cleanly shutting down.
        """

        logger.log_debug('Running tests on {0}'.format(self.student_repo_path))

        working_dir = TemporaryDirectory()
        temp_path = working_dir.name

        # check out the student repo in the temp dir
        git_clone(self.student_repo_path, temp_path)

        # copy the tests - this creates a test folder inside the temp dir...
        cp(self.tests_path, temp_path, recursive=True)

        # execute action.sh and capture the output
        try:
            assignment_name = parse_submission_repo_path(self.student_repo_path)[2]
            cmd = ['bash', 'action.sh', temp_path + '/' + assignment_name]
            body = run_command_in_directory(temp_path + '/tests/' , cmd)

            # The following version of running action.sh uses docker
            #cmd = 'docker run -it -v '
            #cmd += temp_path
            #cmd += ':/temp coleman/git-keeper-test-env bash go'
            #body = run_command(cmd)

            # send output as email
            subject = assignment_name + ' submission test results'
            email_sender.enqueue(Email(self.student.email_address, subject, body))

            # put the report file into the reports repo
            git_clone(self.reports_repo_path, temp_path)

            report_path = temp_path + '/reports/' + self.student.username
            os.makedirs(report_path, exist_ok=True)

            report_filename = 'report-{0}.txt'.format(strftime('%Y-%m-%d-%H:%M:%S-%Z'))
            report_file_path = report_path + '/' + report_filename

            with open(report_file_path, 'w') as f:
                f.write(body)

            reports_repo_path = temp_path + '/reports'

            git_add_all(reports_repo_path)
            git_commit(reports_repo_path, 'report submission')
            git_push(reports_repo_path, dest='origin')

        except (OSError, IOError, CommandError) as e:
            report_failure(assignment_name, self.student,
                           self.faculty_email, str(e))

        logger.log_debug('Done running tests on {0}'
                         .format(self.student_repo_path))


def report_failure(assignment, student, faculty_email, message):

    s_subject = '{0}: Failed to process submission - contact instructor'.format(assignment)
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


