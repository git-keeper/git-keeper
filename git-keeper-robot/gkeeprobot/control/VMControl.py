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

from gkeepcore.shell_command import run_command
from tempfile import TemporaryDirectory
from robot.api import logger

"""Provides methods to execute commands on gkclient and gkserver
during testing."""


class VMControl:

    temp_dir = TemporaryDirectory(prefix='temp_ssh_keys', dir='.')

    def run_vm_python_script(self, username, script, port, *args):
        base = 'python3 /vagrant/vm_scripts/' + script
        cmd = ' '.join([base] + list(args))
        return self.run(username, port, cmd).strip()

    def run_vm_bash_script(self, username, script, port, *args):
        base = 'source /vagrant/vm_scripts/' + script
        cmd = ' '.join([base] + list(args))
        return self.run(username, port, cmd).strip()

    def run(self, username, port, cmd):
        base = 'ssh localhost'
        port = '-p {}'.format(port)
        if username == 'keeper':
            user_and_key = '-l {} -i ssh_keys/{}_rsa'.format(username,
                                                             username)
        else:
            user_and_key = '-l {} -i {}/{}_rsa'.format(username,
                                                       self.temp_dir.name,
                                                       username)
        suppress_warnings = '-o StrictHostKeyChecking=no ' \
                            '-o UserKnownHostsFile=/dev/null ' \
                            '-o LogLevel=ERROR'

        full_cmd = ' '.join([base, port, user_and_key, suppress_warnings, cmd])
        return run_command(full_cmd)

    def copy(self, username, port, filename, target_filename):
        base = 'scp'
        port = '-P {}'.format(port)
        if username == 'keeper':
            key = '-i ssh_keys/{}_rsa'.format(username)
        else:
            key = '-i {}/{}_rsa'.format(self.temp_dir.name, username)
        suppress_warnings = '-o StrictHostKeyChecking=no ' \
                            '-o UserKnownHostsFile=/dev/null ' \
                            '-o LogLevel=ERROR'
        copy_cmd = '{} {}@localhost:{}'.format(filename, username,
                                               target_filename)

        full_cmd = ' '.join([base, port, key, suppress_warnings, copy_cmd])
        return run_command(full_cmd)
