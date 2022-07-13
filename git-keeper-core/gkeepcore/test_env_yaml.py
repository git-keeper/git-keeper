# Copyright 2022, 2018 Nathan Sommer and Ben Coleman
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
Provides a class to validate and provide access to the data in a test_env.yaml file
"""

import yaml
from gkeepcore.shell_command import run_command, CommandError
from gkeepcore.gkeep_exception import GkeepException


valid_types = ['docker', 'host']


class TestEnv:
    """
    Represents the data in a test_env.yaml file.  "type" is a required field,
    and may contain the values "host" or "docker".  If "type" is "docker" then
    "image" is also required.  It's value should specify a valid Docker image.
    """

    def __init__(self, test_env_path):
        """
        Open the file and load the value.  This will raise a GKeepException if
        the YAML is not valid, but no additional validation is performed.
        """
        with open(test_env_path) as test_env_file:
            try:
                self.data = yaml.safe_load(test_env_file)
            except yaml.YAMLError:
                raise GkeepException('Bad YAML file: {}'.format(test_env_path))

    def type(self):
        """ Get the type """
        return self.data['type'].lower()

    def image(self):
        """ Get the image """
        return self.data['image']

    def validate(self, verify_image=False):
        """
        Validate the data.  If verify_image is True, this will use Docker
        to determine if the specified image is valid.

        Raises a GkeepException if any checks fail
        """
        if 'type' not in self.data:
            raise GkeepException('missing type')
        if self.data['type'] not in valid_types:
            raise GkeepException('Type must be one of: {}'.format(valid_types))
        if self.type() == 'docker' and 'image' not in self.data:
            raise GkeepException('missing image in docker type')

        if verify_image and self.type() == 'docker':
            verify_docker_image(self.data['image'])


def verify_docker_image(image):
    """
    Determine whether a Docker image exits.
    Raises GkeepException if the image does not exist

    NOTE: Docker is a requirement on the server, but not faculty machines, so this
          should only be run on the server.
    """
    # This command taken from https://github.com/distribution/distribution/issues/2412
    cmd = ['docker', 'buildx', 'imagetools', 'inspect', image]
    try:
        run_command(cmd)
    except CommandError:
        raise GkeepException('Docker image not found: '.format(image))
