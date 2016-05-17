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

from configuration import GraderConfiguration, ConfigurationError
from repository import Repository
from subprocess_commands import CommandError, directory_exists

from student import Student


def clone_or_pull_repo(local_repo: Repository, remote_repo: Repository):
    if not os.path.isdir(local_repo.path):
        local_repo.clone_from_remote(remote_repo)
        return 'clone'
    else:
        remote_hash = remote_repo.get_head_hash()
        local_hash = local_repo.get_head_hash()

        if remote_hash != local_hash:
            local_repo.pull()
            return 'pull'
        else:
            return ''


def fetch_assignment(assignment, dest_dir, class_name,
                     config: GraderConfiguration):
    remote_reports_repo_dir = config.get_reports_repo_dir(class_name,
                                                          assignment)

    if not directory_exists(remote_reports_repo_dir, ssh=config.ssh):
        print('Assignment {0} does not exist, skipping'.format(assignment))
        return

    print('Fetching assignment {0}'.format(assignment))

    remote_reports_repo = Repository(remote_reports_repo_dir,
                                     assignment, is_local=False,
                                     is_bare=True,
                                     remote_user=config.username,
                                     remote_host=config.host,
                                     ssh=config.ssh)

    assignment_dir = os.path.join(dest_dir, assignment)
    submissions_dir = os.path.join(assignment_dir, 'submissions')

    if not directory_exists(submissions_dir):
        os.makedirs(submissions_dir)
        print('Created {0}'.format(submissions_dir))

    reports_repo_dir = os.path.join(assignment_dir, 'reports')
    reports_repo = Repository(reports_repo_dir, assignment, ssh=config.ssh)

    try:
        action = clone_or_pull_repo(reports_repo, remote_reports_repo)

        if action == 'clone':
            print('Cloned new reports for {0}'.format(assignment))
        elif action == 'pull':
            print('Pulled new reports for {0}'.format(assignment))
    except CommandError as e:
        print('Error in reports repo for {0}:\n{1}'.format(assignment, e),
              file=sys.stderr)
        return

    assert class_name in config.students_by_class

    for student in config.students_by_class[class_name]:
        assert isinstance(student, Student)

        username = student.username

        remote_assignment_repo_dir = student.get_bare_repo_dir(class_name,
                                                               assignment)
        remote_assignment_repo = Repository(remote_assignment_repo_dir,
                                            assignment, is_local=False,
                                            is_bare=True,
                                            remote_user=config.username,
                                            remote_host=config.host,
                                            ssh=config.ssh,
                                            student_username=username)

        assignment_repo_dir = os.path.join(submissions_dir,
                                           student.get_last_first_username())
        assignment_repo = Repository(assignment_repo_dir, assignment,
                                     ssh=config.ssh,
                                     student_username=username)

        try:
            action = clone_or_pull_repo(assignment_repo,
                                        remote_assignment_repo)

            if action == 'clone':
                print('Cloned assignment {0} for {1}'.format(assignment,
                                                             student))
            elif action == 'pull':
                print('Pulled new submission of {0} from {1}'
                      .format(assignment, student))
        except CommandError as e:
            print('Error fetching {0} for {1}'.format(assignment, student))


def fetch_submissions(class_name, dest_dir, assignment_to_fetch):

    if not os.path.isdir(dest_dir):
        sys.exit('{0} does not exist, please create it first'.format(dest_dir))

    try:
        config = GraderConfiguration(single_class_name=class_name)
    except ConfigurationError as e:
        sys.exit(e)

    if class_name not in config.students_by_class:
        sys.exit('Class {0} does not exist'.format(class_name))

    if assignment_to_fetch == '-a':
        assignments_to_fetch = config.get_assignments(class_name)
    else:
        assignments_to_fetch = [assignment_to_fetch]

    for assignment in assignments_to_fetch:
        fetch_assignment(assignment, dest_dir, class_name, config)
