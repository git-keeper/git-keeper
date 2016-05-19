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
from threading import Thread
from queue import Queue, Empty
from time import time, sleep


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

        self._polling_interval = polling_interval
        self._last_poll_time = 0

        # Dictionaries indexed by file paths

        # Previous most recent byte count, used to detect changes and to know
        # where to seek to for the next read
        self._file_byte_counts = {}

    def _start_watching_log_file(self, file_path):
        # Start watching the file at file_path. Do not call directly, pass
        # file paths in through the queue

        try:
            byte_count = os.path.getsize(file_path)
            self._file_byte_counts[file_path] = byte_count
        except OSError:
            # FIXME - log this
            pass

    def _stop_watching_log_file(self, file_path):
        # Simply remove the file from the dictionary
        del self._file_byte_counts

    def _get_new_log_data(self, file_path, seek_position):
        # Return any data that was added to the log since the last poll

        # FIXME - log failures
        with open(file_path) as f:
            f.seek(seek_position)
            return f.read()

    def _get_new_lines(self, file_path) -> list:
        # Get the new lines from the log file since the last poll.
        #
        # :param file_path: path to the log file
        # :return: a list of strings, one per line

        lines = []

        try:
            current_byte_count = os.path.getsize(file_path)
            old_byte_count = self._file_byte_counts[file_path]

            # if the file shrunk, something went wrong
            if current_byte_count < old_byte_count:
                # FIXME - log this
                self._stop_watching_log_file(file_path)
            elif current_byte_count > old_byte_count:
                # get any new data past the old byte count
                new_data = self._get_new_log_data(file_path, old_byte_count)

                self._file_byte_counts[file_path] = current_byte_count

                # strip the data since split does not remove the trailing
                # newline
                lines = new_data.strip().split('\n')
        except OSError:
            # FIXME - log this
            self._stop_watching_log_file(file_path)
        finally:
            # we always need to return a list
            return lines

    def run(self):
        """Poll forever.

         This should not be called directly, the thread should be started by
         calling start()
         """

        while True:
            self._poll()

    def _poll(self):
        # Poll once for changes in files, and check the queue for new files
        # to watch.

        self._last_poll_time = time()

        # get keys as a list to avoid an iteration error if we remove a file
        file_paths = list(self._file_byte_counts.keys())

        # for each file that we're watching, add any new lines to the queue
        for file_path in file_paths:
            for line in self._get_new_lines(file_path):
                self._new_log_line_queue.put((file_path, line))

        # consume all new log files until the queue is empty
        try:
            while True:
                new_file_path = self._add_log_queue.get(block=False)
                self._start_watching_log_file(new_file_path)
        except Empty:
            pass

        # each file should be polled on average once per polling_interval
        next_poll_time = self._last_poll_time + self._polling_interval
        sleep_time = next_poll_time - time()

        if sleep_time > 0:
            sleep(sleep_time)
