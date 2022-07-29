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
Provides a run_command() function for running shell commands.
"""

import os
from subprocess import check_output, CalledProcessError, STDOUT

from gkeepcore.gkeep_exception import GkeepException


class CommandError(GkeepException):
    """
    Base class for command errors.
    """
    pass


class InvalidCommandError(CommandError):
    """
    Raised if the given command is not a string or a list, or of the command
    is a list and the program to run does not exist.
    """
    pass


class CommandExitCodeError(CommandError):
    """
    Raised if a command exits with a non-zero exit code. The exit code is
    available through the exit_code attribute.
    """

    def __init__(self, message, exit_code):
        super().__init__(message)
        self.exit_code = exit_code


def run_command(command, sudo=False, user=None, stderr=STDOUT) -> str:
    """
    Run a shell command and return the output.

    By default the output is stdout and stderr combined.

    Raises a CommandError exception if the command has a non-zero exit code.

    :param command: a shell command as a string or a list of strings
     representing each argument
    :param sudo: set to True to run the command using sudo
    :param user: if sudo is True, run as this user or root if None
    :param stderr: where to send stderr
    :return: the output of the command

    """

    # command must be a string or list
    if not isinstance(command, str) and not isinstance(command, list):
        raise InvalidCommandError('command must be a string or a list, not {0}'
                                  .format(type(command)))

    # prepend sudo and specify user if need be
    if sudo:
        if isinstance(command, str):
            if user is None:
                command = 'sudo -n ' + command
            else:
                command = 'sudo -n -u {}'.format(user) + command
        else:
            if user is None:
                command = ['sudo', '-n'] + command
            else:
                command = ['sudo', '-n', '-u', user] + command

    # run the command
    try:
        if isinstance(command, str):
            # shell must be True if we're using a string instead of a list
            output = check_output(command, stderr=stderr, shell=True)
        else:
            output = check_output(command, stderr=stderr, shell=False)
    except CalledProcessError as e:
        # the CommandError exception will contain the output as a string
        # and the exit code
        raise CommandExitCodeError(e.output.decode('utf-8'), e.returncode)
    except FileNotFoundError:
        error = 'Error running command, {} does not exist'.format(command[0])
        raise InvalidCommandError(error)

    # convert the output from bytes to a string when returning, replacing any
    # byte sequences that are not valid utf-8 with the � character
    return output.decode('utf-8', 'replace')


class ChangeDirectoryContext:
    """
    For use as a context manager to change into a directory and change out
    again.

    THE WORKING DIRECTORY IS CHANGED AT THE PROCESS LEVEL, AND AS SUCH IT IS
    NOT SAFE FOR MORE THAN ONE THREAD TO USE THIS CONTEXT MANAGER.

    Example:

        with ChangeDirectoryContext('path/to/dir'):
            # do stuff in the new working directory

        # changed back to old directory
    """

    def __init__(self, path):
        self._old_wd = os.getcwd()
        self._new_wd = path

    def __enter__(self):
        os.chdir(self._new_wd)

    def __exit__(self, *args):
        os.chdir(self._old_wd)


def run_command_in_directory(path, command, sudo=False, user=None,
                             stderr=STDOUT):
    """
    Change into a new working directory, run a command, and change back.

    THE WORKING DIRECTORY IS CHANGED AT THE PROCESS LEVEL, AND AS SUCH IT IS
    NOT SAFE FOR MORE THAN ONE THREAD TO USE THIS FUNCTION.

    Raises CommandError if the command could not be called or has a non-zero
    exit code.

    After returning, the working directory will be the original working
    directory regardless of whether an exception was thrown or not.

    :param path: new working directory to change in to
    :param command: a shell command as a string or a list of strings
     representing each argument
    :param sudo: set to True to run the command using sudo
    :param user: if sudo is True, run as this user or root if None
    :param stderr: where to send stderr
    :return: the output of the command
    """
    try:
        with ChangeDirectoryContext(path):
            output = run_command(command, sudo=sudo, user=user, stderr=stderr)
    except Exception as e:
        raise CommandError(e)

    return output
