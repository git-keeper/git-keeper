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
Provides a class for running tests on a student submission in a separate
thread.
"""


from threading import Thread

from gkeepserver.submission import Submission


class SubmissionTestThread(Thread):
    """
    A Thread for running tests on a student submission.
    """
    def __init__(self, submission: Submission):
        """
        Store the submission and start the thread.

        :param submission: the student submission
        """

        Thread.__init__(self)
        self._submission = submission
        self.start()

    def run(self):
        # Run the tests.
        #
        # This should not be called directly.

        self._submission.run_tests()
