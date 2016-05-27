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

A snapshot of the sizes of the log files is stored after every log
modification. This allows the poller to start where it left off if the process
is restarted.

Example usage::

    from gkeepcore.log_polling import log_poller
    # import whatever byte_count_function and read_bytes_function you need

    def main():
        # set up other stuff

        log_poller.initialize(new_log_line_queue, byte_count_function,
                              read_bytes_function,
                              config.log_snapshot_file_path, system_logger)

        log_poller.start()

        log_poller.watch_log_file('/path/to/log')

        while keep_going:
            log_file_path, log_line = new_log_line_queue.get()
            # do something with the line

        log_poller.shutdown()

"""

import os
import json
from threading import Thread
from queue import Queue, Empty
from time import time, sleep

from gkeepcore.log_file import LogFileReader, LogFileException
from gkeepcore.system_logger import SystemLoggerThread


class LogPollingThreadError(Exception):
    pass


class LogPollingThread(Thread):
    """
    Watches log files for modifications.

    New lines from log files are put in a queue to be processed by another
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

        self._new_log_line_queue = None
        self._byte_count_function = None
        self._read_bytes_function = None
        self._snapshot_file_path = None
        self._polling_interval = None
        self._last_poll_time = None
        self._logger = None
        self._log_file_readers = None
        self._shutdown_flag = None

    def initialize(self, new_log_line_queue: Queue, byte_count_function,
                   read_bytes_function, snapshot_file_path: str,
                   logger: SystemLoggerThread, polling_interval=1):
        """
        Initialize the attributes.

        byte_count_function must have the following signature:
            byte_count_function(file_path: str) -> int

        read_bytes_function must have the following signature:
            read_bytes_function(file_path: str, seek_position: int) -> bytes

        These functions are used to create LogFileReader objects. This allows
        reading from local or remote files, depending on what functions are
        passed in.

        :param new_log_line_queue: the poller places (file_path, line) pairs
         into this queue
        :param byte_count_function: function which gets the number of bytes in
         a file
        :param read_bytes_function: function which gets the data from a file
         from a seek position to the end
        :param snapshot_file_path: path to the snapshot file
        :param logger: the system logger, used to log runtime information
        :param polling_interval: number of seconds between polling files

        """

        self._new_log_line_queue = new_log_line_queue

        self._byte_count_function = byte_count_function
        self._read_bytes_function = read_bytes_function

        self._snapshot_file_path = snapshot_file_path

        self._polling_interval = polling_interval
        self._last_poll_time = 0

        self._logger = logger

        # maps log file paths to log readers
        self._log_file_readers = {}

        self._load_snapshot()

        self._shutdown_flag = False

    def watch_log_file(self, file_path: str):
        """
        Add a log file to be watched.

        This method can be called from any other thread.

        :param file_path: path to the log file

        """

        self._add_log_queue.put(file_path)

    def shutdown(self):
        """
        Shut down the poller.

        This method is thread safe.

        The poller thread will not shut down until the current polling cycle
        is complete.

        """

        self._shutdown_flag = True

    def run(self):
        # Poll until _shutdown_flag is True.
        #
        # This should not be called directly, the thread should be started by
        # calling start()

        while not self._shutdown_flag:
            self._poll()

    def _load_snapshot(self):
        # Called from initialize() and should not be called again.
        # Loads byte counts from the snapshot file.

        if not os.path.isfile(self._snapshot_file_path or ''):
            self._logger.log_debug('Snapshot file does not exist')
            return
        elif self._byte_count_function(self._snapshot_file_path) == 0:
            self._logger.log_debug('Snapshot file is empty')
            return

        self._logger.log_debug('Loading snapshot')

        # snapshots are stored as JSON, and can be directly loaded into a
        # dictionary
        try:
            with open(self._snapshot_file_path, 'r') as f:
                json_data = f.read()
                log_byte_counts = json.loads(json_data)
        except OSError as e:
            raise LogPollingThreadError('Error reading {0}: {1}'
                                        .format(self._snapshot_file_path, e))

        if not isinstance(log_byte_counts, dict):
            error = ('{0} is not a valid snapshot file'
                     .format(self._snapshot_file_path))
            raise LogPollingThreadError(error)

        self._logger.log_debug('Loaded ' + self._snapshot_file_path)

        # start watching all the files from the snapshot file
        for log_file_path, byte_count in log_byte_counts.items():
            self._logger.log_debug('Watching ' + log_file_path)
            self._create_and_add_reader(log_file_path)

    def _write_snapshot(self):
        # Writes the current file byte counts to the snapshot file.
        # Called after updates.

        if self._snapshot_file_path is None:
            return

        byte_counts_by_file_path = {}

        for file_path, reader in self._log_file_readers.items():
            byte_counts_by_file_path[file_path] = reader.get_seek_position()

        try:
            with open(self._snapshot_file_path, 'w') as f:
                json_data = json.dumps(byte_counts_by_file_path)
                f.write(json_data)
                self._logger.log_debug('Wrote ' + self._snapshot_file_path)
        except OSError as e:
            raise LogPollingThreadError('Error writing to {0}: {1}'
                                        .format(self._snapshot_file_path, e))

    def _start_watching_log_file(self, file_path: str):
        # Start watching the file at file_path. This should only be called
        # internally. Other threads should call watch_log_file()

        try:
            self._create_and_add_reader(file_path)
            self._write_snapshot()
        except LogFileException as e:
            self._logger.log_warning(str(e))

    def _create_and_add_reader(self, file_path: str, seek_position=None):
        # Create a LogFileReader object for reading new data from the file
        # and add it to the dictionary of readers.

        reader = LogFileReader(file_path, self._byte_count_function,
                               self._read_bytes_function,
                               seek_position=seek_position)
        self._log_file_readers[file_path] = reader

    def _stop_watching_log_file(self, log_file: LogFileReader):
        # Simply remove the file reader from the dictionary

        del self._log_file_readers[log_file.get_file_path()]
        self._write_snapshot()

    def _get_new_lines(self, log_file: LogFileReader) -> list:
        # Get the new lines from a single log file since the last poll.
        #
        # :param log_file: LogFileReader object
        # :return: a list of strings, one per line, in chronological order

        lines = []

        try:
            if log_file.has_new_text():
                self._logger.log_debug('New text in ' +
                                       log_file.get_file_path())
                new_text = log_file.get_new_text()
                self._write_snapshot()

                # split the new text into lines. strip the text because split
                # will not remove the trailing newline
                lines = new_text.strip().split('\n')
        except LogFileException as e:
            self._logger.log_warning(str(e))
            # if something goes wrong we should not keep watching this file
            self._stop_watching_log_file(log_file)
        finally:
            # we always need to return a list
            return lines

    def _poll(self):
        # Poll once for changes in files, and check the queue for new files
        # to watch.

        self._last_poll_time = time()

        readers = list(self._log_file_readers.values())

        # for each file reader, add any new lines to the queue
        for reader in readers:
            for line in self._get_new_lines(reader):
                self._new_log_line_queue.put((reader.get_file_path(), line))

        # consume all new log files until the queue is empty
        try:
            while True:
                new_file_path = self._add_log_queue.get(block=False)
                if isinstance(new_file_path, str):
                    self._start_watching_log_file(new_file_path)
                else:
                    self._logger.log_warning('Log poller: {0} is not a string'
                                             .format(new_file_path))
        except Empty:
            pass

        # each file should be polled on average once per polling_interval
        next_poll_time = self._last_poll_time + self._polling_interval
        sleep_time = next_poll_time - time()

        if sleep_time > 0:
            sleep(sleep_time)


# module-level instance for global access
log_poller = LogPollingThread()
