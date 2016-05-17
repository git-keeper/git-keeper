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

import configparser
import csv
import os

from paramiko.client import SSHClient
from subprocess_commands import home_dir_from_username, directory_exists,\
    list_directory, CommandError

from student import Student


class ConfigurationError(Exception):
    pass


class GraderConfiguration:
    def __init__(self, single_class_name=None, on_grading_server=False):
        self.on_grading_server = on_grading_server

        self.config_dir = os.path.expanduser('~/.config/grader')

        if not os.path.isdir(self.config_dir):
            error = '{0} does not exist'.format(self.config_dir)
            raise ConfigurationError(error)

        self.config_filename = os.path.join(self.config_dir, 'grader.conf')

        if not os.path.isfile(self.config_filename):
            error = '{0} does not exist'.format(self.config_filename)
            raise ConfigurationError(error)

        parser = configparser.ConfigParser()

        try:
            parser.read(self.config_filename)
        except configparser.MissingSectionHeaderError:
            error = 'Error reading {0}'.format(self.config_filename)
            raise ConfigurationError(error)

        sections = parser.sections()

        sections.sort()

        if sections != ['email', 'server']:
            error = 'Config file requires two sections: server and email'
            raise ConfigurationError(error)

        try:
            self.username = parser.get('server', 'username')
            self.host = parser.get('server', 'host')
            self.group = parser.get('server', 'group')

            self.from_name = parser.get('email', 'from_name')
            self.from_address = parser.get('email', 'from_address')
            if parser.has_option('email', 'smtp_server'):
                self.smtp_server = parser.get('email', 'smtp_server')
            else:
                self.smtp_server = None
            if parser.has_option('email', 'smtp_port'):
                self.smtp_port = parser.get('email', 'smtp_port')
            else:
                self.smtp_port = None
            if parser.has_option('email', 'email_username'):
                self.email_username = parser.get('email', 'email_username')
            else:
                self.email_username = None
            if parser.has_option('email', 'email_password'):
                self.email_password = parser.get('email', 'email_password')
            else:
                self.email_password = None
        except configparser.NoOptionError as e:
            raise ConfigurationError(e.message)

        if self.on_grading_server:
            self.ssh = None
        else:
            try:
                self.ssh = SSHClient()
                self.ssh.load_system_host_keys()
                self.ssh.connect(self.host, username=self.username)
            except OSError as e:
                error = ('Error opening SSH connection to {0}:\n{1}'
                         .format(self.host, e))
                raise ConfigurationError(error)

        try:
            self.home_dir = home_dir_from_username(self.username, ssh=self.ssh)
        except CommandError as e:
            raise ConfigurationError('Error connecting to {0} via SSH:\n{1}'
                                     .format(self.host, e))

        self.students_by_class = {}
        self.students_csv_filenames_by_class = {}
        self.students_by_username = {}

        for filename in os.listdir(self.config_dir):
            if not filename.endswith('.csv'):
                continue

            class_name, _ = os.path.splitext(filename)

            if single_class_name is not None \
                    and class_name != single_class_name:
                continue

            if ' ' in class_name:
                error = 'Error in class name "{0}".\n'.format(class_name)
                error += 'Class names may not contain spaces'
                raise ConfigurationError(error)

            self.students_by_class[class_name] = []

            filepath = os.path.join(self.config_dir, filename)

            self.students_csv_filenames_by_class[class_name] = filepath

            try:
                with open(filepath) as f:
                    rows = list(csv.reader(f))
            except OSError as e:
                error = 'Error opening {0}:\n{1}'.format(filepath, e)
                raise ConfigurationError(error)

            for row in rows:
                try:
                    student_row = row
                    student = Student(*student_row, ssh=self.ssh)
                    self.students_by_class[class_name].append(student)
                    self.students_by_username[student.username] = student
                except TypeError:
                    row_str = ','.join(row)
                    error = 'Error in {0} at this row:\n{1}'.format(filepath,
                                                                    row_str)
                    raise ConfigurationError(error)

        if len(self.students_by_class) == 0:
            raise ConfigurationError('No classes defined')

        for class_name, students in self.students_by_class.items():
            if len(students) == 0:
                error = 'No students in {0}'.format(class_name)
                raise ConfigurationError(error)

    def get_assignments(self, class_name):
        assignments_dir = os.path.join(self.home_dir, class_name, 'assignments')

        if not directory_exists(assignments_dir, ssh=self.ssh):
            raise ConfigurationError('{0} does not exist'
                                     .format(assignments_dir))

        return list_directory(assignments_dir, ssh=self.ssh)

    def get_reports_repo_dir(self, class_name, assignment):
        repo_dir = os.path.join(self.home_dir, class_name, 'assignments',
                                assignment, assignment + '_reports.git')
        return repo_dir
