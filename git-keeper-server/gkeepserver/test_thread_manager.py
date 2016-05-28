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
Provides global access to a Thread class that waits for new submissions to
arrive via a queue and spawns threads in which to test them.

Global access is provided through the module-level test_thread_manager
reference.

Interface:

start() - start the thread manager
enqueue_submission(submission: Submission) - add a submission to be tested
shutdown() - shutdown the thread, blocks until joined

The maximum number of test threads is specified in the server configuration. If
there are already the maximum number of threads running, new submissions will
remain in the queue until there is a free slot.

"""


from queue import Queue
from threading import Thread
from time import sleep

from gkeepserver.submission import Submission
from gkeepserver.submission_test_thread import SubmissionTestThread
from gkeepserver.server_configuration import config


class TestThreadManagerThread(Thread):
    """
    Provides a manager which waits for new submissions to arrive and spawns
    threads to test them.

    See the module-level documentation for use.
    """
    def __init__(self):
        """
        Initialize the thread manager.

        The thread will not start until start() is called.
        """

        Thread.__init__(self)

        # Store the current threads in a list. This may contain dead threads.
        # They will be removed when new threads are needed.
        self._threads = []

        # New submissions arrive in this queue
        self._new_submission_queue = Queue()

        # This is set from the server configuration which will not yet be
        # when the module is imported
        self._max_thread_count = None

        # Switched to True by shutdown() when it's time to shut down
        self._shutdown_flag = False

    def start(self):
        """Initialize the max thread count and start the thread."""

        self._max_thread_count = config.max_test_thread_count
        Thread.start(self)

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
        # Continually check the queue for new submissions and test them.
        #
        # Do not call this method directly, call start() instead.

        while not self._shutdown_flag:
            # test all new submissions in the queue
            while not self._new_submission_queue.empty():
                # if the max number of threads are already running, wait until
                # one finishes
                while len(self._threads) >= self._max_thread_count:
                    if not self._purge_dead_threads():
                        # don't hog the CPU while waiting for threads to
                        # finish
                        sleep(0.1)

                submission = self._new_submission_queue.get()

                # create and start the thread, the constructor calls start()
                thread = SubmissionTestThread(submission)

                self._threads.append(thread)

            # If the queue is empty, don't hog the CPU
            else:
                sleep(0.1)

        # wait until all tests are done to shut down
        for thread in self._threads:
            thread.join()

    def enqueue_submission(self, submission: Submission):
        """
        Add a new submission to be tested.

        The submission may have to wait in the queue if other tests are
        running.

        :param submission:
        """

        self._new_submission_queue.put(submission)

    def _purge_dead_threads(self) -> bool:
        # remove any dead thrads from _threads
        #
        # return True if any dead threads were removed, False otherwise

        original_thread_count = len(self._threads)

        # only keep the live threads
        self._threads = [t for t in self._threads if t.is_alive()]

        live_thread_count = len(self._threads)

        return live_thread_count < original_thread_count


test_thread_manager = TestThreadManagerThread()
