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
This module allows the parsing of and provides access to the the server
configuration file.

The default configuration file localtion is ~/server.cfg. This can be
customized by passing a path to parser().

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


Attributes:

    username - user that is running gkeepd
    home_dir - path to gkeepd user's home directory

    log_file_path - path to system log
    log_snapshot_file_path - path to file containing current log file sizes
    log_level - how detailed the log messages should be

    faculty_csv_path - path to file containing faculty members
    faculty_log_dir_path - path to directory containing faculty event logs

    from_name - the name that emails are from
    from_address - the address that emails are from
    smtp_server - SMTP server host
    smtp_port - SMTP server port
    email_username - username for the SMTP server
    email_password - password for the SMTP server

"""

import configparser
import os
from getpass import getuser

from gkeepcore.system_logger import LogLevel


class ServerConfigurationError(Exception):
    """
    Raised if anything goes wrong parsing the configuration file, which should
    always be treated as a fatal error.
    """
    pass


class ServerConfiguration:
    """
    Allows parsing client.cfg and stores the configuration values as
    attributes.

    It is not advisable to make instances of this class directly. Instead,
    use the module-level instance that is created when the module is imported.

    See the module docstring for usage.

    """
    
    def __init__(self):
        """
        Create the object and set home_dir and username.

        parse() must be called before any configuration attributes are
        accessed.
        """

        self.home_dir = os.path.expanduser('~')
        self.username = getuser()

        self._config_path = None

        self._parsed = False

    def parse(self, config_path=None):
        """
        Parse the configuration file and initialize the attributes.

        May only be called once.

        Raises ServerConfigurationError

        :param config_path: optional path to the config file
        """

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
        # Initialize attributes that have default values

        # logging
        self.log_file_path = os.path.join(self.home_dir, 'gkeepd.log')

        log_snapshot_filename = 'snapshot.json'
        self.log_snapshot_file_path = os.path.join(self.home_dir,
                                                   log_snapshot_filename)
        self.log_level = LogLevel.DEBUG

        # faculty info locations
        self.faculty_csv_path = os.path.join(self.home_dir, 'faculty.csv')
        self.faculty_log_dir_path = os.path.join(self.home_dir, 'faculty_logs')

        # users and groups
        self.keeper_user = 'keeper'
        self.keeper_group = 'keeper'
        self.faculty_group = 'faculty'

    def _parse_config_file(self):
        # Use a ConfigParser object to parse the configuration file and store
        # the state

        self._parser = configparser.ConfigParser()

        try:
            self._parser.read(self._config_path)
        except configparser.ParsingError as e:
            error = 'Error reading {0}: {1}'.format(self._config_path,
                                                    e.message)
            raise ServerConfigurationError(error)

    def _ensure_section_is_present(self, section):
        # Raise an exception if section is not in the config file

        if section not in self._parser.sections():
            error = ('section {0} is not present in {1}'
                     .format(section, self._config_path))
            raise ServerConfigurationError(error)

    def _initialize_email_attributes(self):
        # Initialize all the email-related attributes

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
