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

from gkeepcore.command_runner import CommandRunner, CommandRunnerError


class LocalCheckOutputRunner(CommandRunner):
    def __init__(self, stderr=STDOUT):
        self._stderr = stderr

    def run_command(self, command) -> str:
        try:
            if isinstance(command, str):
                output = check_output(command, stderr=self._stderr, shell=True)
            elif isinstance(command, list):
                output = check_output(command, stderr=self._stderr,
                                      shell=False)
            else:
                error = ('{0} may not be used as a command'
                         .format(type(command)))
                raise CommandRunnerError(error)
        except CalledProcessError as e:
            raise CommandRunnerError(e.output.decode('utf-8'))

        return output.decode('utf-8')
