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

import argparse
import sys

import argcomplete
import create_student_directories
import delete_assignment
import fetch_submissions
import initialize_class
import populate_students
import send_feedback
import send_passwords
import update_assignment_tests
import upload_assignment
import upload_handout


# We need to define our own subclass of argparse, purely so when a user doesn't
# use a command correctly, may it be be too many arguments, not enough
# arguments, etc.. the help message will also be displayed rather than just an
# error
class GraderParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


# Helper method for establishing a consistent added argument 'class_name'
# gsp refers to a reference to a sub-parsers that is passed into the func
def add_class_name(subparser):
    # name of the argument to the user is "<class name>", but it will be
    # stored as class_name
    subparser.add_argument("class_name", type=str, metavar="<class name>",
                           help="name of the class")


# This helper method initializes and returns the parser object
def initialize_parser():
    # Start the argument parser object, and declare that it will have
    # sub-commands.
    # e.g. git checkout and git clone, where checkout and clone are
    # both subparse commands for git
    parser = GraderParser(prog='')
    subparsers = parser.add_subparsers(dest='subparser_name',
                                       title="Actions")

    # Sub-command: Initializing a class
    # add the sub-command "initialize_class" and a little help message to the
    # subparsers object
    initialize_class_subparser = subparsers.add_parser("initialize_class",
                                                       help="initializes a class")
    # Specify that the sub-command needs an argument <class name>
    add_class_name(initialize_class_subparser)

    # Sub-command: Populating Students
    populate_students_subparser = subparsers.add_parser("populate_students",
                                                        help="populates students "
                                                             "in a specified class")
    add_class_name(populate_students_subparser)

    # Sub-command: Uploading an Assignment
    upload_assignment_subparser = subparsers.add_parser("upload_assignment",
                                                        help="uploads an assignment to a "
                                                             "specified class")
    add_class_name(upload_assignment_subparser)
    upload_assignment_subparser.add_argument('local_dir',
                                             metavar="<local assignment directory>",
                                             type=str,
                                             help="local directory containing the "
                                                  "assignment to be distributed")

    # Sub-command: Fetching Submissions and Reports
    fetch_submissions_subparser = subparsers.add_parser("fetch_submissions",
                                                        help="fetches student submissions for a "
                                                             "single specified or all assignments")
    add_class_name(fetch_submissions_subparser)
    fetch_submissions_subparser.add_argument("sub_dir", metavar="<class submission dir>",
                                             type=str,
                                             help="destination directory to put each of the "
                                                  "student's submissions")
    fetch_submissions_subparser.add_argument("assignment", metavar="(<assignment> | -a)",
                                             type=str,
                                             help="the assignment to be fetched; if \'-a\' is "
                                                  "presented, all assignments for the class "
                                                  "will be fetched")

    # Sub-command: Creating Student Directories
    create_student_directories_subparser = subparsers.add_parser("create_student_directories",
                                                                 help="creates student directories in a "
                                                                      "specified directory; useful for "
                                                                      "manually sending feedback to "
                                                                      "students")
    add_class_name(create_student_directories_subparser)
    create_student_directories_subparser.add_argument("parent_dir", metavar="<parent directory>",
                                                      type=str,
                                                      help="directory that will contain all "
                                                           "of the student directories to be "
                                                           "created")

    # Sub-command: Sending Feedback
    send_feedback_subparser = subparsers.add_parser("send_feedback",
                                                    help="sends emails to students containing "
                                                         "feedback about a specified assignment")
    add_class_name(send_feedback_subparser)
    send_feedback_subparser.add_argument("assignment", metavar="<assignment name>", type=str,
                                         help="name of the assignment that the students "
                                              "will be receiving feeback about. Note: the "
                                              "assignment does not need to be a legitimate "
                                              "assignment contained on the grading system.")
    send_feedback_subparser.add_argument("feedback_dir", metavar="<feedback directory>",
                                         type=str,
                                         help="name of the parent directory containing all "
                                              "of student directories that contain feedback")

    # Sub-command: Deleting an assignment
    delete_assignment_subparser = subparsers.add_parser("delete_assignment",
                                                        help="deletes an assignment present on "
                                                             "the grading server")
    add_class_name(delete_assignment_subparser)
    delete_assignment_subparser.add_argument("assignment", metavar="<assignment name>",
                                             type=str,
                                             help="name of the assignment to be deleted")

    # Sub-command: Sending passwords
    send_passwords_subparser = subparsers.add_parser("send_passwords",
                                                     help="sends passwords for the grading "
                                                          "server out to the students")
    add_class_name(send_passwords_subparser)
    send_passwords_subparser.add_argument("user_pass_file", metavar="<user pass file>",
                                          type=str,
                                          help="file containing all of the passwords for "
                                               "each of the newly created accounts "
                                               "on the server")

    # Sub-command: Updating tests for an Assignment
    update_assignment_tests_subparser = subparsers.add_parser("update_assignment_tests",
                                                              help="updates the test files that an "
                                                                   "assignment is tested against "
                                                                   "following a student submission")
    add_class_name(update_assignment_tests_subparser)
    update_assignment_tests_subparser.add_argument("local_dir",
                                                   metavar="<local assignment directory>",
                                                   type=str,
                                                   help="directory containing the updated "
                                                        "tests to be pushed to the "
                                                        "grading server")

    # Sub-command: Upload handout
    upload_handout_subparser = subparsers.add_parser("upload_handout",
                                                     help="uploads a handout to the class")
    add_class_name(upload_handout_subparser)
    upload_handout_subparser.add_argument("local_handout_dir",
                                          metavar="<local handout directory>",
                                          type=str,
                                          help="directory containing the handout "
                                               "to be pushed to the grading server")

    return parser


def main():
    # Initialize the parser object that will interpret the passed in
    # command line arguments
    parser = initialize_parser()

    # Allow for auto-complete
    argcomplete.autocomplete(parser)

    # If no arguments are given when teacher_interface is called, just
    # display the help message and exit
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Parse the args
    parsed_args = parser.parse_args()

    action_name = parsed_args.subparser_name

    # call the appropriate functions associated with each sub-command
    if action_name == 'initialize_class':
        initialize_class.initialize_class(parsed_args.class_name)
    elif action_name == 'populate_students':
        populate_students.populate_students(parsed_args.class_name)
    elif action_name == 'upload_assignment':
        upload_assignment.upload_assignment(parsed_args.class_name, parsed_args.local_dir)
    elif action_name == 'fetch_submissions':
        fetch_submissions.fetch_submissions(parsed_args.class_name, parsed_args.sub_dir, parsed_args.assignment)
    elif action_name == 'create_student_directories':
        create_student_directories.create_student_directories(parsed_args.class_name, parsed_args.parent_dir)
    elif action_name == 'send_feedback':
        send_feedback.send_feedback(parsed_args.class_name, parsed_args.assignment, parsed_args.feedback_dir)
    elif action_name == 'delete_assignment':
        delete_assignment.delete_assignment(parsed_args.class_name, parsed_args.assignment)
    elif action_name == 'send_passwords':
        send_passwords.send_passwords(parsed_args.class_name, parsed_args.user_pass_file)
    elif action_name == 'update_assignment_tests':
        update_assignment_tests.update_assignment_tests(parsed_args.class_name, parsed_args.local_dir)
    elif action_name == 'upload_handout':
        upload_handout.upload_handout(parsed_args.class_name, parsed_args.local_handout_dir)
    else:
        parsed_args.func(parsed_args)


if __name__ == '__main__':
    main()
