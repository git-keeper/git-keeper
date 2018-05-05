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


from gkeeprobot.control.ClientControl import ClientControl
from gkeeprobot.control.ServerControl import ServerControl
from gkeepcore.shell_command import CommandError

"""Provides keywords for robotframework to configure faculty and student
accounts before testing begins."""

client_control = ClientControl()
server_control = ServerControl()


class ClientSetupKeywords:

    def create_accounts(self, *names):
        for name in names:
            client_control.run_vm_bash_script('keeper',
                                              'make_user_with_password.sh',
                                              name)

    def establish_ssh_keys(self, *names):
        temp_dir_name = client_control.vm_control.temp_dir.name
        for name in names:
            client_control.run_vm_bash_script('keeper',
                                              'make_ssh_keys.sh',
                                              name,
                                              temp_dir_name)
            server_control.run_vm_bash_script('keeper',
                                              'make_authorized_keys.sh',
                                              name,
                                              temp_dir_name)

    def add_to_class(self, faculty, class_name, student):
        line = 'Last,First,{}@gitkeeper.edu'.format(student)
        client_control.run_vm_python_script(faculty, 'add_to_file.py',
                                            '{}.csv'.format(class_name), line)

    def remove_from_class(self, faculty, class_name, student):
        cmd = 'sed -i /{}/d {}.csv'.format(student, class_name)
        client_control.run(faculty, cmd)

    def add_file_to_client(self, username, filename, target_filename):
        client_control.copy(username, filename, target_filename)

    def make_empty_file(self, username, filename):
        client_control.run(username, 'touch {}'.format(filename))

    def create_gkeep_config_file(self, faculty):
        client_control.run_vm_bash_script(faculty, 'make_gkeep_config.sh',
                                          faculty)

    def reset_client(self):
        client_control.run_vm_python_script('keeper', 'reset_client.py')
