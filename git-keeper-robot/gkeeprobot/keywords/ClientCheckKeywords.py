# Copyright 2018 Nathan Sommer and Ben Coleman
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


from robot.utils.asserts import assert_equal

from gkeeprobot.control.ClientControl import ClientControl
from gkeeprobot.exceptions import GkeepRobotException
from gkeeprobot.control.VMControl import ExitCodeException

"""Provides keywords used by robotframework to check the results of
user actions."""

client_control = ClientControl()


class ClientCheckKeywords:

    def gkeep_add_succeeds(self, faculty, class_name):
        client_control.run(faculty, 'gkeep add {} {}.csv'.format(class_name,
                                                                 class_name))

    def gkeep_add_no_csv_succeeds(self, faculty, class_name):
        client_control.run(faculty, 'gkeep add {}'.format(class_name))

    def gkeep_add_fails(self, faculty, class_name):
        try:
            cmd = 'gkeep add {} {}.csv'.format(class_name, class_name)
            client_control.run(faculty, cmd)
            raise GkeepRobotException('gkeep add should have non-zero return')
        except ExitCodeException:
            pass

    def gkeep_modify_succeeds(self, faculty, class_name):
        cmd = 'gkeep modify {} {}.csv'.format(class_name, class_name)
        client_control.run(faculty, cmd)

    def gkeep_modify_fails(self, faculty, class_name):
        try:
            cmd = 'gkeep modify {} {}.csv'.format(class_name, class_name)
            client_control.run(faculty, cmd)
            raise GkeepRobotException('gkeep modify should have non-zero return')
        except ExitCodeException:
            pass

    def gkeep_query_contains(self, faculty, sub_command, *expected_strings):
        cmd = 'gkeep query {}'.format(sub_command)
        results = client_control.run(faculty, cmd)
        for expected in expected_strings:
            assert expected in results

    def gkeep_query_does_not_contain(self, faculty, sub_command,
                                     *forbidden_strings):
        cmd = 'gkeep query {}'.format(sub_command)
        results = client_control.run(faculty, cmd)
        for forbidden in forbidden_strings:
            assert forbidden not in results

    def gkeep_query_json_produces_results(self, faculty, sub_command, expected_results):
        cmd = 'gkeep query --json {}'.format(sub_command)
        results = client_control.run(faculty, cmd)
        import pprint
        import json
        pp_results = pprint.pformat(json.loads(results.strip()))
        pp_expected = pprint.pformat(json.loads(expected_results))
        assert_equal(pp_results, pp_expected)

    def gkeep_query_fails(self, faculty, sub_command):
        cmd = 'gkeep query --json {}'.format(sub_command)
        try:
            client_control.run(faculty, cmd)
            raise GkeepRobotException('gkeep query should return non-zero')
        except ExitCodeException:
            pass

    def gkeep_add_faculty_succeeds(self, admin, new_faculty):
        last_name = 'Professor'
        first_name = 'Doctor'
        email_address = '{}@school.edu'.format(new_faculty)

        client_control.run(admin, 'gkeep add_faculty {} {} {}'
                                   .format(last_name, first_name,
                                           email_address))

    def gkeep_add_faculty_fails(self, admin, new_faculty):
        last_name = 'Professor'
        first_name = 'Doctor'
        email_address = '{}@school.edu'.format(new_faculty)

        try:
            client_control.run(admin, 'gkeep add_faculty {} {} {}'
                                       .format(last_name, first_name,
                                               email_address))
            error = 'gkeep add_faculty should have non-zero return'
            raise GkeepRobotException(error)
        except ExitCodeException:
            pass

    def gkeep_upload_succeeds(self, faculty, course_name, assignment_name):
        client_control.run(faculty, 'gkeep upload {} {}'.format(course_name, assignment_name))

    def gkeep_upload_fails(self, faculty, course_name, assignment_name):
        try:
            client_control.run(faculty, 'gkeep upload {} {}'.format(course_name, assignment_name))
            error = 'gkeep upload should have non-zero return'
            raise GkeepRobotException(error)
        except ExitCodeException:
            pass

    def gkeep_publish_succeeds(self, faculty, course_name, assignment_name):
        client_control.run(faculty, 'gkeep publish {} {}'.format(course_name, assignment_name))

    def gkeep_publish_fails(self, faculty, course_name, assignment_name):
        try:
            client_control.run(faculty, 'gkeep publish {} {}'.format(course_name, assignment_name))
            error = 'gkeep publish should have non-zero return'
            raise GkeepRobotException(error)
        except ExitCodeException:
            pass

    def gkeep_trigger_succeeds(self, faculty, course_name, assignment_name, student_name=None):
        if student_name is None:
            client_control.run(faculty, 'gkeep trigger {} {}'.format(course_name, assignment_name))
        else:
            client_control.run(faculty, 'gkeep trigger {} {} {}'.format(course_name, assignment_name, student_name))

    def gkeep_trigger_fails(self, faculty, course_name, assignment_name, student_name=None):
        if student_name is None:
            cmd = 'gkeep trigger {} {}'.format(course_name, assignment_name)
        else:
            cmd = 'gkeep trigger {} {} {}'.format(course_name, assignment_name, student_name)

        try:
            client_control.run(faculty, cmd)
            error = 'gkeep trigger should have non-zero return'
            raise GkeepRobotException(error)
        except ExitCodeException:
            pass

    def verify_submission_count(self, faculty_name, submission_folder, class_name, assignment_name, student_name, submission_count):
        reports_dir = '{}/{}/{}/reports'.format(submission_folder, class_name, assignment_name)
        student_report_dir = reports_dir + '/last_first_{}'.format(student_name)
        file_count = client_control.run(faculty_name, 'ls {} | wc -l'.format(student_report_dir)).strip()
        if file_count != submission_count:
            raise GkeepRobotException('Expected {} files but found {}'.format(submission_count, file_count))

    def gkeep_test_succeeds(self, faculty, course_name, assignment_name, solution_path):
        cmd = 'gkeep test {} {} {}'.format(course_name, assignment_name, solution_path)
        client_control.run(faculty, cmd)

    def gkeep_test_fails(self, faculty, course_name, assignment_name, solution_path):
        cmd = 'gkeep test {} {} {}'.format(course_name, assignment_name, solution_path)
        try:
            client_control.run(faculty, cmd)
            error = 'gkeep test should have non-zero return'
            raise GkeepRobotException(error)
        except ExitCodeException:
            pass
