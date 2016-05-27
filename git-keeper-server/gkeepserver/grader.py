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
from queue import Queue, Empty
from tempfile import TemporaryDirectory
from threading import Thread
from time import strftime, time, sleep

from configuration import GraderConfiguration, ConfigurationError
from email_sender import Email, process_email_queue
from inotify_monitors import PushMonitor
from repository import Repository
from subprocess_commands import call_action, CommandError

import locator
from student import Student


def write_report(file_path, output, report_repo: Repository,
                 commit_message='new submission'):
    try:
        with open(file_path, 'w') as f:
            f.write(output)
    except OSError as e:
        print('Error opening {0}:\n{1}'.format(file_path, e), file=sys.stderr)
        report_repo = None

    if report_repo is not None:
        report_repo.add_all_and_commit(commit_message)
        report_repo.push()


def create_failure_email(to_address, assignment):
    subject = '{0}: Failed to process submission - contact instructor'.format(assignment)
    body = ['Your submission was received, but something went wrong.',
            'This is likely your instructor\'s fault, not yours.',
            'Please contact your instructor about this error!']

    return Email(to_address, subject, body)


def report_failure(error, to_address, assignment, email_queue: Queue,
                   report_path, report_repo):
    print('FAILURE: {0}'.format(error), file=sys.stderr)
    write_report(report_path, error, report_repo,
                 commit_message='new submission, action.sh failure')
    email_queue.put(create_failure_email(to_address, assignment))


def run_tests(student_repo: Repository, test_repo: Repository,
              report_repo: Repository, call_action_path, student: Student,
              email_queue: Queue):
    starting_dir = os.getcwd()

    code_tempdir = TemporaryDirectory()
    test_tempdir = TemporaryDirectory()
    report_tempdir = TemporaryDirectory()

    code_path = code_tempdir.name
    test_path = test_tempdir.name
    report_path = report_tempdir.name

    report_file_path = ''

    tmp_report_repo = None
    try:
        tmp_report_repo = report_repo.clone_to(report_path)
        student_repo.clone_to(code_path)
        test_repo.clone_to(test_path)
    except CommandError as e:
        error = 'Failed to clone:\n{0}'.format(e)
        report_failure(error, student.email_address, student_repo.assignment,
                       email_queue, report_file_path, tmp_report_repo)
        os.chdir(starting_dir)
        return

    report_filename = 'report-{0}.txt'.format(strftime('%Y-%m-%d-%H:%M:%S-%Z'))

    for item in os.listdir(report_path):
        item_path = os.path.join(report_path, item)
        if os.path.isdir(item_path) and student.username in item:
            report_file_path = os.path.join(item_path, report_filename)
            break

    os.chdir(test_path)

    try:
        output = call_action(call_action_path, code_path, student.first_name,
                             student.last_name, student.username,
                             student.email_address)
    except CommandError as e:
        error = '!!!  ERROR: SCRIPT RETURNED NON-ZERO EXIT CODE  !!!\n\n'
        error += str(e)
        report_failure(error, student.email_address, student_repo.assignment,
                       email_queue, report_file_path, tmp_report_repo)
        os.chdir(starting_dir)
        return

    write_report(report_file_path, output, tmp_report_repo)

    email_subject = student_repo.assignment + ' submission test results'
    email_queue.put(Email(student.email_address, email_subject, output))

    os.chdir(starting_dir)


def add_update_flag_watches(class_name, config: GraderConfiguration,
                            push_monitor: PushMonitor,
                            repos_by_update_flag_path,
                            assignment=None):
    for student in config.students_by_class[class_name]:
        assert isinstance(student, Student)
        repos = student.get_class_repositories(class_name)
        for repo in repos:
            assert isinstance(repo, Repository)
            update_flag_path = repo.get_update_flag_path()
            if update_flag_path not in repos_by_update_flag_path \
                    or assignment == repo.assignment:
                repos_by_update_flag_path[update_flag_path] = repo
                push_monitor.add_file(update_flag_path)


def email_students_new_assignment(class_name, assignment, email_file_path,
                                  config, email_queue):
    relative_repo_path = '{0}/{1}.git'.format(class_name, assignment)
    email_subject = 'New assignment: {0}'.format(assignment)

    try:
        with open(email_file_path) as f:
            email_body_from_file = f.read()
    except OSError as e:
        print('Error opening {0}'.format(email_file_path), file=sys.stderr)
        email_body_from_file = ''

    for student in config.students_by_class[class_name]:
        assert isinstance(student, Student)
        clone_url = '{0}@{1}:{2}'.format(student.username, config.host,
                                         relative_repo_path)

        email_body = 'Clone URL:\n{0}\n\n{1}'.format(clone_url,
                                                     email_body_from_file)

        email_queue.put(Email(student.email_address, email_subject, email_body))


def main():
    if len(sys.argv) != 2:
        sys.exit('Usage: {0} <class name>'.format(sys.argv[0]))

    class_name = sys.argv[1]

    try:
        config = GraderConfiguration(on_grading_server=True)
    except ConfigurationError as e:
        sys.exit(e)

    if class_name not in config.students_by_class:
        sys.exit('No student CSV file for {0}'.format(class_name))

    call_action_path = os.path.join(locator.module_path(), 'call_action.sh')

    if not os.path.isfile(call_action_path):
        sys.exit('{0} does not exist'.format(call_action_path))

    update_flag_queue = Queue()
    push_monitor = PushMonitor(update_flag_queue)

    # stores student submission repositories indexed by their
    # update_flag file paths, which are watched by inotify
    repos_by_update_flag_path = {}

    add_update_flag_watches(class_name, config, push_monitor,
                            repos_by_update_flag_path)

    assignments_path = os.path.join(config.home_dir, class_name, 'assignments')

    active_assignments = set(os.listdir(assignments_path))

    print('Current assignments:')
    for assignment in active_assignments:
        print(assignment)

    last_assignment_poll_time = time()

    email_queue = Queue()
    email_thread = Thread(target=process_email_queue, args=(email_queue,
                                                            class_name,
                                                            config))
    email_thread.start()

    print('daemon initialized, waiting for pushes')

    while True:
        try:
            if time() - last_assignment_poll_time > 5:
                current_assignments = set(os.listdir(assignments_path))
                last_assignment_poll_time = time()

                if current_assignments != active_assignments:
                    new_assignments = \
                        current_assignments.difference(active_assignments)
                    for new_assignment in new_assignments:
                        print('I see a new directory for assignment {0}'
                              .format(new_assignment))
                        new_assignment_path = os.path.join(assignments_path,
                                                           new_assignment)
                        print('Path:', new_assignment_path)
                        email_file_path = os.path.join(new_assignment_path,
                                                       'email.txt')

                        retries = 0
                        while (not os.path.isfile(email_file_path) and
                               retries < 10):
                            retries += 1
                            print('I see no email.txt, retry', retries)
                            sleep(2)

                        if os.path.isfile(email_file_path):
                            print('email.txt exists, adding assignment')
                            add_update_flag_watches(class_name, config,
                                                    push_monitor,
                                                    repos_by_update_flag_path,
                                                    assignment=new_assignment)
                            email_students_new_assignment(class_name,
                                                          new_assignment,
                                                          email_file_path,
                                                          config, email_queue)
                        else:
                            print('No email.txt, skipping assignment')

                    active_assignments = current_assignments

            update_flag_path = update_flag_queue.get(block=True, timeout=0.5)
            repo = repos_by_update_flag_path[update_flag_path]
            assert isinstance(repo, Repository)
            student = config.students_by_username[repo.student_username]
            print('{0}: New push from {1}'.format(class_name, student.username))
            test_repo_path = os.path.join(assignments_path,
                                          repo.assignment,
                                          repo.assignment + '_tests.git')
            reports_repo_path = os.path.join(assignments_path,
                                             repo.assignment,
                                             repo.assignment + '_reports.git')
            test_repo = Repository(test_repo_path, repo.assignment,
                                   is_bare=True)
            reports_repo = Repository(reports_repo_path, repo.assignment,
                                      is_bare=True)
            run_tests(repo, test_repo, reports_repo, call_action_path,
                      student, email_queue)
        except Empty:
            pass
        except KeyboardInterrupt:
            print('Keyboard interrupt caught')
            break

    print('Shutting down')

    email_queue.put(None)
    emailer_shutdown_time = 10
    print('Waiting up to {0} seconds for emailer to shut down'
          .format(emailer_shutdown_time))

    email_thread.join(timeout=emailer_shutdown_time)


if __name__ == '__main__':
    main()
