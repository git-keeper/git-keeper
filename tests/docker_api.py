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

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
import json
import requests
import base64
import iso8601
from subprocess import Popen, PIPE
from urllib.parse import urlparse


class DockerAPI:

    def __init__(self):

        # We will use an unverified certificate, which would
        # normally print a warning.
        urllib3.disable_warnings(category=InsecureRequestWarning)

        # FIXME this assumes MAC/PC verion of Docker
        # FIXME this is a near-duplication to code in DockerCommand
        # we need to determine the host IP and the port number
        # as well as the base address of the TLS certificate
        command = 'docker-machine env'
        with Popen(command, shell=True, stdout=PIPE, stderr=PIPE,\
                   universal_newlines=True) as proc:
            env_values, std_error = proc.communicate()

            for line in env_values.split('\n'):
                line = line.strip()
                if len(line) == 0 or line.startswith('#'):
                    continue

                # each line is "export KEY=VALUE", isolate the key/value
                pair = line.split()[1]
                [key, value] = pair.split('=')

                # get rid of surrounding quotes.
                value = value.strip('"')

                if 'HOST' in key:
                    result = urlparse(value)

                    # we will always use https for communication
                    self.url_base = 'https://' + result.netloc
                elif 'CERT' in key:
                    self.cert = (value + '/cert.pem',\
                                 value + '/key.pem')

    def is_running(self, container_name):

        url = self.url_base + '/containers/json'

        ret = requests.get(url, cert=self.cert, verify=False)

        container_list = list(ret.json())

        for container_dict in container_list:
            if container_dict['Image'] == container_name:
                return True

        return False

    def get_file_mod_date(self, container_name, file_path):

        url = self.url_base + "/containers/" + container_name + "/archive"
        params = {"path":file_path}
        ret = requests.head(url, params=params, cert = self.cert, verify=False)

        if ret.status_code != 200:
            return None

        file_stats_str = base64.b64decode(ret.headers['X-Docker-Container-Path-Stat']).decode()

        file_stats_dict = json.loads(file_stats_str)

        file_timestamp = file_stats_dict['mtime']

        print(file_timestamp)
        return iso8601.parse_date(file_timestamp)
