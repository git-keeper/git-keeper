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

The configuration file should be in the INI format:
https://docs.python.org/3/library/configparser.html#supported-ini-file-structure

There should be only one instance of the ServerConfiguration class. You can
get it by calling the get_config() method provided by this module.
"""

import configparser
import os


# Store one module-level ServerConfiguration instance
config_instance = None


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
        """Parse the configuration file and initialize the attributes"""

        self._config_path = \
            os.path.expanduser('~/.config/git-keeper/server.cfg')

        if not os.path.isfile(self._config_path):
            error = '{0} does not exist'.format(self._config_path)
            raise ServerConfigurationError(error)

        self._parse_config_file()
        self._initialize_email_attributes()

    def _parse_config_file(self):
        """Use a ConfigParser object to parse the configuration file"""

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
        """Initialize all the email-related attributes"""

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


def get_config() -> ServerConfiguration:
    """Returns the ServerConfiguration instance, intializing it if need be.

    :return: An object containing the server configuration options parsed from
     server.cfg
    """
    global config_instance

    if config_instance is None:
        config_instance = ServerConfiguration()

    return config_instance

