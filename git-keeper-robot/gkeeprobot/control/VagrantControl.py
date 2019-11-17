# Copyright 2018 Nathan Sommer and Ben Coleman
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

import vagrant

"""Provides methods to interact with the gkclient and gkserver VMs."""


class VagrantControl:
    up_verified = False
    client_port = -1
    server_port = -1

    def __init__(self):
        self.v = vagrant.Vagrant()

    def is_server_running(self):
        result = self.v.status(vm_name='gkserver')
        return result[0].state == 'running'

    def is_client_running(self):
        result = self.v.status(vm_name='gkclient')
        return result[0].state == 'running'

    def get_client_port(self):
        if VagrantControl.client_port == -1:
            VagrantControl.client_port = self.v.port(vm_name='gkclient')
        return VagrantControl.client_port

    def get_server_port(self):
        if VagrantControl.server_port == -1:
            VagrantControl.server_port = self.v.port(vm_name='gkserver')
        return VagrantControl.server_port
