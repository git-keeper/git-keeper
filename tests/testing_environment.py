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

from tests.docker_gkeepserver import start_docker_gkeepserver, \
    stop_docker_gkeepserver
from tests.docker_gkeeperclient import start_docker_gitkeepclient, \
    stop_docker_gkeepclient, run_client_command
from tests.docker_api import DockerAPI
import shutil
from tempfile import TemporaryDirectory
import os


class TestingEnvironment:
    """
    This class encapsulates the functionality to bring up a clean git-keeper
    server.  To be honest, this process is quite fragile.  It puts files
    in the server_files folder on the server and files in client_files on
    the client, but that is done via custom code.  Don't expect files you
    put there to automatically show up!

    Current activities:
    - Establish the Docker env variables (if necessary)
    - stop any existing client/server
    - create temp files for server and client files / copy files to those dirs
    - start the server container
        - install current source for core and server
        - start gkeepd (this will create professor accounts from faculty.csv
    - start the client container
        - install current source for core, server, and client
        - establish ssh keys for prof account on server (reads email from server)
    """

    def __init__(self, server_home_dir=None, client_home_dir=None, debug_output=False):
        """
        Initialize the environment be stopping existing server/client and
                starting new ones.
        :param server_home_dir: Files to copy to the server (NOT TESTED!)
        :param client_home_dir: Files to copy to the client (NOT TESTED!)
        :param debug_output: whether to show verbose output
        :return: None
        """

        self._debug_output = debug_output
        self.docker_api = DockerAPI()
        self.temp_server_home = None
        self.temp_client_home = None
        self.temp_email = None

        self.restart(server_home_dir=server_home_dir, client_home_dir=client_home_dir)

    def restart(self, server_home_dir=None, client_home_dir=None):
        """
        Stop existing instances of the server/client and start new ones
        :param server_home_dir: Files to copy to the server (NOT TESTED!)
        :param client_home_dir: Files to copy to the client (NOT TESTED!)
        :return: None
        """
        # check for the client first because the server stops the network
        if self.docker_api.is_running('git-keeper-client'):
            stop_docker_gkeepclient(self._debug_output)

        if self.docker_api.is_running('git-keeper-server'):
            stop_docker_gkeepserver(self._debug_output)

        self.temp_server_home = TemporaryDirectory(prefix='tmp_server', dir=os.getcwd())
        temp_server_home_dir = self.temp_server_home.name

        # Copy files to temp dir if provided
        if server_home_dir is not None:
            self._copydir(server_home_dir, temp_server_home_dir)

        # copytree first because it creates the directories needed by the copy
        # copy ssh keys and known_host file
        shutil.copytree('server_files/ssh', temp_server_home_dir + '/.ssh')
        # copy the git-keeper configuration files
        shutil.copy('server_files/server.cfg', temp_server_home_dir)
        shutil.copy('server_files/faculty.csv', temp_server_home_dir)


        # FIXME changed to only mount keeper home.  When /home mounted
        # accounts made by gkeepd weren't accessible - permissions problem.
        # I also changed code in docker_gkeepserver.py to make this work.
        #shutil.copytree('server_files/ssh', temp_server_home_dir + '/keeper/.ssh')
        # copy the git-keeper configuration files
        #shutil.copy('server_files/server.cfg', temp_server_home_dir + '/keeper')
        #shutil.copy('server_files/faculty.csv', temp_server_home_dir + '/keeper')

        self.temp_email = TemporaryDirectory(prefix='tmp_mail', dir=os.getcwd())
        temp_email_dir = self.temp_email.name

        start_docker_gkeepserver(temp_server_home_dir, temp_email_dir,
                                 debug_output=self._debug_output)

        self.temp_client_home = TemporaryDirectory(prefix='tmp_client', dir=os.getcwd())
        temp_client_home_dir = self.temp_client_home.name

        if client_home_dir is not None:
            self._copydir(client_home_dir, temp_client_home_dir)

        shutil.copytree('client_files/ssh', temp_client_home_dir + '/prof/.ssh')
        shutil.copytree('client_files/config', temp_client_home_dir + '/prof/.config')
        shutil.copy('client_files/gitconfig', temp_client_home_dir + '/prof/.gitconfig')
        shutil.copy('client_files/set-keys', temp_client_home_dir + '/prof/set-keys')

        start_docker_gitkeepclient(temp_client_home_dir, debug_output=self._debug_output)

        # To set up the ssh key for prof@gkclient we need to know the pw
        # gkeepd has to create the account and send the password, and this
        # takes time.  If we do this before starting the client, that work
        # isn't done, and the following fails.
        pw = self._get_prof_pw()
        print('\n\nprof password:', pw)

        run_client_command('./set-keys prof gkserver ' + pw, debug_output=self._debug_output)

    def _copydir(self, from_dir, to_dir):
        """
        helper function, but I don't remember why I did it.  The name
        implies it only works for directory, but the implementation  seems
        to work for a file or a directory
        """
        for name in os.listdir(from_dir):
            pathname = from_dir + '/' + name
            if os.path.isdir(pathname):
                shutil.copytree(pathname, to_dir + '/' + name)
            else:
                shutil.copy(pathname, to_dir)

    def _get_prof_pw(self):
        """
        Get the password for the prof account on the server.

        This is fragile.  It assumes the professor account will be named
        prof and that the server has had enough time running to create the
        account / welcome email.  It also assumes that the welcome email
        will be the first email.

        :return: the password of prof (string)
        """
        email_dir = self.temp_email.name

        with open(email_dir + '/prof1.txt') as f:

            for line in f:
                if line.startswith('Password'):
                    return line.split()[1]

    def take_down(self):
        """
        Bring down the client, server, and docker network.  Cleanup the temp
        directories.
        :return:
        """
        # bring the client down first because server stops the network
        if self.docker_api.is_running('git-keeper-client'):
            stop_docker_gkeepclient(self._debug_output)

        if self.docker_api.is_running('git-keeper-server'):
            stop_docker_gkeepserver(self._debug_output)

        self.temp_server_home.cleanup()
        self.temp_client_home.cleanup()
        self.temp_email.cleanup()
