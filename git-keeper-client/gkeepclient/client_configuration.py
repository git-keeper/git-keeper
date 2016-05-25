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
This module allows the parsing of and provides access to the client
configuration file.

The default configuration file location is ~/.config/git-keeper/client.cfg.
This can be customized by passing a path to parse().

The configuration file must be in the INI format:
https://docs.python.org/3/library/configparser.html#supported-ini-file-structure

This module stores a ClientConfiguration instance in the module-level variable
named config. Call parse() on this instance as early as possible, probably in
main() or whatever your entry point function is. Attempting to call
parse() a second time will raise an exception.

Any other modules that import the config will have access to the same instance
without having to call parse().

Example usage:

    import sys
    from gkeepclient.client_configuration import config

    def main():
        try:
            config.parse()
        except ClientConfigurationError as e:
            sys.exit(e)

        # Now access attributes using config.host, etc.


Attributes:

    local_username - the user that is running gkeep
    local_home_dir - the local user's home directory on the client machine

    server_host - hostname of the server
    server_username - the faculty member's username on the server
    server_ssh_port - the port to use for SSH connections (defaults to 22)

"""

import configparser
import os
from getpass import getuser


class ClientConfigurationError(Exception):
    """
    Raised if anything goes wrong parsing the configuration file, which should
    always be treated as a fatal error.
    """
    pass


class ClientConfiguration:
    """
    Allows parsing client.cfg and stores the configuration values as
    attributes.

    It is not advisable to make instances of this class directly. Instead,
    use the module-level instance that is created when the module is imported.

    See the module docstring for usage.

    """

    def __init__(self):
        """
        Create the object and set local_home_dir and local_username.

        parse() must be called before any other configuration attributes are
        accessed.
        """

        self.local_home_dir = os.path.expanduser('~')
        self.local_username = getuser()

        self._config_path = None

        self._parsed = False

    def parse(self, config_path=None):
        """
        Parse the configuration file and initialize the attributes.

        May only be called once.

        Raises ClientConfigurationError

        :param config_path: optional path to the config file
        """

        if self._parsed:
            raise ClientConfigurationError('parse() may only be called once')

        if config_path is None:
            relative_path = '.config/git-keeper/client.cfg'
            self._config_path = os.path.join(self.local_home_dir, relative_path)
        else:
            self._config_path = config_path

        if not os.path.isfile(self._config_path):
            error = '{0} does not exist'.format(self._config_path)
            raise ClientConfigurationError(error)

        self._parse_config_file()
        self._initialize_server_attributes()

        self._parsed = True

    def _parse_config_file(self):
        # Use a ConfigParser object to parse the configuration file and store
        # the state

        self._parser = configparser.ConfigParser()

        try:
            self._parser.read(self._config_path)
        except configparser.ParsingError as e:
            error = 'Error reading {0}: {1}'.format(self._config_path,
                                                    e.message)
            raise ClientConfigurationError(error)

    def _ensure_section_is_present(self, section):
        # Raise an exception if section is not in the config file

        if section not in self._parser.sections():
            error = '{0} is not present in {1}'.format(section,
                                                       self._config_path)
            raise ClientConfigurationError(error)

    def _initialize_server_attributes(self):
        # Initialize all the server-related attributes

        self._ensure_section_is_present('server')

        try:
            # Required fields
            self.server_host = self._parser.get('server', 'host')
            self.server_username = self._parser.get('server', 'username')

            # Optional fields
            if self._parser.has_option('server', 'ssh_port'):
                port_string = self._parser.get('server', 'ssh_port')
                try:
                    self.server_ssh_port = int(port_string)
                except ValueError:
                    error = ('ssh_port is not an integer: {0}'
                             .format(port_string))
                    raise ClientConfigurationError(error)
            else:
                self.server_ssh_port = 22

        except configparser.NoOptionError as e:
            raise ClientConfigurationError(e.message)


# Module-level configuration instance. Someone must call parse() on this
# before it is used
config = ClientConfiguration()
