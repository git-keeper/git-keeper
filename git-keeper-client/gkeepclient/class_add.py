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

"""Provides a function for adding a class to the server."""

import os
import sys

from gkeepclient.client_function_decorators import config_parsed, \
    class_does_not_exist
from gkeepclient.client_function_decorators import server_interface_connected
from gkeepclient.server_interface import server_interface
from gkeepclient.server_response_poller import communicate_event
from gkeepcore.csv_files import CSVError
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.student import StudentError, students_from_csv


class ClassAddError(GkeepException):
    """Raised if there are any errors adding the class."""
    pass


@config_parsed
@server_interface_connected
@class_does_not_exist
def class_add(class_name: str, csv_file_path: str):
    """
    Add a class on the server.

    :param class_name: name of the class
    :param csv_file_path: path to the CSV file of students
    """

    if not os.path.isfile(csv_file_path):
        raise ClassAddError('{0} does not exist'.format(csv_file_path))

    try:
        students = students_from_csv(LocalCSVReader(csv_file_path))
    except (StudentError, CSVError) as e:
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


if __name__ == '__main__':
    class_add(sys.argv[1], sys.argv[2])
