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

"""Provides an abstract base class CommandRunner. Classes that inherit from
this class will be used to run command-line commands in different ways
(i.e. locally, over a paramiko SSH connection, etc)
"""


import abc


class CommandRunnerError(Exception):
    pass


class CommandRunner(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def run_command(self, command) -> str:
        """Runs the given command and returns the output.

        :param command: a command-line command as a string or list of
         arguments
        :return: the output of the command
        """
