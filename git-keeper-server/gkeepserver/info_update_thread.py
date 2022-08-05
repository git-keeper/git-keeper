# Copyright 2017, 2018 Nathan Sommer and Ben Coleman
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
Provides a thread which updates the info for a faculty member's classes, and
a module-level object that acts as a global access point. Other threads request
an update by calling one of the various enqueue_*() functions of the global
info_updater instance of the InfoUpdateThread class.
"""

import json
import os
from collections import defaultdict
from enum import Enum
from queue import Queue, Empty
from tempfile import TemporaryDirectory
from threading import Thread
from time import time

from gkeepserver.directory_locks import directory_locks
from gkeepcore.git_commands import git_head_hash, git_hashes_and_times
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import user_home_dir, student_assignment_repo_path, \
    faculty_info_path, user_gitkeeper_path, faculty_assignment_dir_path
from gkeepcore.system_commands import sudo_chown, chmod, mv, mkdir, rm
from gkeepserver.assignments import AssignmentDirectory
from gkeepserver.database import db
from gkeepserver.gkeepd_logger import gkeepd_logger as logger
from gkeepserver.server_configuration import config


def nested_defaultdict():
    """
    Constructs a recursively nested defaultdict that works for arbitrarily
    deeply nested dictionaries.

    :return: an empty defaultdict
    """
    return defaultdict(nested_defaultdict)


class InfoInstruction(Enum):
    """An Enum for all of the different update requests."""
    FULL_SCAN = 0
    CLASS_SCAN = 1
    ASSIGNMENT_SCAN = 2
    DELETE_ASSIGNMENT = 3
    DISABLE_ASSIGNMENT = 4
    SUBMISSION_SCAN = 5


class InfoUpdatePayload:
    """
    Provides objects that contain all the information needed to request that
    certain information be updated.

    This class is meant only for use internal to InfoUpdateThread.
    """

    def __init__(self, faculty_username, instruction: InfoInstruction,
                 class_name=None, assignment_name=None, student_username=None):
        self.faculty_username = faculty_username
        self.instruction = instruction
        self.class_name = class_name
        self.assignment_name = assignment_name
        self.student_username = student_username

    def __repr__(self):
        string = '{}, {}'.format(self.faculty_username, self.instruction.name)

        if self.instruction in (InfoInstruction.CLASS_SCAN,
                                InfoInstruction.ASSIGNMENT_SCAN,
                                InfoInstruction.SUBMISSION_SCAN):
            string += ', {}'.format(self.class_name)

        if self.instruction in (InfoInstruction.ASSIGNMENT_SCAN,
                                InfoInstruction.SUBMISSION_SCAN,
                                InfoInstruction.DELETE_ASSIGNMENT,
                                InfoInstruction.DISABLE_ASSIGNMENT):
            string += ', {}'.format(self.assignment_name)

        if self.instruction == InfoInstruction.SUBMISSION_SCAN:
            string += ', {}'.format(self.student_username)

        return string


class InfoUpdateThread(Thread):
    """
    Provides a Thread which waits for the name of a faculty member to show up
    in its queue, and then updates the info for that faculty's classes.

    Usage:

    Call the inherited start() method to start the thread.

    Shutdown the thread by calling shutdown(). All items in the queue will be
    processed before fully shutting down.

    Request that information be updated by calling one of the enqueue_*()
    methods.
    """
    def __init__(self):
        """
        Construct the object.

        Constructing the object does not start the thread. Call start() to
        actually start the thread.
        """

        Thread.__init__(self)

        self._update_request_queue = Queue()
        self._info = nested_defaultdict()
        self._shutdown_flag = False

    def enqueue_full_scan(self, faculty_username):
        """
        Enqueue a request for a full scan of a faculty's classes.

        :param faculty_username: username of the faculty to scan
        """

        payload = InfoUpdatePayload(faculty_username,
                                    InfoInstruction.FULL_SCAN)
        self._update_request_queue.put(payload)

    def enqueue_submission_scan(self, faculty_username, class_name,
                                assignment_name, student_username):
        """
        Enqueue a request for a scan of an assignment directory for a specific
        student.

        :param faculty_username: name of the faculty that owns the class
        :param class_name: name of the class
        :param assignment_name: name of the assignment
        :param student_username: username of the student
        """

        instruction = InfoInstruction.SUBMISSION_SCAN
        payload = InfoUpdatePayload(faculty_username, instruction, class_name,
                                    assignment_name, student_username)
        self._update_request_queue.put(payload)

    def enqueue_class_scan(self, faculty_username, class_name):
        """
        Enqueue a request for a scan of an entire class.

        When processed, this action updates the information about all students,
        assignments, and submissions for a class.

        :param faculty_username: faculty that owns the class
        :param class_name: name of the class
        """

        payload = InfoUpdatePayload(faculty_username,
                                    InfoInstruction.CLASS_SCAN, class_name)
        self._update_request_queue.put(payload)

    def enqueue_assignment_scan(self, faculty_username, class_name,
                                assignment_name):
        """
        Enqueue a request for a scan of a single assignment.

        When processed, this action updates the information about all of the
        assignment directories for all of the students in the class tha the
        assignment belongs to.

        :param faculty_username: faculty that owns the assignment
        :param class_name: the class that the assignment belongs to
        :param assignment_name: name of the assignment
        :return:
        """

        payload = InfoUpdatePayload(faculty_username,
                                    InfoInstruction.ASSIGNMENT_SCAN,
                                    class_name, assignment_name)
        self._update_request_queue.put(payload)

    def enqueue_delete_assignment(self, faculty_username, class_name,
                                  assignment_name):
        """
        Enqueue a request for an assignment's information to be deleted.

        :param faculty_username: faculty that owns the assignment
        :param class_name: the class the assignment belongs to
        :param assignment_name: the name of the assignment
        """
        payload = InfoUpdatePayload(faculty_username,
                                    InfoInstruction.DELETE_ASSIGNMENT,
                                    class_name, assignment_name)
        self._update_request_queue.put(payload)

    def enqueue_disable_assignment(self, faculty_username, class_name,
                                   assignment_name):
        """
        Enqueue a request for an assignment to be disabled.

        :param faculty_username: faculty that owns the assignment
        :param class_name: the class the assignment belongs to
        :param assignment_name: the name of the assignment
        """
        payload = InfoUpdatePayload(faculty_username,
                                    InfoInstruction.DISABLE_ASSIGNMENT,
                                    class_name, assignment_name)
        self._update_request_queue.put(payload)

    def shutdown(self):
        """
        Shutdown the thread.

        The run loop will not exit until all queued payloads have been
        processed.

        This method blocks until the thread has died.
        """

        self._shutdown_flag = True
        self.join()

    def run(self):
        """
        Refresh info for a faculty's classes as their usernames arrive in the
        queue.

        This method should not be called directly. Call the start() method
        instead.

        Loops until someone calls shutdown().
        """

        while not self._shutdown_flag:
            try:
                while True:
                    payload = self._update_request_queue.get(block=True, timeout=0.1)

                    if not isinstance(payload, InfoUpdatePayload):
                        warning = ('Item was enqueued for info refresh that '
                                   'is not an InfoRefreshPayload: {0}'
                                   .format(payload))
                        logger.log_warning(warning)
                    else:
                        self._update_info(payload)
            except Empty:
                pass
            except Exception as e:
                logger.log_error('Error in info refresh thread: {0}'
                                 .format(e))

    def _update_info(self, payload: InfoUpdatePayload):
        # Carries out the payload's instructions

        logger.log_info('Info update: {}'.format(payload))

        try:
            if payload.instruction == InfoInstruction.FULL_SCAN:
                self._full_scan(payload.faculty_username)

            elif payload.instruction == InfoInstruction.CLASS_SCAN:
                self._class_scan(payload.faculty_username, payload.class_name)

            elif payload.instruction == InfoInstruction.ASSIGNMENT_SCAN:
                students = db.get_class_students(payload.class_name,
                                                 payload.faculty_username)

                self._assignment_scan(payload.faculty_username,
                                      payload.class_name,
                                      payload.assignment_name,
                                      students)

            elif payload.instruction == InfoInstruction.DELETE_ASSIGNMENT:
                self._delete_assignment(payload.faculty_username,
                                        payload.class_name,
                                        payload.assignment_name)

            elif payload.instruction == InfoInstruction.DISABLE_ASSIGNMENT:
                self._disable_assignment(payload.faculty_username,
                                         payload.class_name,
                                         payload.assignment_name)

            elif payload.instruction == InfoInstruction.SUBMISSION_SCAN:
                student = db.get_class_student_by_username(payload.student_username,
                                                           payload.class_name,
                                                           payload.faculty_username)

                self._assignment_scan(payload.faculty_username,
                                      payload.class_name,
                                      payload.assignment_name, (student,))

            self._write_info(payload.faculty_username)

            logger.log_info('Completed info update: {}'.format(payload))
        except Exception as e:
            error = 'Info update failed: {0}'.format(e)
            logger.log_error(error)

    def _write_info(self, faculty_username):
        # Write the info to the info file

        gitkeeper_path = user_gitkeeper_path(faculty_username)
        info_path = faculty_info_path(gitkeeper_path)

        if not os.path.isdir(info_path):
            mkdir(info_path, sudo=True)
            sudo_chown(info_path, faculty_username, config.keeper_group,
                       recursive=True)

        json_filename = '{0}.json'.format(str(time()))

        info_json_path = os.path.join(info_path, json_filename)

        with TemporaryDirectory() as temp_dir_path:
            temp_info_json_path = os.path.join(temp_dir_path, 'info.json')

            with open(temp_info_json_path, 'w') as f:
                json.dump(self._info[faculty_username], f)

            sudo_chown(temp_info_json_path, faculty_username,
                       config.keeper_group)
            chmod(temp_info_json_path, '640', sudo=True)
            mv(temp_info_json_path, info_json_path, sudo=True)

        info_files = [f for f in os.listdir(info_path) if f.endswith('.json')]
        info_files.sort()

        # keep at most 10 info files on the server
        while len(info_files) > 10:
            delete_filename = info_files.pop(0)
            delete_path = os.path.join(info_path, delete_filename)
            rm(delete_path, sudo=True)

    def _full_scan(self, faculty_username):
        class_names = db.get_faculty_class_names(faculty_username)

        for class_name in class_names:
            self._class_scan(faculty_username, class_name)

    def _class_scan(self, faculty_username, class_name):
        # Update the info for a single class

        class_info = self._info[faculty_username][class_name]

        if db.class_is_open(class_name, faculty_username):
            class_info['open'] = True

            students_info = nested_defaultdict()

            students = db.get_class_students(class_name, faculty_username)

            for student in students:
                student_info = {
                    'last': student.last_name,
                    'first': student.first_name,
                    'username': student.username,
                    'email_address': student.email_address,
                    'home_dir': user_home_dir(student.username),
                    'last_first_username': student.get_last_first_username()
                }

                students_info[student.username] = student_info

            class_info['students'] = students_info

            assignment_names = [
                assignment.name for assignment in
                db.get_class_assignments(class_name,
                                         faculty_username)
            ]

            for assignment_name in assignment_names:
                self._assignment_scan(faculty_username, class_name,
                                      assignment_name, students)
        else:
            class_info['open'] = False
            class_info['students'] = nested_defaultdict()
            class_info['assignments'] = nested_defaultdict()

    def _delete_assignment(self, faculty_username, class_name,
                           assignment_name):
        class_info = self._info[faculty_username][class_name]
        del class_info['assignments'][assignment_name]

    def _disable_assignment(self, faculty_username, class_name,
                            assignment_name):
        class_info = self._info[faculty_username][class_name]
        assignment_info = class_info['assignments'][assignment_name]
        assignment_info['disabled'] = True
        assignment_info['reports_repo'] = None
        assignment_info['students_repos'] = None

    def _assignment_scan(self, faculty_username, class_name, assignment_name,
                         students):
        # Update the information for a single assignment

        gitkeeper_path = user_gitkeeper_path(faculty_username)
        assignment_path = faculty_assignment_dir_path(class_name,
                                                      assignment_name,
                                                      gitkeeper_path)

        class_info = self._info[faculty_username][class_name]

        assignments_info = class_info['assignments']

        assignment_info = assignments_info[assignment_name]

        assignment_info['name'] = assignment_name
        assignment_info['published'] = db.is_published(class_name,
                                                       assignment_name,
                                                       faculty_username)
        assignment_info['disabled'] = db.is_disabled(class_name,
                                                     assignment_name,
                                                     faculty_username)

        if 'reports_repo' not in assignment_info:
            assignment_info['reports_repo'] = None

        if 'students_repos' not in assignment_info:
            assignment_info['students_repos'] = None

        # If the assignment is not published, or if the assignment is disabled,
        # we're done
        if not assignment_info['published'] or assignment_info['disabled']:
            return

        with directory_locks.get_lock(assignment_path):
            assignment_dir = AssignmentDirectory(assignment_path)
            reports_repo_path = assignment_dir.reports_repo_path
            reports_repo_hash = git_head_hash(assignment_dir.reports_repo_path,
                                              user=faculty_username)

        reports_repo_info = {
            'path': reports_repo_path,
            'hash': reports_repo_hash,
        }

        assignment_info['reports_repo'] = reports_repo_info

        if assignment_info['students_repos'] is None:
            assignment_info['students_repos'] = nested_defaultdict()

        students_info = assignment_info['students_repos']

        for student in students:
            student_home_dir = user_home_dir(student.username)

            assignment_repo_path = \
                student_assignment_repo_path(faculty_username, class_name,
                                             assignment_name, student_home_dir)

            try:
                hashes_and_times = git_hashes_and_times(assignment_repo_path,
                                                        user=student.username)
            except GkeepException as e:
                warning = ('Could not get hashes for {0}: {1}'
                           .format(assignment_repo_path, e))
                logger.log_warning(warning)
                continue

            student_info = {
                'first': student.first_name,
                'last': student.last_name,
                'path': assignment_repo_path,
                'hash': hashes_and_times[0][0],
                'time': hashes_and_times[0][1],
                'submission_count': len(hashes_and_times) - 1
            }

            students_info[student.username] = student_info


# module-level instance for global access
info_updater = InfoUpdateThread()
