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

import pyinotify
import queue


class PushEventHandler(pyinotify.ProcessEvent):
    def __init__(self, update_flag_queue):
        assert(isinstance(update_flag_queue, queue.Queue))
        pyinotify.ProcessEvent.__init__(self)
        self.updated_repo_queue = update_flag_queue

    def process_IN_ATTRIB(self, event):
        self.updated_repo_queue.put(event.pathname)


class PushMonitor:
    def __init__(self, update_flag_queue):
        self.wm = pyinotify.WatchManager()
        self.mask = pyinotify.IN_ATTRIB

        self.notifier =\
            pyinotify.ThreadedNotifier(self.wm,
                                       PushEventHandler(update_flag_queue))
        self.notifier.start()

    def add_file(self, filename):
        self.wm.add_watch(filename, self.mask, rec=True)

    def __del__(self):
        self.notifier.stop()


class AssignmentEventHandler(pyinotify.ProcessEvent):
    def __init__(self, assignment_file_queue):
        assert(isinstance(assignment_file_queue, queue.Queue))
        pyinotify.ProcessEvent.__init__(self)
        self.assignment_file_queue = assignment_file_queue

    def process_IN_CREATE(self, event):
        self.assignment_file_queue.put(event.pathname)


class AssignmentMonitor:
    def __init__(self, assignment_file_queue):
        self.wm = pyinotify.WatchManager()
        self.mask = pyinotify.IN_CREATE

        self.notifier =\
            pyinotify.ThreadedNotifier(self.wm,
                                       AssignmentEventHandler(assignment_file_queue))
        self.notifier.start()

    def add_file(self, filename):
        self.wm.add_watch(filename, self.mask, rec=True)

    def __del__(self):
        self.notifier.stop()
