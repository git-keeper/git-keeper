# Copyright 2016, 2017 Nathan Sommer and Ben Coleman
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


"""
Provides a globally accessible interface for interacting with a git-keeper
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

Example usage::

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

import csv
import json
import os
from shlex import quote
from time import time

from paramiko import SSHClient, AutoAddPolicy, SSHException

from gkeepclient.client_configuration import config
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.log_file import log_append_command
from gkeepcore.path_utils import user_log_path, gkeepd_to_faculty_log_path, \
    faculty_upload_dir_path, faculty_assignment_dir_path, \
    faculty_class_dir_path, assignment_published_file_path, \
    faculty_classes_dir_path, class_student_csv_path, faculty_info_path, \
    user_gitkeeper_path, user_gitkeeper_path_from_home_dir
from gkeepcore.student import Student
from gkeepcore.faculty_class_info import FacultyClassInfo


class ServerInterfaceError(GkeepException):
    """Raised by ServerInterface methods."""
    pass


class ServerCommandExitFailure(ServerInterfaceError):
    """Raised when a command has a non-zero exit code."""
    pass


class ServerInterface:
    """
    Provides methods for interacting with the server over a paramiko SSH
    connection.

    All methods raise a ServerInterfaceError exception on errors.
    """
    def __init__(self):
        """Create the object but do not connect to the server."""

        self._ssh_client = None
        self._sftp_client = None

        self._home_dir = None
        self._event_log_path = None

        self._info_cache = None
        self._info_cache_fetch_time = None

    def is_connected(self):
        """
        Determine if we're connected to the server.

        :return: True if connected, False otherwise
        """
        return self._ssh_client is not None

    def my_home_dir(self):
        """
        Get the home directory path on the server for the faculty member
        running the client.

        :return: home directory path on the server
        """
        return self._home_dir

    def connect(self):
        """
        Connect to the server.

        This method may only be called once.
        """

        # raise exception if we're already connected
        if self._ssh_client is not None:
            raise ServerInterfaceError('SSH connection already established')

        # connect the SSH client and open an SFTP client
        try:
            self._ssh_client = SSHClient()
            self._ssh_client.load_system_host_keys()
            self._ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            self._ssh_client.connect(hostname=config.server_host,
                                     username=config.server_username,
                                     port=config.server_ssh_port,
                                     timeout=5,
                                     compress=True)
            self._sftp_client = self._ssh_client.open_sftp()

            self._home_dir = self.user_home_dir(config.server_username)
            self._gitkeeper_path = \
                user_gitkeeper_path_from_home_dir(self._home_dir)
            self._event_log_path = self.me_to_gkeepd_log_path()
        except Exception as e:
            error = ('Error connecting to {0}: {1}'.format(config.server_host,
                                                           e))
            raise ServerInterfaceError(error)

    def run_command(self, command) -> str:
        """
        Run a shell command on the server.

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
        except Exception as e:
            error = ('Error running command "{0}" on the server: {1}'
                     .format(command, e))
            raise ServerInterfaceError(error)

        if exit_status != 0:
            raise ServerCommandExitFailure(output.decode('utf-8'))

        # output is bytes, we want a utf-8 string
        return output.decode('utf-8')

    def list_directory(self, path: str) -> list:
        """
        List the contents of a directory on the server.

        It is the responsibility of the caller to ensure the directory exists.

        :param path: directory path
        :return: list of file and directory names
        """

        try:
            directory_listing = self._sftp_client.listdir(path)
        except Exception as e:
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
        """
        Check if file_path is a file on the server.

        :param file_path:
        :return: True if file_path is a file, False if not
        """

        return self._bash_file_test('-f', file_path)

    def is_directory(self, dir_path: str) -> bool:
        """
        Check if dir_path is a directory on the server.

        :param dir_path:
        :return: True if dir_path is a directory, False if not
        """

        return self._bash_file_test('-d', dir_path)

    def copy_file(self, local_path: str, remote_path: str):
        """
        Copy a local file to the server.

        It is the responsibility of the caller to ensure the local path exists
        and that the remote path does not exist.

        The remote_path is the full destination file path. After a
        successful copy, local_path and remote_path will be the same file.

        :param local_path: path to the local file
        :param remote_path: full destination path on the server
        """

        try:
            self._sftp_client.put(local_path, remote_path)
        except Exception as e:
            raise ServerInterfaceError(e)

    def create_empty_file(self, remote_path: str):
        """
        Create an empty file on the server.

        It is the responsibility of the caller to ensure that the remote
        path does not exist.

        The remote_path is the full destination file path.

        :param remote_path: full path on the server
        """
        cmd = ['touch', remote_path]
        self.run_command(cmd)

    def create_directory(self, remote_path):
        """
        Create a new directory on the server.

        It is the responsibility of the caller to ensure the remote path does
        not already exist.

        :param remote_path: new path to create on the server
        """

        cmd = ['mkdir', '-p', remote_path]

        self.run_command(cmd)

    def copy_directory(self, source_path: str, dest_path: str):
        """
        Copy a local directory to the server.

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

        except Exception as e:
            raise ServerInterfaceError(e)

    def file_byte_count(self, file_path: str) -> int:
        """
        Get the number of bytes in a file on the server.

        It is the responsibility of the caller to ensure that the file exists.

        :param file_path: path to the file
        :return: number of bytes in the file
        """

        try:
            count = self._sftp_client.stat(file_path).st_size
        except Exception as e:
            raise ServerInterfaceError(e)

        return count

    def append_to_file(self, file_path, string):
        """
        Append a string to a file on the server, adding a trailing newline.

        :param file_path: the path to the file
        :param string: the string to append
        """

        try:
            with self._sftp_client.open(file_path, 'a') as f:
                print(string, file=f)
        except Exception as e:
            raise ServerInterfaceError(e)

    def log_event(self, event_type: str, payload: str):
        """
        Write an event to the faculty's log file on the server.

        :param event_type: type of the event
        :param payload: event information
        """

        command = log_append_command(self._event_log_path, event_type, payload)
        self.run_command(command)

    def read_file_bytes(self, file_path: str, seek_position=0) -> bytes:
        """
        Read a file from the server, optionally starting at a byte
        offset, and return the data as bytes.

        :param file_path: path to the file
        :param seek_position: byte offset at which to start reading
        :return: data from the file as bytes
        """

        try:
            with self._sftp_client.open(file_path) as f:
                f.seek(seek_position)
                data = f.read()
        except Exception as e:
            raise ServerInterfaceError(e)

        return data

    def read_file_text(self, file_path: str, seek_position=0) -> str:
        """
        Read a file from the server, optionally starting at a byte
        offset, and return the data as a string.

        :param file_path: path to the file
        :param seek_position: byte offset at which to start reading
        :return: data from the file as a string
        """

        data_bytes = self.read_file_bytes(file_path, seek_position)

        return data_bytes.decode('utf-8')

    def csv_rows(self, file_path: str) -> list:
        """
        Retrieve rows from a CSV file as a list of lists.

        :param file_path: path to the CSV file
        :return: list of rows, where each row is a list of strings
        """

        try:
            with self._sftp_client.open(file_path) as f:
                rows = list(csv.reader(f))
        except Exception as e:
            raise ServerInterfaceError(e)

        return rows

    def user_home_dir(self, username: str) -> str:
        """
        Find a user's home directory path on the server.

        :param username: the user whose home directory we want
        :return: the home directory path
        """

        tilde_home_dir = '~{0}'.format(username)

        # expand ~<username> into the full path of the home directory
        command = 'eval echo {0}'.format(tilde_home_dir)

        return self.run_command(command).strip()

    def users_home_dirs(self, usernames: list) -> dict:
        """
        Find multiple users' home directory paths on the server.

        :param usernames: the users whose home directory we want
        :return: dictionary of home directory paths indexed by usernames
        """

        tilde_home_dirs = ''

        for username in usernames:
            tilde_home_dirs += '~{0} '.format(username)

        # expand each ~<username> into the full paths of the home directories
        command = 'eval echo {0}'.format(tilde_home_dirs)

        home_dirs = self.run_command(command).strip().split(' ')

        return dict(zip(usernames, home_dirs))

    def me_to_gkeepd_log_path(self) -> str:
        """
        Build the path to a student or faculty's event log file path on the
        server.

        :return: the path to the faculty user's event log file
        """

        log_path = user_log_path(self._gitkeeper_path, config.server_username)

        return log_path

    def gkeepd_to_me_log_path(self) -> str:
        """
        Build the path to gkeepd's log file for communicating to the faculty
        member.

        :return: gkeepd log path
        """

        log_path = gkeepd_to_faculty_log_path(self._gitkeeper_path)

        return log_path

    def upload_dir_path(self):
        """
        Build the path to the faculty's upload directory on the server.

        :return: upload directory path
        """

        return faculty_upload_dir_path(self._gitkeeper_path)

    def create_new_upload_dir(self):
        """
        Create a directory on the server to upload to and return the path.

        :return: path to the newly created directory on the server
        """

        new_upload_path = os.path.join(self.upload_dir_path(), str(time()))

        self.create_directory(new_upload_path)

        return new_upload_path

    def class_exists(self, class_name: str) -> bool:
        """
        Determine if a class exists on the server.

        :param class_name:
        :return: True if the class exists, False otherwise
        """

        path = faculty_class_dir_path(class_name, self._gitkeeper_path)
        return self.is_directory(path)

    def is_open(self, class_name: str) -> bool:
        """
        Determine if a class is open.

        :param class_name: name of the class
        :return: True if the class is open, False i fnot
        """

        return self.get_info().is_open(class_name)

    def assignment_exists(self, class_name: str, assignment_name: str) -> bool:
        """
        Determine if an assignment exists on the server.

        :param class_name: name of the class that the assignment belongs to
        :param assignment_name: name of the assignment
        :return: True if the assignment exists, False otherwise
        """

        path = faculty_assignment_dir_path(class_name, assignment_name,
                                           self._gitkeeper_path)
        return self.is_directory(path)

    def assignment_published(self, class_name: str,
                             assignment_name: str) -> bool:
        """
        Determine if an assignment is published.

        :param class_name: name of the class that the assignment belongs to
        :param assignment_name: name of the assignment
        :return: True if the assignment is published, False otherwise
        """

        return self.get_info().is_published(class_name, assignment_name)

    def assignment_disabled(self, class_name: str,
                            assignment_name: str) -> bool:
        """
        Determine if an assignment is disabled.

        :param class_name: name of the class that the assignment belongs to
        :param assignment_name: name of the assignment
        :return: True if the assignment is disabled, False otherwise
        """

        return self.get_info().is_disabled(class_name, assignment_name)

    def get_classes(self):
        """
        Get a list of the names of the classes for this faculty member.

        :return: list of class names
        """

        classes_path = faculty_classes_dir_path(self._gitkeeper_path)

        directory_items = self.list_directory(classes_path)

        classes = []

        for item in sorted(directory_items):
            item_path = os.path.join(classes_path, item)

            if self.is_directory(item_path):
                classes.append(item)

        return classes

    def get_assignment_names(self, class_name: str):
        """
        Get a list of the names of assignments for a class.

        :param class_name: name of the class
        :return: list of assignment names
        """

        class_path = faculty_class_dir_path(class_name, self._gitkeeper_path)

        directory_items = self.list_directory(class_path)

        assignment_names = []

        for item in sorted(directory_items):
            item_path = os.path.join(class_path, item)

            if self.is_directory(item_path):
                assignment_names.append(item)

        return assignment_names

    def get_assignment_info(self, class_name: str) -> list:
        """
        Get a list of the names of assignments for a class, and whether or not
        each assignment is published.

        Each entry in the list is a tuple containing (name, published) where
        published is a boolean value which is True if the assignment is
        published and False if it is not.

        :param class_name: name of the class
        :return: list of assignment information
        """

        assignments_info = []

        for assignment_name in self.get_info().assignment_list(class_name):
            published = self.get_info().is_published(class_name,
                                                     assignment_name)
            assignments_info.append((assignment_name, published))

        return assignments_info

    def get_students(self, class_name: str) -> list:
        """
        Get a list of Student objects from a class.

        :param class_name: name of the class
        :return: list of Student objects
        """
        students = []

        csv_path = class_student_csv_path(class_name, self._gitkeeper_path)

        if not self.is_file(csv_path):
            return []

        rows = self.csv_rows(csv_path)

        for row in rows:
            if len(row) != 0:
                students.append(Student.from_csv_row(row))

        return students

    def get_info(self, freshness_threshold=5) -> FacultyClassInfo:
        """
        Fetch info from the server and return it as an FacultyClassInfo object.

        :param freshness_threshold: If the number of seconds since the last
         fetch is smaller than freshness_threshold, the last cached fetch is
         returned. If freshness_threshold is None, the cached version will be
         used regardless of freshness.
        :return: FacultyClassInfo object
        """

        # If the cache exists and is fresh enough, return the cached info
        if self._info_cache_fetch_time is not None:
            if freshness_threshold is None:
                return self._info_cache
            else:
                freshness = time() - self._info_cache_fetch_time
                if freshness < freshness_threshold:
                    return self._info_cache

        info_path = faculty_info_path(self._gitkeeper_path)

        # Get the contents of the last file in the directory, or an empty
        # string if the directory is empty.
        command = \
            'echo | cat {0}/`ls {0} | tail -1`'.format(info_path).rstrip()

        try:
            info_json = self.run_command(command)
            info = json.loads(info_json)
        except Exception as e:
            raise ServerInterfaceError('Error loading info from JSON: {0}'
                                       .format(e))

        self._info_cache = FacultyClassInfo(info)
        self._info_cache_fetch_time = time()

        return self._info_cache


# Module-level interface instance. Someone must call connect() on this before
# it is used
server_interface = ServerInterface()
