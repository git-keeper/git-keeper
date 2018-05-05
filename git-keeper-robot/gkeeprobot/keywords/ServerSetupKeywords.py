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

"""Provides keywords for robotframework to configure gkserver before
testing begins."""

control = ServerControl()


class ServerSetupKeywords:

    def configure_faculty(self, *faculty_list):
        for faculty_name in faculty_list:
            line = 'Professor,Doctor,{}@gitkeeper.edu'.format(faculty_name)
            control.run_vm_python_script('keeper', 'add_to_file.py',
                                         'faculty.csv', line)

    def add_file_to_server(self, username, filename, target_filename):
        control.copy(username, filename, target_filename)

    def start_gkeepd(self):
        control.run('keeper', 'screen -S gkserver -d -m gkeepd')

    def add_account_on_server(self, faculty_name):
        cmd = 'sudo useradd -ms /bin/bash {}'.format(faculty_name)
        control.run('keeper', cmd)

    def reset_server(self):
        control.run_vm_python_script('keeper', 'reset_server.py')
