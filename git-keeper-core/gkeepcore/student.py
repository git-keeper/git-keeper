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

from repository import Repository
from subprocess_commands import home_dir_from_username, directory_exists,\
    list_directory


class StudentException(Exception):
    pass


class Student:
    def __init__(self, last_name, first_name, email_address, ssh=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email_address
        self.ssh = ssh

        split_email = self.email_address.split('@')

        if len(split_email) != 2:
            error = '{0} does not appear to be a valid email address'\
                .format(email_address)
            raise StudentException(error)

        self.username = split_email[0]

        self.home_dir = home_dir_from_username(self.username, ssh=self.ssh)

    def __repr__(self):
        return '{0} {1} ({2})'.format(self.first_name, self.last_name,
                                      self.username)

    def get_bare_repo_dir(self, class_name, assignment):
        return os.path.join(self.home_dir, class_name, assignment + '.git')

    def get_class_repositories(self, class_dir):
        repos = []

        class_path = os.path.join(self.home_dir, class_dir)
        if not directory_exists(class_path, ssh=self.ssh):
            return repos

        for name in list_directory(class_path, ssh=self.ssh):
            path = os.path.join(class_path, name)
            if directory_exists(path, ssh=self.ssh) and name.endswith('.git'):
                assignment, _ = os.path.splitext(name)
                if self.ssh is not None:
                    repos.append(Repository(path, assignment, is_bare=True,
                                            is_local=False, ssh=self.ssh,
                                            student_username=self.username))
                else:
                    repos.append(Repository(path, assignment, is_bare=True,
                                            student_username=self.username))

        return repos

    def get_last_first_username(self):
        lower_first_name = self.first_name.lower().replace(' ', '')
        lower_last_name = self.last_name.lower().replace(' ', '')

        return '{0}_{1}_{2}'.format(lower_last_name, lower_first_name,
                                    self.username)
