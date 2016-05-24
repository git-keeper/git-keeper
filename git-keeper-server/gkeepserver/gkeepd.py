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

import os
import sys
from queue import Queue

from gkeepserver.server_configuration import config, ServerConfigurationError
from gkeepserver.email_sender_thread import email_sender
from gkeepcore.log_event_parser import LogEventParserThread
from gkeepcore.log_polling import LogPollingThread
from gkeepserver.local_log_file import LocalLogFileReader
from gkeepserver.event_handlers.handler_registry import event_handlers_by_type
from gkeepserver.gkeepd_logger import gkeepd_logger


def main():
    try:
        config.parse()
    except ServerConfigurationError as e:
        sys.exit(e)

    gkeepd_logger.initialize(config.log_file_path)

    gkeepd_logger.log_info('logger intialized')

    add_log_queue = Queue()
    new_log_line_queue = Queue()
    event_handler_queue = Queue()

    event_parser = LogEventParserThread(new_log_line_queue,
                                        event_handler_queue,
                                        event_handlers_by_type)

    poller = LogPollingThread(add_log_queue, new_log_line_queue,
                              LocalLogFileReader, config.log_snapshot_file_path)

    email_sender.start()
    event_parser.start()
    poller.start()

    try:
        while True:
            handler = event_handler_queue.get()
            handler.handle()
    except KeyboardInterrupt:
        pass

    poller.shutdown()
    poller.join()

    event_parser.shutdown()
    event_parser.join()

    email_sender.shutdown()
    email_sender.join()


if __name__ == '__main__':
    main()
