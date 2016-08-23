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
Provides RefreshInfoHandler, the handler for refreshing a faculty's info.json

Event type: REFRESH_INFO
"""
import json
import os
from tempfile import TemporaryDirectory

from gkeepcore.git_commands import git_head_hash
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import user_home_dir, student_assignment_repo_path, \
    faculty_info_file_path
from gkeepcore.system_commands import mv, sudo_chown, chmod
from gkeepserver.assignments import AssignmentDirectory, \
    get_class_assignment_dirs
from gkeepserver.event_handler import EventHandler
from gkeepserver.gkeepd_logger import gkeepd_logger
from gkeepserver.server_configuration import config
from gkeepserver.students_and_classes import get_faculty_class_names, \
    get_class_students


class RefreshInfoHandler(EventHandler):
    """
    Handles a request from the client to refresh the list of repository hashes.
    """

    def handle(self):
        """
        Take action after a client requests that the info be refreshed.
        """

        try:
            class_names = get_faculty_class_names(self._faculty_username)

            for class_name in class_names:
                self._refresh_class_info(class_name)

            self._write_hashes()

            self._report_success(str(self._timestamp))
            info = 'Info refreshed for {0}'.format(self._faculty_username)
            gkeepd_logger.log_info(info)
        except Exception as e:
            self._report_error(str(e))
            error = 'Refresh info failed: {0}'.format(e)
            gkeepd_logger.log_error(error)

    def _write_hashes(self):
        # Write the info to the info file

        home_dir = user_home_dir(self._faculty_username)
        info_json_path = faculty_info_file_path(home_dir)

        with TemporaryDirectory() as temp_dir_path:
            temp_info_json_path = os.path.join(temp_dir_path, 'info.json')

            with open(temp_info_json_path, 'w') as f:
                json.dump(self._info, f)

            sudo_chown(temp_info_json_path, self._faculty_username,
                       config.keeper_group)
            chmod(temp_info_json_path, '640', sudo=True)
            mv(temp_info_json_path, info_json_path, sudo=True)

    def _refresh_class_info(self, class_name):
        # Refresh the info for a single class

        self._info[class_name] = {}

        students = get_class_students(self._faculty_username, class_name)

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

        self._info[class_name] = {
            'students': students_info,
            'assignments': {}
        }

        assignment_dirs = get_class_assignment_dirs(self._faculty_username,
                                                    class_name)

        for assignment_dir in assignment_dirs:
            if assignment_dir.is_published():
                self._refresh_assignment_info(assignment_dir, students)

    def _refresh_assignment_info(self, assignment_dir: AssignmentDirectory,
                                 students):
        # Refresh the hashes for a single assignment

        class_name = assignment_dir.class_name
        assignment_name = assignment_dir.assignment_name

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
                student_assignment_repo_path(self._faculty_username,
                                             class_name, assignment_name,
                                             student_home_dir)

            try:
                assignment_repo_hash = git_head_hash(assignment_repo_path)
            except GkeepException as e:
                warning = ('Could not get hash for {0}: {1}'
                           .format(assignment_repo_path, e))
                self._report_warning(warning)
                continue

            student_info = {
                'path': assignment_repo_path,
                'hash': assignment_repo_hash
            }

            students_info[student.username] = student_info

        assignment_info = {
            'name': assignment_name,
            'reports_repo': reports_repo_info,
            'students_repos': students_info
        }

        self._info[class_name]['assignments'][assignment_name] = \
            assignment_info

    def _parse_payload(self):
        """
        No real parsing to do here, just setup _hashes attribute.
        """

        self._info = {}
