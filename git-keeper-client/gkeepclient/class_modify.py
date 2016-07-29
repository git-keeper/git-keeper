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

"""Provides a function for modifying a class on the server."""

import os
import sys

from gkeepclient.client_configuration import config, ClientConfigurationError
from gkeepclient.server_interface import server_interface, ServerInterfaceError
from gkeepclient.server_response_poller import ServerResponsePoller, \
    ServerResponseType
from gkeepcore.csv_files import CSVError
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.local_csv_files import LocalCSVReader
from gkeepcore.student import StudentError, students_from_csv


class ClassModifyError(GkeepException):
    """Raised if there are any errors modifying the class."""
    pass


def class_modify(class_name, csv_file_path):
    if not os.path.isfile(csv_file_path):
        raise ClassModifyError('{0} does not exist'.format(csv_file_path))

    try:
        config.parse()
    except ClientConfigurationError as e:
        raise ClassModifyError('Configuration error: {0}'.format(e))

    try:
        server_interface.connect()
    except ServerInterfaceError as e:
        raise ClassModifyError('Error connecting to the server: {0}'.format(e))

    if not server_interface.class_exists(class_name):
        raise ClassModifyError('Class does not exist')

    try:
        students = students_from_csv(LocalCSVReader(csv_file_path))
    except (StudentError, CSVError) as e:
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

    poller = ServerResponsePoller('CLASS_MODIFY', timeout=20)

    # log that we added the class
    server_interface.log_event('CLASS_MODIFY', '{0} {1}'
                               .format(class_name, remote_csv_file_path))

    try:
        for response in poller.response_generator():
            if response.response_type == ServerResponseType.SUCCESS:
                print('Class added successfully')
            elif response.response_type == ServerResponseType.ERROR:
                print('Error adding class:')
                print(response.message)
            elif response.response_type == ServerResponseType.WARNING:
                print(response.message)
            elif response.response_type == ServerResponseType.TIMEOUT:
                print('Server response timeout. Class add status unknown.')
    except ServerInterfaceError as e:
        error = 'Server communication error: {0}'.format(e)
        raise ClassModifyError(error)


if __name__ == '__main__':
    class_modify(sys.argv[1], sys.argv[2])
