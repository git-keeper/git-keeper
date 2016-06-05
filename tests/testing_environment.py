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

from tests.docker_gkeepserver import start_docker_gkeepserver, stop_docker_gkeepserver
from tests.docker_gkeeperclient import start_docker_gitkeepclient, stop_docker_gkeepclient
from tests.docker_api import DockerAPI
import shutil
from tempfile import TemporaryDirectory
import os

class TestingEnvironment:

    def __init__(self, server_home_dir=None, debug_output=False):

        self._debug_output = debug_output
        self.dapi = DockerAPI()
        self.temp_home = TemporaryDirectory(dir=os.getcwd())

        self.restart(server_home_dir)

    def restart(self, server_home_dir=None):
        # check for the client first because the server stops the network
        if self.dapi.is_running('git-keeper-client'):
            stop_docker_gkeepclient(self._debug_output)

        if self.dapi.is_running('git-keeper-server'):
            stop_docker_gkeepserver(self._debug_output)

        self.temp_home = TemporaryDirectory(dir=os.getcwd())
        temp_home_dir = self.temp_home.name

        print(temp_home_dir)

        # copy the git-keeper configuration file
        shutil.copytree('server_files/config', temp_home_dir + '/keeper/.config/grader')
        # copy ssh keys and known_host file
        shutil.copytree('server_files/ssh', temp_home_dir + '/keeper/.ssh')

        start_docker_gkeepserver(temp_home_dir, debug_output=self._debug_output)
        start_docker_gitkeepclient(debug_output=self._debug_output)

    def get_server_home_dir(self):
        return self.temp_home.name

    def take_down(self):
        # bring the client down first because server stops the network
        if self.dapi.is_running('git-keeper-client'):
            stop_docker_gkeepclient(self._debug_output)

        if self.dapi.is_running('git-keeper-server'):
            stop_docker_gkeepserver(self._debug_output)

        self.temp_home.cleanup()