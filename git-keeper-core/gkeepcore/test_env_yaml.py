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
Provides a class to validate and provide access to the data in a test_env.yaml
file, which specifies an environment in which to run tests on student code.

To add a new environment type, add entries to TestEnvType, required_fields, and
optional_fields below, add verification to the verify_env() method, add a
method to Submission in gkeepserver.submission to generate a command to run
tests in the new environment, and add a call to your new method to
Submission.run_tests()
"""

import os
from enum import Enum, unique

import yaml
from gkeepcore.shell_command import run_command, CommandError
from gkeepcore.gkeep_exception import GkeepException


@unique
class TestEnvType(Enum):
    """
    Enum for test environment types. The value for each type matches the name
    of the type that is used in test_env.yaml
    """
    HOST = 'host'
    DOCKER = 'docker'
    FIREJAIL = 'firejail'


# Lists of all the required fields for each environment type
required_fields = {
    TestEnvType.HOST: ['type'],
    TestEnvType.DOCKER: ['type', 'image'],
    TestEnvType.FIREJAIL: ['type'],
}

# Lists of optional fields for each environment type
optional_fields = {
    TestEnvType.HOST: [],
    TestEnvType.DOCKER: [],
    TestEnvType.FIREJAIL: ['append_args'],
}

valid_types = [env_type.value for env_type in TestEnvType]


class TestEnv:
    """
    Represents the data in a test_env.yaml file. Attributes will be set based
    on the appropriate fields for each environment type, which are defined in
    required_fields and optional_fields above. If any optional fields are
    omitted, the corresponding attribute is set to None.
    """

    def __init__(self, test_env_path):
        """
        If test_env_path is a valid file path, the file is opened and
        attributes are set according to the contents. If the path is invalid,
        the environment type is set to 'host'.

        A GkeepException is raised for the following conditions:
        - the file contains invalid YAML
        - the YAML data is not key/value pairs
        - the value for any field is not a string
        - the 'type' field is missing
        - any required fields for the specified type are missing
        - any fields are used that are not required or optional fields for the
          type

        :param test_env_path: the path to the test_env.yaml file, which may or
         may not exist
        """

        if os.path.isfile(test_env_path):
            with open(test_env_path) as test_env_file:
                try:
                    data = yaml.safe_load(test_env_file)
                except yaml.YAMLError as e:
                    raise GkeepException('Error in YAML file {}:\n{}'
                                         .format(test_env_path, e))
        else:
            # if there is no test env config file, default to host
            data = {'type': 'host'}

        if type(data) != dict:
            raise GkeepException('{} must contain key/value pairs'
                                 .format(test_env_path))

        if 'type' not in data:
            raise GkeepException('{} is missing the type field'
                                 .format(test_env_path))

        if type(data['type']) != str:
            raise GkeepException('The "type" field in {} must be a string'
                                 .format(test_env_path))

        try:
            self.type = TestEnvType(data['type'].lower())
        except ValueError:
            raise GkeepException('Invalid type "{}" in {}\n'
                                 'Type must be one of: {}'
                                 .format(data['type'], test_env_path,
                                         ','.join(valid_types)))

        # ensure all required fields are present
        for field in required_fields[self.type]:
            if field not in data:
                raise GkeepException('Missing field "{}" for test env type '
                                     '"{}" in {}'
                                     .format(field, self.type.value,
                                             test_env_path))

        # ensure that all fields set in test_env.yaml are valid fields, and
        # set attributes for this object based on the fields
        available_fields = \
            required_fields[self.type] + optional_fields[self.type]
        for field in data:
            if field not in available_fields:
                raise GkeepException('Invalid field "{}" for test env type '
                                     '"{}" in {}'.format(field,
                                                         self.type.value,
                                                         test_env_path))
            if type(data[field]) != str:
                raise GkeepException('The value for field "{}" in {} must be '
                                     'a string'.format(field, test_env_path))
            # only set an attribute if the field is not 'type', since that
            # would overwrite the enum type
            if field != 'type':
                setattr(self, field, data[field])

        # set any unused optional fields for this type to None
        for field in optional_fields[self.type]:
            if not hasattr(self, field):
                setattr(self, field, None)

    def verify_env(self):
        """
        Verify that the server is set up to support the test environment type.

        For Docker, it must be installed and the selected image must exist.
        For firejail, it must be installed.

        Raises GkeepException if there is an issue with the environment.
        """
        if self.type == TestEnvType.DOCKER:
            verify_docker_installed()
            verify_docker_image(self.image)
        elif self.type == TestEnvType.FIREJAIL:
            verify_firejail_installed()


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
