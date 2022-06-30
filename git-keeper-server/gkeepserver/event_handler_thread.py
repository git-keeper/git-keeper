# Copyright 2022 Nathan Sommer and Ben Coleman
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
Provides a thread which runs event handlers.
"""

import traceback
from queue import Queue, Empty
from threading import Thread

from gkeepcore.gkeep_exception import GkeepException


class EventHandlerThread(Thread):
    """
    Thread class for running event handlers. Event handlers are passed to the
    thread through the queue given to the initializer. Call the inherited
    start() method to start the thread, and shut down the thread by calling
    shutdown(). All items in the queue will be processed before fully shutting
    down.
    """
    def __init__(self, event_handler_queue: Queue, logger):
        """
        Initialize the thread.

        :param event_handler_queue: queue through which event handlers are
         passed
        :param logger: system logger
        """
        Thread.__init__(self)

        self._event_handler_queue = event_handler_queue
        self._logger = logger
        self._shutdown_flag = False

    def shutdown(self):
        """
        Shut down the thread.

        The run loop will not exit until all events have been handled.

        This thread blocks until the thread has died.
        """

        self._shutdown_flag = True
        self.join()

    def run(self):
        """
        Continually handle events as they arrive in the queue.

        This method should not be called directly. Call the start() method
        instead.
        """
        while not self._shutdown_flag:
            self._handle_all_new_events()

    def _handle_all_new_events(self):
        # Handles all events in the queue until the queue is empty
        empty = False
        while not empty:
            try:
                handler = self._event_handler_queue.get(block=True,
                                                        timeout=0.1)

                self._logger.log_debug('New task: ' + str(handler))

                handler.handle()
            except Empty:
                empty = True
            except (GkeepException, Exception) as e:
                # A handler's handle() method should catch all exceptions. If
                # we get here there is likely an issue with the handler.
                error = ('**ERROR: UNEXPECTED EXCEPTION**\n'
                         'This is likely due to a bug.\n'
                         'Please report this to the git-keeper developers '
                         'along with the following stack trace:\n{0}'
                         .format(traceback.format_exc()))
                print(error)
                log_error = ('Unexpected exception. Please report this bug '
                             'along with the stack trace from gkeepd\'s '
                             'standard output if possible. '
                             '{0}: {1}'.format(type(e), e))
                self._logger.log_error(log_error)
