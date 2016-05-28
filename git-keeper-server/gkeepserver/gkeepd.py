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
Main entry point for gkeepd, the git-keeper server process.

Spawns a number of threads:

logger - SystemLoggerThread for logging runtime information
email_sender - EmailSenderThread for sending rate-limited emails
log_poller - LogPollingThread for watching student and faculty logs for events
event_parser - LogEventParserThread for creating event handlers from log events
test_thread_manager - TestThreadManagerThread for running tests on submissions

"""


import sys
from queue import Queue, Empty
from signal import signal, SIGINT, SIGTERM

from gkeepserver.server_configuration import config, ServerConfigurationError
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.local_log_file_functions import (byte_count_function,
                                                  read_bytes_function)
from gkeepserver.event_handlers.handler_registry import event_handlers_by_type
from gkeepserver.local_log_file_functions import log_append_function
from gkeepcore.system_logger import system_logger as logger
from gkeepcore.log_event_parser import LogEventParserThread
from gkeepserver.test_thread_manager import test_thread_manager
from gkeepcore.log_polling import log_poller
from gkeepserver.check_system import check_system, CheckSystemError


# switched to True by the signal handler on SIGINT or SIGTERM
shutdown_flag = False


def signal_handler(signum, frame):
    """
    Handle SIGINT and SIGTERM signals.

    The main loop keeps looping while shutdown_flag is False. This will switch
    it to True so the server shuts down.

    :param signum: unused
    :param frame: unused
    """

    global shutdown_flag
    shutdown_flag = True


def main():
    """
    Entry point of the gkeepd process.

    gkeepd takes no arguments.

    """

    # setup signal handling
    global shutdown_flag
    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)

    # do not run if there are errors in the configuration file
    try:
        config.parse()
    except ServerConfigurationError as e:
        sys.exit(e)

    # initialize and start system logger
    logger.initialize(config.log_file_path, log_append_function,
                      log_level=config.log_level)
    logger.start()

    logger.log_info('--- Starting gkeepd ---')

    # check for fatal errors in the system state, and correct correctable
    # issues including new faculty members
    try:
        check_system()
    except CheckSystemError as e:
        logger.log_error(e)
        logger.log_info('Shutting down')
        logger.shutdown()
        sys.exit(1)

    # queues for thread communication
    new_log_line_queue = Queue()
    event_handler_queue = Queue()

    # the event parser creates event handlers for the main loop to call upon
    event_parser = LogEventParserThread(new_log_line_queue,
                                        event_handler_queue,
                                        event_handlers_by_type, logger)

    # the log poller detects new events and passes them to the event parser
    log_poller.initialize(new_log_line_queue, byte_count_function,
                          read_bytes_function,
                          config.log_snapshot_file_path, logger)

    # start the rest of the threads
    email_sender.start()
    test_thread_manager.start()
    event_parser.start()
    log_poller.start()

    logger.log_info('Server is running')

    # main loop
    while not shutdown_flag:
        try:
            # do not fully block since we need to check shutdown_flag
            # regularly
            handler = event_handler_queue.get(block=True, timeout=0.1)

            logger.log_debug('New task: ' + str(handler))

            # all of the main thread's actions are carried out by handlers
            handler.handle()

        # get() raises Empty after blocking for timeout seconds
        except Empty:
            pass

    print('Shutting down. Waiting for threads to finish ... ', end='')
    # flush so it prints immediately despite no newline
    sys.stdout.flush()

    logger.log_info('Shutting down threads')

    # shut down the pipeline in this order so that no new log events are lost
    log_poller.shutdown()
    event_parser.shutdown()
    test_thread_manager.shutdown()
    email_sender.shutdown()

    logger.log_info('Shutting down gkeepd')

    logger.shutdown()

    print('done')


if __name__ == '__main__':
    main()
