# Copyright 2017 Nathan Sommer and Ben Coleman
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
Provides a thread which updates the info for a faculty member's classes. Other
threads request an update by enqueuing a faculty username.
"""
import json
import os
from queue import Queue, Empty
from tempfile import TemporaryDirectory
from threading import Thread
from time import time

from gkeepcore.git_commands import git_head_hash, git_head_hash_date
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import user_home_dir, student_assignment_repo_path, \
    faculty_info_path
from gkeepcore.system_commands import sudo_chown, chmod, mv, mkdir, rm
from gkeepserver.assignments import get_class_assignment_dirs, \
    AssignmentDirectory
from gkeepserver.gkeepd_logger import gkeepd_logger as logger
from gkeepserver.server_configuration import config
from gkeepserver.students_and_classes import get_faculty_class_names, \
    get_class_students


class InfoRefreshThread(Thread):
    """
    Provides a Thread which waits for the name of a faculty member to show up
    in its queue, and then updates the info for that faculty's classes.

    Usage:

    Call the inherited start() method to start the thread.

    Shutdown the thread by calling shutdown(). All items in the queue will be
    processed before fully shutting down.

    Add faculty usernames to the thread by calling enqueue(username).
    """
    def __init__(self):
        """
        Construct the object.

        Constructing the object does not start the thread. Call start() to
        actually start the thread.
        """

        Thread.__init__(self)

        self._username_queue = Queue()

        self._shutdown_flag = False

    def enqueue(self, faculty_username: str):
        """
        Add a new faculty username to the queue.

        :param faculty_username: the username of the faculty
        """

        self._username_queue.put(faculty_username)

    def shutdown(self):
        """
        Shutdown the thread.

        The run loop will not exit until all queued usernames have been
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
                    faculty_username = self._username_queue.get(block=True,
                                                                timeout=0.1)

                    if not isinstance(faculty_username, str):
                        warning = ('Item enqueued for info refresh that is ' 
                                   ' not a string: {0}'
                                   .format(faculty_username))
                        logger.log_warning(warning)
                    else:
                        self._refresh_info(faculty_username)
            except Empty:
                pass
            except Exception as e:
                logger.log_error('Error in info refresh thread: {0}'
                                 .format(e))

    def _refresh_info(self, faculty_username):
        logger.log_info('Refreshing info for {0}'.format(faculty_username))

        # Refresh the info for a faculty member
        info = {}

        try:
            class_names = get_faculty_class_names(faculty_username)

            for class_name in class_names:
                self._refresh_class_info(faculty_username, class_name, info)

            self._write_hashes(faculty_username, info)

            info = 'Info refreshed for {0}'.format(faculty_username)
            logger.log_info(info)
        except Exception as e:
            error = 'Refresh info failed: {0}'.format(e)
            logger.log_error(error)

    def _write_hashes(self, faculty_username, info):
        # Write the info to the info file

        home_dir = user_home_dir(faculty_username)
        info_path = faculty_info_path(home_dir)

        if not os.path.isdir(info_path):
            mkdir(info_path, sudo=True)
            sudo_chown(info_path, faculty_username, config.keeper_group,
                       recursive=True)

        json_filename = '{0}.json'.format(str(time()))

        info_json_path = os.path.join(info_path, json_filename)

        with TemporaryDirectory() as temp_dir_path:
            temp_info_json_path = os.path.join(temp_dir_path, 'info.json')

            with open(temp_info_json_path, 'w') as f:
                json.dump(info, f)

            sudo_chown(temp_info_json_path, faculty_username,
                       config.keeper_group)
            chmod(temp_info_json_path, '640', sudo=True)
            mv(temp_info_json_path, info_json_path, sudo=True)

        info_files = [f for f in os.listdir(info_path) if f.endswith('.json')]
        info_files.sort()

        while len(info_files) > 10:
            delete_filename = info_files.pop(0)
            delete_path = os.path.join(info_path, delete_filename)
            rm(delete_path, sudo=True)

    def _refresh_class_info(self, faculty_username, class_name, info):
        # Refresh the info for a single class

        info[class_name] = {}

        students = get_class_students(faculty_username, class_name)

        students_info = {}

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

        info[class_name] = {
            'students': students_info,
            'assignments': {}
        }

        assignment_dirs = get_class_assignment_dirs(faculty_username,
                                                    class_name)

        for assignment_dir in assignment_dirs:
            self._refresh_assignment_info(faculty_username, assignment_dir,
                                          students, info)

    def _refresh_assignment_info(self, faculty_username,
                                 assignment_dir: AssignmentDirectory,
                                 students, info):
        # Refresh the hashes for a single assignment

        class_name = assignment_dir.class_name
        assignment_name = assignment_dir.assignment_name

        # If the assignment is not published, there isn't much to do
        if not assignment_dir.is_published():
            assignment_info = {
                'name': assignment_name,
                'published': False,
                'reports_repo': None,
                'students_repos': None
            }

            info[class_name]['assignments'][assignment_name] = \
                assignment_info

            return

        reports_repo_path = assignment_dir.reports_repo_path
        reports_repo_hash = git_head_hash(assignment_dir.reports_repo_path)

        reports_repo_info = {
            'path': reports_repo_path,
            'hash': reports_repo_hash
        }

        students_info = {}

        for student in students:
            student_home_dir = user_home_dir(student.username)

            assignment_repo_path = \
                student_assignment_repo_path(faculty_username,
                                             class_name, assignment_name,
                                             student_home_dir)

            try:
                assignment_repo_hash, last_commit_time = \
                    git_head_hash_date(assignment_repo_path)
            except GkeepException as e:
                warning = ('Could not get hash for {0}: {1}'
                           .format(assignment_repo_path, e))
                logger.log_warning(warning)
                continue

            student_info = {
                'first': student.first_name,
                'last': student.last_name,
                'path': assignment_repo_path,
                'hash': assignment_repo_hash,
                'time': last_commit_time
            }

            students_info[student.username] = student_info

        assignment_info = {
            'name': assignment_name,
            'published': True,
            'reports_repo': reports_repo_info,
            'students_repos': students_info
        }

        info[class_name]['assignments'][assignment_name] = \
            assignment_info


# module-level instance for global access
info_refresher = InfoRefreshThread()
