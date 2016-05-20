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

"""Provides two classes for reading from and writing to remote log files
over paramiko SSH connections.

Thread-safe if the strings written to the log are <= 512 bytes.

See the gkeepcore.log_file module for more information.
"""

from paramiko import SSHClient, SSHException

from gkeepcore.log_file import LogFileReader, LogFileWriter,\
    LogFileException
from gkeepcore.subprocess_commands import append_to_file, get_byte_count,\
    CommandError


class RemoteLogFileReader(LogFileReader):
    """Allows reading from watched remote log files. Intended for use
    with a LogPollingThread.
    """
    def __init__(self, file_path, ssh: SSHClient):
        """
        :param file_path: path to the log file
        :param ssh: paramiko SSHClient, must be connected to a remote host
        """
        self._file_path = file_path
        self._ssh = ssh

    def get_data(self, seek_position=0) -> str:
        """Retrieve data from the log file from seek_position to the end

        :param seek_position: position to seek to before reading
        :return: string containing text from the file
        """
        try:
            sftp_client = self._ssh.open_sftp()
            with sftp_client.open(self._file_path) as f:
                f.seek(seek_position)
                data = f.read()
        except SSHException as e:
            raise LogFileException from e

        return data.decode()

    def get_file_path(self) -> str:
        """Getter for the log file path

        :return: the path to the log file
        """
        return self._file_path

    def get_byte_count(self) -> int:
        """Retrieve the number of bytes in the log file

        :return: number of bytes in the log file
        """
        try:
            byte_count = get_byte_count(self.get_file_path(), ssh=self._ssh)
        except CommandError as e:
            raise LogFileException from e

        return byte_count


class RemoteLogFileWriter(LogFileWriter):
    """Allows writing to remote log files over a paramiko SSH connection
    """
    def __init__(self, file_path, ssh: SSHClient):
        """
        :param file_path: path to the log file
        :param ssh: a paramiko SSH client which is connected to a remote host
        """
        self._file_path = file_path
        self._ssh = ssh

    def _append(self, string):
        # Appends a string to the log. Should not be called directly, use the
        # inherited log() method instead.
        try:
            append_to_file(self._file_path, string, ssh=self._ssh)
        except CommandError as e:
            print(e)
            raise LogFileException from e
