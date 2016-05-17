#!/usr/bin/env python3

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
import sys
from queue import Queue
from threading import Thread

from configuration import GraderConfiguration, ConfigurationError
from email_sender import Email, EmailException, process_email_queue
from subprocess_commands import directory_exists

from student import Student


def create_feedback_email(student: Student, assignment_name, directory):
    subject = 'Feedback for {0}'.format(assignment_name)

    body = ''

    files = []

    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)

        if not os.path.isfile(path):
            continue

        if filename == 'body.txt':
            with open(path) as f:
                body = f.read()
        else:
            files.append(path)

    if body == '' and len(files) == 0:
        print('No files or body.txt for {0}, skipping'.format(student))
        return None

    print('Sending files in {0} to {1}'.format(directory, student))

    email = Email(student.email_address, subject, body, files_to_attach=files)

    return email


def send_feedback(class_name, assignment_name, feedback_dir):

    if not directory_exists(feedback_dir):
        sys.exit('{0} does not exist'.format(feedback_dir))

    try:
        config = GraderConfiguration(single_class_name=class_name)
    except ConfigurationError as e:
        sys.exit(e)

    if class_name not in config.students_by_class:
        sys.exit('class {0} does not exist'.format(class_name))

    email_queue = Queue()
    email_thread = Thread(target=process_email_queue, args=(email_queue,
                                                            class_name,
                                                            config))
    email_thread.start()

    subdirs = os.listdir(feedback_dir)

    for subdir in subdirs:
        for student in config.students_by_class[class_name]:
            if student.username in subdir:
                try:
                    email = create_feedback_email(student, assignment_name,
                                                  os.path.join(feedback_dir,
                                                  subdir))
                    if email is not None:
                        email_queue.put(email)
                except EmailException as e:
                    print('Error creating email:\n{0}'.format(e))

    email_queue.put(None)
    email_thread.join()
