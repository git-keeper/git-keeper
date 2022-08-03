# Copyright 2016, 2018 Nathan Sommer and Ben Coleman
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

The default configuration file location is ~/server.cfg. This can be
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

    keeper_user - username of the user running gkeepd
    keeper_group - group name of the user running gkeepd
    tester_user - username of the user that runs the tests
    faculty_group - group that all faculty accounts belong to
    student_group - group that all student accounts belong to

    log_file_path - path to system log
    db_path - path to gkeepd's SQLite database file
    log_level - how detailed the log messages should be

    faculty_json_path - path to file containing faculty members
    faculty_log_dir_path - path to directory containing faculty event logs

    test_thread_count - maximum number of threads for testing student code
    tests_timeout - maximum number of seconds for tests to run
    tests_memory_limit - maximum amount of memory per test, in MB
    default_test_env - default TestEnv for running tests

    from_name - the name that emails are from
    from_address - the address that emails are from
    smtp_server - SMTP server host
    smtp_port - SMTP server port
    email_username - username for the SMTP server
    email_password - password for the SMTP server
    email_interval - minimum amount of time to wait between sending emails
"""

import configparser
import os
from getpass import getuser
from time import time

from gkeepcore.assignment_config import TestEnv, AssignmentConfig
from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.path_utils import user_home_dir
from gkeepserver.gkeepd_logger import LogLevel


class ServerConfigurationError(GkeepException):
    """
    Raised if anything goes wrong parsing the configuration file, which should
    always be treated as a fatal error.
    """
    pass


class ServerConfiguration:
    """
    Allows parsing server.cfg and stores the configuration values as
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

        self._init_time = time()

        self.home_dir = os.path.expanduser('~')
        self.username = getuser()

        self.config_path = None

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
            self.config_path = os.path.join(self.home_dir, config_filename)
        else:
            self.config_path = config_path

        if not os.path.isfile(self.config_path):
            error = '{0} does not exist'.format(self.config_path)
            raise ServerConfigurationError(error)

        self._initialize_default_attributes()

        self._parse_config_file()
        self._set_email_options()
        self._set_gkeepd_options()
        self._set_server_options()
        self._set_admin_options()

        self._verify_sections(['email', 'gkeepd', 'server', 'admin'])

        self._parsed = True

    def uptime(self):
        """
        gkeepd uptime, in seconds

        :return: number of seconds since the config object was initialized
        """

        return time() - self._init_time

    @property
    def run_action_sh_file_path(self):
        """
        Get the location of run_action.sh

        run_action.sh is in the home directory of the tester user, so that user
        must exist before this is called.

        :return: location of run_action.sh
        """

        # path to run_action.sh
        return os.path.join(user_home_dir(config.tester_user), 'run_action.sh')

    def _initialize_default_attributes(self):
        # Initialize attributes that have default values

        # path to .gitconfig
        self.gitconfig_file_path = os.path.join(self.home_dir, '.gitconfig')

        # logging
        self.log_file_path = os.path.join(self.home_dir, 'gkeepd.log')

        self.log_level = LogLevel.DEBUG

        # database file location
        self.db_path = os.path.join(self.home_dir, 'gkeepd_db.sqlite')

        # lock file to prevent multiple instances
        self.lock_file_path = os.path.join(self.home_dir, 'gkeepd.lock')

        # testing student code
        self.test_thread_count = 1
        self.tests_timeout = 300
        self.tests_memory_limit = 1024
        self.default_test_env = TestEnv.FIREJAIL

        # users and groups
        self.keeper_user = 'keeper'
        self.keeper_group = 'keeper'
        self.tester_user = 'tester'
        self.faculty_group = 'faculty'
        self.student_group = 'student'

        # email
        self.use_tls = True
        self.email_username = None
        self.email_password = None
        self.email_interval = 2
        self.use_html = True

        # admin
        self.admin_email = None
        self.admin_first_name = None
        self.admin_last_name = None

        self.admin_username = None

    def _parse_config_file(self):
        # Use a ConfigParser object to parse the configuration file and store
        # the state

        self._parser = configparser.ConfigParser()

        try:
            self._parser.read(self.config_path)
        except configparser.ParsingError as e:
            error = 'Error reading {0}: {1}'.format(self.config_path,
                                                    e.message)
            raise ServerConfigurationError(error)

    def _ensure_section_is_present(self, section):
        # Raise an exception if section is not in the config file

        if section not in self._parser.sections():
            error = ('section {0} is not present in {1}'
                     .format(section, self.config_path))
            raise ServerConfigurationError(error)

    def _set_email_options(self):
        # Initialize all the email-related attributes

        self._ensure_section_is_present('email')

        required_options = [
            'from_name',
            'from_address',
            'smtp_server',
            'smtp_port',
        ]

        try:
            for option in required_options:
                setattr(self, option, self._parser.get('email', option))

        except configparser.NoOptionError as e:
            raise ServerConfigurationError(e.message)

        optional_options = [
            'use_tls',
            'email_username',
            'email_password',
            'email_interval',
            'use_html',
        ]

        for name in optional_options:
            # default values of all these options must be set first
            assert hasattr(self, name)

            if self._parser.has_option('email', name):
                value = self._parser.get('email', name)
                setattr(self, name, value)

        # use_tls and use_html must be true or false
        for attr in ('use_tls', 'use_html'):
            if isinstance(getattr(self, attr), str):
                if getattr(self, attr).lower() == 'true':
                    setattr(self, attr, True)
                elif getattr(self, attr).lower() == 'false':
                    setattr(self, attr, False)
                else:
                    error = '{} must be true or false'.format(attr)
                    raise ServerConfigurationError(error)

        # email_interval must be a non-negative number
        if isinstance(self.email_interval, str):
            try:
                self.email_interval = float(self.email_interval)
                if self.email_interval < 0:
                    raise ValueError
            except ValueError:
                error = 'email_interval must be a non-negative number'
                raise ServerConfigurationError(error)

        self._ensure_options_are_valid('email',
                                       required_options + optional_options)

    def _set_server_options(self):
        self._ensure_section_is_present('server')

        try:
            self.hostname = self._parser.get('server', 'hostname')
        except configparser.NoOptionError as e:
            raise ServerConfigurationError(e.message)

    def _set_admin_options(self):
        # set admin-related attributes

        self._ensure_section_is_present('admin')

        required_options = [
            'admin_email',
            'admin_first_name',
            'admin_last_name',
        ]

        try:
            for option in required_options:
                setattr(self, option, self._parser.get('admin', option))
        except configparser.NoOptionError as e:
            raise ServerConfigurationError(e.message)

        try:
            self.admin_username, _ = self.admin_email.split('@')
        except ValueError:
            raise ServerConfigurationError('{} is not a valid email address'
                                           .format(self.admin_email))

        self._ensure_options_are_valid('admin', required_options)

    def _ensure_positive_integer(self, name):
        # raises an exception if the attribute specified by name is not a
        # positive integer

        try:
            setattr(self, name, int(getattr(self, name)))
        except:
            error = '{} must be an integer'
            raise ServerConfigurationError(error)

        if getattr(self, name) <= 0:
            error = '{} must be a positive integer'
            raise ServerConfigurationError(error)

    def _set_gkeepd_options(self):
        # get any optional parameters from the parser and update the attributes
        # from their default values

        if not self._parser.has_section('gkeepd'):
            return

        optional_options = [
            'test_thread_count',
            'tests_timeout',
            'tests_memory_limit',
            'default_test_env',
        ]

        for name in optional_options:
            # default values of all these options must be set first
            assert hasattr(self, name)

            if self._parser.has_option('gkeepd', name):
                value = self._parser.get('gkeepd', name)
                setattr(self, name, value)

        # test_thread_count, tests_timeout, and tests_memory_limit must be
        # positive integers
        positive_integer_options = [
            'test_thread_count',
            'tests_timeout',
            'tests_memory_limit'
        ]

        for name in positive_integer_options:
            self._ensure_positive_integer(name)

        self._validate_default_test_env()

        self._ensure_options_are_valid('gkeepd', optional_options)

    def _validate_default_test_env(self):

        valid_default_envs = [
            TestEnv.HOST,
            TestEnv.FIREJAIL,
        ]

        valid_default_env_names = [
            'host',
            'firejail',
        ]

        if type(self.default_test_env) == str:
            try:
                self.default_test_env = TestEnv[self.default_test_env.upper()]
            except KeyError:
                error = ('{} is not a valid default_test_env, it must be one '
                         'of: {}'.format(self.default_test_env,
                                     ','.join(valid_default_env_names)))
                raise ServerConfigurationError(error)

        if self.default_test_env not in valid_default_envs:
            error = ('{} is not a valid default_test_env, it must be one of: '
                     '{}'.format(self.default_test_env.value,
                                 ','.join(valid_default_env_names)))
            raise ServerConfigurationError(error)

        try:
            AssignmentConfig(config_path='',
                             default_env=self.default_test_env).verify_env()
        except GkeepException as e:
            error = ('Error in default_test_env: {}'.format(e))
            raise ServerConfigurationError(error)

    def _ensure_options_are_valid(self, section, allowed_fields):
        # all section's options must exist be allowed

        for name in self._parser.options(section):
            if not hasattr(self, name) or name not in allowed_fields:
                error = ('{0} is not a valid option in config section [{1}]'
                         .format(name, section))
                raise ServerConfigurationError(error)

    def _verify_sections(self, allowed_sections):
        # check for extra sections

        for section in self._parser.sections():
            if section not in allowed_sections:
                error = ('[{}] is not a valid section'.format(section))
                raise ServerConfigurationError(error)


# Module-level configuration instance. Someone must call parse() on this
# before it is used
config = ServerConfiguration()
