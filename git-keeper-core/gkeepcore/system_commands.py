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
from pwd import getpwuid, getpwnam
from grp import getgrgid, getgrnam

from gkeepcore.shell_command import run_command, CommandError


def chmod(path, permissions_mode, recursive=False, sudo=False):
    if type(permissions_mode) == int:
        permissions_mode = str(permissions_mode)

    if recursive:
        cmd = ['chmod', '-R', permissions_mode, path]
    else:
        cmd = ['chmod', permissions_mode, path]

    run_command(cmd, sudo=sudo)


def sudo_chown(path, user, group, recursive=False):
    if recursive:
        cmd = ['chown', '-R', '{0}:{1}'.format(user, group), path]
    else:
        cmd = ['chown', '{0}:{1}'.format(user, group), path]

    run_command(cmd, sudo=True)


def sudo_add_user_to_group(user, group):
    cmd = ['usermod', '-a', '-G', group, user]
    run_command(cmd, sudo=True)


def sudo_add_group(group):
    cmd = ['groupadd', group]
    run_command(cmd, sudo=True)


def sudo_add_user(username, groups):
    cmd = ['useradd', '-m', '-U']
    if len(groups) > 0:
        cmd += ['-G', ','.join(groups)]
    cmd += [username]

    run_command(cmd, sudo=True)


def sudo_set_password(username, password):
    cmd = 'echo {0}:{1} | sudo chpasswd'.format(username, password)
    run_command(cmd)


def user_exists(user):
    try:
        getpwnam(user)
        return True
    except KeyError:
        return False


def group_exists(group):
    try:
        getgrnam(group)
        return True
    except KeyError:
        return False


def user_owner(path):
    uid = os.stat(path).st_uid
    username = getpwuid(uid).pw_name

    return username


def group_owner(path):
    gid = os.stat(path).st_gid
    group_name = getgrgid(gid).gr_name

    return group_name


def mode(path):
    decimal_mode = os.stat(path).st_mode
    octal_string = oct(decimal_mode)

    # we only care about the last 3 digits
    return octal_string[-3:]


def mkdir(path, sudo=False):
    cmd = ['mkdir', '-p', path]
    run_command(cmd, sudo=sudo)


