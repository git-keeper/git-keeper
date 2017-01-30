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
Provides functions for querying the server for information and printing the
query results.
"""
from time import time, localtime, strftime

from gkeepclient.client_function_decorators import config_parsed, \
    server_interface_connected
from gkeepclient.server_interface import server_interface


@config_parsed
@server_interface_connected
def list_classes():
    """Print the names of all the classes owned by the faculty."""

    for class_name in server_interface.get_classes():
        print(class_name)


@config_parsed
@server_interface_connected
def list_assignments():
    """
    Print the names of all the assignments owned by the faculty, grouped by
    class.
    """

    info = server_interface.get_info()

    for class_name in sorted(info.keys()):
        print(class_name, ':', sep='')

        for assignment_name in sorted(info[class_name]['assignments'].keys()):
            published = \
                info[class_name]['assignments'][assignment_name]['published']

            if published:
                published_prefix = 'P'
            else:
                published_prefix = 'U'

            print(published_prefix, assignment_name)

        print()


@config_parsed
@server_interface_connected
def list_students():
    """
    Print all the students in classes owned by the faculty, grouped by class.
    """

    for class_name in server_interface.get_classes():
        print(class_name, ':', sep='')

        for student in server_interface.get_students(class_name):
            print(student)

        print()


@config_parsed
@server_interface_connected
def list_recent(number_of_days):
    """
    Print recent submissions.

    :param number_of_days: submissions past this number of days ago are not
     recent
    """

    if number_of_days is None:
        number_of_days = 1

    print('Recent submissions:')
    print()

    info = server_interface.get_info()

    for class_name in sorted(info.keys()):
        class_name_printed = False

        for assignment_name in sorted(info[class_name]['assignments'].keys()):
            assignment_info = info[class_name]['assignments'][assignment_name]
            students_info = assignment_info['students_repos']

            if students_info is None:
                continue

            cutoff_time = time() - (60 * 60 * 24 * number_of_days)

            recent = []

            for username in students_info:
                student_info = students_info[username]

                if 'submission_count' in student_info and \
                   student_info['submission_count'] == 0:
                    continue

                if student_info['time'] >= cutoff_time:
                    recent.append((student_info['time'], student_info['first'],
                                   student_info['last']))

            if len(recent) > 0:
                recent.sort()

                if not class_name_printed:
                    print(class_name, ':', sep='')
                    class_name_printed = True

                print('  ', assignment_name, ':', sep='')

                for timestamp, first_name, last_name in recent:
                    human_timestamp = strftime('%Y-%m-%d %H:%M:%S',
                                               localtime(timestamp))
                    print('   ', human_timestamp, first_name, last_name)

                print()