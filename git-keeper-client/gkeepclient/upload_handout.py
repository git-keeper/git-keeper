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
from repository import Repository
from subprocess_commands import directory_exists, CommandError

from student import Student


def upload_handout(class_name, local_handout_dir):

    local_handout_dir = os.path.expanduser(local_handout_dir)
    local_handout_dir = os.path.abspath(local_handout_dir)

    handout_name = os.path.basename(local_handout_dir.rstrip('/'))

    if handout_name.count(' ') != 0:
        sys.exit('NO spaces allowed in handout directory')

    if not os.path.isdir(local_handout_dir):
        sys.exit('{0} does not exist'.format(local_handout_dir))

    try:
        config = GraderConfiguration(single_class_name=class_name)
    except ConfigurationError as e:
        sys.exit(e)

    if class_name not in config.students_by_class:
        sys.exit('Class {0} does not exist'.format(class_name))

    remote_handout_repo_basename = handout_name + '.git'
    remote_handout_repo_dir = os.path.join('/home/git', class_name,
                                           remote_handout_repo_basename)

    if directory_exists(remote_handout_repo_dir, ssh=config.ssh):
        sys.exit('{0} already exists on the grader'
                 .format(remote_handout_repo_dir))

    local_handout_repo = Repository(local_handout_dir, handout_name)
    if not local_handout_repo.is_initialized():
        print('Initializing local git repository in {0}'
              .format(local_handout_dir))
        try:
            local_handout_repo.init()
            local_handout_repo.add_all_and_commit('Initial commit')
        except CommandError as e:
            sys.exit('Error initializing local repository:\n{0}'
                     .format(e))
    else:
        print('{0} is already a git repository, it will be pushed'
              .format(local_handout_dir))

    print('Creating a bare repository on the grader at this path:\n{0}'
          .format(remote_handout_repo_dir))

    remote_handout_repo = Repository(remote_handout_repo_dir, handout_name,
                                     is_local=False, is_bare=True,
                                     remote_user=config.username,
                                     remote_host=config.host,
                                     ssh=config.ssh)
    try:
        remote_handout_repo.init()
    except CommandError as e:
        sys.exit('Error initializing remote bare repository:\n{0}'.format(e))

    print('Setting the remote of the local repository')
    try:
        local_handout_repo.set_remote(remote_handout_repo)
    except CommandError as e:
        print('Error setting remote:\n{0}'.format(e))
        print('Set the remote manually if need be')

    print('Pushing local handout to the grader')
    try:
        local_handout_repo.push(remote_handout_repo)
    except CommandError as e:
        sys.exit('Error pushing handout:\n{0}'.format(e))

    email_queue = Queue()
    email_thread = Thread(target=process_email_queue, args=(email_queue,
                                                            class_name,
                                                            config))
    email_thread.start()

    for student in config.students_by_class[class_name]:
        assert isinstance(student, Student)
        clone_url = '{0}@{1}:{2}'.format(student.username, config.host,
                                         remote_handout_repo_dir)
        body = 'Clone URL:\n{0}'.format(clone_url)
        subject = 'New handout: {0}'.format(handout_name)

        email_queue.put(Email(student.email_address, subject, body))

    email_queue.put(None)
    email_thread.join()
