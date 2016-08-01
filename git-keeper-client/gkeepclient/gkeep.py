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

import sys
from argparse import ArgumentParser

from argcomplete import autocomplete

from gkeepclient.actions.class_add import class_add
from gkeepclient.actions.class_modify import class_modify
from gkeepclient.actions.delete_assignment import delete_assignment
from gkeepclient.actions.publish_assignment import publish_assignment
from gkeepclient.actions.update_assignment import update_assignment
from gkeepclient.actions.upload_assignment import upload_assignment
from gkeepclient.queries import list_classes, list_assignments, list_students
from gkeepcore.gkeep_exception import GkeepException


class GraderParser(ArgumentParser):
    """
    ArgumentParser with a custom error() method so that the help message is
    displayed when the user has not used a command correctly.
    """
    def error(self, message):
        print('Error: {0}\n'.format(message), file=sys.stderr)
        self.print_help()
        sys.exit(2)


def add_class_name(subparser):
    """
    Add a class_name argument to a subparser.

    :param subparser: the subparser to add the argument to
    """

    subparser.add_argument('class_name', type=str, metavar='<class name>',
                           help='name of the class')


def add_add_subparser(subparsers):
    """
    Add a subparser for action 'add', which adds a class.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('add', help='add a class')
    add_class_name(subparser)
    subparser.add_argument('csv_file_path', type=str, metavar='<csv filename>',
                           help='name of the CSV file containing students')


def add_modify_subparser(subparsers):
    """
    Add a subparser for action 'modify', which modifies a class's enrollment.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('modify',
                                      help='modify the enrollment for a class')
    add_class_name(subparser)
    subparser.add_argument('csv_file_path', type=str, metavar='<csv filename>',
                           help='name of the CSV file containing students')


def add_upload_subparser(subparsers):
    """
    Add a subparser for action 'upload', which uploads an assignment.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('upload', help='upload an assignment')
    add_class_name(subparser)
    subparser.add_argument('assignment_path', metavar='<assignment directory>',
                           help='directory containing the assignment')


def add_publish_subparser(subparsers):
    """
    Add a subparser for action 'publish', which publishes an assignment.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('publish', help='publish an assignment')
    add_class_name(subparser)
    subparser.add_argument('assignment_name', metavar='<assignment name>',
                           help='name of the assignment')


def add_update_subparser(subparsers):
    """
    Add a subparser for action 'update', which updates an assignment's files.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('update', help='update an assignment')
    add_class_name(subparser)
    subparser.add_argument('assignment_path', metavar='<assignment directory>',
                           help='directory containing the assignment')
    subparser.add_argument('item', metavar='<update item>',
                           help='item to update: base_code, email, tests, '
                                'or all')


def add_delete_subparser(subparsers):
    """
    Add a subparser for action 'delete', which deletes an assignment.

    :param subparsers: subparsers to add to
    """

    subparser = subparsers.add_parser('delete', help='delete an assignment')
    add_class_name(subparser)
    subparser.add_argument('assignment_name', metavar='<assignment name>',
                           help='name of the assignment')


def add_query_subparser(subparsers):
    subparser = subparsers.add_parser('query', help='query the server')
    subparser.add_argument('query_type', metavar='<query type>',
                           help='classes, assignments, or students',
                           choices=['classes', 'assignments', 'students'])


def initialize_action_parser() -> GraderParser:
    """
    Initialize a GraderParser object.

    :return: an initialized GraderParser object
    """

    # Create the argument parser object, and declare that it will have
    # sub-commands.
    # e.g. gkeep upload, gkeep publish, etc.
    parser = GraderParser()
    subparsers = parser.add_subparsers(dest='subparser_name', title="Actions")

    # add subparsers
    add_add_subparser(subparsers)
    add_modify_subparser(subparsers)
    add_upload_subparser(subparsers)
    add_update_subparser(subparsers)
    add_publish_subparser(subparsers)
    add_delete_subparser(subparsers)
    add_query_subparser(subparsers)

    return parser


def run_query(query_type: str):
    if query_type == 'classes':
        list_classes()
    elif query_type == 'assignments':
        list_assignments()
    elif query_type == 'students':
        list_students()


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

    # If no arguments are given when teacher_interface is called,
    # just display the help message and exit
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Parse the args
    parsed_args = parser.parse_args()

    action_name = parsed_args.subparser_name

    try:
        # call the appropriate function for the action
        if action_name == 'add':
            class_add(parsed_args.class_name, parsed_args.csv_file_path)
        elif action_name == 'modify':
            class_modify(parsed_args.class_name, parsed_args.csv_file_path)
        elif action_name == 'upload':
            upload_assignment(parsed_args.class_name,
                              parsed_args.assignment_path)
        elif action_name == 'update':
            if parsed_args.item == 'all':
                items = ('base_code', 'email', 'tests')
            else:
                items = (parsed_args.item,)
            update_assignment(parsed_args.class_name,
                              parsed_args.assignment_path, items)
        elif action_name == 'publish':
            publish_assignment(parsed_args.class_name,
                               parsed_args.assignment_name)
        elif action_name == 'delete':
            delete_assignment(parsed_args.class_name,
                              parsed_args.assignment_name)
        elif action_name == 'query':
            run_query(parsed_args.query_type)
    except GkeepException as e:
        sys.exit(e)


if __name__ == '__main__':
    main()
