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


from time import sleep
from random import random

from gkeepcore.student import Student
from gkeepcore.system_logger import system_logger as logger


class Submission:
    """
    Stores student submission information and allows test running.
    """
    def __init__(self, student: Student, student_repo_path, tests_repo_path,
                 reports_repo_path):
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
        self.tests_repo_path = tests_repo_path
        self.reports_repo_path = reports_repo_path

    def run_tests(self):
        """
        Run tests on the student's submission.

        This thread must terminate in a reasonable amount of time or it may
        prevent future tests from being run and will prevent gkeepd from
        cleanly shutting down.
        """

        # FIXME - actually run tests
        logger.log_debug('Running tests on {0}'.format(self.student_repo_path))

        # just sleep for testing
        sleep(random() * 5)

        logger.log_debug('Done running tests on {0}'
                         .format(self.student_repo_path))
