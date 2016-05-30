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

# FIXME
"""
This is a proof-of-concept script for adding a class from the client.
"""


import os
import sys
from time import sleep

from gkeepclient.server_interface import server_interface, ServerInterfaceError
from gkeepclient.client_configuration import config, ClientConfigurationError
from gkeepclient.server_log_file_reader import ServerLogFileReader
from gkeepcore.csv_files import CSVError
from gkeepcore.path_utils import faculty_class_directory
from gkeepcore.local_csv_files import csv_rows
from gkeepcore.student import Student, StudentError


def class_add(csv_file_path='class.csv'):
    # FIXME - catch exception
    class_name, extension = csv_file_path.split(os.extsep)

    if extension.lower() != 'csv':
        sys.exit('{0} must be a csv file'.format(csv_file_path))

    if not os.path.isfile(csv_file_path):
        sys.exit('{0} does not exist'.format(csv_file_path))

    try:
        config.parse()
    except ClientConfigurationError as e:
        sys.exit('Configuration error:\n{0}'.format(e))

    try:
        server_interface.connect()
    except ServerInterfaceError as e:
        sys.exit('Error connecting to the server:\n{0}'.format(e))

    home_dir = server_interface.user_home_dir(config.server_username)

    class_dir_path = faculty_class_directory(class_name, home_dir)

    if server_interface.is_directory(class_dir_path):
        sys.exit('Class {0} already exists'.format(class_name))

    students = []

    try:
        for row in csv_rows(csv_file_path):
            students.append(Student.from_csv_row(row))
    except CSVError as e:
        sys.exit(e)
    except StudentError as e:
        sys.exit(e)

    print('Adding class {0} with the following students:'.format(class_name))

    for student in students:
        print(student)

    # create directory and upload CSV
    server_interface.create_directory(class_dir_path)
    remote_csv_file_path = os.path.join(class_dir_path, 'students.csv')
    server_interface.copy_file(csv_file_path, remote_csv_file_path)

    print('CSV file uploaded')

    # initialize a log reader for reading the server's response
    gkeepd_log_path = server_interface.gkeepd_to_me_log_path()
    reader = ServerLogFileReader(gkeepd_log_path)

    # log that we added the class
    server_interface.log_event('CLASSADD', class_dir_path)

    print('Waiting for server confirmation')
    sys.stdout.flush()

    class_added = False

    # poll for the server's response
    while not class_added:
        while not reader.has_new_lines():
            print('.', end='')
            sys.stdout.flush()
            sleep(1)

        for line in reader.get_new_lines():
            if line.endswith('CLASSADDED ' + class_dir_path):
                class_added = True
                print('\nClass added successfully')
                break


if __name__ == '__main__':
    class_add()
