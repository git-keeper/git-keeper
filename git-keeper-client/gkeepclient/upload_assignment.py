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
from gkeepclient.client_function_decorators import config_parsed, \
    server_interface_connected, class_exists
from gkeepclient.server_response_poller import communicate_event
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.upload_directory import UploadDirectory


@config_parsed
@server_interface_connected
@class_exists
def upload_assignment(class_name: str, upload_dir_path: str):
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

    :param class_name: name of the class the assignment belongs to
    :param upload_dir_path: path to the assignment
    """

    # expand any special path components, strip trailing slash
    upload_dir_path = os.path.abspath(upload_dir_path)

    # build an UploadDirectory object, ensuring all files are in place
    try:
        upload_dir = UploadDirectory(upload_dir_path)
    except GkeepException as e:
        error = 'Error in {0}: {1}'.format(upload_dir_path, str(e))
        raise GkeepException(error)

    print('uploading', upload_dir.assignment_name, 'in', class_name)

    # upload base_code, email.txt, and tests
    try:
        uploader = AssignmentUploader(upload_dir)
        uploader.upload_base_code()
        uploader.upload_email_txt()
        uploader.upload_tests()
    except GkeepException as e:
        error = 'Error uploading assignment: {0}'.format(str(e))
        raise GkeepException(error)

    payload = '{0} {1} {2}'.format(class_name, upload_dir.assignment_name,
                                   uploader.get_target_path())

    communicate_event('UPLOAD', payload,
                      success_message='Assignment uploaded successfully',
                      error_message='Error uploading assignment:',
                      timeout_message='Server response timeout. '
                                      'Upload status unknown')


if __name__ == '__main__':
    upload_assignment(sys.argv[1], sys.argv[2])
