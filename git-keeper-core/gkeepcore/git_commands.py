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
import os

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


def git_push(repo_path, dest=None, branch='master', force=False, sudo=False):
    """
    Push a repository to its upstream remote, or to a specific destination.

    Raises CommandError on failure.

    :param repo_path: path to the repository
    :param dest: optional destination to push to
    :param branch: optional branch, if dest is specified
    :param force: set to True to force a push (be careful!)
    :param sudo: if true command is run as root
    """
    cmd = ['git', 'push']

    if force:
        cmd.append('-f')

    if dest is not None:
        cmd += [dest, branch]

    run_command_in_directory(repo_path, cmd, sudo=sudo)


def git_pull(repo_path, remote_url=None):
    """
    Pull from a remote repository.

    :param repo_path: path to the local repository
    :param remote_url: URL to pull from, None to pull from upstream remote
    """

    cmd = ['git', 'pull']

    if remote_url is not None:
        cmd.append(remote_url)

    run_command_in_directory(repo_path, cmd)


def is_non_bare_repo(repo_path):
    """
    Determine if a directory is a non-bare git repository by checking for the
    existance of a .git folder.

    :param repo_path: path to the repository
    :return: True if the repository contains a .git folder, False otherwise
    """

    git_path = os.path.join(repo_path, '.git')

    return os.path.isdir(git_path)


def git_clone(remote_repo_url, local_repo_path):
    """
    Clone a remote repository.

    :param remote_repo_url: URL of the remote repository
    :param local_repo_path: path to the new local repository
    """

    cmd = ['git', 'clone', remote_repo_url, local_repo_path]
    run_command(cmd)


def git_head_hash(repo_path):
    """
    Get the hash of the HEAD of a git repository.

    :param repo_path: path to the repository
    :return: commit hash of HEAD
    """

    cmd = ['git', 'rev-parse', 'HEAD']

    return run_command_in_directory(repo_path, cmd).rstrip()
