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
from tests.docker_mail_server import start_docker_mail_server, stop_docker_mail_server
from tests.docker_api import DockerAPI
import shutil
from tempfile import TemporaryDirectory
import os


class TestingEnvironment:

    def __init__(self, server_home_dir=None, client_home_dir=None, debug_output=False):

        self._debug_output = debug_output
        self.docker_api = DockerAPI()
        self.temp_server_home = None
        self.temp_client_home = None
        self.temp_email = None

        self.restart(server_home_dir=server_home_dir, client_home_dir=client_home_dir)

    def restart(self, server_home_dir=None, client_home_dir=None):
        # check for the client first because the server stops the network
        if self.docker_api.is_running('git-keeper-client'):
            stop_docker_gkeepclient(self._debug_output)

        if self.docker_api.is_running('git-keeper-mailer'):
            stop_docker_mail_server()

        if self.docker_api.is_running('git-keeper-server'):
            stop_docker_gkeepserver(self._debug_output)

        self.temp_server_home = TemporaryDirectory(dir=os.getcwd())
        temp_server_home_dir = self.temp_server_home.name

        # Copy files to temp dir if provided
        if server_home_dir is not None:
            self._copydir(server_home_dir, temp_server_home_dir)

        # copy the git-keeper configuration file
        shutil.copytree('server_files/config', temp_server_home_dir + '/keeper/.config/grader')
        # copy ssh keys and known_host file
        shutil.copytree('server_files/ssh', temp_server_home_dir + '/keeper/.ssh')

        # FIXME used for testing.  Remove before commit.
        shutil.copy('server_files/send.py', temp_server_home_dir + 'send.py')

        start_docker_gkeepserver(temp_server_home_dir, debug_output=self._debug_output)

        self.temp_client_home = TemporaryDirectory(dir=os.getcwd())
        temp_client_home_dir = self.temp_client_home.name

        if client_home_dir is not None:
            self._copydir(client_home_dir, temp_client_home_dir)

        shutil.copytree('client_files/ssh', temp_client_home_dir + '/prof/.ssh')
        shutil.copytree('client_files/config', temp_client_home_dir + '/prof/.config')
        shutil.copy('client_files/gitconfig', temp_client_home_dir + '/prof/.gitconfig')

        start_docker_gitkeepclient(temp_client_home_dir, debug_output=self._debug_output)

        self.temp_email = TemporaryDirectory(dir=os.getcwd())

        start_docker_mail_server(self.temp_email.name, self._debug_output)

    def _copydir(self, from_dir, to_dir):
        for name in os.listdir(from_dir):
            pathname = from_dir + '/' + name
            if os.path.isdir(pathname):
                shutil.copytree(pathname, to_dir + '/' + name)
            else:
                shutil.copy(pathname, to_dir)

    def get_server_home_dir(self):
        return self.temp_server_home.name

    def get_client_home_dir(self):
        return self.temp_client_home.name

    def get_email_dir(self):
        return self.temp_email.name

    def take_down(self):
        # bring the client down first because server stops the network
        if self.docker_api.is_running('git-keeper-client'):
            stop_docker_gkeepclient(self._debug_output)

        if self.docker_api.is_running('git-keeper-mailer'):
            stop_docker_mail_server()

        if self.docker_api.is_running('git-keeper-server'):
            stop_docker_gkeepserver(self._debug_output)

        self.temp_server_home.cleanup()
        self.temp_client_home.cleanup()
        self.temp_email.cleanup()
