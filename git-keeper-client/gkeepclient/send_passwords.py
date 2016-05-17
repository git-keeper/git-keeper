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
from email_sender import Email, process_email_queue


def send_passwords(class_name, user_pass_filename):

    try:
        config = GraderConfiguration(single_class_name=class_name)
    except ConfigurationError as e:
        sys.exit(e)

    if class_name not in config.students_by_class:
        sys.exit('class {0} does not exist'.format(class_name))

    if not os.path.isfile(user_pass_filename):
        sys.exit('{0} does not exist'.format(user_pass_filename))

    passwords_by_username = {}

    try:
        with open(user_pass_filename) as f:
            for line in f:
                try:
                    username, password = line.split()
                    passwords_by_username[username] = password
                finally:
                    pass
    except OSError as e:
        sys.exit(e)

    email_queue = Queue()
    email_thread = Thread(target=process_email_queue, args=(email_queue,
                                                            class_name,
                                                            config))
    email_thread.start()

    subject = 'Password for the grading server'

    for student in config.students_by_class[class_name]:
        if student.username not in passwords_by_username:
            continue

        body = ('Hello {0},\n\nYour password for the grading server is {1}\n\n'
                'Please save this email, you will receive further\n'
                'instructions from your instructor.\n\n'
                'Enjoy!'.format(student.first_name,
                                passwords_by_username[student.username]))

        email = Email(student.email_address, subject, body)

        email_queue.put(email)

    email_queue.put(None)

    email_thread.join()
