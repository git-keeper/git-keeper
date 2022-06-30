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
Provides a class and a global access point for a log polling object.

The module stores a LogPollingThread instance in the module-level variable
named log_poller. Call initialize() on this object as early as possible to set
it up, and then call start() to start the thread.

Files to be watched can be added to the polling object. New events from the
log are passed on to a parser and then an appropriate handler.

It is possible to add files to be watched before calling initialize(), but no
actions can be taken until the thread is initialized and started.

The sizes of the log files are stored in the database after every log
modification. This allows the poller to start where it left off if the process
is restarted.

Example usage::

    from gkeepcore.log_polling import log_poller
    # import whatever byte_count_function and read_bytes_function you need

    def main():
        # set up other stuff

        log_poller.initialize(new_log_event_queue, byte_count_function,
                              read_bytes_function, gkeepd_logger)

        log_poller.start()

        log_poller.watch_log_file('/path/to/log')

        while keep_going:
            log_file_path, log_event = new_log_event_queue.get()
            # do something with the event

        log_poller.shutdown()

"""

import os
from queue import Queue, Empty
from threading import Thread
from time import time, sleep

from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.log_file import LogFileReader, LogFileException
from gkeepcore.system_commands import file_is_readable
from gkeepserver.database import db
from gkeepserver.gkeepd_logger import GkeepdLoggerThread


class LogPollingThreadError(GkeepException):
    """Raised if there is an error polling log files."""
    pass


class LogPollingThread(Thread):
    """
    Watches log files for modifications.

    New events from log files are put in a queue to be processed by another
    thread.

    See the module-level documentation for usage.

    """
    def __init__(self):
        """
        Constructor.

        Create the _add_log_queue so that files to be watched can be added
        before the thread is started. Initialize all other attributes to None.

        Poller will be fully set up and ready to start after initialize() is
        called.

        """

        Thread.__init__(self)

        # initialize this so we can add files to watch before the thread starts
        self._add_log_queue = Queue()

        self._new_log_event_queue = None
        self._reader_class = None
        self._polling_interval = None
        self._last_poll_time = None
        self._logger = None
        self._log_file_readers = None
        self._shutdown_flag = None

    def initialize(self, new_log_event_queue: Queue, reader_class,
                   logger: GkeepdLoggerThread, polling_interval=0.5):
        """
        Initialize the attributes.

        :param new_log_event_queue: the poller places (file_path, event) pairs
         into this queue
        :param reader_class: LogFileReader class to use for creating readers
        :param logger: the system logger, used to log runtime information
        :param polling_interval: number of seconds between polling files

        """

        self._new_log_event_queue = new_log_event_queue

        self._reader_class = reader_class

        self._polling_interval = polling_interval
        self._last_poll_time = 0

        self._logger = logger

        # maps log file paths to log readers
        self._log_file_readers = {}

        self._load_paths_from_db()

        self._shutdown_flag = False

    def watch_log_file(self, file_path: str):
        """
        Add a log file to be watched.

        This method can be called from any other thread.

        :param file_path: path to the log file

        """

        if not file_is_readable(file_path):
            error = '{} is not a readable file'.format(file_path)
            raise GkeepException(error)

        self._add_log_queue.put(file_path)

    def shutdown(self):
        """
        Shut down the poller.

        The run loop will not shut down until the current polling cycle
        is complete.

        This method will block until the thread dies.

        """

        self._shutdown_flag = True
        self.join()

    def run(self):
        # Poll until _shutdown_flag is True.
        #
        # This should not be called directly, the thread should be started by
        # calling start()

        while not self._shutdown_flag:
            try:
                self._poll()
            except Exception as e:
                self._logger.log_error('Error polling logs: {0}'
                                       .format(e))

    def _load_paths_from_db(self):
        for log_file_path, byte_count in db.get_byte_counts():
            self._logger.log_debug('Watching {} from byte {}'
                                   .format(log_file_path, byte_count))
            self._create_and_add_reader(log_file_path,
                                        seek_position=byte_count)

    def _write_byte_counts_to_db(self):
        # Writes all of the current file byte counts to the database.
        # Called after updates.

        byte_counts_by_file_path = {}

        for file_path, reader in self._log_file_readers.items():
            byte_counts_by_file_path[file_path] = reader.get_seek_position()

        try:
            db.update_byte_counts(byte_counts_by_file_path)
        except GkeepException as e:
            raise LogPollingThreadError('Error updating byte counts: {}'
                                        .format(e))

    def _write_byte_count_to_db(self, file_path):
        # Writes a single file's byte count to the database.

        update = {
            file_path: self._log_file_readers[file_path].get_seek_position()
        }

        db.update_byte_counts(update)

    def _start_watching_log_file(self, file_path: str):
        # Start watching the file at file_path. This should only be called
        # internally. Other threads should call watch_log_file()

        try:
            self._create_and_add_reader(file_path)
            self._write_byte_count_to_db(file_path)
        except GkeepException as e:
            self._logger.log_warning(str(e))

    def _create_and_add_reader(self, file_path: str, seek_position=None):
        # Create a LogFileReader object for reading new data from the file
        # and add it to the dictionary of readers.

        # bail if the log does not exist
        if not os.path.isfile(file_path):
            warning = ('{0} does not exist and will not be watched'
                       .format(file_path))
            self._logger.log_warning(warning)
            return

        # bail if already watching file
        if file_path in self._log_file_readers:
            info = ('Already watching {}'.format(file_path))
            self._logger.log_info(info)
            return

        reader = self._reader_class(file_path, seek_position=seek_position)
        self._log_file_readers[file_path] = reader

    def _stop_watching_log_file(self, log_file: LogFileReader):
        # Simply remove the file reader from the dictionary

        file_path = log_file.get_file_path()

        del self._log_file_readers[file_path]
        self._write_byte_count_to_db(file_path)

    def _poll(self):
        # Poll once for changes in files, and check the queue for new files
        # to watch.

        self._last_poll_time = time()

        readers = list(self._log_file_readers.values())

        # for each file reader, add any new events to the queue
        for reader in readers:
            try:
                for event in reader.get_new_events():
                    file_path = reader.get_file_path()
                    self._new_log_event_queue.put((file_path, event))
                    self._write_byte_count_to_db(file_path)

            except LogFileException as e:
                self._logger.log_warning(str(e))
                # if something goes wrong we should not keep watching this file
                self._stop_watching_log_file(reader)

        # consume all new log files until the queue is empty
        empty = False
        while not empty:
            try:
                new_file_path = self._add_log_queue.get(block=False)
                if not isinstance(new_file_path, str):
                    self._logger.log_warning('Log poller: {0} is not a string'
                                             .format(new_file_path))
                else:
                    self._start_watching_log_file(new_file_path)
            except Empty:
                empty = True

        # each file should be polled on average once per polling_interval
        next_poll_time = self._last_poll_time + self._polling_interval
        sleep_time = next_poll_time - time()

        if sleep_time > 0 and not self._shutdown_flag:
            sleep(sleep_time)


# module-level instance for global access
log_poller = LogPollingThread()
