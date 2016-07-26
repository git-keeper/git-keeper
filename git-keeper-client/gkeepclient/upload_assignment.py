#!/usr/bin/env python3

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

"""Provides a function for uploading an assignment to the server."""

import os
import sys
from time import time, sleep

from gkeepclient.server_interface import server_interface, ServerInterfaceError
from gkeepclient.client_configuration import config, ClientConfigurationError
from gkeepclient.server_log_file_reader import ServerLogFileReader
from gkeepcore.upload_directory import UploadDirectory, UploadDirectoryError


class UploadAssignmentError(Exception):
    """Raised if there are any errors uploading the assignment."""
    pass


def upload_assignment(class_name: str, upload_dir_path: str,
                      response_timeout=20):
    """
    Upload an assignment to the server.

    The name of the assignment will be the name of the upload_dir_path.

    upload_dir_path must contain the following:

        base_code/
        email.txt
        tests/
            action.sh

    Copies files to the server, writes a log entry to notify the server of the
    upload, and waits for a logged confirmation of success or error from the
    server.

    Raises UploadAssignmentError if anything goes wrong.

    :param class_name: name of the class the assignment belongs to
    :param upload_dir_path: path to the assignment
    :param response_timeout: seconds to wait for server response
    """

    # expand any special path components, strip trailing slash
    upload_dir_path = os.path.abspath(upload_dir_path)

    # build an UploadDirectory object, ensuring all files are in place
    try:
        upload_dir = UploadDirectory(upload_dir_path)
    except UploadDirectoryError as e:
        error = 'Error in {0}: {1}'.format(upload_dir_path, str(e))
        raise UploadAssignmentError(error)

    # parse the configuration file
    try:
        config.parse()
    except ClientConfigurationError as e:
        error = 'Configuration error:\n{0}'.format(str(e))
        raise UploadAssignmentError(error)

    # connect to the server
    try:
        server_interface.connect()
    except ServerInterfaceError as e:
        error = 'Error connecting to the server:\n{0}'.format(str(e))
        raise UploadAssignmentError(error)

    # path that the assignment will eventually end up in
    assignment_path =\
        server_interface.my_assignment_dir_path(class_name,
                                                upload_dir.assignment_name)

    # check to see if the assignment path already exists
    if server_interface.is_directory(assignment_path):
        error = '{0} already exists'.format(upload_dir.assignment_name)
        raise UploadAssignmentError(error)

    # directory that we'll upload to on the server, the server will then
    # move the files to their final location
    upload_target = os.path.join(server_interface.upload_dir_path(),
                                 str(time()), class_name,
                                 upload_dir.assignment_name)

    print('uploading', upload_dir_path, 'to', upload_target)

    # create the directory to upload to
    try:
        server_interface.create_directory(upload_target)
    except ServerInterfaceError as e:
        error = 'Error creating remote upload directory: {0}'.format(str(e))
        raise UploadAssignmentError(error)

    # copy base_code, email.txt, and tests
    try:
        server_interface.copy_directory(upload_dir.base_code_path,
                                        os.path.join(upload_target,
                                                     'base_code'))
        server_interface.copy_file(upload_dir.email_path,
                                   os.path.join(upload_target, 'email.txt'))
        server_interface.copy_directory(upload_dir.tests_path,
                                        os.path.join(upload_target, 'tests'))
    except ServerInterfaceError as e:
        error = 'Error uploading assignment: {0}'.format(str(e))
        raise UploadAssignmentError(error)

    # start watching server log for the response. done before writing to our
    # log so we don't miss the response due to latency
    gkeepd_log_path = server_interface.gkeepd_to_me_log_path()
    reader = ServerLogFileReader(gkeepd_log_path)

    # log the event
    try:
        server_interface.log_event('UPLOAD', upload_target)
    except ServerInterfaceError as e:
        error = 'Error logging event: {0}'.format(str(e))
        raise UploadAssignmentError(error)

    print('Waiting for server confirmation ...', end='')
    sys.stdout.flush()

    keep_polling = True
    poll_start_time = time()

    # poll for the server's response
    while keep_polling:
        try:
            while not reader.has_new_lines() and keep_polling:
                print('.', end='')
                sys.stdout.flush()
                sleep(1)
                if time() > poll_start_time + response_timeout:
                    keep_polling = False
                    print('\nTimed out waiting for response. '
                          'Upload status is unclear.')

            for line in reader.get_new_lines():
                if line.endswith('UPLOAD_SUCCESS ' + upload_target):
                    keep_polling = False
                    print('\nAssignment uploaded successfully')
                    break
                if 'UPLOAD_ERROR ' + upload_target in line:
                    keep_polling = False
                    print(line)
                    break
        except ServerInterfaceError as e:
            error = 'Error reading server log file: {0}'.format(str(e))
            raise UploadAssignmentError(error)

if __name__ == '__main__':
    upload_assignment(sys.argv[1], sys.argv[2])
