# Copyright 2019 Nathan Sommer and Ben Coleman
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

from paramiko import SSHClient, AutoAddPolicy


class ServerCommunication:

    def __init__(self, username, port, key_file_path):
        self._ssh_client = None
        self._sftp_client = None
        self.username = username
        self.port = port
        self.key_file_path = key_file_path

    def run_command(self, command):
        if self._ssh_client is None:
            self._connect()

        transport = self._ssh_client.get_transport()
        channel = transport.open_session()
        channel.set_combine_stderr(True)
        f = channel.makefile()
        channel.exec_command(command)
        output = f.read().decode('utf-8')
        exit_code = channel.recv_exit_status()
        return output, exit_code

    def copy_file(self, local_path: str, remote_path: str):
        if self._ssh_client is None:
            self._connect()
        self._sftp_client.put(local_path, remote_path)

    def _connect(self):
        self._ssh_client = SSHClient()
        self._ssh_client.load_system_host_keys()
        self._ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        self._ssh_client.connect(hostname='localhost',
                                 username=self.username,
                                 port=self.port,
                                 key_filename=self.key_file_path,
                                 timeout=5,
                                 compress=True)
        self._sftp_client = self._ssh_client.open_sftp()

    def close(self):
        self._ssh_client.close()
        self._sftp_client.close()
