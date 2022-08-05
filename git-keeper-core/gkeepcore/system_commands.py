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


"""
Provides functions for system calls and command line filesystem operations.
"""

import os
from getpass import getuser
from grp import getgrgid, getgrnam
from pwd import getpwuid, getpwnam, getpwall
from shutil import which

from gkeepcore.path_utils import user_home_dir
from gkeepcore.shell_command import run_command, CommandError


def this_user():
    """
    Get the username of the user that is running this process.

    :return: the username
    """

    return getuser()


def this_group():
    """
    Get the name of the default group of the user that is running this process.

    :return: the group name
    """

    username = getuser()
    gid = getpwnam(username).pw_gid
    group_name = getgrgid(gid).gr_name

    return group_name


def chmod(path, permissions_mode, recursive=False, sudo=False):
    """
    Change the permissions of a file or directory using chmod.

    The mode specifies the read/write/execute permissions for the user, group,
    and others. The mode is passed to chmod.

    :param path: path to the file or directory
    :param permissions_mode: chmod mode
    :param recursive: if True it will change files and directories recursively
    :param sudo: if True it will be run using sudo
    """

    # the mode can be an int or a string
    if isinstance(permissions_mode, int):
        permissions_mode = str(permissions_mode)
    elif not isinstance(permissions_mode, str):
        raise CommandError('mode must be int or string, not {0}: {1}'
                           .format(type(mode), mode))

    if recursive:
        cmd = ['chmod', '-R', permissions_mode, path]
    else:
        cmd = ['chmod', permissions_mode, path]

    run_command(cmd, sudo=sudo)


def sudo_chown(path, user, group, recursive=False):
    """
    Change the ownership of a file or directory using sudo and chown.

    Can recursively change the ownership of all files and directories under
    a top directory.

    :param path: path to the file or directory
    :param user: new user owner
    :param group: new group owner
    :param recursive: if True will apply to all files and directories under
     path
    """

    if recursive:
        cmd = ['chown', '-R', '{0}:{1}'.format(user, group), path]
    else:
        cmd = ['chown', '{0}:{1}'.format(user, group), path]

    run_command(cmd, sudo=True)


def sudo_add_user_to_group(user, group):
    """
    Add a user to a group using sudo and usermod.

    :param user: username of the user
    :param group: group to add the user to
    """

    cmd = ['usermod', '-a', '-G', group, user]
    run_command(cmd, sudo=True)


def sudo_add_group(group):
    """
    Add a new group to the system and groupadd.

    :param group: name of the group
    """

    cmd = ['groupadd', group]
    run_command(cmd, sudo=True)


def sudo_add_user(username, groups=None, shell=None, home_dir_mode=755):
    """
    Add a new user to the system using sudo and useradd.

    A group with the same name as the user will be created and will be the
    user's default group.

    Unless specified, the user's shell will be bash.

    Any additional groups that the user should be in can be passed as well.

    :param username: username of the new user
    :param groups: additional groups that the user shoul be in
    :param shell: name of the user's shell, will be bash if None
    :param home_dir_mode: read, write, and execute permissions for the user's
     home directory, defaults to 755
    """

    if shell is None:
        shell = 'bash'

    shell_path = which(shell)

    if shell_path is None:
        raise CommandError('{0} is not a valid shell'.format(shell))

    cmd = ['useradd', '-m', '-U', '-s', shell_path]
    if groups is not None and len(groups) > 0:
        cmd += ['-G', ','.join(groups)]
    cmd += [username]

    run_command(cmd, sudo=True)

    home_dir_path = user_home_dir(username)
    chmod(home_dir_path, home_dir_mode, sudo=True)


def sudo_add_user_to_groups(username, groups):
    """
    Add a user to all of the groups in the provided list.

    :param username: username of the user
    :param groups: a list of groups to add the user to
    """

    for group in groups:
        cmd = ['usermod', '-a', '-G', group, username]
        run_command(cmd, sudo=True)


def sudo_set_shell(username, shell):
    """
    Set a user's shell. Raises a CommandError if the shell does not exist.

    :param username: username of the user
    :param shell: name of the shell
    """

    shell_path = which(shell)

    if shell_path is None:
        raise CommandError('{0} is not a valid shell'.format(shell))

    cmd = ['chsh', '-s', shell_path, username]
    run_command(cmd, sudo=True)


def sudo_set_password(username, password):
    """
    Set a user's password using sudo and chpasswd.

    :param username: username of the user
    :param password: new password for the user
    """

    cmd = 'echo {0}:{1} | sudo chpasswd'.format(username, password)
    run_command(cmd)


def get_all_users():
    """
    Return a list of the usernames of all the users on the system.

    :return: list of all usernames
    """

    return [user[0] for user in getpwall()]


def user_exists(user):
    """
    Determine if a user exists on the system.

    :param user: username of the user
    :return: True if the user exists, False if not
    """

    try:
        getpwnam(user)
        return True
    except KeyError:
        return False


def group_exists(group):
    """
    Determine if a group exists on the system.

    :param group: name of the group
    :return: True if the group exists, False if not
    """

    try:
        getgrnam(group)
        return True
    except KeyError:
        return False


def user_owner(path):
    """
    Get the username of the owner of a file or directory.

    :param path: the path to the file or directory
    :return: the username of the owner
    """

    uid = os.stat(path).st_uid
    username = getpwuid(uid).pw_name

    return username


def group_owner(path):
    """
    Get the name of the group which owns a file or directory.

    :param path: the path to the file or directory
    :return: the name of the group owner
    """

    gid = os.stat(path).st_gid
    group_name = getgrgid(gid).gr_name

    return group_name


def mode(path):
    """
    Get the user, group, and others permissions of a file or directory.

    Returns a 3-character string representation of the octal mode.

    :param path: path to the file or directory
    :return: the permissions mode
    """

    decimal_mode = os.stat(path).st_mode
    octal_string = oct(decimal_mode)

    # we only care about the last 3 digits
    return octal_string[-3:]


def mkdir(path, sudo=False):
    """
    Create a directory, including all parent directories if they do not exist.

    :param path: path to the new directory
    :param sudo: set to True to run as root using sudo
    """

    cmd = ['mkdir', '-p', path]
    run_command(cmd, sudo=sudo)


def make_symbolic_link(source_path: str, link_path: str, sudo=False):
    """
    Create a symbolic link to a file or directory.

    :param source_path: path to the actual file or directory
    :param link_path: path to the symbolic link to be created
    :param sudo: if True, it will be run as root using sudo
    """

    cmd = ['ln', '-s', source_path, link_path]
    run_command(cmd, sudo=sudo)


def touch(path, sudo=False):
    """
    Update the access and modification times of a file or directory to the
    current time.

    :param path: path to the file or directory
    :param sudo: if True, it will run as root using sudo
    """

    cmd = ['touch', path]
    run_command(cmd, sudo=sudo)


def mv(source_path, dest_path, sudo=False):
    """
    Move or rename a file or directory.

    If the destination is a directory that exists, the source will be moved
    into that directory.

    :param source_path: the original path to the file or directory
    :param dest_path: the new path or an existing directory to move the file
     into
    :param sudo: if True, it will be run as root using sudo
    """

    cmd = ['mv', source_path, dest_path]
    run_command(cmd, sudo=sudo)


def cp(source_path, dest_path, recursive=False, sudo=False):
    """
    Copy a file or directory.

    recursive must be True if copying a directory.

    If the destination is a directory that exists, the source will be copied
    into that directory.

    :param source_path: path to the file or directory to be copied
    :param dest_path: the new path or an existing directory to copy the file
     into
    :param recursive: if True, will copy directories
    :param sudo: if True, it will be run as root using sudo
    """

    cmd = ['cp']

    if recursive:
        cmd.append('-r')

    cmd += [source_path, dest_path]

    run_command(cmd, sudo=sudo)


def rm(path, recursive=False, sudo=False):
    """
    Remove a file or directory.

    recursive must be True if removing a directory.

    :param path: path to the file or directory to be removed
    :param recursive: if True, will remove directories
    :param sudo: if True, it will be run as root using sudo
    """

    cmd = ['rm', '-f']

    if recursive:
        cmd.append('-r')

    cmd.append(path)

    run_command(cmd, sudo=sudo)


def file_is_readable(path):
    """
    Check to see if a file is readable.

    Returns True if the file is readable, False if it is not.

    :param path: path to the file
    :return: True if the file is readable, False if it is not
    """

    return os.access(path, os.R_OK)
