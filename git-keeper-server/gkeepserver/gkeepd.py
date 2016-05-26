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

"""


import sys
import csv
from queue import Queue, Empty
from signal import signal, SIGINT, SIGTERM

from gkeepserver.server_configuration import config, ServerConfigurationError
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.local_log_file_functions import (byte_count_function,
                                                  read_bytes_function)
from gkeepserver.event_handlers.handler_registry import event_handlers_by_type
from gkeepcore.system_logger import LogLevel
from gkeepserver.local_log_file_functions import log_append_function
from gkeepcore.system_logger import system_logger as gkeepd_logger
from gkeepcore.log_event_parser import LogEventParserThread
from gkeepcore.log_polling import log_poller
from gkeepcore.faculty import Faculty
from gkeepserver.check_system import check_system, CheckSystemError


shutdown_flag = False


def signal_handler(signum, frame):
    global shutdown_flag
    shutdown_flag = True


def main():
    """
    Entry point of the gkeepd process.

    gkeepd takes no arguments.

    """

    global shutdown_flag
    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)

    # do not run if there are errors in the configuration file
    try:
        config.parse()
    except ServerConfigurationError as e:
        sys.exit(e)

    gkeepd_logger.initialize(config.log_file_path, log_append_function,
                             log_level=config.log_level)
    gkeepd_logger.start()

    gkeepd_logger.log_info('--- Starting gkeepd ---')

    try:
        check_system()
    except CheckSystemError as e:
        gkeepd_logger.log_error(e)
        gkeepd_logger.log_info('Shutting down')
        gkeepd_logger.shutdown()
        gkeepd_logger.join()
        sys.exit(1)

    # queues for thread communication
    new_log_line_queue = Queue()
    event_handler_queue = Queue()

    event_parser = LogEventParserThread(new_log_line_queue,
                                        event_handler_queue,
                                        event_handlers_by_type, gkeepd_logger)

    log_poller.initialize(new_log_line_queue, byte_count_function,
                          read_bytes_function,
                          config.log_snapshot_file_path, gkeepd_logger)

    # start all threads
    email_sender.start()
    event_parser.start()
    log_poller.start()

    gkeepd_logger.log_info('Server is running')

    try:
        while not shutdown_flag:
            try:
                handler = event_handler_queue.get(block=True, timeout=0.1)
                gkeepd_logger.log_debug('New task: ' + str(handler))
                handler.handle()
            except Empty:
                pass
    except KeyboardInterrupt:
        pass

    print('Shutting down. Waiting for threads to finish ... ', end='')
    sys.stdout.flush()

    gkeepd_logger.log_info('Shutting down threads')

    # shut down the pipeline in this order so that no new log events are lost
    log_poller.shutdown()
    log_poller.join()

    event_parser.shutdown()
    event_parser.join()

    email_sender.shutdown()
    email_sender.join()

    gkeepd_logger.log_info('Shutting down gkeepd')

    gkeepd_logger.shutdown()
    gkeepd_logger.join()

    print('done')


if __name__ == '__main__':
    main()
