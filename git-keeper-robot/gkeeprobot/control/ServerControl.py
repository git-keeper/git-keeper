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

from gkeeprobot.control.VagrantControl import VagrantControl
from gkeeprobot.control.VMControl import VMControl

"""Provides methods to run commands on gkserver during testing."""


class ServerControl:

    def __init__(self):
        self.v = VagrantControl()
        self.vm_control = VMControl()

    def run_vm_python_script(self, username, script, *args):
        return self.vm_control.run_vm_python_script(username, script,
                                                    self.v.get_server_port(),
                                                    *args)

    def run_vm_bash_script(self, username, script, *args):
        return self.vm_control.run_vm_bash_script(username, script,
                                                  self.v.get_server_port(),
                                                  *args)

    def run(self, username, cmd):
        return self.vm_control.run(username, self.v.get_server_port(), cmd)

    def copy(self, username, filename, target_filename):
        self.vm_control.copy(username, self.v.get_server_port(),
                                    filename, target_filename)
