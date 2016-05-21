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

"""Provides concrete classes for reading and writing remote CSV files using
an active paramiko SSH connection."""

import csv
from paramiko import SSHClient, SSHException

from gkeepcore.csv_files import CSVReader, CSVWriter, CSVException


class RemoteCSVReader(CSVReader):
    """Allows reading from a remote CSV file."""
    def __init__(self, file_path, ssh: SSHClient):
        """
        :param file_path: path to the CSV file on the remote machine
        :param ssh: connected paramiko SSHClient
        """
        try:
            sftp_client = ssh.open_sftp()
            with sftp_client.open(file_path) as f:
                self._rows = list(csv.reader(f))
        except SSHException:
            raise CSVException('Error reading from {0} remotely.'
                               .format(file_path))

    def get_rows(self):
        """Retrieve the rows from the CSV file

        :return: list of lists representing all rows from the file
        """
        return self._rows


class RemoteCSVWriter(CSVWriter):
    """Allows writing to a remote CSV file."""
    def __init__(self, file_path, ssh: SSHClient):
        """
        :param file_path: path to the CSV file on the remote machine
        :param ssh: connected paramiko SSHClient
        """
        self._file_path = file_path
        self._ssh = ssh

    def write_rows(self, rows):
        """Write rows to the file

        :param rows: list of lists (or tuples) to write
        """
        try:
            sftp_client = self._ssh.open_sftp()
            with sftp_client.open(self._file_path, 'w') as f:
                writer = csv.writer(f)

                for row in rows:
                    writer.writerow(row)
        except SSHException:
            raise CSVException('Error writing to {0} remotely'
                               .format(self._file_path))
