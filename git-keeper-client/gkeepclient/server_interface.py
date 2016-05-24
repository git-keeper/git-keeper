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


"""Provides a globally accessible interface for interacting with a git-keeper
server through a paramiko SSH connection.

This module stores a SeverInterface instance in the module-level instance
variable named server_interface. Call connect() on this instance as early as
possible, probably in main() or whatever your entry point function is.
Attempting to call connect() a second time will raise a ServerInterfaceError
exception.

Any other modules that import the config will have access to the same instance
without having to call connect().

Before calling connect, be sure that you have called parse() on the global
ClientConfiguration object.

Example usage:

    import sys
    from gkeepclient.client_configuration import config
    from gkeepclient.server_interface import server_interface

    def main():
        try:
            config.parse()
            server_interface.connect()
        except ClientConfigurationError, ServerInterfaceError as e:
            sys.exit(e)

        # Now call methods such as server_interface.is_file(file_path)
"""


import os
from paramiko import SSHClient, SSHException
from shlex import quote

from gkeepclient.client_configuration import config
from gkeepcore.path_utils import build_user_log_path


class ServerInterfaceError(Exception):
    """Raised by ServerInterface methods."""
    pass


class ServerCommandExitFailure(ServerInterfaceError):
    """Raised when a command has a non-zero exit code."""
    pass


class ServerInterface:
    """Provides methods for interacting with the server over a paramiko SSH
    connection.

    All methods raise a ServerInterfaceError exception on errors.
    """
    def __init__(self):
        """Creates the object but does not connect to the server."""

        self._ssh_client = None
        self._sftp_client = None

    def connect(self):
        """Connects to the server.

        This method may only be called once.
        """

        # raise exception if we're already connected
        if self._ssh_client is not None:
            raise ServerInterfaceError('SSH connection already established')

        # connect the SSH client and open an SFTP client
        try:
            self._ssh_client = SSHClient()
            self._ssh_client.load_system_host_keys()
            self._ssh_client.connect(hostname=config.host,
                                     username=config.username,
                                     port=config.ssh_port)
            self._sftp_client = self._ssh_client.open_sftp()
        except SSHException as e:
            raise ServerInterfaceError(e)

    def run_command(self, command) -> str:
        """Runs a shell command on the server.

        Raises a ServerCommandExitFailure exception if the command has a
        non-zero exit code.

        :param command: the command to be run as a single string or as a list
         of string arguments
        :return: the stdout output of the command
        """

        # join the command into a single string if it is a list
        if isinstance(command, list):
            # quote all the arguments in case of special characters
            command = ' '.join([quote(arg) for arg in command])

        # open a channel and run the command
        try:
            transport = self._ssh_client.get_transport()
            channel = transport.open_session()
            channel.get_pty()
            f = channel.makefile()
            channel.exec_command(command)
            output = f.read()

            exit_status = channel.recv_exit_status()
            if exit_status != 0:
                raise ServerCommandExitFailure(output.decode('utf-8'))
        except SSHException as e:
            raise ServerInterfaceError(e)

        # output is bytes, we want a utf-8 string
        return output.decode('utf-8')

    def list_directory(self, path: str) -> list:
        """Lists the contents of a directory on the server.

        It is the responsibility of the caller to ensure the directory exists.

        :param path: directory path
        :return: list of file and directory names
        """

        try:
            directory_listing = self._sftp_client.listdir(path)
        except SSHException as e:
            raise ServerInterfaceError(e)

        return directory_listing

    def _bash_file_test(self, operator, path) -> bool:
        # Helper method, runs a bash file test on the server
        #
        # Useful operators:
        #     -f  path is a regular file
        #     -d  path is a directory
        #
        # :param operator: file test operator
        # :param path: path to the file
        # :return: boolean result of the test

        # quote the path in case of special characters
        quoted_path = quote(path)

        command = '[ {0} {1} ]'.format(operator, quoted_path)

        # only has a 0 exit code if the test returns true
        try:
            self.run_command(command)
            return True
        except ServerCommandExitFailure:
            return False

    def is_file(self, file_path: str) -> bool:
        """Checks if file_path is a file on the server.

        :param file_path:
        :return: True if file_path is a file, False if not
        """

        return self._bash_file_test('-f', file_path)

    def is_directory(self, dir_path: str) -> bool:
        """Checks if dir_path is a directory on the server.

        :param dir_path:
        :return: True if dir_path is a directory, False if not
        """

        return self._bash_file_test('-d', dir_path)

    def copy_file(self, local_path: str, remote_path: str):
        """Copies a local file to the server.

        It is the responsibility of the caller to ensure the local path exists
        and that the remote path does not exist.

        The remote_path is the full destination file path. After a
        successful copy, local_path and remote_path will be the same file.

        :param local_path: path to the local file
        :param remote_path: full destination path on the server
        """

        try:
            self._sftp_client.put(local_path, remote_path)
        except SSHException as e:
            raise ServerInterfaceError(e)

    def create_directory(self, remote_path):
        """Creates a new directory on the server.

        It is the responsibility of the caller to ensure the remote path does
        not already exist.

        :param remote_path: new path to create on the server
        """

        try:
            self._sftp_client.mkdir(remote_path)
        except SSHException as e:
            raise ServerInterfaceError(e)

    def copy_directory(self, source_path: str, dest_path: str):
        """Copies a local directory to the server.

        It is the responsibility of the caller to ensure that source_path
        exists locally and that dest_path does not already exist on the
        server.

        The dest_path is the full destination directory path. After a
        successful copy, source_path and dest_path have the same contents.

        :param source_path: path to the local directory to copy
        :param dest_path: path of the copy on the server
        """

        # we'll be replacing source_path with dest_path in strings later, so
        # make sure neither have trailing slashes
        source_path = source_path.rstrip('/')
        dest_path = dest_path.rstrip('/')

        try:
            # create the top directory
            self.create_directory(dest_path)

            # paramiko will not copy entire directories, so we have to walk
            # through the local directory tree, make the needed directories,
            # and copy the files individually.
            for dir_path, dir_names, file_names in os.walk(source_path):
                for dir_name in dir_names:
                    local_path = os.path.join(dir_path, dir_name)
                    remote_path = local_path.replace(source_path, dest_path, 1)
                    self.create_directory(remote_path)

                for file_name in file_names:
                    local_path = os.path.join(dir_path, file_name)
                    remote_path = local_path.replace(source_path, dest_path, 1)
                    self.copy_file(local_path, remote_path)

        except SSHException as e:
            raise ServerInterfaceError(e)

    def get_file_byte_count(self, file_path: str) -> int:
        """Get the number of bytes in a file on the server.

        It is the responsibility of the caller to ensure that the file exists.

        :param file_path: path to the file
        :return: number of bytes in the file
        """

        try:
            count = self._sftp_client.stat(file_path).st_size
        except SSHException as e:
            raise ServerInterfaceError(e)

        return count

    def append_to_file(self, file_path, string):
        """Append a string to a file on the server, adding a trailing newline.

        :param file_path: the path to the file
        :param string: the string to append
        """

        try:
            with self._sftp_client.open(file_path, 'a') as f:
                print(string, file=f)
        except SSHException as e:
            raise ServerInterfaceError(e)

    def read_file_bytes(self, file_path: str, seek_position=0) -> bytes:
        """Read a file from the server, optionally starting at a byte
        offset, and return the data as bytes.

        :param file_path: path to the file
        :param seek_position: byte offset at which to start reading
        :return: data from the file as bytes
        """

        try:
            with self._sftp_client.open(file_path) as f:
                f.seek(seek_position)
                data = f.read()
        except SSHException as e:
            raise ServerInterfaceError(e)

        return data

    def read_file_text(self, file_path: str, seek_position=0) -> str:
        """Read a file from the server, optionally starting at a byte
        offset, and return the data as a string.

        :param file_path: path to the file
        :param seek_position: byte offset at which to start reading
        :return: data from the file as a string
        """

        data_bytes = self.read_file_bytes(file_path, seek_position)

        return data_bytes.decode('utf-8')

    def get_user_home_dir(self, username: str) -> str:
        """Finds the user's home directory path on the server.

        :param username: the user whose home directory we want
        :return: the home directory path
        """

        tilde_home_dir = '~{0}'.format(username)

        # expand ~<username> into the full path of the home directory
        command = 'eval echo {0}'.format(tilde_home_dir)

        return self.run_command(command).strip()

    def get_user_log_path(self, username) -> str:
        """Builds the path to a student or faculty's event log file path on the
        server.

        :param username: username of the user
        :return: the path to the user's event log file
        """

        home_dir = self.get_user_home_dir(username)

        log_path = build_user_log_path(home_dir, username)

        return log_path


# Module-level interface instance. Someone must call connect() on this before
# it is used
server_interface = ServerInterface()
