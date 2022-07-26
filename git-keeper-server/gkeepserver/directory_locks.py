# Copyright 2022 Nathan Sommer and Ben Coleman
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


from collections import defaultdict
from threading import RLock


class DirectoryLocks:
    """
    Implements a lock manager that maintains RLock objects associated with
    directory paths. get_lock() returns a lock for a given directory, and
    callers are responsible for actually acquiring and releasing the lock.
    """
    def __init__(self):
        self._locks = defaultdict(RLock)
        self._lock = RLock()

    def get_lock(self, path):
        """
        Get an RLock object for a directory.

        :param path: path to the directory for which to get the lock
        :return: an RLock object for the directory
        """
        with self._lock:
            lock = self._locks[path]
        return lock


# global instance shared by threads
directory_locks = DirectoryLocks()
