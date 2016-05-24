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

"""Parses and provides access to the server configuration.

The configuration file must be stored at ~/.config/git-keeper/server.cfg

The configuration file must be in the INI format:
https://docs.python.org/3/library/configparser.html#supported-ini-file-structure

This module stores a ServerConfiguration instance in the module-level variable
named config. Call parse() on this instance as early as possible, probably in
main() or whatever your entry point function is. Attempting to call
parse() a second time will raise an exception.

Any other modules that import the config will have access to the same instance
without having to call parse().

Example usage:

    import sys
    from gkeepserver.server_configuration import config

    def main():
        try:
            config.parse()
        except ServerConfigurationError as e:
            sys.exit(e)

        # Now access attributes using config.email_username, etc.

"""

import configparser
import os
from getpass import getuser


class ServerConfigurationError(Exception):
    pass


class ServerConfiguration:
    """Parses server.cfg and stores the configuration values as attributes.

    Public attributes:

    Email sending attributes:
        from_name - the name that emails are from
        from_address - the address that emails are from
        smtp_server - server used for sending mail
        smtp_port - port used for sending mail
        email_username - username for the SMTP server
        email_password - password for the SMTP server

    """
    
    def __init__(self):
        """Creates the object and setup the config path. parse() must be called
         before any configuration attributes are accessed.
        """

        self.home_dir = os.path.expanduser('~')
        self.username = getuser()

        self._config_path = None

        self._parsed = False

    def parse(self, config_path=None):
        """Parses the configuration file and initialize the attributes.

        May only be called once."""

        if self._parsed:
            raise ServerConfigurationError('parse() may only be called once')

        if config_path is None:
            config_filename = 'server.cfg'
            self._config_path = os.path.join(self.home_dir, config_filename)
        else:
            self._config_path = config_path

        if not os.path.isfile(self._config_path):
            error = '{0} does not exist'.format(self._config_path)
            raise ServerConfigurationError(error)

        self._initialize_default_attributes()

        self._parse_config_file()
        self._initialize_email_attributes()

        self._parsed = True

    def _initialize_default_attributes(self):
        self.log_file_path = os.path.join(self.home_dir, 'gkeepd.log')

        log_snapshot_filename = 'log-snapshot.json'
        self.log_snapshot_file_path = os.path.join(self.home_dir,
                                                   log_snapshot_filename)

    def _parse_config_file(self):
        """Uses a ConfigParser object to parse the configuration file"""

        self._parser = configparser.ConfigParser()

        try:
            self._parser.read(self._config_path)
        except configparser.ParsingError as e:
            error = 'Error reading {0}: {1}'.format(self._config_path,
                                                    e.message)
            raise ServerConfigurationError(error)

    def _ensure_section_is_present(self, section):
        """Raises an exception if section is not in the config file"""

        if section not in self._parser.sections():
            error = ('section {0} is not present in {1}'
                     .format(section, self._config_path))
            raise ServerConfigurationError(error)

    def _initialize_email_attributes(self):
        """Initializes all the email-related attributes"""

        self._ensure_section_is_present('email')

        try:
            # Required fields
            self.from_name = self._parser.get('email', 'from_name')
            self.from_address = self._parser.get('email', 'from_address')
            self.smtp_server = self._parser.get('email', 'smtp_server')
            self.smtp_port = self._parser.get('email', 'smtp_port')
            self.email_username = self._parser.get('email', 'email_username')
            self.email_password = self._parser.get('email', 'email_password')

        except configparser.NoOptionError as e:
            raise ServerConfigurationError(e.message)


# Module-level configuration instance. Someone must call parse() on this
# before it is used
config = ServerConfiguration()
