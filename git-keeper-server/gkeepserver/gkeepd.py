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
import argparse
from time import sleep

import fcntl
import sys
from queue import Queue
from signal import signal, SIGINT, SIGTERM

from gkeepcore.version import __version__ as core_version
from gkeepserver.check_config import check_config
from gkeepserver.check_system import check_system
from gkeepserver.database import db
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.event_handler_assigner import EventHandlerAssignerThread
from gkeepserver.event_handler_thread import EventHandlerThread
from gkeepserver.event_handlers.handler_registry import event_handlers_by_type
from gkeepserver.gkeepd_logger import gkeepd_logger as logger
from gkeepserver.info_update_thread import info_updater
from gkeepserver.local_log_file_reader import LocalLogFileReader
from gkeepserver.log_polling import log_poller
from gkeepserver.server_configuration import config, ServerConfigurationError
from gkeepserver.submission_test_thread import SubmissionTestThread
from gkeepserver.version import __version__ as server_version

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


def verify_core_version_match():
    """
    Exits with a non-zero exit code if the gkeepserver version does not match
    the gkeepcore version.
    """

    if server_version != core_version:
        error = 'git-keeper-server and git-keeper-core versions must match.\n'
        error += 'server version: {}\n'.format(server_version)
        error += 'core version: {}'.format(core_version)
        sys.exit(error)


def main():
    """
    Entry point of the gkeepd process.

    If gkeepd is run with the --version or -v flags, it will print the current
    version and exit.
    """

    verify_core_version_match()

    description = ('gkeepd, the git-keeper server, version {}'
                   .format(server_version))
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-v', '--version', action='store_true',
                        help='Print gkeepd version')
    parser.add_argument('-c', '--check', action='store_true',
                        help='Validate config and send test email to admins')

    args = parser.parse_args()

    if args.version:
        print('gkeepd version {}'.format(server_version))
        sys.exit(0)

    if args.check:
        try:
            check_config()
            sys.exit(0)
        except Exception as e:
            print(e)
            sys.exit(1)

    # setup signal handling
    global shutdown_flag
    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)

    # do not run if there are errors in the configuration file
    try:
        config.parse()
    except ServerConfigurationError as e:
        error = 'Configuration error:\n{}: {}'.format(config.config_path, e)
        sys.exit(error)

    # prevent multiple instances
    try:
        fp = open(config.lock_file_path, 'w')
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        error_message = ('Could not lock {}, gkeepd may already be running'
                         .format(config.lock_file_path))
        sys.exit(error_message)

    # initialize and start system logger
    logger.initialize(config.log_file_path, log_level=config.log_level)
    logger.start()

    logger.log_info('--- Starting gkeepd version {}---'.format(server_version))

    db.connect(config.db_path)

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
    info_updater.start()

    for faculty in db.get_all_faculty():
        info_updater.enqueue_full_scan(faculty.username)

    # queues for thread communication
    new_log_event_queue = Queue()
    event_handler_queue = Queue()

    # the handler assigner creates event handlers for the event handler thread
    # to call upon
    handler_assigner = EventHandlerAssignerThread(new_log_event_queue,
                                                  event_handler_queue,
                                                  event_handlers_by_type,
                                                  logger)

    # the event handler thread handles events created by the assigner
    event_handler_thread = EventHandlerThread(event_handler_queue, logger)

    # the log poller detects new events and passes them to the handler assigner
    log_poller.initialize(new_log_event_queue, LocalLogFileReader, logger)

    # start the rest of the threads
    email_sender.start()

    submission_test_threads = []
    for count in range(config.test_thread_count):
        # thread is automatically started by the constructor
        submission_test_threads.append(SubmissionTestThread())

    event_handler_thread.start()
    handler_assigner.start()
    log_poller.start()

    logger.log_info('Server is running')

    # spin until shutdown
    while not shutdown_flag:
        sleep(0.1)

    print('Shutting down. Waiting for threads to finish ... ', end='')
    # flush so it prints immediately despite no newline
    sys.stdout.flush()

    logger.log_info('Shutting down threads')

    # shut down the pipeline in this order so that no new log events are lost
    log_poller.shutdown()
    handler_assigner.shutdown()
    event_handler_thread.shutdown()

    for thread in submission_test_threads:
        thread.shutdown()

    info_updater.shutdown()

    email_sender.shutdown()

    logger.log_info('Shutting down gkeepd')

    logger.shutdown()

    print('done')


if __name__ == '__main__':
    main()
