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
from queue import Queue

from gkeepserver.server_configuration import config, ServerConfigurationError
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.local_log_file_functions import (byte_count_function,
                                                  read_bytes_function)
from gkeepserver.event_handlers.handler_registry import event_handlers_by_type
from gkeepcore.system_logger import LogLevel
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepcore.log_event_parser import LogEventParserThread
from gkeepcore.log_polling import LogPollingThread


LOG_LEVEL = LogLevel.DEBUG


def main():
    """
    Entry point of the gkeepd process.

    gkeepd takes no arguments.

    """

    # do not run if there are errors in the configuration file
    try:
        config.parse()
    except ServerConfigurationError as e:
        sys.exit(e)

    gkeepd_logger.initialize(config.log_file_path, log_level=LOG_LEVEL)

    gkeepd_logger.log_info('Starting gkeepd')

    # queues for thread communication
    new_log_line_queue = Queue()
    event_handler_queue = Queue()

    event_parser = LogEventParserThread(new_log_line_queue,
                                        event_handler_queue,
                                        event_handlers_by_type, gkeepd_logger)

    poller = LogPollingThread(new_log_line_queue, byte_count_function,
                              read_bytes_function,
                              config.log_snapshot_file_path, gkeepd_logger)

    # start all threads
    email_sender.start()
    event_parser.start()
    poller.start()

    gkeepd_logger.log_info('Threads have been initialized')

    gkeepd_logger.log_info('Server is running')

    try:
        while True:
            handler = event_handler_queue.get()
            gkeepd_logger.log_debug('New task: ' + str(handler))
            handler.handle()
    except KeyboardInterrupt:
        pass

    print('Shutting down. Waiting for threads to finish ... ', end='')
    sys.stdout.flush()

    gkeepd_logger.log_info('Shutting down threads')

    poller.shutdown()
    event_parser.shutdown()
    email_sender.shutdown()

    poller.join()
    event_parser.join()
    email_sender.join()

    print('done')

    gkeepd_logger.log_info('Shutting down gkeepd')


if __name__ == '__main__':
    main()
