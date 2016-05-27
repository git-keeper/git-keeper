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
Provides a logger with global access for logging system information.

This module stores a SystemLoggerThread instance in the module level variable named
system_logger. Call initialize() on this instance as early as possible after
initializing the configuration.

After the logger has been initialized, start the logging thread by calling
start().

To shut the thread down, call shutdown() followed join(). All messages in the
queue will be logged before the thread dies.

Each line of the log is one of these types:
    ERROR
    WARNING
    INFO
    DEBUG

The level of logging can be set when initializing the method. Log level
INFO is advisable for a normally running server. DEBUG can be enabled during
development.

There is a method for logging a message at each level:
    log_error()
    log_warning()
    log_info()
    log_debug()

"""


from enum import IntEnum
from threading import Thread
from queue import Queue, Empty

from gkeepcore.log_file import LogFileWriter


class LogLevel(IntEnum):
    """
    Enumeration of log levels.

    It is an IntEnum so that the levels can be ordered.

    """
    NONE = -1
    ERROR = 0
    WARNING = 1
    INFO = 2
    DEBUG = 3


class SystemLoggerThread(Thread):
    """
    Provides a Thread which logs system messages to a log file.

    Typically this will be accessed with the provided module-level global
    instance rather than making an instance directly.

    Call initialize() before starting the thread. Call start() to start it.

    Shutdown the thread by calling shutdown() followed by a call to join().

    Log messages using these methods:
        log_error()
        log_warning()
        log_info()
        log_debug()

    """
    def __init__(self):
        """
        Construct the object.

        Constructing the object does not start the thread. Call initialize()
        followed by start() to actually start the thread.

        Attributes are initialized to None.

        """

        # daemon=True means if the main thread dies this will die along with it
        Thread.__init__(self, daemon=True)

        self._log_file_path = None
        self._log_append_function = None
        self._writer = None
        self._log_level = None
        self._new_line_queue = None
        self._shutdown_flag = None

    def initialize(self, log_file_path: str, log_append_function,
                   log_level=LogLevel.DEBUG):
        """
        Initialize the attributes.

        log_append_function() is used in creating a LogFileWriter and it must
        have the following signature:

            log_append_function(file_path: str, item_type: str, text: str)

        This allows writing to local or remote files, depending on the function
        passed in.

        log_append_function() should ensure that the log line is at most 4KB
        to ensure atomic writes.

        log_level is the maximum log level to log. LogLevel.DEBUG will log
        everything, LogLevel.INFO will log everything but debug messages, etc.

        :param log_file_path: path to the log file
        :param log_append_function: function used to append to the log
        :param log_level:
        :return: the maximum log level to log
        """

        self._log_file_path = log_file_path
        self._log_append_function = log_append_function
        self._writer = LogFileWriter(log_file_path, self._log_append_function)
        self._log_level = log_level
        self._new_line_queue = Queue()
        self._shutdown_flag = False

    def shutdown(self):
        """
        Shut down the logger.

        This method is thread safe.

        The logger thread will not shut down until all messages in the queue
        are logged.
        """

        self._shutdown_flag = True

    def run(self):
        # Log until _shutdown_flag is True.
        #
        # This should not be called directly, the thread should be started by
        # calling start()

        while not self._shutdown_flag:
            try:
                while True:
                    # We can't fully block because we need to check
                    # _shutdown_flag regularly
                    log_level, text = self._new_line_queue.get(block=True,
                                                               timeout=0.1)
                    self._cleanup_and_log(log_level, text)
            # git() raises Empty after blocking for timeout seconds and the
            # queue is still empty
            except Empty:
                pass

    def _cleanup_and_log(self, log_level, text: str):
        # Replace newlines with spaces and pass the message off to the writer.

        # Only log if we're logging this log level
        if self._log_level >= log_level:
            # Replace newlines in text with spaces so the entire log text is on
            # one line
            text = text.replace('\n', ' ')
            self._writer.log(log_level.name, text)

    def log_debug(self, text: str):
        """
        Log a debugging message.

        :param text: text to log
        """

        self._new_line_queue.put((LogLevel.DEBUG, text))

    def log_info(self, text: str):
        """
        Log an informative message.

        :param text: text to log
        :return:
        """

        self._new_line_queue.put((LogLevel.INFO, text))

    def log_warning(self, text: str):
        """
        Log a warning message.

        :param text: text to log
        :return:
        """

        self._new_line_queue.put((LogLevel.WARNING, text))

    def log_error(self, text: str):
        """
        Log an error message.

        :param text: text to log
        :return:
        """

        self._new_line_queue.put((LogLevel.ERROR, text))


# module-level instance for global access.
system_logger = SystemLoggerThread()
