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

from threading import Thread
from queue import Queue, Empty
from time import time, sleep

from gkeepcore.log_file import LogFileReader, LogFileException


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
        self._log_byte_counts = {}

    def _start_watching_log_file(self, log_file: LogFileReader):
        # Start watching the file at file_path. Do not call directly, pass
        # file paths in through the queue

        try:
            byte_count = log_file.get_byte_count()
            self._log_byte_counts[log_file] = byte_count
        except LogFileException:
            # FIXME - log this
            pass

    def _stop_watching_log_file(self, log_file: LogFileReader):
        # Simply remove the file from the dictionary
        del self._log_byte_counts[log_file]

    def _get_new_lines(self, log_file: LogFileReader) -> list:
        # Get the new lines from the log file since the last poll.
        #
        # :param log_file: LogFileReader object
        # :return: a list of strings, one per line

        lines = []

        try:
            current_byte_count = log_file.get_byte_count()
            old_byte_count = self._log_byte_counts[log_file]

            # if the file shrunk, something went wrong
            if current_byte_count < old_byte_count:
                # FIXME - log this
                self._stop_watching_log_file(log_file)
            elif current_byte_count > old_byte_count:
                # get any new data past the old byte count
                new_data = log_file.get_data(old_byte_count)

                self._log_byte_counts[log_file] = current_byte_count

                # strip the data since split does not remove the trailing
                # newline
                lines = new_data.strip().split('\n')
        except LogFileException as e:
            # FIXME - log this
            print(e)
            self._stop_watching_log_file(log_file)
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
        log_files = list(self._log_byte_counts.keys())

        # for each file that we're watching, add any new lines to the queue
        for log_file in log_files:
            for line in self._get_new_lines(log_file):
                self._new_log_line_queue.put((log_file.get_file_path(),
                                              line))

        # consume all new log files until the queue is empty
        try:
            while True:
                new_log_file = self._add_log_queue.get(block=False)
                if isinstance(new_log_file, LogFileReader):
                    self._start_watching_log_file(new_log_file)
                else:
                    # FIXME - log this
                    pass

        except Empty:
            pass

        # each file should be polled on average once per polling_interval
        next_poll_time = self._last_poll_time + self._polling_interval
        sleep_time = next_poll_time - time()

        if sleep_time > 0:
            sleep(sleep_time)
