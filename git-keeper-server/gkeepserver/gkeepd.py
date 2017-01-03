# Copyright 2016, 2017 Nathan Sommer and Ben Coleman
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

logger - GkeepdLoggerThread for logging runtime information
email_sender - EmailSenderThread for sending rate-limited emails
log_poller - LogPollingThread for watching student and faculty logs for events
handler_assigner - EventHandlerAssignerThread for creating event handlers from
                   log events
submission_test_threads - list of SubmissionTestThread objects which run tests

"""

import sys
from queue import Queue, Empty
from signal import signal, SIGINT, SIGTERM
from traceback import extract_tb

from gkeepcore.faculty import faculty_from_csv_file
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.local_csv_files import LocalCSVReader
from gkeepserver.check_system import check_system, CheckSystemError
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.event_handlers.handler_registry import event_handlers_by_type
from gkeepserver.gkeepd_logger import gkeepd_logger as logger
from gkeepserver.info_refresh_thread import info_refresher
from gkeepserver.local_log_file_reader import LocalLogFileReader
from gkeepserver.event_handler_assigner import EventHandlerAssignerThread
from gkeepserver.log_polling import log_poller
from gkeepserver.server_configuration import config, ServerConfigurationError
from gkeepserver.submission_test_thread import SubmissionTestThread

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
    logger.initialize(config.log_file_path, log_level=config.log_level)
    logger.start()

    logger.log_info('--- Starting gkeepd ---')

    # check for fatal errors in the system state, and correct correctable
    # issues including new faculty members
    try:
        check_system()
    except Exception as e:
        logger.log_error(str(e))
        logger.log_info('Shutting down')
        logger.shutdown()
        sys.exit(1)

    # start the info refresher thread and refresh the info for each faculty
    info_refresher.start()

    reader = LocalCSVReader(config.faculty_csv_path)
    faculty_list = faculty_from_csv_file(reader)

    for faculty in faculty_list:
        info_refresher.enqueue(faculty.username)

    # queues for thread communication
    new_log_event_queue = Queue()
    event_handler_queue = Queue()

    # the handler assigner creates event handlers for the main loop to call
    # upon
    handler_assigner = EventHandlerAssignerThread(new_log_event_queue,
                                                  event_handler_queue,
                                                  event_handlers_by_type,
                                                  logger)

    # the log poller detects new events and passes them to the handler assigner
    log_poller.initialize(new_log_event_queue, LocalLogFileReader,
                          config.log_snapshot_file_path, logger)

    # start the rest of the threads
    email_sender.start()

    submission_test_threads = []
    for count in range(config.test_thread_count):
        # thread is automatically started by the constructor
        submission_test_threads.append(SubmissionTestThread())

    handler_assigner.start()
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
        except (GkeepException, Exception) as e:
            # A handler's handle() method should catch all exceptions. If we
            # get here there is likely an issue with the handler.
            error = ('An exception was caught that should have been caught\n'
                     'earlier. This is likely due to a bug in the code.\n'
                     'Please report this to the git-keeper developers along\n'
                     'with the following stack trace:\n{0}'
                     .format(extract_tb(e)))
            print(error, file=sys.stderr)
            logger.log_error('Unexpected exception. Please report this bug. '
                             '{0}: {1}'.format(type(e), e))

    print('Shutting down. Waiting for threads to finish ... ', end='')
    # flush so it prints immediately despite no newline
    sys.stdout.flush()

    logger.log_info('Shutting down threads')

    # shut down the pipeline in this order so that no new log events are lost
    log_poller.shutdown()
    handler_assigner.shutdown()

    for thread in submission_test_threads:
        thread.shutdown()

    info_refresher.shutdown()

    email_sender.shutdown()

    logger.log_info('Shutting down gkeepd')

    logger.shutdown()

    print('done')


if __name__ == '__main__':
    main()
