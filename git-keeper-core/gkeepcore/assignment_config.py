# Copyright 2022 Nathan Sommer and Ben Coleman
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
This module provides access to the data from an assignments assignment.cfg
file, and provides functions for verifying suitable server environments for
running tests.
"""

import configparser
import os
from enum import Enum, unique

from gkeepcore.gkeep_exception import GkeepException
from gkeepcore.shell_command import run_command, CommandError


@unique
class TestEnv(Enum):
    """
    Enum for test environment types. The value for each type matches the name
    of the type that is used in assignment.cfg
    """
    HOST = 'host'
    DOCKER = 'docker'
    FIREJAIL = 'firejail'


# Lists of all the required fields for each environment type
env_required_fields = {
    TestEnv.HOST: [],
    TestEnv.DOCKER: ['image'],
    TestEnv.FIREJAIL: [],
}

# Lists of optional fields for each environment type
env_optional_fields = {
    TestEnv.HOST: [],
    TestEnv.DOCKER: [],
    TestEnv.FIREJAIL: ['append_args'],
}

valid_envs = [env_type.value for env_type in TestEnv]


class AssignmentConfig:
    """
    Represents the data in an assignment.cfg file.
    """

    def __init__(self, config_path, default_env=None):
        """
        If config_path is a valid file path, the file is opened and attributes
        are set according to the contents. If the path does not exist, default
        attributes are used.

        Raises GkeepException if options are missing or should not be present
        given the test env type, if an invalid option or section is used,
        or if an option has an invalid type or value.

        :param config_path: path to the config file, which may or may not
         exist
        :param default_env: TestEnv to use if none is specified
        """

        self.config_path = config_path

        self._initialize_default_attributes(default_env)

        self._parse_config_file()

        self._validate_sections()

        self._set_tests_options()
        self._set_email_options()

    def verify_env(self):
        """
        Verify that the server is set up to support the test environment type.

        For Docker, it must be installed and the selected image must exist.
        For firejail, it must be installed.

        Raises GkeepException if there is an issue with the environment.
        """
        if self.env == TestEnv.DOCKER:
            verify_docker_installed()
            verify_docker_image(self.image)
        elif self.env == TestEnv.FIREJAIL:
            verify_firejail_installed()

    def _initialize_default_attributes(self, default_env):
        # Initialize attributes to their defaults

        # [tests]
        self.env = default_env
        self.append_args = None
        self.image = None
        self.timeout = None
        self.memory_limit = None

        # [email]
        self.use_html = None
        self.announcement_subject = '[{class_name}] New assignment: {assignment_name}'
        self.results_subject = '[{class_name}] {assignment_name} submission test results'

    def _parse_config_file(self):
        # Use a ConfigParser object to parse the configuration file and store
        # the state

        self._parser = configparser.ConfigParser()

        if os.path.isfile(self.config_path):
            try:
                self._parser.read(self.config_path)
            except configparser.ParsingError as e:
                error = 'Error reading {0}: {1}'.format(self.config_path,
                                                        e.message)
                raise GkeepException(error)
        else:
            self._parser.read('')

    def _validate_sections(self):
        valid_sections = [
            'tests',
            'email',
        ]

        for section in self._parser.sections():
            if section not in valid_sections:
                error = 'Invalid section [{}] in {}'.format(section,
                                                            self.config_path)
                raise GkeepException(error)

    def _set_tests_options(self):
        # get any optional parameters from the parser and update the attributes
        # from their default values

        if not self._parser.has_section('tests'):
            return

        optional_options = [
            'env',
            'append_args',
            'image',
            'timeout',
            'memory_limit',
        ]

        for name in optional_options:
            # default values of all these options must be set first
            assert hasattr(self, name)

            if self._parser.has_option('tests', name):
                value = self._parser.get('tests', name)
                setattr(self, name, value)

        # timeout and memory_limit must be positive integers
        positive_integer_options = [
            'timeout',
            'memory_limit',
        ]

        for name in positive_integer_options:
            if getattr(self, name) is not None:
                self._ensure_positive_integer(name)

        if self.env is not None:
            self._validate_test_env()

        self._ensure_options_are_valid('tests', optional_options)

    def _validate_test_env(self):
        # Validate that the test env type is valid, and that any options used
        # work with that env type

        if type(self.env) != TestEnv:
            try:
                self.env = TestEnv(self.env.lower())
            except ValueError:
                raise GkeepException('Invalid test env "{}" in {}\n'
                                     'env must be one of: {}'
                                     .format(self.env, self.config_path,
                                             ','.join(valid_envs)))

        for field in env_required_fields[self.env]:
            if getattr(self, field) is None:
                raise GkeepException('Missing field "{}" for test env type '
                                     '"{}" in {}'
                                     .format(field, self.env.value,
                                             self.config_path))

        available_fields = \
            env_required_fields[self.env] + env_optional_fields[self.env]

        all_env_options = []
        for required in env_required_fields.values():
            for option in required:
                all_env_options.append(option)

        for optional in env_optional_fields.values():
            for option in optional:
                all_env_options.append(option)

        for option in all_env_options:
            value = getattr(self, option)
            if value is not None and option not in available_fields:
                raise GkeepException('Invalid field "{}" for test env type '
                                     '"{}" in {}'.format(option,
                                                         self.env.value,
                                                         self.config_path))

    def _set_email_options(self):
        # Initialize all the email-related attributes

        if not self._parser.has_section('email'):
            return

        optional_options = [
            'use_html',
            'announcement_subject',
            'results_subject',
        ]

        for name in optional_options:
            # default values of all these options must be set first
            assert hasattr(self, name)

            if self._parser.has_option('email', name):
                value = self._parser.get('email', name)
                setattr(self, name, value)

        # use_html must be true or false if not None
        for attr in ('use_html',):
            if isinstance(getattr(self, attr), str):
                if getattr(self, attr).lower() == 'true':
                    setattr(self, attr, True)
                elif getattr(self, attr).lower() == 'false':
                    setattr(self, attr, False)
                else:
                    error = '{} must be true or false'.format(attr)
                    raise GkeepException(error)

        self._ensure_options_are_valid('email', optional_options)

    def _ensure_options_are_valid(self, section, allowed_fields):
        # all section's options must be allowed

        for name in self._parser.options(section):
            if name not in allowed_fields:
                error = ('{0} is not a valid option in config section [{1}]'
                         .format(name, section))
                raise GkeepException(error)

    def _ensure_positive_integer(self, name):
        # raises an exception if the attribute specified by name is not a
        # positive integer

        try:
            setattr(self, name, int(getattr(self, name)))
        except ValueError:
            error = '{} must be an integer'
            raise GkeepException(error)

        if getattr(self, name) <= 0:
            error = '{} must be a positive integer'
            raise GkeepException(error)


def verify_firejail_installed():
    """
    Determine if firejail is installed.
    Raises GkeepException firejail is not installed.
    """
    cmd = ['firejail', '--version']
    try:
        run_command(cmd)
    except CommandError:
        raise GkeepException('firejail does not appear to be installed on '
                             'the server')


def verify_docker_installed():
    """
    Determine if Docker is installed.
    Raises GkeepException if Docker is not installed.
    """
    cmd = ['docker', '--version']

    try:
        run_command(cmd)
    except CommandError:
        raise GkeepException('docker does not appear to be installed on the '
                             'server')


def verify_docker_image(image):
    """
    Determine whether a Docker image exits.
    Raises GkeepException if the image does not exist

    NOTE: Docker is a requirement on the server, but not faculty machines, so
          this should only be run on the server.
    """
    # This command taken from https://github.com/distribution/distribution/issues/2412
    cmd = ['docker', 'manifest', 'inspect', image]
    try:
        run_command(cmd)
    except CommandError:
        raise GkeepException('Docker image not found: {}'.format(image))
