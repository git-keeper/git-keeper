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

import os
from pkg_resources import resource_exists, resource_string, ResolutionError, \
    ExtractionError

from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import student_assignment_repo_path,\
    student_class_dir_path
from gkeepcore.shell_command import CommandError
from gkeepcore.system_commands import chmod, sudo_chown, cp, mkdir
from gkeepserver.assignment_directory import AssignmentDirectory
from gkeepserver.email_sender_thread import email_sender
from gkeepserver.server_configuration import config
from gkeepserver.server_email import Email, EmailException


class StudentAssignmentError(GkeepException):
    """Raised if anything goes wrong with a student assignment."""
    pass


def setup_student_assignment(assignment_dir: AssignmentDirectory,
                             student, faculty_username: str):
    """
    Setup the bare repository that a student will clone and push to for an
    assignment and email the student.

    Raises StudentAssignmentError if anything goes wrong.

    :param assignment_dir: object representing the directory
    :param student: Student object representing the student
    :param faculty_username: username of the faculty who owns the class
    """

    # path to the student's directory containing the class that this assignment
    # belongs to
    class_path = student_class_dir_path(student.username, faculty_username,
                                        assignment_dir.class_name)

    # path to the student's bare repository for this assignment
    assignment_repo_path = \
        student_assignment_repo_path(student.username, faculty_username,
                                     assignment_dir.class_name,
                                     assignment_dir.assignment_name)

    # the repo should not already exist
    if os.path.isdir(assignment_repo_path):
        error = '{0} already exists'.format(assignment_repo_path)
        raise StudentAssignmentError(error)

    # make the class directory if it does not exist
    if not os.path.isdir(class_path):
        try:
            mkdir(class_path, sudo=True)
            sudo_chown(class_path, student.username, config.keeper_group)
        except OSError as e:
            error = 'error creating {0}: {1}'.format(assignment_repo_path,
                                                     str(e))
            raise StudentAssignmentError(error)

    # copy the base code repo from the faculty's home directory
    try:
        cp(assignment_dir.base_code_repo_path, assignment_repo_path,
           recursive=True, sudo=True)
    except OSError as e:
        error = ('error copying {0} to {1}: {2}'
                 .format(assignment_dir.base_code_repo_path,
                         assignment_repo_path, str(e)))
        raise StudentAssignmentError(error)

    # set permissions on the assignment repo
    try:
        chmod(assignment_repo_path, '750', sudo=True)
        sudo_chown(assignment_repo_path, student.username,
                   config.keeper_group, recursive=True)
    except CommandError as e:
        error = ('error setting permissions on {0}: {1}'
                 .format(assignment_repo_path, str(e)))
        raise StudentAssignmentError(error)

    email_subject = ('[{0}] New assignment: {1}'
                     .format(assignment_dir.class_name,
                             assignment_dir.assignment_name))

    # build the clone URL for the assignment
    clone_url = '{0}@{1}:{2}'.format(student.username,
                                     config.hostname,
                                     assignment_repo_path)

    # read email.txt to get the customizable part of the email body
    try:
        with open(assignment_dir.email_path) as f:
            email_body = f.read()
    except OSError as e:
        error = 'error reading {0}: {1}'.format(assignment_dir.email_path,
                                                str(e))
        raise StudentAssignmentError(error)

    # clone URL followed by email.txt contents
    email_body = 'Clone URL:\n{0}\n\n'.format(clone_url, email_body)

    # build the email
    try:
        email = Email(student.email_address, email_subject, email_body)
    except EmailException as e:
        raise StudentAssignmentError(e)

    # enqueue the email for sending
    email_sender.enqueue(email)


def write_post_receive_script(dest_path: str):
    """
    Write the contents of data/post-receive to a file.

    This will overwrite an existing file.

    Raises PostReceiveScriptError on any errors.

    :param dest_path: path to write to
    """
    if not resource_exists('gkeepserver', 'data/post-receive'):
        raise StudentAssignmentError('post-receive script does not exist')

    try:
        script_text = resource_string('gkeepserver', 'data/post-receive')
        script_text = script_text.decode()
    except (ResolutionError, ExtractionError, UnicodeDecodeError):
        raise StudentAssignmentError('error reading post-receive script data')

    try:
        with open(dest_path, 'w') as f:
            f.write(script_text)
    except OSError as e:
        error = 'error writing {0}: {1}'.format(dest_path, str(e))
        raise StudentAssignmentError(error)
