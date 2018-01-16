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

    for class_name in sorted(info.class_list()):
        print(class_name, ':', sep='')

        for assignment_name in sorted(info.assignment_list(class_name)):
            published = info.is_published(class_name, assignment_name)

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


    for class_name in sorted(info.class_list()):
        class_name_printed = False

        for assignment_name in sorted(info.assignment_list(class_name)):
            students_submitted = info.students_submitted_list(class_name,
                                                              assignment_name)

            if students_submitted is None:
                continue

            cutoff_time = time() - (60 * 60 * 24 * number_of_days)

            recent = []

            for username in students_submitted:

                if info.student_submission_count(
                        class_name, assignment_name, username) == 0:
                    continue

                submission_time = \
                    info.student_submission_time(class_name, assignment_name,
                                                 username)

                if submission_time >= cutoff_time:
                    first_name = info.student_first_name(class_name, username)
                    last_name = info.student_last_name(class_name, username)
                    recent.append((submission_time, first_name, last_name))

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