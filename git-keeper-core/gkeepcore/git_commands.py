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


"""Provides functions for running git commands."""


from gkeepcore.shell_command import run_command_in_directory, run_command


def git_remote_add(repo_path, remote_name, url):
    """
    Add a remote to a repository.

    Raises CommandError on failure.

    :param repo_path: path to the repository
    :param remote_name: name of the remote
    :param url: URL of the remote
    """
    cmd = ['git', 'remote', 'add', remote_name, url]
    run_command_in_directory(repo_path, cmd)


def git_init(repo_path):
    """
    Initialize a non-bare repository in an existing directory.

    Raises CommandError on failure.

    :param repo_path: path to the directory in which to initialize the
     repository
    """
    cmd = ['git', 'init']
    run_command_in_directory(repo_path, cmd)


def git_init_bare(repo_path):
    """
    Initialize a bare repository in an existing empty directory.

    Raises CommandError on failure.

    :param repo_path: path to the directory in which to initialize the
     repository
    """
    cmd = ['git', 'init', '--bare']
    run_command_in_directory(repo_path, cmd)


def git_add_all(repo_path):
    """
    Stage all files in a repository's working tree.

    Raises CommandError on failure.

    :param repo_path: path to the repository
    """
    cmd = ['git', 'add', '-A']
    run_command_in_directory(repo_path, cmd)


def git_commit(repo_path, message):
    """
    Commit staged changes to a repository.

    Raises CommandError on failure.

    :param repo_path: path to the repository
    :param message: commit message
    """
    cmd = ['git', 'commit', '-m', message]
    run_command_in_directory(repo_path, cmd)


def git_push(repo_path, dest=None, branch='master', force=False):
    """
    Push a repository to its upstream remote, or to a specific destination.

    Raises CommandError on failure.

    :param repo_path: path to the repository
    :param dest: optional destination to push to
    :param branch: optional branch, if dest is specified
    :param force: set to True to force a push (be careful!)
    """
    cmd = ['git', 'push']

    if force:
        cmd.append('-f')

    if dest is not None:
        cmd += [dest, branch]

    run_command_in_directory(repo_path, cmd)


def git_clone(source_repo_path, target_path):
    """
    Clone a local repo to a specific location

    :param source_repo_path: the path to the (bare) source repo
    :param target_path: the path where the git clone should be executed.
    :return: None
    """

    cmd = ['git', 'clone', source_repo_path]

    run_command_in_directory(target_path, cmd)
