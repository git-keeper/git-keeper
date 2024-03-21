# Copyright 2023 Nathan Sommer and Ben Coleman
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


"""Provides a function for building a git clone URL."""


DEFAULT_SSH_PORT = 22


def git_clone_url(username, host, port, path):
    """
    Build a git clone URL with the following form:

    ssh://<username>@<host>:<port><path>

    <path> must begin with a forward slash.

    :param username: username of the user on the server
    :param host: hostname or IP address of the server
    :param port: port number of the SSH server
    :param path: absolute path to the repository on the server
    :return:
    """

    if str(port) == str(DEFAULT_SSH_PORT):
        return 'ssh://{0}@{1}{2}'.format(username, host, path)
    else:
        return 'ssh://{0}@{1}:{2}{3}'.format(username, host, port, path)
