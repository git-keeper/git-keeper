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
Provides a class for running tests on student submissions in a separate
thread.

New submissions are pulled from the global new_submission_queue.
"""

from queue import Empty
from threading import Thread
from gkeepserver.gkeepd_logger import gkeepd_logger as logger
from gkeepserver.new_submission_queue import new_submission_queue


class SubmissionTestThread(Thread):
    """
    A Thread for running tests on student submissions.

    Gets new submissions from the global new_submission_queue.
    """
    def __init__(self):
        """Create the object and start the thread."""

        Thread.__init__(self)

        # set to True when shutdown() is called
        self._shutdown_flag = False

        self.start()

    def shutdown(self):
        """
        Shut down the thread.

        Sets the shutdown flag to True. The run() loop will then exit after all
        submissions in the queue have been tested.

        This method blocks until the thread dies.
        """

        self._shutdown_flag = True
        self.join()

    def run(self):
        # Continually check for new submissions from new_submission_queue
        # and test them.
        #
        # Do not call this method directly.

        while not self._shutdown_flag:
            try:
                # consume all submissions in the queue before shutdown
                while True:
                    submission = new_submission_queue.get(block=True,
                                                          timeout=0.1)
                    submission.run_tests()

            # get() raises Empty when there is nothing in the queue after
            # timeout seconds
            except Empty:
                pass
            except Exception as e:
                logger.log_error('Error while running tests: {0}'.format(e))
