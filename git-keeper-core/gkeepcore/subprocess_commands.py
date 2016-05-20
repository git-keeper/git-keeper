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
import shlex
from pwd import getpwnam
from subprocess import check_output, check_call, CalledProcessError, STDOUT
from paramiko.client import SSHClient


class CommandError(Exception):
    pass


def run_command(command, remote_user=None, remote_host=None, ssh=None,
                sudo=False, stderr=STDOUT):
    output = b''

    try:
        if ssh is not None:
            assert isinstance(ssh, SSHClient)
            if isinstance(command, list):
                command = ' '.join(command)
            if sudo:
                command = 'sudo ' + command
            tran = ssh.get_transport()
            chan = tran.open_session()
            chan.get_pty()
            f = chan.makefile()
            chan.exec_command(command)
            output = f.read()
            exit_status = chan.recv_exit_status()
            if exit_status != 0:
                raise CommandError(output.decode('utf-8'))

        else:
            if remote_user is not None and remote_host is not None:
                user_at_host = '{0}@{1}'.format(remote_user, remote_host)
                if sudo:
                    prefix = ['ssh', user_at_host, '-t', 'sudo']
                    command = prefix + command
                else:
                    command = ['ssh', user_at_host] + command
            elif sudo:
                command = ['sudo'] + command

            if sudo:
                check_call(command)
            else:
                if isinstance(command, str):
                    output = check_output(command, stderr=stderr, shell=True)
                else:
                    output = check_output(command, stderr=stderr, shell=False)
    except CalledProcessError as e:
        raise CommandError(e.output.decode('utf-8'))

    return output.decode('utf-8')


def chown(path, username, group, remote_user=None, remote_host=None, ssh=None):
    owner_str = '{0}:{1}'.format(username, group)
    run_command(['chown', owner_str, path], remote_user, remote_host, ssh,
                sudo=True)


def chmod(path, mode, recursive=False, remote_user=None, remote_host=None,
          ssh=None, sudo=False):
    if type(mode) == int:
        mode = str(mode)

    if recursive:
        cmd = ['chmod', '-R', mode, path]
    else:
        cmd = ['chmod', mode, path]
    run_command(cmd, remote_user, remote_host, ssh, sudo=sudo)


def create_user(username, remote_user=None, remote_host=None, ssh=None):
    run_command(['useradd', '-m', username], remote_user, remote_host, ssh,
                sudo=True)


def scp_file(local_path, remote_user, remote_host, remote_path):
    dest = '{0}@{1}:{2}'.format(remote_user, remote_host, remote_path)
    cmd = ['scp', local_path, dest]
    run_command(cmd)


def scp_directory(local_path, remote_user, remote_host, remote_path):
    dest = '{0}@{1}:{2}'.format(remote_user, remote_host, remote_path)
    cmd = ['scp', '-r', local_path, dest]
    run_command(cmd)


def git_remote_add(remote_name, url):
    cmd = ['git', 'remote', 'add', remote_name, url]
    run_command(cmd)


def directory_exists(directory, remote_user=None, remote_host=None, ssh=None):
    if (remote_user is not None and remote_host is not None) or ssh is not None:
        cmd = ['[ -d {0} ]'.format(directory)]

        try:
            run_command(cmd, remote_user, remote_host, ssh)
            return True
        except CommandError:
            return False
    else:
        return os.path.isdir(directory)


def create_directory(directory, remote_user=None, remote_host=None, ssh=None):
    cmd = ['mkdir', '-p', directory]
    run_command(cmd, remote_user, remote_host, ssh)


def move_directory(source, dest, remote_user=None, remote_host=None, ssh=None):
    cmd = ['mv', source, dest]
    run_command(cmd, remote_user, remote_host, ssh)


def list_directory(path, remote_user=None, remote_host=None, ssh=None):
    cmd = ['ls', path]
    output = run_command(cmd, remote_user, remote_host, ssh)
    return output.split()


def git_init(repo_path, remote_user=None, remote_host=None, ssh=None):
    cmd = ['git', 'init', repo_path]
    run_command(cmd, remote_user, remote_host, ssh)


def git_init_bare(repo_path, remote_user=None, remote_host=None, ssh=None):
    cmd = ['git', 'init', '--bare', repo_path]
    run_command(cmd, remote_user, remote_host, ssh)


def git_add_all():
    cmd = ['git', 'add', '-A']
    run_command(cmd)


def git_commit(message):
    cmd = ['git', 'commit', '-am', message]
    run_command(cmd)


def chmod_world_writable_recursive(remote_path, remote_user=None,
                                   remote_host=None, ssh=None):
    cmd = ['chmod', '-R', 'o+w', remote_path]
    run_command(cmd, remote_user, remote_host, ssh)


def git_push():
    cmd = ['git', 'push']
    run_command(cmd)


def git_push_explicit_url(url, branch, force):
    if force:
        cmd = ['git', 'push', '-f', url, branch]
    else:
        cmd = ['git', 'push', url, branch]
    run_command(cmd)


def git_clone(source_path, dest_path, remote_user=None, remote_host=None,
              ssh=None, local_to_remote=False):
    if local_to_remote:
        dest_path = '{0}@{1}:{2}'.format(remote_user, remote_host, dest_path)
        cmd = ['git', 'clone', source_path, dest_path]
        run_command(cmd)
    else:
        cmd = ['git', 'clone', source_path, dest_path]
        run_command(cmd, remote_user, remote_host, ssh)


def touch(path, remote_user=None, remote_host=None, ssh=None):
    cmd = ['touch', path]
    run_command(cmd, remote_user, remote_host, ssh)


def call_action(*args):
    cmd = ['bash']
    cmd.extend(args)
    return run_command(cmd)


def user_exists(username, remote_user=None, remote_host=None, ssh=None):
    tilde_home_dir = '~{0}'.format(username)

    if (remote_user is not None and remote_host is not None) or ssh is not None:
        remote_cmd = ['cd', tilde_home_dir]
        try:
            run_command(remote_cmd, remote_user, remote_host, ssh)
            return True
        except CommandError:
            return False
    else:
        try:
            getpwnam(username)
            return True
        except KeyError:
            return False


def home_dir_from_username(username, remote_user=None, remote_host=None,
                           ssh=None):
    tilde_home_dir = '~{0}'.format(username)

    if (remote_user is not None and remote_host is not None) or ssh is not None:
        remote_cmd = 'cd {0} && pwd'.format(tilde_home_dir)
        output = run_command([remote_cmd], remote_user, remote_host, ssh)
        return output.strip()
    else:
        return os.path.expanduser(tilde_home_dir)


def copy_directory_contents(source, dest):
    source_wildcard = '"{0}"/*'.format(source)
    dest_quoted = '"{0}"'.format(dest)
    cmd = 'cp -r {0} {1}'.format(source_wildcard, dest_quoted)
    run_command(cmd)


def append_to_file(file_path, text, ssh=None):
    quoted_text = shlex.quote(text)
    quoted_path = shlex.quote(file_path)
    cmd = 'echo {0} >> {1}'.format(quoted_text, quoted_path)
    run_command(cmd, ssh)


def get_byte_count(file_path, ssh=None):
    quoted_path = shlex.quote(file_path)
    cmd = "ls -n1 {0} | awk '{{print $5}}'".format(quoted_path)
    try:
        count = int(run_command(cmd, ssh=ssh))
    except ValueError:
        raise CommandError('Error getting byte count from {0}'
                           .format(file_path))

    return count
