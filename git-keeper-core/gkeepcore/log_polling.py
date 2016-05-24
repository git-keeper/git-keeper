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
import json
from threading import Thread
from queue import Queue, Empty
from time import time, sleep

from gkeepcore.log_file import LogFileReader, LogFileException
from gkeepcore.system_logger import SystemLogger


class LogPollingThreadError(Exception):
    pass


class LogPollingThread(Thread):
    """Watches log files for modifications.

    Stores 3 queues:

        add_log_queue - used to pass in new log files for the poller to watch
        new_log_line_queue - the poller places (file_path, line) pairs into
         this queue

    Extends Thread, so you need to call start() to start the poller in a new
    thread.

    Example usage:

    ```
    poller = LogPollingThread(add_log_queue, new_log_line_queue)
    poller.start()

    add_log_queue.put('/path/to/log/file')

    while True:
        log_file_path, log_line = new_log_line_queue.get()
        # do something with the line
    ```
    """

    def __init__(self, add_log_queue: Queue, new_log_line_queue: Queue,
                 reader_class, snapshot_file_path, logger: SystemLogger,
                 polling_interval=1):
        """Constructor

        :param add_log_queue: used to pass new log files to watch to the poller
        :param new_log_line_queue: the poller places (file_path, line) pairs
         into this queue
        :param polling_interval: amount of time between polling files
        """
        Thread.__init__(self)

        self._add_log_queue = add_log_queue
        self._new_log_line_queue = new_log_line_queue

        self._reader_class = reader_class

        self._snapshot_file_path = snapshot_file_path

        self._polling_interval = polling_interval
        self._last_poll_time = 0

        self._logger = logger

        # maps log file paths to log readers
        self._log_file_readers = {}

        self._load_snapshot()

        self._shutdown_flag = False

    def _load_snapshot(self):
        if not os.path.isfile(self._snapshot_file_path or ''):
            return

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

        for log_file_path, byte_count in log_byte_counts.items():
            reader = self._reader_class(log_file_path, byte_count)
            self._log_file_readers[log_file_path] = reader

    def _write_snapshot(self):
        if self._snapshot_file_path is None:
            return

        byte_counts_by_file_path = {}

        for file_path, reader in self._log_file_readers.items():
            byte_counts_by_file_path[file_path] = reader.get_seek_position()

        try:
            with open(self._snapshot_file_path, 'w') as f:
                json_data = json.dumps(byte_counts_by_file_path)
                f.write(json_data)
        except OSError as e:
            raise LogPollingThreadError('Error writing to {0}: {1}'
                                        .format(self._snapshot_file_path, e))

    def _start_watching_log_file(self, file_path: str):
        # Start watching the file at file_path. Do not call directly, pass
        # file paths in through the queue

        try:
            reader = self._reader_class(file_path)
            self._log_file_readers[file_path] = reader
            self._write_snapshot()
        except LogFileException as e:
            self._logger.log_warning(str(e))
            pass

    def _stop_watching_log_file(self, log_file: LogFileReader):
        # Simply remove the file from the dictionary
        del self._log_file_readers[log_file.get_file_path()]
        self._write_snapshot()

    def _get_new_lines(self, log_file: LogFileReader) -> list:
        # Get the new lines from the log file since the last poll.
        #
        # :param log_file: LogFileReader object
        # :return: a list of strings, one per line

        lines = []

        try:
            if log_file.has_new_text():
                new_text = log_file.get_new_text()
                self._write_snapshot()

                # split the new text into lines. strip the text because split
                # will not remove the trailing newline
                lines = new_text.strip().split('\n')
        except LogFileException as e:
            self._logger.log_warning(str(e))
            self._stop_watching_log_file(log_file)
        finally:
            # we always need to return a list
            return lines

    def shutdown(self):
        self._shutdown_flag = True

    def run(self):
        """Poll forever.

         This should not be called directly, the thread should be started by
         calling start()
         """

        while not self._shutdown_flag:
            self._poll()

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
