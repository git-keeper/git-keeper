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

from subprocess_commands import scp_file, git_remote_add, git_push_explicit_url,\
    git_init, git_init_bare, git_add_all, git_commit, git_clone, git_push,\
    copy_directory_contents, directory_exists, create_directory, run_command,\
    CommandError


def copy_and_create_repo(source, dest, assignment,
                         commit_message='initial commit'):
    copy_directory_contents(source, dest)

    repo = Repository(dest, assignment)
    repo.init()
    repo.add_all_and_commit(commit_message)

    return repo


class Repository:
    def __init__(self, path, assignment, is_local=True, is_bare=False,
                 remote_user=None, remote_host=None, ssh=None,
                 student_username=''):
        self.path = path
        self.assignment = assignment
        self.is_local = is_local
        self.is_bare = is_bare
        self.remote_user = remote_user
        self.remote_host = remote_host
        self.ssh = ssh
        self.student_username = student_username

    @classmethod
    def local_bare(cls, path, assignment):
        return Repository(path, assignment, is_local=True, is_bare=True)

    def __repr__(self):
        string = '{0}\n{1}\n{2}'.format(self.path, self.assignment,
                                        self.student_username)
        if self.is_local:
            string += '\nlocal'
        else:
            string += '\n{0}@{1}'.format(self.remote_user, self.remote_host)

        if self.ssh is not None:
            string += '\nssh set'

        if self.student_username != '':
            string += '\nstudent: {0}'.format(self.student_username)

        return string

    @property
    def url(self):
        assert not self.is_local
        return '{0}@{1}:{2}'.format(self.remote_user, self.remote_host,
                                    self.path)

    def get_update_flag_path(self):
        return os.path.join(self.path, 'update_flag')

    def add_update_flag_hook(self, post_update_path):
        assert (not self.is_local and os.path.isfile(post_update_path))

        hook_dir = os.path.join(self.path, 'hooks')

        if not self.is_local:
            scp_file(post_update_path, self.remote_user, self.remote_host,
                     hook_dir)

    def set_remote(self, remote_repo, remote_name='origin'):
        cwd = os.getcwd()
        os.chdir(self.path)
        try:
            git_remote_add(remote_name, remote_repo.url)
        except CommandError as e:
            os.chdir(cwd)
            raise e

        os.chdir(cwd)

    def add_all_and_commit(self, commit_message):
        assert (self.is_local and not self.is_bare)
        cwd = os.getcwd()
        os.chdir(self.path)
        try:
            git_add_all()
            git_commit(commit_message)
        finally:
            os.chdir(cwd)

    def push(self, remote_repo=None, branch='master', force=False):
        assert self.is_local
        cwd = os.getcwd()
        os.chdir(self.path)
        try:
            if remote_repo is None:
                git_push()
            else:
                git_push_explicit_url(remote_repo.url, branch, force)
        finally:
            os.chdir(cwd)

    def pull(self):
        assert self.is_local
        assert not self.is_bare

        cwd = os.getcwd()
        os.chdir(self.path)
        try:
            run_command(['git', 'pull'])
        except CommandError as e:
            print('Error pulling in {0}:\n{1}'.format(self.path, e))
        os.chdir(cwd)

    def is_initialized(self):
        assert not self.is_bare
        return directory_exists(os.path.join(self.path, '.git'),
                                self.remote_user, self.remote_host, self.ssh)

    def init(self):
        if not directory_exists(self.path, self.remote_user, self.remote_host,
                                self.ssh):
            create_directory(self.path, self.remote_user, self.remote_host,
                             self.ssh)

        if self.is_local and not self.is_bare:
            git_init(self.path)
        elif not self.is_local and self.is_bare:
            git_init_bare(self.path, self.remote_user, self.remote_host,
                          self.ssh)
        else:
            assert False

    def clone_to(self, dest_path, remote_user=None, remote_host=None, ssh=None,
                 local_to_remote=False):
        assert self.is_local
        git_clone(self.path, dest_path, remote_user, remote_host, ssh,
                  local_to_remote)
        if (remote_user is not None and remote_host is not None) or ssh is not None:
            return Repository(dest_path, self.assignment, is_local=False,
                              is_bare=False, remote_user=remote_user,
                              remote_host=remote_host, ssh=ssh,
                              student_username=self.student_username)
        else:
            return Repository(dest_path, self.assignment, is_local=True,
                              is_bare=False,
                              student_username=self.student_username)

    def clone_from_remote(self, remote_repo):
        assert self.is_local
        assert not self.is_bare
        assert isinstance(remote_repo, Repository)

        git_clone(remote_repo.url, self.path)

    def get_head_hash(self):
        head_hash = ''
        if self.is_local:
            current_dir = os.getcwd()
            os.chdir(self.path)
            try:
                head_hash = run_command(['git', 'rev-parse', 'HEAD']).rstrip()
            except CommandError as e:
                print('Error getting commit hash for {0}:\n{1}'
                      .format(self.path, e), file=sys.stderr)
            os.chdir(current_dir)
        else:
            command = 'cd {0}; git rev-parse HEAD'.format(self.path)
            try:
                head_hash = run_command(command, remote_user=self.remote_user,
                                        remote_host=self.remote_host,
                                        ssh=self.ssh)
                head_hash = head_hash.rstrip()
            except CommandError as e:
                print('Error getting commit hash for {0}:\n{1}'
                      .format(self.path, e), file=sys.stderr)

        return head_hash
