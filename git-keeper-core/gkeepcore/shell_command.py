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


from subprocess import check_output, CalledProcessError, STDOUT


class CommandError(Exception):
    """
    Raised if a command is run that returns a non-zero exit code, or if the
    command is not a list or a string.
    """
    pass


def run_command(command, sudo=False, stderr=STDOUT) -> str:
    """
    Run a shell command and return the output.

    By default the output is stdout and stderr combined.

    Raises a CommandError exception if the command has a non-zero exit code.

    :param command: a shell command as a string or a list of strings
     representing each argument
    :param sudo: set to True to run the command using sudo
    :param stderr: where to send stderr
    :return: the output of the command

    """

    # command must be a string or list
    if not isinstance(command, str) and not isinstance(command, list):
        raise CommandError('command must be a string or a list, not {0}'
                           .format(type(command)))

    # prepend sudo if need be
    if sudo:
        if isinstance(command, str):
            command = 'sudo ' + command
        else:
            command = ['sudo'] + command

    # run the command
    try:
        if isinstance(command, str):
            # shell must be True if we're using a string instead of a list
            output = check_output(command, stderr=stderr, shell=True)
        else:
            output = check_output(command, stderr=stderr, shell=False)
    except CalledProcessError as e:
        # the CommandError exception will contain the output as a string
        raise CommandError(e.output.decode('utf-8'))

    # convert the output from bytes to a string when returning
    return output.decode('utf-8')
