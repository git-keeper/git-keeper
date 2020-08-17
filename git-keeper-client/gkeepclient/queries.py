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

import json
from time import time, localtime, strftime

from gkeepclient.client_function_decorators import config_parsed, \
    server_interface_connected
from gkeepclient.server_interface import server_interface


@config_parsed
@server_interface_connected
def list_classes(output_json: bool):
    """Print the names of all the classes owned by the faculty."""

    class_list = sorted(server_interface.get_info().class_list())

    open_classes = []
    closed_classes = []

    for class_name in class_list:
        if server_interface.is_open(class_name):
            open_classes.append(class_name)
        else:
            closed_classes.append(class_name)

    if output_json:
        json_classes = []

        for class_name in sorted(open_classes):
            json_classes.append({'name': class_name, 'open': True})

        for class_name in sorted(closed_classes):
            json_classes.append({'name': class_name, 'open': False})

        print(json.dumps(json_classes))
    else:
        for class_name in sorted(open_classes):
            print(class_name)

        for class_name in sorted(closed_classes):
            print(class_name, '(closed)')


@config_parsed
@server_interface_connected
def list_assignments(output_json: bool):
    """
    Print the names of all the assignments owned by the faculty, grouped by
    class.

    :param output_json: True if the output should be JSON, False otherwise
    """

    info = server_interface.get_info()

    text_output = ''
    json_output = {}

    for class_name in sorted(info.class_list()):
        if not info.is_open(class_name):
            continue

        text_output += '{}:\n'.format(class_name)
        json_output[class_name] = []

        for assignment_name in sorted(info.assignment_list(class_name)):
            published = info.is_published(class_name, assignment_name)
            disabled = info.is_disabled(class_name, assignment_name)

            json_assignment = {
                'name': assignment_name,
                'published': published,
                'disabled': disabled,
            }

            if disabled:
                prefix = 'D'
            elif published:
                prefix = 'P'
            else:
                prefix = 'U'

            text_output += '{} {}\n'.format(prefix, assignment_name)
            json_output[class_name].append(json_assignment)

        text_output += '\n'

    if output_json:
        print(json.dumps(json_output))
    else:
        print(text_output, end='')


@config_parsed
@server_interface_connected
def list_students(output_json: bool):
    """
    Print all the students in classes owned by the faculty, grouped by class.

    :param output_json: True if the output should be JSON, False otherwise
    """

    text_output = ''
    json_output = {}

    info = server_interface.get_info()
    class_list = info.class_list()

    for class_name in sorted(class_list):
        if not info.is_open(class_name):
            continue

        text_output += '{}:\n'.format(class_name)
        json_output[class_name] = []

        student_list = info.student_list(class_name)

        lines = []

        for username in sorted(student_list):
            first_name = info.student_first_name(class_name, username)
            last_name = info.student_last_name(class_name, username)
            email_address = info.student_email_address(class_name, username)

            lines.append('{}, {} ({})'.format(last_name, first_name, username))
            json_output[class_name].append({
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email_address': email_address,
            })

        text_output += '\n'.join(sorted(lines))
        text_output += '\n\n'

    if output_json:
        print(json.dumps(json_output))
    else:
        print(text_output, end='')


@config_parsed
@server_interface_connected
def list_recent(number_of_days, output_json: bool):
    """
    Print recent submissions.

    :param number_of_days: submissions past this number of days ago are not
     recent
    :param output_json: True if the output should be JSON, False otherwise
    """

    text_output = ''
    json_output = {}

    if number_of_days is None:
        number_of_days = 1

    text_output += 'Recent submissions:\n\n'

    info = server_interface.get_info()

    for class_name in sorted(info.class_list()):
        if not server_interface.is_open(class_name):
            continue

        class_name_printed = False

        for assignment_name in sorted(info.assignment_list(class_name)):
            published = info.is_published(class_name, assignment_name)
            disabled = info.is_disabled(class_name, assignment_name)

            if not published or disabled:
                continue

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
                    email_address = info.student_email_address(class_name,
                                                               username)
                    recent.append((submission_time, first_name, last_name,
                                   username, email_address))

            if len(recent) > 0:
                recent.sort()

                if not class_name_printed:
                    text_output += '{}:\n'.format(class_name)
                    json_output[class_name] = {}
                    class_name_printed = True

                text_output += '  {}:\n'.format(assignment_name)
                json_output[class_name][assignment_name] = []

                for (timestamp, first_name, last_name, username,
                     email_address) in recent:
                    human_timestamp = strftime('%Y-%m-%d %H:%M:%S',
                                               localtime(timestamp))
                    text_output += '   {} {} {} ({})\n'.format(human_timestamp,
                                                               first_name,
                                                               last_name,
                                                               email_address)
                    json_entry = {
                        'time': timestamp,
                        'human_time': human_timestamp,
                        'first_name': first_name,
                        'last_name': last_name,
                        'username': username,
                        'email_address': email_address,
                    }
                    json_output[class_name][assignment_name].append(json_entry)

                text_output += '\n'

    if output_json:
        print(json.dumps(json_output))
    else:
        print(text_output)
