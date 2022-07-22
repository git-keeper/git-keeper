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


import json
from robot.utils.asserts import assert_equal

from gkeeprobot.control.ClientControl import ClientControl
from gkeeprobot.exceptions import GkeepRobotException
from gkeeprobot.control.VMControl import ExitCodeException

"""Provides keywords used by robotframework to check the results of
user actions."""

client_control = ClientControl()


def run_gkeep_json_query(faculty, query):
    cmd = 'gkeep query --json {}'.format(query)

    try:
        result = client_control.run(faculty, cmd)
    except ExitCodeException:
        raise GkeepRobotException('Running the following query as {} failed:\n'
                                  '{}'.format(faculty, query))

    try:
        parsed_result = json.loads(result)
    except json.decoder.JSONDecodeError as e:
        raise GkeepRobotException('Running the query "{}" as {} produced '
                                  'invalid JSON:\n{}'.format(query, faculty,
                                                             result))

    return parsed_result


class ClientCheckKeywords:

    def gkeep_add_succeeds(self, faculty, class_name):
        cmd = 'gkeep --yes add {} {}.csv'.format(class_name, class_name)
        client_control.run(faculty, cmd)

    def gkeep_add_no_csv_succeeds(self, faculty, class_name):
        client_control.run(faculty, 'gkeep --yes add {}'.format(class_name))

    def gkeep_add_fails(self, faculty, class_name):
        try:
            cmd = 'gkeep --yes add {} {}.csv'.format(class_name, class_name)
            client_control.run(faculty, cmd)
            raise GkeepRobotException('gkeep add should have non-zero return')
        except ExitCodeException:
            pass

    def gkeep_modify_succeeds(self, faculty, class_name):
        cmd = 'gkeep --yes modify {} {}.csv'.format(class_name, class_name)
        client_control.run(faculty, cmd)

    def gkeep_modify_fails(self, faculty, class_name):
        try:
            cmd = 'gkeep --yes modify {} {}.csv'.format(class_name, class_name)
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
        results = run_gkeep_json_query(faculty, sub_command)
        import pprint
        pp_results = pprint.pformat(results)
        pp_expected = pprint.pformat(json.loads(expected_results))
        assert_equal(pp_results, pp_expected)

    def gkeep_query_fails(self, faculty, sub_command):
        cmd = 'gkeep query --json {}'.format(sub_command)
        try:
            client_control.run(faculty, cmd)
            raise GkeepRobotException('gkeep query should return non-zero')
        except ExitCodeException:
            pass

    def class_exists(self, faculty, class_name):
        found = False
        for class_info in run_gkeep_json_query(faculty, 'classes'):
            if class_info['name'] == class_name:
                found = True

        if not found:
            raise GkeepRobotException('{} has no class named {}'
                                      .format(faculty, class_name))

    def class_is_open(self, faculty, class_name):
        is_open = False
        for class_info in run_gkeep_json_query(faculty, 'classes'):
            if class_info['name'] == class_name and class_info['open']:
                is_open = True

        if not is_open:
            raise GkeepRobotException('Class {} is not open'
                                      .format(faculty, class_name))

    def class_is_closed(self, faculty, class_name):
        is_closed = False
        for class_info in run_gkeep_json_query(faculty, 'classes'):
            if class_info['name'] == class_name and not class_info['open']:
                is_closed = True

        if not is_closed:
            raise GkeepRobotException('Class {} is not closed'
                                      .format(faculty, class_name))

    def class_contains_student(self, faculty, class_name, username,
                               first_name='First', last_name='Last'):
        result = run_gkeep_json_query(faculty, 'students')
        if class_name not in result:
            raise GkeepRobotException('{} has no class {}'
                                      .format(faculty, class_name))

        expected_student_dict = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
        }

        present = False

        for student_dict in result[class_name]:
            if all(item in student_dict.items()
                   for item in expected_student_dict.items()):
                present = True

        if not present:
            error = ('Student "{},{},{}" not in {}'
                     .format(last_name, first_name, username, class_name))
            raise GkeepRobotException(error)

    def class_does_not_contain_student(self, faculty, class_name, username,
                                       first_name='First', last_name='Last'):
        result = run_gkeep_json_query(faculty, 'students')
        if class_name not in result:
            raise GkeepRobotException('{} has no class {}'
                                      .format(faculty, class_name))

        expected_student_dict = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
        }

        present = False

        for student_dict in result[class_name]:
            if all(item in student_dict.items()
                   for item in expected_student_dict.items()):
                present = True

        if present:
            error = ('Student "{},{},{}" should not be in {}'
                    .format(last_name, first_name, username, class_name))
            raise GkeepRobotException(error)

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

    def gkeep_admin_promote_succeeds(self, admin, faculty_to_promote):
        email_address = '{}@school.edu'.format(faculty_to_promote)

        client_control.run(admin, 'gkeep admin_promote {}'
                                   .format(email_address))

    def gkeep_admin_promote_fails(self, admin, faculty_to_promote):
        email_address = '{}@school.edu'.format(faculty_to_promote)

        try:
            client_control.run(admin, 'gkeep admin_promote {}'
                                      .format(email_address))
            error = 'gkeep admin_promote should have non-zero return'
            raise GkeepRobotException(error)
        except ExitCodeException:
            pass

    def gkeep_admin_demote_succeeds(self, admin, faculty_to_demote):
        email_address = '{}@school.edu'.format(faculty_to_demote)

        client_control.run(admin, 'gkeep admin_demote {}'
                                   .format(email_address))

    def gkeep_admin_demote_fails(self, admin, faculty_to_demote):
        email_address = '{}@school.edu'.format(faculty_to_demote)

        try:
            client_control.run(admin, 'gkeep admin_demote {}'
                                      .format(email_address))
            error = 'gkeep admin_demote should have non-zero return'
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

    def gkeep_delete_succeeds(self, faculty, course_name, assignment_name):
        client_control.run(faculty, 'gkeep --yes delete {} {}'.format(course_name, assignment_name))

    def gkeep_delete_fails(self, faculty, course_name, assignment_name):
        try:
            client_control.run(faculty, 'gkeep --yes delete {} {}'.format(course_name, assignment_name))
            error = 'gkeep delete should have non-zero return'
            raise GkeepRobotException(error)
        except ExitCodeException:
            pass

    def gkeep_disable_succeeds(self, faculty, course_name, assignment_name):
        client_control.run(faculty, 'gkeep --yes disable {} {}'.format(course_name, assignment_name))

    def gkeep_disable_fails(self, faculty, course_name, assignment_name):
        try:
            client_control.run(faculty, 'gkeep --yes disable {} {}'.format(course_name, assignment_name))
            error = 'gkeep disable should have non-zero return'
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

    def gkeep_passwd_succeeds(self, faculty, username):
        client_control.run(faculty, 'gkeep passwd {}'.format(username))

    def gkeep_passwd_fails(self, faculty, username):
        try:
            client_control.run(faculty, 'gkeep passwd {}'.format(username))
            error = 'gkeep passwd should have non-zero exit code'
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

    def gkeep_status_succeeds(self, faculty, class_name, status):
        cmd = 'gkeep status {} {}'.format(class_name, status)
        try:
            client_control.run(faculty, cmd)
        except ExitCodeException as e:
            error = 'Command failed: {}\n{}'.format(cmd, e)
            raise GkeepRobotException(error)

    def gkeep_status_fails(self, faculty, class_name, status):
        cmd = 'gkeep status {} {}'.format(class_name, status)
        try:
            client_control.run(faculty, cmd)
            error = ('Command should have had non-zero exit code: {}'
                     .format(cmd))
            raise GkeepRobotException(error)
        except ExitCodeException:
            pass

    def gkeep_update_succeeds(self, faculty, class_name, assignment_name, update_type):
        cmd = 'gkeep update {} {} {}'.format(class_name, assignment_name, update_type)
        try:
            client_control.run(faculty, cmd)
        except ExitCodeException as e:
            error = 'Command failed: {}\n{}'.format(cmd, e)
            raise GkeepRobotException(error)

    def gkeep_update_fails(self, faculty, class_name, assignment_name, update_type):
        cmd = 'gkeep update {} {} {}'.format(class_name, assignment_name, update_type)
        try:
            client_control.run(faculty, cmd)
            error = ('Command should have had non-zero exit code: {}'
                     .format(cmd))
            raise GkeepRobotException(error)
        except ExitCodeException as e:
            pass
