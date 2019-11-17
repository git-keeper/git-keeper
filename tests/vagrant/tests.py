# Copyright 2017 Nathan Sommer and Ben Coleman
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
This module provides a means to test git-keeper. These are high level tests in
which the server is run in a VM which is managed by Vagrant. Client code is run
locally and interacts with the server. A mock SMTP server runs on the VM and
captures outgoing emails to files. The state of the server is checked using
gkeep queries and by examining the email files.

This may be run as a standalone script or with pytest. Make sure the working
directory is the directory that this file is in.

Once the tests are finished running, the VM will still be running to allow
for manual inspection and interaction. Run vagrant destroy to kill the VM.

Here is the structure of the directory that contains these tests:

.
├── Vagrantfile
├── assignments
│   └── <faculty>
│       └── <class>
│           └── <assignment>
│               ├── base_code
│               │   └── ...
│               ├── email.txt
│               ├── solutions
│               │   ├── <student or faculty username>
│               │   │   ├── expected_output.txt
│               │   │   └── files
│               │   │       └── ...
│               │   └── ...
│               └── tests
│                   └── action.sh
├── faculty.csv
├── mysmtpd.py
├── server.cfg
├── start_server_services.sh
├── student_csv_files
│   └── <faculty>
│       └── <class>.csv
└── tests.py

When writing new tests, look at test_one_class_two_students() as an example.
In addition to adding new things to the directory structure, you will need to
write new test code to define the order in which things are added, solutions
are submitted, etc.

To add test faculty account, edit faculty.csv. To add a class, put a new CSV
file in student_csv_files under the appropriate faculty subdirectory. To add
assignments, put them in the assignments directory following the above
structure.
"""


import os
import re
from collections import defaultdict
from tempfile import TemporaryDirectory
from time import sleep

import sys
import vagrant

from gkeepcore.shell_command import run_command, run_command_in_directory


GKEEP_CONFIG_PATH = 'faculty_gkeep_configs'
ASSIGNMENTS_PATH = 'assignments'
STUDENT_CSV_PATH = 'student_csv_files'


def run_gkeep_command(faculty_username, command):
    """
    Run a gkeep command locally using a test faculty config file.

    :param faculty_username: username of the test faculty account
    :param command: command to run
    :return: output of the command
    """

    return run_command('gkeep -f {}/{}.cfg {}'
                       .format(GKEEP_CONFIG_PATH, faculty_username, command))


def check_email_counts(email_counts, port):
    """
    Ensure that the email files on the server match what we expect based on
    email_counts.

    :param email_counts: a dictionary mapping usernames to counts
    :param port: SSH port of the test VM
    """

    expected_filenames = set()
    for username, count in email_counts.items():
        for x in range(1, count + 1):
            expected_filenames.add(get_email_filename(username, x))

    # we'll try listing the email files numerous times since there will be
    # a delay before the email is sent
    max_tries = 10
    tries = 0
    found = False

    server_filenames = set()

    while not found and tries < max_tries:
        server_filenames = set(run_as_keeper('ls email', port).split())

        if server_filenames == expected_filenames:
            found = True
        else:
            tries += 1
            sleep(0.1)

    if not found:
        error = 'Expected to see these emails on the server:\n'
        for filename in sorted(expected_filenames):
            error += '{}\n'.format(filename)
        error += 'Instead, I saw these:'
        for filename in sorted(server_filenames):
            error += '{}\n'.format(filename)

        sys.exit(error)


def get_email_filename(username, email_number):
    """
    Build and return the filename for an email on the server.

    The filenames are of the form <username>_<number>.txt

    :param username: username that the email was sent to
    :param email_number: number of the email
    :return: the filename of the email
    """
    return '{}_{}.txt'.format(username, email_number)


class Class:
    """
    Provides functionality for testing a class.
    """

    def __init__(self, faculty_username, class_name, email_counts,
                 users_with_injected_keys, port):
        """
        Constructor. Sets up attributes.

        :param faculty_username: username of the faculty account that owns the
        class
        :param class_name: name of the class
        :param email_counts: dictionary mapping usernames to the expected
        number of emails that have been sent to that user
        :param users_with_injected_keys: set of usernames that already have
        the local public key added to their authorized_keys file
        :param port: port to the VM's SSH server
        """

        self.faculty_username = faculty_username
        self.class_name = class_name
        student_csv_filename = '{}.csv'.format(self.class_name)
        self.student_csv_path = os.path.join('student_csv_files',
                                             self.faculty_username,
                                             student_csv_filename)
        self.email_counts = email_counts
        self.users_with_injected_keys = users_with_injected_keys
        self.port = port

        self.email_contents = dict()
        self.report_contents = defaultdict(list)

        self.student_usernames = set()

        with open(self.student_csv_path) as f:
            for line in f:
                match = re.search('[\s,](\w+)@', line)
                if match:
                    self.student_usernames.add(match.group(1))

    def _gkeep(self, command):
        """
        Run a gkeep command as the faculty who owns the class.

        :param command: command to run
        :return: output of the command
        """

        return run_gkeep_command(self.faculty_username, command)

    def add(self):
        """
        Add the class to the git-keeper server and check the state.

        Checked assertions:
            - students in CSV match students in query
            - class is present when querying for classes
            - the proper number of emails have been sent
        """

        # add the class to the server
        self._gkeep('add {} {}'.format(self.class_name, self.student_csv_path))

        student_query_result = self._gkeep('query students')

        # collect the student usernames from the query in this set
        query_student_usernames = set()

        current_class = ''
        for line in student_query_result.split('\n'):
            # the query will list all students in all classes, so we need to
            # update the current class whenever we see a line like '<class>:'
            match = re.match('(\S+):$', line)
            if match:
                current_class = match.group(1)
                continue

            if current_class == self.class_name:
                match = re.search('<(.+)@', line)
                if match:
                    query_student_usernames.add(match.group(1))

        # the student usernames we collected from the query should match the
        # usernames from the class csv file
        assert self.student_usernames == query_student_usernames

        # for users that were just added, we need to add the local public
        # key to that user's ~/.ssh/authorized_keys file on the server
        for username in self.student_usernames:
            if username not in self.users_with_injected_keys:
                inject_public_key(username, self.port)
                self.users_with_injected_keys.add(username)
                # if this is the first class the student was added to, they'll
                # get an email
                self.email_counts[username] += 1

        # the class we just added should be in the list of classes when we
        # query for classes
        classes_query_result = self._gkeep('query classes')
        assert self.class_name in classes_query_result.split('\n')

        check_email_counts(self.email_counts, self.port)

    def upload(self, assignment_name):
        """
        Upload an assignment and check the state.

        Checked assertions:
            - assignment shows up as unpublished in query
            - email counts are as expected

        :param assignment_name: name of the assignment
        """

        assignment_path = os.path.join(ASSIGNMENTS_PATH, self.faculty_username,
                                       self.class_name, assignment_name)

        assert os.path.isdir(assignment_path)

        self._gkeep('upload {} {}'.format(self.class_name, assignment_path))

        # since we just uploaded an assignment and it is unpublished, we should
        # see 'U <assignment>' from an assignments query
        assignments_query_result = self._gkeep('query assignments')
        expected_string = 'U {}'.format(assignment_name)
        assert expected_string in assignments_query_result.split('\n')

        # the faculty gets an email with a clone URL to test the assignment
        self.email_counts[self.faculty_username] += 1

        check_email_counts(self.email_counts, self.port)

    def publish(self, assignment_name):
        """
        Publish an assignment and check the state.

        Checked assertions:
            - assignment shows up as published in query
            - email counts are as expected

        :param assignment_name: name of the assignment
        """

        self._gkeep('publish {} {}'.format(self.class_name, assignment_name))

        # we should now see 'P <assignment>' from an assignments query
        assignments_query_result = self._gkeep('query assignments')
        expected_string = 'P {}'.format(assignment_name)
        assert expected_string in assignments_query_result.split('\n')

        # all the students are sent an email with a clone URL
        for username in self.student_usernames:
            self.email_counts[username] += 1

        check_email_counts(self.email_counts, self.port)

    def clone_and_push_solution(self, assignment_name, student_username,
                                commit_message='test'):
        """
        Clone an assignment and then push a solution back to the server.

        Updates self.email_counts, self.email_contents, and
        self.report_contents but does not check that they are correct.

        :param assignment_name: name of the assignment
        :param student_username: username of the submitter
        :param commit_message: commit message, defaults to 'test'
        """

        # we'll clone to a temporary directory
        temp_dir = TemporaryDirectory()
        temp_path = temp_dir.name

        # ASSIGNMENTS_PATH/<faculty>/<class>/<assignment>/solutions/<student>
        solution_path = ('{}/{}/{}/{}/solutions/{}'
                         .format(ASSIGNMENTS_PATH, self.faculty_username,
                                 self.class_name, assignment_name,
                                 student_username))
        solution_files_path = os.path.join(solution_path, 'files')

        with open(os.path.join(solution_path, 'expected_output.txt')) as f:
            expected_output = f.read()

        # FIXME: the clone URL could be extracted from the email
        run_command('git clone ssh://{}@localhost:{}/home/{}/{}/{}/{}.git {}'
                    .format(student_username, self.port, student_username,
                            self.faculty_username, self.class_name,
                            assignment_name, temp_path))

        # remove the original files, copy in the solution files, add, commit,
        # and push
        run_command('rm -rf {}/*'.format(temp_path))
        run_command('cp -r {}/* {}/'.format(solution_files_path, temp_path))
        run_command_in_directory(temp_path, 'git add -A')
        run_command_in_directory(temp_path,
                                 'git commit -m "{}"'.format(commit_message))
        run_command_in_directory(temp_path, 'git push')

        # the student will receive an email with feedback
        self.email_counts[student_username] += 1

        # the feedback will be in this file on the server
        email_filename = \
            get_email_filename(student_username,
                               self.email_counts[student_username])

        # store the expected output. later call check_email_contents() and
        # check_repots() to make sure the content is as expected
        self.email_contents[email_filename] = expected_output
        if student_username != self.faculty_username:
            self.report_contents[(assignment_name,
                                 student_username)].append(expected_output)

        check_email_counts(self.email_counts, self.port)

    def check_email_contents(self):
        """
        Ensure that the email contents in self.email_contents match the emails
        on the server.
        """

        for filename in self.email_contents:
            file_contents = run_as_keeper('cat email/{}'.format(filename),
                                          self.port)

            # the first two lines of the email are the from address and the
            # subject, the third is a blank line, the rest is the body
            body = '\n'.join(file_contents.splitlines()[3:]) + '\n'

            assert body == self.email_contents[filename]

    def check_reports(self):
        """
        Ensure that the report contents in self.report_contents match the
        contents of the fetched reports.
        """

        temp_dir = TemporaryDirectory()

        self._gkeep('fetch class_one all {}'.format(temp_dir.name))

        for (assignment_name, student_username), report_list in \
                self.report_contents.items():
            reports_path = os.path.join(temp_dir.name, assignment_name,
                                        'reports')

            student_report_dir = None
            for student_dir in os.listdir(reports_path):
                if student_dir.endswith(student_username):
                    student_report_dir = student_dir

            assert student_report_dir is not None

            student_report_path = os.path.join(reports_path,
                                               student_report_dir)

            report_filenames = sorted([x
                                       for x in os.listdir(student_report_path)
                                       # skip the .placeholder file
                                       if not x.startswith('.')])

            for i, report_filename in enumerate(report_filenames):
                path = os.path.join(student_report_path, report_filename)
                with open(path) as f:
                    contents = f.read()
                assert contents == report_list[i]


def get_public_key():
    """
    Get the local public key of the user running the tests.

    Assumes the key resides in ~/.ssh/id_rsa.pub

    :return: SSH public key
    """

    public_key_path = os.path.expanduser('~/.ssh/id_rsa.pub')

    assert os.path.isfile(public_key_path)

    with open(public_key_path) as f:
        public_key = f.read().strip()

    return public_key


def run_as_keeper(command, port):
    """
    Run a command on the server VM as the keeper user.

    :param command: command to run
    :param port: SSH port on the server
    :return: output of the command
    """

    full_command = 'ssh -p {} keeper@localhost "{}"'.format(port, command)
    return run_command(full_command)


def inject_public_key(user, port):
    """
    Add the local public SSH key to the authorized_keys file for a user on the
    server.

    :param user: user on the server
    :param port: SSH port on the server
    """

    run_as_keeper('sudo mkdir -p ~{}/.ssh'.format(user), port)
    run_as_keeper("sudo bash -c 'echo \\\"{}\\\" >> ~{}/.ssh/authorized_keys'"
                  .format(get_public_key(), user), port)
    run_as_keeper('sudo chown -R {}:{} ~{}/.ssh'.format(user, user, user),
                  port)
    run_as_keeper('sudo chmod 700 ~{}/.ssh'.format(user), port)
    run_as_keeper('sudo chmod 600 ~{}/.ssh/authorized_keys'.format(user), port)


def write_provision_script():
    """
    Write server_provision.sh, the Vagrant provision script to be run when
    setting up the VM.
    """

    text = '''#!/usr/bin/env bash

# install dependencies
apt-get update
apt-get install -y python3 python3-setuptools git

# add the keeper user, give it sudo privledges, and put the host machine's
# public key in ~/.ssh/authorized_keys
useradd -m -U -s /bin/bash keeper
echo keeper:keeper | chpasswd
echo "keeper ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/keeper
mkdir -p ~keeper/.ssh
echo "{}" >> ~keeper/.ssh/authorized_keys
chown -R keeper:keeper ~keeper/.ssh
chmod 700 ~keeper/.ssh
chmod 600 ~keeper/.ssh/authorized_keys

# stop exim4 to free up port 25
systemctl stop exim4.service
systemctl disable exim4.service
'''.format(get_public_key())

    with open('server_provision.sh', 'w') as f:
        f.write(text)


def write_faculty_client_cfg(faculty_username, port):
    """
    Write a gkeep configuration file for a test faculty account.

    Config is written to GKEEP_CONFIG_DIR/<faculty_username>.cfg

    :param faculty_username: username of the test faculty account
    :param port: SSH port of the server
    """

    if not os.path.isdir(GKEEP_CONFIG_PATH):
        os.makedirs(GKEEP_CONFIG_PATH)

    text = '''[server]
host = localhost
ssh_port = {}
username = {}
'''.format(port, faculty_username)

    file_path = os.path.join(GKEEP_CONFIG_PATH,
                             '{}.cfg'.format(faculty_username))

    with open(file_path, 'w') as f:
        f.write(text)


def start_vm():
    """
    Start the Vagrant VM and return the SSH port for the server.

    :return: SSH port
    """

    v = vagrant.Vagrant()
    v.destroy()
    write_provision_script()
    v.up()

    port = int(v.port())

    # connect via SSH with no host key checking so the server gets added to
    # known_hosts
    run_command('ssh -o StrictHostKeyChecking=no -p {} keeper@localhost true'
                .format(port))

    return port


def install_gitkeeper(port):
    """
    Copy git-keeper to the VM and install git-keeper-core and git-keeper-server

    :param port: SSH port for the VM
    """

    run_command('scp -r -P {} {} keeper@localhost:'
                .format(port, os.path.abspath('../..')))
    run_as_keeper('cd git-keeper/git-keeper-core; '
                  'sudo python3 setup.py install', port)
    run_as_keeper('cd git-keeper/git-keeper-server; '
                  'sudo python3 setup.py install', port)


def copy_needed_files(port):
    """
    Copies the following to the server:
        - server.cfg
        - faculty.csv
        - mysmtpd.py

    :param port: SSH port for the VM
    """

    run_command('scp -P {} server.cfg faculty.csv mysmtpd.py keeper@localhost:'
                .format(port))


def start_services(port):
    """
    Start mystmpd.py and gkeepd on the server in the background.

    Outputs from the 2 programs are stored in mysmtpd.out and gkeepd.out

    :param port: SSH port for the VM
    """

    run_as_keeper('mkdir email', port)
    run_as_keeper('nohup sudo python3 mysmtpd.py 25 email > mysmtpd.out 2>&1 &',
                  port)
    run_as_keeper('nohup gkeepd > gkeepd.out 2>&1 &', port)

    # give gkeepd a chance to start fully
    sleep(2)


def test_one_class_two_students():
    """
    Test normal use cases for git-keeper.

    Creates the class class_one owned by the faculty user faculty_one. Two
    students are added to the class, student_one and student_two. The
    assignment python_print is added. The faculty and both students push
    solutions.
    """

    port = start_vm()
    install_gitkeeper(port)
    copy_needed_files(port)
    start_services(port)

    # give the services some time to start
    sleep(5)

    write_faculty_client_cfg('faculty_one', port)
    inject_public_key('faculty_one', port)

    users_with_injected_keys = {'faculty_one'}
    email_counts = defaultdict(int)

    # faculty is emailed about account
    email_counts['faculty_one'] += 1

    # this object will be used to interact with the server
    class_one = Class('faculty_one', 'class_one', email_counts,
                      users_with_injected_keys, port)

    class_one.add()

    class_one.upload('python_print')
    class_one.clone_and_push_solution('python_print', 'faculty_one')
    class_one.publish('python_print')
    class_one.clone_and_push_solution('python_print', 'student_one')
    class_one.clone_and_push_solution('python_print', 'student_two')

    class_one.check_email_contents()
    class_one.check_reports()


if __name__ == '__main__':
    test_one_class_two_students()
