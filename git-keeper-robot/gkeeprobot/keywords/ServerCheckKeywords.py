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

"""Provides keywords for robotframework to check the state of gkserver
and gkeepd."""

control = ServerControl()


class ServerCheckKeywords:
    def gkeepd_is_running(self):
        result = control.run_vm_python_script('keeper', 'server_is_running.py')
        assert result == 'True'

    def gkeepd_is_not_running(self):
        result = control.run_vm_python_script('keeper', 'server_terminated.py')
        assert result == 'True'

    def new_account_email_exists(self, username):
        result = control.run_vm_python_script('keeper', 'email_to.py',
                                              username, 'New git-keeper account',
                                              'Password')
        assert result == 'True'

    def new_assignment_email_exists(self, username, course_name, assignment_name):
        # assignment name is in the body of the message
        subject = '[{}] New Assignment: {}'.format(course_name, assignment_name)
        result = control.run_vm_python_script('keeper', 'email_to.py',
                                              username, 'New assignment',
                                              assignment_name)

        assert result == 'True'

    def submission_test_results_email_exists(self, username, course_name, assignment_name, body_contains):
        subject = '[{}] {} submission test results'.format(course_name, assignment_name)
        result = control.run_vm_python_script('keeper', 'email_to.py',
                                              username, subject,
                                              body_contains)

        assert result == 'True'

    def email_exists(self, to_user, subject_contains=None, body_contains=None):
        result = control.run_vm_python_script('keeper', 'email_to.py',
                                              to_user, subject_contains, body_contains)
        assert result == 'True'

    def email_does_not_exist(self, username):
        result = control.run_vm_python_script('keeper', 'no_email_to.py',
                                              username)
        assert result == 'True'

    def user_exists_on_server(self, username):
        result = control.run_vm_python_script('keeper', 'user_exists.py',
                                              username)
        assert result == 'True'

    def user_does_not_exist_on_server(self, username):
        result = control.run_vm_python_script('keeper',
                                              'user_does_not_exist.py',
                                              username)
        assert result == 'True'
