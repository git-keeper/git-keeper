# Copyright 2016, 2018 Nathan Sommer and Ben Coleman
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
import json
import os
from tempfile import TemporaryDirectory

from gkeepclient.client_configuration import config
from gkeepclient.duration_to_string import duration_to_string
from gkeepclient.text_ui import confirmation
from gkeepcore.valid_names import validate_class_name, validate_assignment_name
from gkeepclient.assignment_uploader import AssignmentUploader
from gkeepclient.client_function_decorators import config_parsed, \
    server_interface_connected, class_does_not_exist, class_exists, \
    assignment_exists, assignment_not_published, assignment_not_disabled, \
    class_is_open
from gkeepclient.server_interface import server_interface
from gkeepclient.server_response_poller import communicate_event, ServerResponsePoller, ServerResponseType, \
    ServerResponseWarning, ServerResponseError
from gkeepclient.version import __version__
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.local_csv_files import LocalCSVReader, LocalCSVWriter
from gkeepcore.student import students_from_csv
from gkeepcore.upload_directory import UploadDirectory


@config_parsed
@server_interface_connected
@class_does_not_exist
def class_add(class_name: str, csv_file_path: str, yes: bool):
    """
    Add a class on the server.

    :param class_name: name of the class
    :param csv_file_path: path to the CSV file of students
           or None if the user is creating an empty class
    :param yes: if True, will automatically answer yes to confirmation prompts
    """

    validate_class_name(class_name)

    if csv_file_path is not None:
        if not os.path.isfile(csv_file_path):
            raise GkeepException('{0} does not exist'.format(csv_file_path))

        students = students_from_csv(LocalCSVReader(csv_file_path))
    else:
        students = []

    if len(students) > 0:
        print('Class {0} will be added with the following students:'
              .format(class_name))

        for student in students:
            print(student)
    else:
        print('Class {} will be added with no students.'.format(class_name))
        print('You may add students at a later time using gkeep modify.')

    if not yes and not confirmation('Proceed?', 'y'):
        raise GkeepException('Aborting')

    communicate_event('CLASS_ADD', class_name,
                      success_message='Class added successfully',
                      error_message='Error adding class: ',
                      timeout_message='Server response timeout. '
                                      'Class add status unknown')

    if len(students) == 0:
        return

    upload_dir_path = server_interface.create_new_upload_dir()

    remote_csv_file_path = os.path.join(upload_dir_path, 'students.csv')

    if csv_file_path is None:
        server_interface.create_empty_file(remote_csv_file_path)
    else:
        server_interface.copy_file(csv_file_path, remote_csv_file_path)

    print('CSV file uploaded')

    payload = '{0} {1}'.format(class_name, remote_csv_file_path)

    communicate_event('STUDENTS_ADD', payload,
                      success_message='Students added successfully',
                      error_message='Error adding students: ',
                      timeout_message='Server response timeout. '
                                      'Students add status unknown')


@config_parsed
@server_interface_connected
@class_exists
@class_is_open
def class_modify(class_name: str, csv_file_path: str, yes: bool):
    """
    Modify a class on the server based on the contents of a CSV file.

    The following types of changes are detected, and separate requests are
    made to the server to carry out each type of change:
    - Adding new students to the class
    - Removing students from the class
    - Renaming students in the class

    :param class_name: name of the class
    :param csv_file_path: path to CSV file containing students
    :param yes: if True, will automatically answer yes to confirmation prompts
    """

    if not os.path.isfile(csv_file_path):
        raise GkeepException('{0} does not exist'.format(csv_file_path))

    students = students_from_csv(LocalCSVReader(csv_file_path))
    existing_students = server_interface.get_info().class_students(class_name)

    print('Modifying class {0}'.format(class_name))

    students_by_email = {}
    existing_students_by_email = {}

    for student in students:
        students_by_email[student.email_address] = student

    for student in existing_students.values():
        existing_students_by_email[student['email_address']] = student

    email_addresses = set(students_by_email.keys())
    existing_email_addresses = set(existing_students_by_email.keys())

    new_email_addresses = email_addresses - existing_email_addresses
    remove_email_addresses = existing_email_addresses - email_addresses
    same_email_addresses = email_addresses & existing_email_addresses

    # This set will store (<first name>, <last name>, <email address>) tuples
    # representing the students whose names should be changed
    new_first_last_email_set = set()

    for email_address in same_email_addresses:
        old_first = existing_students_by_email[email_address]['first']
        old_last = existing_students_by_email[email_address]['last']

        new_first = students_by_email[email_address].first_name
        new_last = students_by_email[email_address].last_name

        if new_first != old_first or new_last != old_last:
            new_first_last_email_set.add((
                new_first,
                new_last,
                email_address
            ))

    changes_exist = False

    # These lists will store the rows that will be written to the CSV files
    # that will indicate which students should be added, removed, or
    # renamed
    new_student_rows = []
    remove_student_rows = []
    update_name_rows = []

    # Populate the lists and print what will change

    if len(new_email_addresses) > 0:
        changes_exist = True
        print('\nThe following students will be added to the class:')
        for email_address in new_email_addresses:
            last_name = students_by_email[email_address].last_name
            first_name = students_by_email[email_address].first_name
            print('{}, {}, {}'.format(last_name, first_name, email_address))
            new_student_rows.append((last_name, first_name, email_address))

    if len(remove_email_addresses) > 0:
        changes_exist = True
        print('\nThe following students will be removed from the class:')
        for email_address in remove_email_addresses:
            last_name = existing_students_by_email[email_address]['last']
            first_name = existing_students_by_email[email_address]['first']
            print('{}, {}, {}'.format(last_name, first_name, email_address))
            remove_student_rows.append((last_name, first_name, email_address))

    if len(new_first_last_email_set) > 0:
        changes_exist = True
        print('\nThe following student names will be updated:')
        for first_name, last_name, email_address in new_first_last_email_set:
            old_first = existing_students_by_email[email_address]['first']
            old_last = existing_students_by_email[email_address]['last']
            print('{}, {} -> {}, {}'.format(old_last, old_first, last_name,
                                            first_name))
            update_name_rows.append((last_name, first_name, email_address))

    if not changes_exist:
        raise GkeepException('There are no changes to be made')

    if not yes and not confirmation('\nProceed?', 'y'):
        raise GkeepException('Aborting')

    temp_dir = TemporaryDirectory()

    if len(new_student_rows) > 0:
        add_csv_path = os.path.join(temp_dir.name, 'add.csv')
        writer = LocalCSVWriter(add_csv_path)
        writer.write_rows(new_student_rows)

        upload_dir_path = server_interface.create_new_upload_dir()
        remote_csv_file_path = os.path.join(upload_dir_path, 'add.csv')

        server_interface.copy_file(add_csv_path, remote_csv_file_path)

        payload = '{0} {1}'.format(class_name, remote_csv_file_path)

        communicate_event('STUDENTS_ADD', payload,
                          success_message='Students added successfully',
                          error_message='Error adding students: ',
                          timeout_message='Server response timeout. '
                                          'Class modify status unknown')

    if len(remove_student_rows) > 0:
        remove_csv_path = os.path.join(temp_dir.name, 'remove.csv')
        writer = LocalCSVWriter(remove_csv_path)
        writer.write_rows(remove_student_rows)

        upload_dir_path = server_interface.create_new_upload_dir()
        remote_csv_file_path = os.path.join(upload_dir_path, 'remove.csv')

        server_interface.copy_file(remove_csv_path, remote_csv_file_path)

        payload = '{0} {1}'.format(class_name, remote_csv_file_path)

        communicate_event('STUDENTS_REMOVE', payload,
                          success_message='Students removed successfully',
                          error_message='Error removing students: ',
                          timeout_message='Server response timeout. '
                                          'Class modify status unknown')

    if len(update_name_rows) > 0:
        update_csv_path = os.path.join(temp_dir.name, 'update.csv')
        writer = LocalCSVWriter(update_csv_path)
        writer.write_rows(update_name_rows)

        upload_dir_path = server_interface.create_new_upload_dir()
        remote_csv_file_path = os.path.join(upload_dir_path, 'update.csv')

        server_interface.copy_file(update_csv_path, remote_csv_file_path)

        payload = '{0} {1}'.format(class_name, remote_csv_file_path)

        communicate_event('STUDENTS_MODIFY', payload,
                          success_message='Students modified successfully',
                          error_message='Error modifying students: ',
                          timeout_message='Server response timeout. '
                                          'Class modify status unknown')


@config_parsed
@server_interface_connected
@class_exists
def update_status(class_name: str, status: str):
    """
    Update the status of a class.

    :param class_name: name of the class
    :param status: new status for the class, 'open' or 'closed'
    """

    is_open = server_interface.is_open(class_name)

    if status == 'open' and is_open:
        raise GkeepException('{} is already open'.format(class_name))
    elif status == 'closed' and not is_open:
        raise GkeepException('{} is already closed'.format(class_name))

    payload = '{0} {1}'.format(class_name, status)

    communicate_event('CLASS_STATUS', payload,
                      success_message='Status updated successfully',
                      error_message='Error updating status: ',
                      timeout_message='Server response timeout. '
                                      'Status of status update unknown')


@config_parsed
@server_interface_connected
def add_faculty(last_name: str, first_name: str, email_address: str,
                admin=False):
    """
    Add a new faculty user.

    :param admin:
    :param email_address:
    :param first_name:
    :param last_name:
    """

    faculty_dictionary = {
        'last_name': last_name,
        'first_name': first_name,
        'email_address': email_address,
        'admin': admin,
    }

    payload = json.dumps(faculty_dictionary)

    communicate_event('FACULTY_ADD', payload,
                      success_message='Faculty added successfully',
                      error_message='Error adding faculty: ',
                      timeout_message='Server response timeout. '
                                      'Status of adding faculty unknown')


@config_parsed
@server_interface_connected
def admin_promote(email_address: str):
    """
    Promote a faculty user to admin

    :param email_address: email address of the faculty user
    """

    print('Attempting to promote {} to admin'.format(email_address))

    communicate_event('ADMIN_PROMOTE', email_address,
                      success_message='User promoted successfully',
                      error_message='Error promoting user: ',
                      timeout_message='Server response timeout. '
                                      'Status of promoting user unknown')


@config_parsed
@server_interface_connected
def admin_demote(email_address: str):
    """
    Remove admin status for a faculty user

    :param email_address: email address of the faculty user
    """

    print('Attempting to demote {} from admin'.format(email_address))

    communicate_event('ADMIN_DEMOTE', email_address,
                      success_message='User demoted successfully',
                      error_message='Error demoting user: ',
                      timeout_message='Server response timeout. '
                                      'Status of demoting user unknown')


@config_parsed
@server_interface_connected
@class_exists
@class_is_open
@assignment_exists
@assignment_not_disabled
def delete_assignment(class_name: str, assignment_name: str,
                      yes: bool):
    """
    Delete an assignment on the server.

    Raises DeleteAssignmentError if anything goes wrong.

    :param class_name: name of the class the assignment belongs to
    :param assignment_name: name of the assignment
    :param yes: if True, will automatically answer yes to confirmation prompts
    """

    if server_interface.get_info().is_published(class_name, assignment_name):
        error = ('Assignment {} is published and cannot be deleted.\n'
                 'Use gkeep disable if you wish to disable this assignment.'
                 .format(assignment_name))
        raise GkeepException(error)

    print('Deleting assignment', assignment_name, 'in class', class_name)

    if not yes and not confirmation('Proceed?', 'y'):
        raise GkeepException('Aborting')

    payload = '{0} {1}'.format(class_name, assignment_name)

    communicate_event('DELETE', payload,
                      success_message='Assignment deleted successfully',
                      error_message='Error deleting response: ',
                      timeout_message='Server response timeout. '
                                      'Delete status unknown')


@config_parsed
@server_interface_connected
@class_exists
@class_is_open
@assignment_exists
@assignment_not_disabled
def disable_assignment(class_name: str, assignment_name: str,
                       yes: bool):
    """
    Disable a published assignment on the server.

    Raises a GkeepException if anything goes wrong.

    :param class_name: name of the class the assignment belongs to
    :param assignment_name: name of the assignment
    :param yes: if True, will automatically answer yes to confirmation prompts
    """

    if not server_interface.assignment_published(class_name, assignment_name):
        error = ('Assignment {} is not published and cannot be disabled.\n'
                 'Use gkeep delete if you wish to delete this assignment.'
                 .format(assignment_name))
        raise GkeepException(error)

    print('Disabling assignment {} in class {}. This cannot be undone.'
          .format(assignment_name, class_name))
    print('Students will be notified that the assignment has been disabled.')
    print('The action script will no longer be run on submissions to this ')
    print('assignment.  Instead, students will receive an email stating')
    print('that the assignment is disabled.')

    if not yes and not confirmation('Proceed?', 'y'):
        raise GkeepException('Aborting')

    payload = '{0} {1}'.format(class_name, assignment_name)

    communicate_event('DISABLE', payload,
                      success_message='Assignment disabled successfully',
                      error_message='Error disabling assignment: ',
                      timeout_message='Server response timeout. '
                                      'Disable status unknown')


@config_parsed
@server_interface_connected
@class_exists
@class_is_open
@assignment_exists
@assignment_not_disabled
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
                      error_message='Error publishing assignment: ',
                      timeout_message='Server response timeout. '
                                      'Publish status unknown.')


@config_parsed
@server_interface_connected
@class_exists
@class_is_open
@assignment_exists
@assignment_not_disabled
def trigger_tests(class_name: str, assignment_name: str,
                  student_usernames: list, yes: bool, response_timeout=20):
    """
    Trigger tests to be run on the server.

    The server will run tests on the assignment for all the students in the
    student_usernames list, or all students if student_usernames is empty

    :param class_name: name of the class the assignment belongs to
    :param assignment_name: name of the assignment
    :param student_usernames: list of student usernames for whom tests should
    be run, or an empty list for all students
    :param yes: if True, will automatically answer yes to confirmation prompts
    :param response_timeout: seconds to wait for server response
    """

    published = server_interface.assignment_published(class_name,
                                                      assignment_name)
    faculty_only = (len(student_usernames) == 1 and
                    config.server_username in student_usernames)

    if not published and not faculty_only:
        error = ('This assignment is not published.\n'
                 'Unpublished assignments may only be triggered for the '
                 'faculty account')
        raise GkeepException(error)

    class_student_usernames = \
        server_interface.get_info().student_list(class_name)

    if len(student_usernames) == 0:
        student_usernames = class_student_usernames
    else:
        for username in student_usernames:
            if (username not in class_student_usernames and
                    username != config.server_username):
                error = ('No student {0} in {1}'.format(username, class_name))
                raise GkeepException(error)

    print('Triggering tests for', assignment_name, 'in class', class_name,
          'for the following students:')

    for username in student_usernames:
        print(username)

    if not yes and not confirmation('Proceed?', 'y'):
        raise GkeepException('Aborting')

    payload = '{0} {1}'.format(class_name, assignment_name)

    for username in student_usernames:
        payload += ' {0}'.format(username)

    communicate_event('TRIGGER', payload, response_timeout=response_timeout,
                      success_message='Tests triggered successfully',
                      error_message='Error triggering tests: ',
                      timeout_message='Server response timeout. '
                                      'Triggering status unknown')


@config_parsed
@server_interface_connected
@class_exists
@class_is_open
@assignment_not_disabled
def update_assignment(class_name: str, upload_dir_path: str,
                      items=('base_code', 'email', 'tests', 'config'),
                      response_timeout=20):
    """
    Update an assignment on the server

    The name of the assignment will be the name of the upload_dir_path.

    upload_dir_path must contain the following:

        base_code/
        email.txt
        tests/
            action.sh or action.py

    Copies items to the server, writes a log entry to notify the server of the
    upload, and waits for a logged confirmation of success or error from the
    server.

    Raises a GkeepException if anything goes wrong.

    :param class_name: name of the class the assignment belongs to
    :param upload_dir_path: path to the assignment
    :param items: tuple or list of items to update
    :param response_timeout: seconds to wait for server response
    """

    valid_items = {'base_code', 'email', 'tests', 'config'}

    for item in items:
        if item not in valid_items:
            error = '{} is not a valid update item'.format(item)
            raise GkeepException(error)

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
        error = 'Assignment is already published, only tests or config may be updated.'
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
        if 'config' in items:
            uploader.upload_config()
    except GkeepException as e:
        error = 'Error uploading assignment updates: {0}'.format(str(e))
        raise GkeepException(error)

    payload = '{0} {1} {2}'.format(class_name, upload_dir.assignment_name,
                                   uploader.get_target_path())

    communicate_event('UPDATE', payload, response_timeout=response_timeout,
                      success_message='Assignment updated successfully',
                      error_message='Error updating assignment: ',
                      timeout_message='Server response timeout. '
                                      'Update status unknown')


@config_parsed
@server_interface_connected
@class_exists
@class_is_open
def upload_assignment(class_name: str, upload_dir_path: str):
    """
    Upload an assignment to the server.

    The name of the assignment will be the name of the upload_dir_path.

    upload_dir_path must contain the following:

        base_code/
        email.txt
        tests/
            action.sh

    The following file is optional:

        assignment.cfg

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

    if not os.path.isfile(upload_dir.config_path):
        print('NOTE: There is no assignment.cfg file for this assignment.')
        print('      Tests for this assignment will be run using the '
              'server\'s default environment.')

    if server_interface.assignment_exists(class_name,
                                          upload_dir.assignment_name):
        error = ('Assignment {0} already exists in class {1}'
                 .format(upload_dir.assignment_name, class_name))
        raise GkeepException(error)

    print('uploading', upload_dir.assignment_name, 'in', class_name)

    # upload base_code, email.txt, , assignment.cfg, and tests
    try:
        uploader = AssignmentUploader(upload_dir)
        uploader.upload_base_code()
        uploader.upload_email_txt()
        uploader.upload_tests()
        uploader.upload_config()
    except GkeepException as e:
        error = 'Error uploading assignment: {0}'.format(str(e))
        raise GkeepException(error)

    payload = '{0} {1} {2}'.format(class_name, upload_dir.assignment_name,
                                   uploader.get_target_path())

    communicate_event('UPLOAD', payload,
                      success_message='Assignment uploaded successfully',
                      error_message='Error uploading assignment: ',
                      timeout_message='Server response timeout. '
                                      'Upload status unknown')


@config_parsed
@server_interface_connected
def reset_password(username: str):
    """
    Reset a user's password.

    :param username: username of the user
    """

    communicate_event('PASSWD', username,
                      success_message='Password reset successfully',
                      error_message='Error resetting password: ',
                      timeout_message='Server response timeout. '
                                      'Password reset status unknown')


@config_parsed
@server_interface_connected
def check():
    """
    Check the connection to the server and print server information.
    """

    event_type = 'CHECK'
    response_timeout = 10

    # requests need a payload, but we have nothing to pass
    payload = 'dummy'

    poller = ServerResponsePoller(event_type, response_timeout)

    server_interface.log_event(event_type, payload)

    success_messages = []

    for response in poller.response_generator():
        if response.response_type == ServerResponseType.SUCCESS:
            success_messages.append(response.message)
        elif response.response_type == ServerResponseType.ERROR:
            message = ('Connection to the server via SSH was successful '
                       'but gkeepd responded with an error:\n{}'
                       .format(response.message))
            raise ServerResponseError(message)
        elif response.response_type == ServerResponseType.WARNING:
            message = ('Connection to the server via SSH was successful '
                       'but gkeepd responded with a warning:\n{}'
                       .format(response.message))
            raise ServerResponseWarning(message)
        elif response.response_type == ServerResponseType.TIMEOUT:
            error = ('Connection to the server via SSH was successful but '
                     'the response from gkeepd\ntimed out. gkeepd may not '
                     'be running on the server.')
            raise GkeepException(error)

    # These should never happen if the code is functioning correctly
    if len(success_messages) == 0:
        raise GkeepException('ERROR: check did not produce a proper response')
    elif len(success_messages) > 1:
        raise GkeepException('ERROR: server unexpectedly produced a stream '
                             'of responses: {}'.format(success_messages))

    payload = success_messages[0]

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as e:
        error = ('ERROR: {}\nServer produced invalid JSON:\n{}'
                 .format(e, payload))
        raise GkeepException(error)

    print()
    print('Successfully communicated with', config.server_host)

    if 'is_admin' in data and data['is_admin']:
        print('You are an admin user')

    print()
    print('Server information:')

    if 'version' in data:
        print('  Version:', data['version'])
        if __version__ != data['version']:
            print('NOTE: client version {} does not match server version {}'
                  .format(__version__, data['version']))
            print('This could potentially cause problems')
    else:
        print('  Version unknown')

    if 'uptime' in data:
        print('  gkeepd uptime:', duration_to_string(data['uptime']))

    if 'firejail_installed' in data:
        print('  Firejail installed:', data['firejail_installed'])

    if 'docker_installed' in data:
        print('  Docker installed:', data['docker_installed'])

    print()
    print('Server default assignment settings that can be overridden:')

    if 'default_test_env' in data:
        print('  env:', data['default_test_env'])

    if 'use_html' in data:
        print('  use_html:', data['use_html'])

    if 'tests_timeout' in data:
        print('  timeout:', data['tests_timeout'])

    if 'tests_memory_limit' in data:
        print('  memory_limit', data['tests_memory_limit'])
