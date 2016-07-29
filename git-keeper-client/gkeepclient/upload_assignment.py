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

from gkeepclient.assignment_uploader import AssignmentUploader
from gkeepclient.client_configuration import config, ClientConfigurationError
from gkeepclient.server_interface import server_interface, ServerInterfaceError
from gkeepclient.server_response_poller import ServerResponsePoller, \
    ServerResponseType
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.upload_directory import UploadDirectory


class UploadAssignmentError(GkeepException):
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
    except GkeepException as e:
        error = 'Error in {0}: {1}'.format(upload_dir_path, str(e))
        raise UploadAssignmentError(error)

    # parse the configuration file
    try:
        config.parse()
    except ClientConfigurationError as e:
        error = 'Configuration error:\n{0}'.format(str(e))
        raise UploadAssignmentError(error)

    try:
        server_interface.connect()
        if server_interface.assignment_exists(class_name,
                                              upload_dir.assignment_name):
            error = '{0} already exists'.format(upload_dir.assignment_name)
            raise UploadAssignmentError(error)
    except ServerInterfaceError as e:
        error = 'Server error: {0}'.format(e)
        raise UploadAssignmentError(error)

    print('uploading', upload_dir.assignment_name, 'in', class_name)

    # upload base_code, email.txt, and tests
    try:
        uploader = AssignmentUploader(upload_dir)
        uploader.upload_base_code()
        uploader.upload_email_txt()
        uploader.upload_tests()
    except GkeepException as e:
        error = 'Error uploading assignment: {0}'.format(str(e))
        raise UploadAssignmentError(error)

    poller = ServerResponsePoller('UPLOAD', response_timeout)

    payload = '{0} {1} {2}'.format(class_name, upload_dir.assignment_name,
                                   uploader.get_target_path())

    try:
        server_interface.log_event('UPLOAD', payload)
    except ServerInterfaceError as e:
        error = 'Error logging event: {0}'.format(str(e))
        raise UploadAssignmentError(error)

    try:
        for response in poller.response_generator():
            if response.response_type == ServerResponseType.SUCCESS:
                print('Assignment uploaded successfully')
            elif response.response_type == ServerResponseType.ERROR:
                print('Error uploading assignment:')
                print(response.message)
            elif response.response_type == ServerResponseType.WARNING:
                print(response.message)
            elif response.response_type == ServerResponseType.TIMEOUT:
                print('Server response timeout. Upload status unknown.')
    except ServerInterfaceError as e:
        error = 'Server communication error: {0}'.format(e)
        raise UploadAssignmentError(error)


if __name__ == '__main__':
    upload_assignment(sys.argv[1], sys.argv[2])
