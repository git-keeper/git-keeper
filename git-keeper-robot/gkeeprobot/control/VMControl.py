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

import shlex

from gkeepcore.system_commands import chmod
from tempfile import TemporaryDirectory

from gkeeprobot.control.ServerCommunication import ServerCommunication

"""Provides methods to execute commands on gkclient and gkserver
during testing."""


class ExitCodeException(Exception):
    """
    Used to indicate that a command
    """
    pass


class VMControl:

    temp_dir = TemporaryDirectory(prefix='temp_ssh_keys', dir='.')
    connections = {}

    def run_vm_python_script(self, username, script, port, *args):
        base = 'python3 /vagrant/vm_scripts/' + script
        cmd = ' '.join([base] + [shlex.quote(arg) for arg in args])
        return self.run(username, port, cmd).strip()

    def run_vm_bash_script(self, username, script, port, *args):
        base = 'source /vagrant/vm_scripts/' + script
        cmd = ' '.join([base] + [shlex.quote(arg) for arg in args])
        return self.run(username, port, cmd).strip()

    def run(self, username, port, cmd):

        connection_key = username + str(port)
        if connection_key not in VMControl.connections:
            VMControl.connections[connection_key] = \
                ServerCommunication(username, port, self._get_key_path(username))

        connection = VMControl.connections[connection_key]
        output, return_code = connection.run_command(cmd)

        if return_code != 0:
            raise ExitCodeException(output)
        return output

    def copy(self, username, port, filename, target_filename):

        connection_key = username + str(port)
        if connection_key not in VMControl.connections:
            VMControl.connections[connection_key] = \
                ServerCommunication(username, port, self._get_key_path(username))

        connection = VMControl.connections[connection_key]
        connection.copy_file(filename, target_filename)
        return

    def _get_key_path(self, username):
        if username == 'keeper':
            chmod('ssh_keys/keeper_rsa', '600')
            chmod('ssh_keys/keeper_rsa.pub', '600')
            return 'ssh_keys/keeper_rsa'
        else:
            return '{}/{}_rsa'.format(self.temp_dir.name, username)

    def close_user_connections(self, port):
        to_delete = []
        for key in VMControl.connections.keys():
            if str(port) in key and 'keeper' not in key:
                VMControl.connections[key].close()
                to_delete.append(key)

        for key in to_delete:
            del VMControl.connections[key]
