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
Provides a thread for parsing new log events and creating handlers to
handle them.
"""


import re
from queue import Queue, Empty
from threading import Thread

from gkeepcore.event_handler import EventHandler, HandlerException


class LogEventParserException(Exception):
    pass


class LogEventParserThread(Thread):
    """
    Parses new log events and create handlers to handle them.

    New log events arrive as (<log file path>, <log line>) tuples from a
    queue which is passed to the constructor. The events are parsed and the
    appropriate EventHandler object is created. The EventHandler object is
    then placed into another queue so that the main thread can actually call
    the handler.

    Log lines look like this:

        <timestamp> <event type> <payload>

    <timestamp> is a float representing seconds from the epoch.

    <event type> determines which EventHandler will handle the event. A
    dictionary mapping <event type> strings to EventHandler subclasses is
    passed in to the constructor.

    Call the inherited start() method to start the thread, do not call run()
    directly.
    """

    def __init__(self, new_log_line_queue: Queue, event_handler_queue: Queue,
                 event_handlers_by_type: dict, logger):
        """
        Set up attributes.

        :param new_log_line_queue: input queue. (<log file path>, <log line>)
         tuples arrive in this queue
        :param event_handler_queue: output queue. EventHandler objects are
         placed in this queue after parsing
        :param event_handlers_by_type: dictionary mapping event type strings
         to EventHandler subclasses
        :param logger: a SystemLoggerThread for reporting information

        """

        Thread.__init__(self)

        self._event_handlers_by_type = event_handlers_by_type
        self._new_log_line_queue = new_log_line_queue
        self._event_handler_queue = event_handler_queue

        self._logger = logger

        self._shutdown_flag = False

    def shutdown(self):
        """
        Shut down the thread after parsing all queued log lines.

        Call join() on the thread after calling shutdown() to make sure the
        thread has shut down before moving on.

        """

        self._shutdown_flag = True

    def run(self):
        # Continually parse new log lines from the input queue and place the
        # appropriate EventHandler object in the output queue.
        #
        # Do not call this method directly. Call start() instead.

        while not self._shutdown_flag:
            self._parse_all_new_lines()

    def _parse_all_new_lines(self):
        # Parse all new log lines that are in the queue

        try:
            while True:
                # block for a short time so we don't hog the CPU when the
                # queue is empty
                log_path, log_line = self._new_log_line_queue.get(block=True,
                                                                  timeout=0.1)
                self._parse_new_line(log_path, log_line)
        except Empty:
            # get() throws an Empty exception when the queue is empty
            pass

    def _parse_new_line(self, log_path: str, log_line: str):
        # Parse a single line from a log.
        #
        # :param log_path: path to the log that the line came from
        # :param log_line: the text of the line

        try:
            # parse the line and get a handler which wll handle the event
            handler = self._parse_line(log_path, log_line)
            # pass the handler off via a queue
            self._event_handler_queue.put(handler)
        # log a warning if the log line is not a valid event that can be handled
        except (LogEventParserException, HandlerException) as e:
            self._logger.log_warning(str(e))

    def _parse_line(self, log_path: str, log_line: str) -> EventHandler:
        # Parse the event. This is done in two stages:
        #
        # - Timestamp, event type, and payload are extracted from the log line
        # - An EventHandler is created, which parses the rest of the event
        #
        # Raises:
        #     LogEventParserException
        #     HandlerException
        #
        # :param log_path: the path to the log file
        # :param log_line: the line from the log file representing the event
        # :return: an EventHandler object which will handle the event

        # use a regular expression to match timestamp, event type, and payload
        match = re.match('(\d+.\d+) (\w+) (.*)', log_line)

        if match is None:
            error = 'Log line does not look like an event: {0}'.format(log_line)
            raise LogEventParserException(error)

        timestamp, event_type, payload = match.groups()

        # raise exception on unknown event type
        if event_type not in self._event_handlers_by_type:
            raise LogEventParserException('No handler for event type {0}'
                                          .format(event_type))

        # get the handler class from the dictionary
        handler_class = self._event_handlers_by_type[event_type]
        # construct the handler from whatever class was selected
        handler = handler_class(log_path, float(timestamp), payload)

        return handler
