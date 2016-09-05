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


"""Provides functions that request action from the server."""


import os
import sys

from gkeepcore.valid_names import validate_class_name, validate_assignment_name

from gkeepclient.assignment_uploader import AssignmentUploader
from gkeepclient.client_configuration import config
from gkeepclient.client_function_decorators import config_parsed, \
    server_interface_connected, class_does_not_exist, class_exists, \
    assignment_exists, assignment_not_published, assignment_does_not_exist
from gkeepclient.server_interface import server_interface
from gkeepclient.server_response_poller import communicate_event
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.student import students_from_csv
from gkeepcore.upload_directory import UploadDirectory


@config_parsed
@server_interface_connected
@class_does_not_exist
def class_add(class_name: str, csv_file_path: str):
    """
    Add a class on the server.

    :param class_name: name of the class
    :param csv_file_path: path to the CSV file of students
    """

    validate_class_name(class_name)

    if not os.path.isfile(csv_file_path):
        raise GkeepException('{0} does not exist'.format(csv_file_path))

    try:
        students = students_from_csv(LocalCSVReader(csv_file_path))
    except GkeepException as e:
        sys.exit(e)

    print('Adding class {0} with the following students:'.format(class_name))

    for student in students:
        print(student)

    # create directory and upload CSV
    upload_dir_path = server_interface.create_new_upload_dir()
    remote_csv_file_path = os.path.join(upload_dir_path, 'students.csv')

    server_interface.copy_file(csv_file_path, remote_csv_file_path)

    print('CSV file uploaded')

    payload = '{0} {1}'.format(class_name, remote_csv_file_path)

    communicate_event('CLASS_ADD', payload,
                      success_message='Class added successfully',
                      error_message='Error adding class:',
                      timeout_message='Server response timeout. '
                                      'Class add status unknown')


@config_parsed
@server_interface_connected
@class_exists
def class_modify(class_name: str, csv_file_path: str):
    """
    Modify a class on the server.

    :param class_name: name of the class
    :param csv_file_path: path to CSV file containing students
    """

    if not os.path.isfile(csv_file_path):
        raise GkeepException('{0} does not exist'.format(csv_file_path))

    try:
        students = students_from_csv(LocalCSVReader(csv_file_path))
    except GkeepException as e:
        sys.exit(e)

    print('Modifying class {0} with the following students:'
          .format(class_name))

    for student in students:
        print(student)

    # create directory and upload CSV
    upload_dir_path = server_interface.create_new_upload_dir()
    remote_csv_file_path = os.path.join(upload_dir_path, 'students.csv')

    server_interface.copy_file(csv_file_path, remote_csv_file_path)

    print('CSV file uploaded')

    payload = '{0} {1}'.format(class_name, remote_csv_file_path)

    communicate_event('CLASS_MODIFY', payload,
                      success_message='Class modified successfully',
                      error_message='Error modifying class:',
                      timeout_message='Server response timeout. '
                                      'Class modify status unknown')


@config_parsed
@server_interface_connected
@class_exists
@assignment_exists
def delete_assignment(class_name: str, assignment_name: str,
                      response_timeout=20):
    """
    Delete an assignment on the server.

    Raises DeleteAssignmentError if anything goes wrong.

    :param class_name: name of the class the assignment belongs to
    :param assignment_name: name of the assignment
    :param response_timeout: seconds to wait for server response
    """

    print('Deleting assignment', assignment_name, 'in class', class_name)

    payload = '{0} {1}'.format(class_name, assignment_name)

    communicate_event('DELETE', payload, response_timeout=response_timeout,
                      success_message='Assignment deleted successfully',
                      error_message='Error deleting response:',
                      timeout_message='Server response timeout. '
                                      'Delete status unknown')


@config_parsed
@server_interface_connected
@class_exists
@assignment_exists
@assignment_not_published
def publish_assignment(class_name: str, assignment_name: str):
    """
    Publish an assignment on the server.

    The server will send emails to all students with clone URLs.

    :param class_name: name of the class the assignment belongs to
    :param assignment_name: name of the assignment
    """

    print('Publishing assignment', assignment_name, 'in class', class_name)

    payload = '{0} {1}'.format(class_name, assignment_name)

    communicate_event('PUBLISH', payload,
                      success_message='Assignment successfully published',
                      error_message='Error publishing assignment:',
                      timeout_message='Server response timeout. '
                                      'Publish status unknown.')


@config_parsed
@server_interface_connected
@class_exists
def update_assignment(class_name: str, upload_dir_path: str,
                      items=('base_code', 'email', 'tests'),
                      response_timeout=20):
    """
    Update an assignment on the server

    The name of the assignment will be the name of the upload_dir_path.

    upload_dir_path must contain the following:

        base_code/
        email.txt
        tests/
            action.sh

    Copies items to the server, writes a log entry to notify the server of the
    upload, and waits for a logged confirmation of success or error from the
    server.

    Raises UpdateAssignmentError if anything goes wrong.

    :param class_name: name of the class the assignment belongs to
    :param upload_dir_path: path to the assignment
    :param items: tuple or list of items to update
    :param response_timeout: seconds to wait for server response
    """

    # expand any special path components, strip trailing slash
    upload_dir_path = os.path.abspath(upload_dir_path)

    # build an UploadDirectory object, ensuring all files are in place
    try:
        upload_dir = UploadDirectory(upload_dir_path)
    except GkeepException as e:
        error = 'Error in {0}: {1}'.format(upload_dir_path, str(e))
        raise GkeepException(error)

    if not server_interface.assignment_exists(class_name,
                                              upload_dir.assignment_name):
        error = ('Assignment {0} does not exist in class {1}'
                 .format(upload_dir.assignment_name, class_name))
        raise GkeepException(error)

    is_published =\
        server_interface.assignment_published(class_name,
                                              upload_dir.assignment_name)

    if is_published and ('base_code' in items or 'email' in items):
        error = 'Assignment is already published, only tests may be updated.'
        raise GkeepException(error)

    print('updating', upload_dir.assignment_name, 'in', class_name)

    # upload base_code, email.txt, and tests
    try:
        uploader = AssignmentUploader(upload_dir)
        if 'base_code' in items:
            uploader.upload_base_code()
        if 'email' in items:
            uploader.upload_email_txt()
        if 'tests' in items:
            uploader.upload_tests()
    except GkeepException as e:
        error = 'Error uploading assignment updates: {0}'.format(str(e))
        raise GkeepException(error)

    payload = '{0} {1} {2}'.format(class_name, upload_dir.assignment_name,
                                   uploader.get_target_path())

    communicate_event('UPDATE', payload, response_timeout=response_timeout,
                      success_message='Assignment updated successfully',
                      error_message='Error updating assignment:',
                      timeout_message='Server response timeout. '
                                      'Update status unknown')


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

    validate_assignment_name(upload_dir.assignment_name)

    if server_interface.assignment_exists(class_name,
                                          upload_dir.assignment_name):
        error = ('Assignment {0} already exists in class {1}'
                 .format(upload_dir.assignment_name, class_name))
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
