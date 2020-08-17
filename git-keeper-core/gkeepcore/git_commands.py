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

from gkeepcore.shell_command import run_command_in_directory, run_command, \
    CommandError


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


def git_config(repo_path, config_options):
    """
    Run a git config command on a repository.

    :param repo_path: path to the repository
    :param config_options: an iterable containing the options to pass to git
      config
    """

    cmd = ['git', 'config']
    cmd.extend(config_options)

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


def git_clone(source_repo_path, target_path):
    """
    Clone a local repo to a specific location
    :param source_repo_path: the path to the (bare) source repo
    :param target_path: the path where the git clone should be executed.
    :return: None
    """

    cmd = ['git', 'clone', source_repo_path]

    run_command_in_directory(target_path, cmd)


def git_clone_remote(remote_repo_url, local_repo_path):
    """
    Clone a remote repository.

    :param remote_repo_url: URL of the remote repository
    :param local_repo_path: path to the new local repository
    """

    cmd = ['git', 'clone', remote_repo_url, local_repo_path]
    run_command(cmd)


def git_checkout(repo_path, branch_or_commit):
    """
    Checkout a branch or a commit in a repository.

    :param repo_path: path of the repository
    :param branch_or_commit: name of the branch or the commit hash to checkout
    """

    cmd = ['git', 'checkout', branch_or_commit]

    run_command_in_directory(repo_path, cmd)


def git_head_hash(repo_path):
    """
    Get the hash of the HEAD of a git repository.

    :param repo_path: path to the repository
    :return: commit hash of HEAD
    """

    cmd = ['git', 'rev-parse', 'HEAD']

    return run_command_in_directory(repo_path, cmd).rstrip()


def git_head_hash_date(repo_path):
    """
    Get the hash and last commit date of the HEAD of a git repository.

    The date is in seconds from the epoch.

    :param repo_path: path to the repository
    :return: tuple containing the hash and the timestamp
    """

    cmd = ['git', 'log', '-1', '--format=%H %at']

    output = run_command_in_directory(repo_path, cmd)
    split_output = output.split()

    if len(split_output) != 2:
        raise CommandError(output)

    repo_hash = split_output[0]
    timestamp = int(split_output[1])

    return repo_hash, timestamp


def git_hashes_and_times(repo_path):
    """
    Get the hashes and commit times of the commits to a git repository.

    The times are integer seconds from the epoch.

    The hashes are strings.

    :param repo_path: path to the repository
    :return: list containing (hash, time) tuples
    """

    cmd = ['git', 'log', '--format=%H %at']

    output = run_command_in_directory(repo_path, cmd)
    lines = output.splitlines()

    hashes_and_times = []

    for line in lines:
        split_line = line.split()

        if len(split_line) != 2:
            raise CommandError(output)

        repo_hash = split_line[0]
        timestamp = int(split_line[1])

        hashes_and_times.append((repo_hash, timestamp))

    if len(hashes_and_times) == 0:
        raise CommandError('No output')

    return hashes_and_times
