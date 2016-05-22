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

"""Parses and provides access to the client configuration.

The configuration file must be stored at ~/.config/git-keeper/client.cfg

The configuration file must be in the INI format:
https://docs.python.org/3/library/configparser.html#supported-ini-file-structure

This module stores a ClientConfiguration instance in the module-level variable
named config. Call parse() on this instance before use. Attempting to call
parse() a second time will raise an exception.

Example usage:

    from gkeepclient.client_configuration import config

    config.parse()

    # Now access attributes using config.host, etc.

    # Any module that imports the config in this fashion will access the same
    # instance.

"""

import configparser
import os


class ClientConfigurationError(Exception):
    pass


class ClientConfiguration:
    """Parses client.cfg and stores the configuration values as attributes.

    Public attributes:

    Server-related attributes:
        host - hostname of the server
        username - the faculty member's username on the server
        ssh_port - the port to use for SSH connections (defaults to 22)

    """

    def __init__(self):
        """Creates the object and setup the config path. parse() must be called
        before any configuration attributes are accessed.
        """

        home_dir = os.path.expanduser('~')
        relative_path = '.config/git-keeper/client.cfg'
        self._config_path = os.path.join(home_dir, relative_path)

        self._parsed = False

    def parse(self):
        """Parses the configuration file and initialize the attributes.

        May only be called once."""

        if self._parsed:
            raise ClientConfigurationError('parse() may only be called once')

        if not os.path.isfile(self._config_path):
            error = '{0} does not exist'.format(self._config_path)
            raise ClientConfigurationError(error)

        self._parse_config_file()
        self._initialize_server_attributes()

        self._parsed = True

    def _parse_config_file(self):
        """Uses a ConfigParser object to parse the configuration file"""

        self._parser = configparser.ConfigParser()

        try:
            self._parser.read(self._config_path)
        except configparser.ParsingError as e:
            error = 'Error reading {0}: {1}'.format(self._config_path,
                                                    e.message)
            raise ClientConfigurationError(error)

    def _ensure_section_is_present(self, section):
        """Raises an exception if section is not in the config file"""

        if section not in self._parser.sections():
            error = '{0} is not present in {1}'.format(section,
                                                       self._config_path)
            raise ClientConfigurationError(error)

    def _initialize_server_attributes(self):
        """Initializes all the server-related attributes"""

        self._ensure_section_is_present('server')

        try:
            # Required fields
            self.host = self._parser.get('server', 'host')
            self.username = self._parser.get('server', 'username')

            # Optional fields
            if self._parser.has_option('server', 'ssh_port'):
                self.ssh_port = self._parser.get('server', 'ssh_port')
            else:
                self.ssh_port = '22'

        except configparser.NoOptionError as e:
            raise ClientConfigurationError(e.message)


# Module-level configuration instance. Someone must call parse() on this
# before it is used
config = ClientConfiguration()
