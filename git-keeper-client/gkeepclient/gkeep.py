#!/usr/bin/env python3

# Copyright 2016 Joshua Russett
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

# PYTHON_ARGCOMPLETE_OK

"""
Provides the main entry point for the gkeep client. Parses command line
arguments and calls the appropriate function.
"""

import sys
from argparse import ArgumentParser

from gkeepclient.version import __version__ as client_version
from gkeepcore.path_utils import path_to_assignment_name
from gkeepcore.version import __version__ as core_version

from argcomplete import autocomplete
from gkeepclient.client_configuration import config
from gkeepclient.client_function_decorators import config_parsed

from gkeepclient.create_config import create_config
from gkeepclient.fetch_submissions import fetch_submissions, build_dest_path
from gkeepclient.server_actions import class_add, class_modify, \
    delete_assignment, publish_assignment, update_assignment, \
    upload_assignment, trigger_tests, update_status, add_faculty
from gkeepclient.queries import list_classes, list_assignments, \
    list_students, list_recent
from gkeepcore.gkeep_exception import GkeepException


class GraderParser(ArgumentParser):
    """
    ArgumentParser with a custom error() method so that the help message is
    displayed when the user has not used a command correctly.
    """

    def error(self, message):
        """
        Print the error message, a usage message, and then exit the program

        :param message: error message
        """
        print('Error: {0}\n'.format(message), file=sys.stderr)
        self.print_help()
        sys.exit(2)


def add_class_name_argument(subparser):
    """
    Add a class_name argument to a subparser.

    :param subparser: the subparser to add the argument to
    """

    subparser.add_argument('class_name', type=str, metavar='<class name>',
                           help='name of the class')


def add_assignment_name_argument(subparser):
    """
    Add an assignment_name argument to a subparser.

    :param subparser: the subparser to add the argument to
    """

    subparser.add_argument('assignment_name', type=str,
                           metavar='<assignment name>',
                           help='name of the assignment')


def add_assignment_path_argument(subparser):
    """
    Add an assignment_path argument to a subparser.

    :param subparser: the subparser to add the argument to
    """

    subparser.add_argument('assignment_path', type=str,
                           metavar='<assignment directory>',
                           help='directory containing the assignment')


def add_csv_file_path_argument(subparser):
    """
    Add a csv_file_path argument to a subparser.

    :param subparser: the subparser to add the argument to
    """

    subparser.add_argument('csv_file_path', type=str, metavar='<csv filename>',
                           help='name of the CSV file containing students')


def add_add_subparser(subparsers):
    """
    Add a subparser for action 'add', which adds a class.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('add', help='add a class')
    add_class_name_argument(subparser)
    add_csv_file_path_argument(subparser)


def add_modify_subparser(subparsers):
    """
    Add a subparser for action 'modify', which modifies a class's enrollment.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('modify',
                                      help='modify the enrollment for a class')
    add_class_name_argument(subparser)
    add_csv_file_path_argument(subparser)


def add_upload_subparser(subparsers):
    """
    Add a subparser for action 'upload', which uploads an assignment.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('upload', help='upload an assignment')
    add_class_name_argument(subparser)
    add_assignment_path_argument(subparser)


def add_publish_subparser(subparsers):
    """
    Add a subparser for action 'publish', which publishes an assignment.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('publish', help='publish an assignment')
    add_class_name_argument(subparser)
    add_assignment_name_argument(subparser)


def add_update_subparser(subparsers):
    """
    Add a subparser for action 'update', which updates an assignment's files.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('update', help='update an assignment')
    add_class_name_argument(subparser)
    add_assignment_path_argument(subparser)
    subparser.add_argument('item', metavar='<update item>',
                           help='item to update: base_code, email, tests, '
                                'or all')


def add_delete_subparser(subparsers):
    """
    Add a subparser for action 'delete', which deletes an assignment.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('delete', help='delete an assignment')
    add_class_name_argument(subparser)
    add_assignment_name_argument(subparser)


def add_fetch_subparser(subparsers):
    """
    Add a subparser for action 'fetch', which fetches student submissions.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('fetch',
                                      help='fetch student submissions')
    add_class_name_argument(subparser)
    subparser.add_argument('assignment_name', type=str,
                           metavar='<assignment name>',
                           help='name of the assignment, or "all"')
    subparser.add_argument('destination_path', type=str,
                           metavar='<destination>',
                           help=('directory in which to fetch the assignment '
                                 '(optional)'), nargs='?')


def add_query_subparser(subparsers):
    """
    Add a subparser for action 'query', which queries the server.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('query', help='query the server')
    subparser.add_argument('query_type', metavar='<query type>',
                           help='classes, assignments, recent, or students',
                           choices=['classes', 'assignments', 'recent',
                                    'students'])
    subparser.add_argument('number_of_days', type=int,
                           metavar='<number of days>',
                           help='number of days considered recent (optional)',
                           nargs='?')


def add_trigger_subparser(subparsers):
    """
    Add a subparser for action 'trigger', which triggers tests to be run for
    an assignment

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('trigger', help='trigger tests')
    add_class_name_argument(subparser)
    add_assignment_name_argument(subparser)
    subparser.add_argument('student_usernames',
                           metavar='<student username>',
                           nargs='*',
                           help='optional, trigger tests for only these '
                                'students')


def add_config_subparser(subparsers):
    """
    Add a subparser for action 'config', which asks to create a new
    configuration file
    or to overwrite the existing one

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('config',
                                      help='create or overwrite configuration '
                                           'file')


def add_status_subparser(subparsers):
    """
    Add a subparser for action 'status', which can change the status of a
    class to 'open' or 'closed'.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('status', help='change the status of a '
                                                     'class')
    add_class_name_argument(subparser)
    subparser.add_argument('status', metavar='<class status>',
                           choices=('open', 'closed'),
                           help='"open" or "closed"')


def add_add_faculty_subparser(subparsers):
    """
    Add a subparser for action 'add_faculty', which can add a new faculty user.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('add_faculty', help='add a new faculty '
                                                          'user')

    subparser.add_argument('last_name', metavar='<last name>',
                           help='last name of the faculty member')
    subparser.add_argument('first_name', metavar='<first name>',
                           help='last name of the faculty member')
    subparser.add_argument('email_address', metavar='<email address>',
                           help='email address of the faculty member')


def initialize_action_parser() -> GraderParser:
    """
    Initialize a GraderParser object.

    :return: an initialized GraderParser object
    """

    # Create the argument parser object, and declare that it will have
    # sub-commands.
    # e.g. gkeep upload, gkeep publish, etc.
    parser = GraderParser()

    parser.add_argument('-f', '--config_file', help='Path to config file')
    parser.add_argument('-v', '--version', action='store_true',
                        help='Print gkeep version')

    subparsers = parser.add_subparsers(dest='subparser_name', title="Actions")

    # add subparsers
    add_add_subparser(subparsers)
    add_modify_subparser(subparsers)
    add_upload_subparser(subparsers)
    add_update_subparser(subparsers)
    add_publish_subparser(subparsers)
    add_delete_subparser(subparsers)
    add_fetch_subparser(subparsers)
    add_query_subparser(subparsers)
    add_trigger_subparser(subparsers)
    add_config_subparser(subparsers)
    add_status_subparser(subparsers)
    add_add_faculty_subparser(subparsers)

    return parser


def run_query(query_type: str, number_of_days: int):
    """
    Run the query specified by query_type.

    :param query_type: type of the query
    """

    if query_type == 'classes':
        list_classes()
    elif query_type == 'assignments':
        list_assignments()
    elif query_type == 'students':
        list_students()
    elif query_type == 'recent':
        list_recent(number_of_days)


def main():
    """
    gkeep entry point.

    Setup the command line argument parser, parse the arguments, and call the
    appropriate function.
    """

    # Initialize the parser object that will interpret the passed in
    # command line arguments
    parser = initialize_action_parser()

    # Allow for auto-complete
    autocomplete(parser)

    # If no arguments are given just display the help message and exit
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Parse the args
    parsed_args = parser.parse_args()

    if parsed_args.config_file is not None:
        config.set_config_path(parsed_args.config_file)

    if parsed_args.version:
        print('gkeep version', client_version)

    # Every action except "config" requires that the configuration file be
    # parsed
    if parsed_args.subparser_name != 'config':
        config.parse()

    try:
        take_action(parsed_args)
    except GkeepException as e:
        sys.exit(e)


def take_action(parsed_args):
    action_name = parsed_args.subparser_name

    # parsed_args.class_name could be an alias
    class_name = getattr(parsed_args, 'class_name', None)
    if class_name and class_name in config.class_aliases:
        class_name = config.class_aliases[class_name]

    # the user may pass a path for the name of an assignment
    assignment_name = getattr(parsed_args, 'assignment_name', None)
    if assignment_name:
        assignment_name = path_to_assignment_name(assignment_name)

    # call the appropriate function for the action
    if action_name == 'add':
        class_add(class_name, parsed_args.csv_file_path)
    elif action_name == 'modify':
        class_modify(class_name, parsed_args.csv_file_path)
    elif action_name == 'upload':
        upload_assignment(class_name, parsed_args.assignment_path)
    elif action_name == 'update':
        if parsed_args.item == 'all':
            items = ('base_code', 'email', 'tests')
        else:
            items = (parsed_args.item,)
        update_assignment(class_name, parsed_args.assignment_path, items)
    elif action_name == 'publish':
        publish_assignment(class_name, assignment_name)
    elif action_name == 'delete':
        delete_assignment(class_name, assignment_name)
    elif action_name == 'fetch':
        dest_path = build_dest_path(parsed_args.destination_path,
                                    class_name)
        fetch_submissions(class_name, assignment_name,
                          dest_path)
    elif action_name == 'query':
        run_query(parsed_args.query_type, parsed_args.number_of_days)
    elif action_name == 'trigger':
        trigger_tests(class_name, assignment_name,
                      parsed_args.student_usernames)
    elif action_name == 'config':
        create_config()
    elif action_name == 'status':
        update_status(class_name, parsed_args.status)
    elif action_name == 'add_faculty':
        add_faculty(parsed_args.last_name, parsed_args.first_name,
                    parsed_args.email_address)


if __name__ == '__main__':
    if core_version != client_version:
        error = 'git-keeper-client and git-keeper-core versions must match.\n'
        error += 'client version: {}\n'.format(client_version)
        error += 'core version: {}'.format(core_version)
        sys.exit(error)

    main()
