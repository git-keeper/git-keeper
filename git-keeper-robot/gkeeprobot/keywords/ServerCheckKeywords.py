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

from gkeeprobot.control.ServerControl import ServerControl
from gkeeprobot.exceptions import GkeepRobotException
from gkeeprobot.control.VMControl import ExitCodeException

"""Provides keywords for robotframework to check the state of gkserver
and gkeepd."""

control = ServerControl()


class ServerCheckKeywords:
    def gkeepd_is_running(self):
        result = control.run_vm_python_script('keeper', 'server_is_running.py')
        if result != 'True':
            raise GkeepRobotException('Server should be running')

    def gkeepd_is_not_running(self):
        result = control.run_vm_python_script('keeper', 'server_terminated.py')
        if result != 'True':
            raise GkeepRobotException('Server should not be running')

    def gkeepd_fails(self):
        try:
            control.run('keeper', 'gkeepd')
            raise GkeepRobotException('gkeepd should return non-zero')
        except ExitCodeException:
            pass

    def new_account_email_exists(self, username):
        result = control.run_vm_python_script('keeper', 'email_to.py',
                                              username, '"New git-keeper account"',
                                              'Password')
        if result != 'True':
            raise GkeepRobotException('No new account email for {}'.format(username))

    def password_reset_email_exists(self, username):
        result = control.run_vm_python_script('keeper', 'email_to.py',
                                              username, 'New git-keeper password',
                                              'Your git-keeper password has been reset to')
        if result != 'True':
            raise GkeepRobotException('No password reset email for {}'.format(username))

    def new_assignment_email_exists(self, username, course_name, assignment_name):
        # assignment name is in the body of the message
        subject = '"[{}] New assignment: {}"'.format(course_name, assignment_name)
        result = control.run_vm_python_script('keeper', 'email_to.py',
                                              username, subject,
                                              assignment_name)
        if result != 'True':
            raise GkeepRobotException('No new assignment email exists for {}, {}, {}'.format(username, course_name,
                                                                                   assignment_name))

    def submission_test_results_email_exists(self, username, course_name, assignment_name, body_contains):
        subject = '"[{}] {} submission test results"'.format(course_name, assignment_name)
        result = control.run_vm_python_script('keeper', 'email_to.py',
                                              username, subject, body_contains)

        if result != 'True':
            raise GkeepRobotException('No submission test result email for {}, {}, {}'.format(username, course_name,
                                                                                    assignment_name))

    def submission_test_results_email_does_not_exist(self, username, course_name, assignment_name, body_contains):
        subject = '"[{}] {} submission test results"'.format(course_name, assignment_name)
        result = control.run_vm_python_script('keeper', 'email_to.py',
                                              username, subject, body_contains)
        if result != 'False':
            raise GkeepRobotException('Submission test result email exists for {}, {}, {}'.format(username, course_name,
                                                                                    assignment_name))

    def email_exists(self, to_user, subject_contains=None, body_contains=None):
        result = control.run_vm_python_script('keeper', 'email_to.py',
                                              to_user, subject_contains, body_contains)
        if result != 'True':
            raise GkeepRobotException('No email to {} containing subject {} and body {}'.format(to_user, subject_contains,
                                                                                      body_contains))

    def new_account_email_does_not_exist(self, username):
        result = control.run_vm_python_script('keeper', 'no_email_to.py',
                                              username)
        if result != 'True':
            raise GkeepRobotException('Email exists to {}'.format(username))

    def user_exists_on_server(self, username):
        result = control.run_vm_python_script('keeper', 'user_exists.py',
                                              username)
        if result != 'True':
            raise GkeepRobotException('User {} does not exist'.format(username))

    def user_does_not_exist_on_server(self, username):
        result = control.run_vm_python_script('keeper',
                                              'user_does_not_exist.py',
                                              username)
        if result != 'True':
            raise GkeepRobotException('User {} exists but should not'.format(username))
