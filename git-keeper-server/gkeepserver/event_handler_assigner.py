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


"""Provides a thread for assigning handlers to  new log events."""

from queue import Queue, Empty
from threading import Thread

from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.log_file import LogEvent
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.event_handler import EventHandler


class EventHandlerAssignerError(GkeepException):
    """Raised if anything goes wrong parsing log events."""
    pass


class EventHandlerAssignerThread(Thread):
    """
    Examines new log events and create handlers to handle them.

    New log events arrive as (<log file path>, <log event>) tuples from a
    queue which is passed to the constructor. The events are examined and
    the appropriate EventHandler object is created. The EventHandler object
    is then placed into another queue so that the main thread can actually
    call the handler.

    Call the inherited start() method to start the thread, do not call run()
    directly.
    """

    def __init__(self, new_log_event_queue: Queue, event_handler_queue: Queue,
                 event_handlers_by_type: dict, logger):
        """
        Set up attributes.

        :param new_log_event_queue: input queue. (<log file path>, <log event>)
         tuples arrive in this queue
        :param event_handler_queue: output queue. EventHandler objects are
         placed in this queue after parsing
        :param event_handlers_by_type: dictionary mapping event type strings
         to EventHandler subclasses
        :param logger: a GkeepdLoggerThread for reporting information
        """

        Thread.__init__(self)

        self._event_handlers_by_type = event_handlers_by_type
        self._new_log_event_queue = new_log_event_queue
        self._event_handler_queue = event_handler_queue

        self._logger = logger

        self._shutdown_flag = False

    def shutdown(self):
        """
        Shut down the thread.

        The run loop will not exit until all queued log events are assigned
        handlers.

        This thread blocks until the thread has died.

        """

        self._shutdown_flag = True
        self.join()

    def run(self):
        # Continually examine new log events from the input queue and place the
        # appropriate EventHandler objects in the output queue.
        #
        # Do not call this method directly. Call start() instead.

        while not self._shutdown_flag:
            try:
                self._examine_all_new_events()
            except Exception as e:
                gkeepd_logger.log_error('Error examining events: {0}'
                                        .format(e))

    def _examine_all_new_events(self):
        # Examine all new log events that are in the queue

        empty = False
        while not empty:
            try:
                # block for a short time so we don't hog the CPU when the
                # queue is empty
                log_path, log_event = \
                    self._new_log_event_queue.get(block=True, timeout=0.1)

                self._examine_new_event(log_path, log_event)
            except Empty:
                # get() throws an Empty exception when the queue is empty
                empty = True
            except Exception as e:
                error = 'Unexpected error in log event assigner: {0}'.format(e)
                gkeepd_logger.log_error(error)

    def _examine_new_event(self, log_path: str, log_event: LogEvent):
        # Examine a single log event.
        #
        # :param log_path: path to the log that the event came from
        # :param log_event: the LogEvent object

        try:
            # get a handler which wll handle the event
            handler = self._get_handler(log_path, log_event)
            # pass the handler off via a queue
            self._event_handler_queue.put(handler)
        # log a warning if the event is not valid
        except GkeepException as e:
            self._logger.log_warning(str(e))

    def _get_handler(self, log_path: str, log_event: LogEvent) -> EventHandler:
        # Instantiate and return the appropriate handler for the event.
        #
        # :param log_path: the path to the log file
        # :param log_event: the LogEvent object
        # :return: an EventHandler object which will handle the event

        # raise exception on unknown event type
        if log_event.event_type not in self._event_handlers_by_type:
            raise EventHandlerAssignerError('No handler for event type {0}'
                                            .format(log_event.event_type))

        # get the handler class from the dictionary
        handler_class = self._event_handlers_by_type[log_event.event_type]
        # construct the handler from whatever class was selected
        handler = handler_class(log_path, log_event)

        return handler
