import os
import re
import sys
from collections import defaultdict
from tempfile import TemporaryDirectory
from time import sleep

import vagrant

from gkeepcore.shell_command import run_command, run_command_in_directory


def run_gkeep_command(faculty_username, command):
    """
    Run a gkeep command locally using a test faculty config file.

    :param faculty_username: username of the test faculty account
    :param command: command to run
    :return: output of the command
    """

    return run_command('gkeep -f faculty_gkeep_configs/{}.cfg {}'
                       .format(faculty_username, command))


def check_email_counts(expected_email_counts, port):
    """
    Ensure that the number of emails to each user matches the expected counts
    in expected_email_counts.

    :param expected_email_counts: a dictionary mapping usernames to counts
    :param port: SSH port of the test VM
    """

    email_counts = defaultdict(int)

    filenames = run_as_keeper('ls email', port).split()

    for filename in filenames:
        match = re.search('(\S+)_(\d+).txt', filename)
        username = match.group(1)
        email_counts[username] += 1

    for username in expected_email_counts:
        assert expected_email_counts[username] == email_counts[username]


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

        self._gkeep('add {} {}'.format(self.class_name, self.student_csv_path))

        student_query_result = self._gkeep('query students')

        query_student_usernames = set()

        for line in student_query_result.split('\n'):
            match = re.search('<(.+)@', line)
            if match:
                query_student_usernames.add(match.group(1))

        assert self.student_usernames == query_student_usernames

        for username in self.student_usernames:
            if username not in self.users_with_injected_keys:
                inject_public_key(username, self.port)
                self.users_with_injected_keys.add(username)
                # if this is the first class the student was added to, they'll
                # get an email
                self.email_counts[username] += 1

        classes_query_result = self._gkeep('query classes')

        assert self.class_name in classes_query_result.split('\n')

        # wait for emails to be sent
        sleep(2 * len(self.student_usernames) + 1)

        check_email_counts(self.email_counts, self.port)

    def upload(self, assignment_name):
        """
        Upload an assignment and check the state.

        Checked assertions:
            - assignment shows up as unpublished in query
            - email counts are as expected

        :param assignment_name: name of the assignment
        """
        assignment_path = os.path.join('assignments', self.faculty_username,
                                       self.class_name, assignment_name)

        assert os.path.isdir(assignment_path)

        self._gkeep('upload {} {}'.format(self.class_name, assignment_path))

        assignments_query_result = self._gkeep('query assignments')

        expected_string = 'U {}'.format(assignment_name)

        assert expected_string in assignments_query_result.split('\n')

        self.email_counts[self.faculty_username] += 1

        # wait for email to be sent
        sleep(3)

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

        assignments_query_result = self._gkeep('query assignments')

        expected_string = 'P {}'.format(assignment_name)

        assert expected_string in assignments_query_result.split('\n')

        for username in self.student_usernames:
            self.email_counts[username] += 1

        # wait for emails to be sent
        sleep(2 * len(self.student_usernames) + 1)

        check_email_counts(self.email_counts, self.port)

    def clone_and_push_solution(self, assignment_name, student_username,
                                solution_path, commit_message='test'):
        """
        Clone an assignment and then push a solution back to the server.

        Updates self.email_counts, self.email_contents, and
        self.report_contents but does not check that they are correct.

        :param assignment_name: name of the assignment
        :param student_username: username of the submitter
        :param solution_path: path to the solution
        :param commit_message: commit message, defaults to 'test'
        """

        temp_dir = TemporaryDirectory()
        temp_path = temp_dir.name

        solution_files_path = os.path.join(solution_path, 'files')
        with open(os.path.join(solution_path, 'expected_output.txt')) as f:
            expected_output = f.read()

        run_command('git clone ssh://{}@localhost:{}/home/{}/{}/{}/{}.git {}'
                    .format(student_username, self.port, student_username,
                            self.faculty_username, self.class_name,
                            assignment_name, temp_path))

        run_command('rm -rf {}/*'.format(temp_path))
        run_command('cp -r {}/* {}/'.format(solution_files_path, temp_path))
        run_command_in_directory(temp_path,
                                 'git commit -am "{}"'.format(commit_message))
        run_command_in_directory(temp_path, 'git push')

        self.email_counts[student_username] += 1

        email_filename = ('{}_{}.txt'
                          .format(student_username,
                                  self.email_counts[student_username]))

        self.email_contents[email_filename] = expected_output
        if student_username != self.faculty_username:
            self.report_contents[(assignment_name,
                                 student_username)].append(expected_output)

    def check_email_contents(self):
        """
        Ensure that the email contents in self.email_contents match the emails
        on the server.
        """

        for filename in self.email_contents:
            file_contents = run_as_keeper('cat email/{}'.format(filename),
                                          self.port)

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

            for student_dir in os.listdir(reports_path):
                if student_dir.endswith(student_username):
                    student_report_dir = student_dir

            student_report_path = os.path.join(reports_path,
                                               student_report_dir)

            report_filenames = sorted([x
                                       for x in os.listdir(student_report_path)
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

    if not os.path.isfile(public_key_path):
        sys.exit('{} does not exist'.format(public_key_path))

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

apt-get update
apt-get install -y python3 python3-setuptools git
useradd -m -U -s /bin/bash keeper
echo keeper:keeper | chpasswd
echo "keeper ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/keeper
mkdir -p ~keeper/.ssh
echo "{}" >> ~keeper/.ssh/authorized_keys
chown -R keeper:keeper ~keeper/.ssh
chmod 700 ~keeper/.ssh
chmod 600 ~keeper/.ssh/authorized_keys
systemctl stop exim4.service
systemctl disable exim4.service
'''.format(get_public_key())

    with open('server_provision.sh', 'w') as f:
        f.write(text)


def write_faculty_client_cfg(faculty_username, port):
    """
    Write a gkeep configuration file for a test faculty account.

    Config is written to faculty_gkeep_configs/<faculty_username>.cfg

    :param faculty_username: username of the test faculty account
    :param port: SSH port of the server
    """

    configs_path = 'faculty_gkeep_configs'

    if not os.path.isdir(configs_path):
        os.makedirs(configs_path)

    text = '''[server]
host = localhost
ssh_port = {}
username = {}
'''.format(port, faculty_username)

    file_path = os.path.join(configs_path, '{}.cfg'.format(faculty_username))

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

    print('Bringing VM up')
    v.up()
    print('VM up')

    port = int(v.port())

    print('copying git-keeper')
    run_command('scp -r -P {} ../../../git-keeper keeper@localhost:'
                .format(port))
    print('installing git-keeper-core')
    run_as_keeper('cd git-keeper/git-keeper-core; '
                  'sudo python3 setup.py install', port)
    print('installing git-keeper-server')
    run_as_keeper('cd git-keeper/git-keeper-server; '
                  'sudo python3 setup.py install', port)

    print('copying config files')
    run_command('scp -P {} server.cfg keeper@localhost:'.format(port))
    run_command('scp -P {} faculty.csv keeper@localhost:'.format(port))

    print('copying mysmtpd.py')
    run_command('scp -P {} mysmtpd.py keeper@localhost:'.format(port))
    print('copying services script')
    run_command('scp -P {} start_server_services.sh keeper@localhost:'
                .format(port))
    print('starting services')
    run_as_keeper('nohup bash start_server_services.sh > /dev/null 2>&1 &',
                  port)

    return port


def test_happy_paths():
    """
    Test the "normal" use cases for git-keeper.
    """

    port = start_vm()

    # give the services some time to start
    sleep(5)

    write_faculty_client_cfg('faculty_one', port)
    inject_public_key('faculty_one', port)

    users_with_injected_keys = {'faculty_one'}
    email_counts = defaultdict(int)

    email_counts['faculty_one'] += 1

    class_one = Class('faculty_one', 'class_one', email_counts,
                      users_with_injected_keys, port)

    class_one.add()

    class_one.upload('python_print')
    class_one.clone_and_push_solution('python_print', 'faculty_one',
                                      'assignments/faculty_one/class_one/python_print/solutions/faculty_one')
    class_one.publish('python_print')
    class_one.clone_and_push_solution('python_print', 'student_one',
                                      'assignments/faculty_one/class_one/python_print/solutions/student_one')
    class_one.clone_and_push_solution('python_print', 'student_two',
                                      'assignments/faculty_one/class_one/python_print/solutions/student_two')

    # wait for emails
    sleep(6)

    check_email_counts(class_one.email_counts, port)
    class_one.check_email_contents()

    class_one.check_reports()


if __name__ == '__main__':
    test_happy_paths()
