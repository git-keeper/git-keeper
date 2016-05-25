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


from subprocess import check_output, CalledProcessError, STDOUT


class CommandError(Exception):
    pass


def run_command(command, sudo=False, stderr=STDOUT):
    if not isinstance(command, str) and not isinstance(command, list):
        raise CommandError('command must be a string or a list, not {0}'
                           .format(type(command)))

    if sudo:
        if isinstance(command, str):
            command = 'sudo ' + command
        else:
            command = ['sudo'] + command

    try:
        if isinstance(command, str):
            output = check_output(command, stderr=stderr, shell=True)
        else:
            output = check_output(command, stderr=stderr, shell=False)
    except CalledProcessError as e:
        raise CommandError(e.output.decode('utf-8'))

    return output.decode('utf-8')

