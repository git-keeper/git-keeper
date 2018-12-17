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
from gkeeprobot.keywords.ServerSetupKeywords import ServerSetupKeywords
from gkeeprobot.keywords.ClientSetupKeywords import ClientSetupKeywords

vagrant = VagrantControl()
server = ServerSetupKeywords()
client = ClientSetupKeywords()

print('Checking that gkserver is running...')
if not vagrant.is_server_running():
    print("Server not running.  Run 'vagrant up' first.")
    exit(1)

print('Checking that gkclient is running')
if not vagrant.is_client_running():
    print("Client not running.  Run 'vagrant up' first.")
    exit(1)

print('Copying valid server.cfg')
server.add_file_to_server('keeper', 'files/valid_server.cfg', 'server.cfg')
print('Starting server with admin_prof as admin')
server.start_gkeepd()

print('Making admin_prof account on gkclient')
client.create_accounts('admin_prof')
client.establish_ssh_keys('admin_prof')
client.create_gkeep_config_file('admin_prof')

print('Adding prof1 as faculty on gkserver')
client.run_gkeep_command('admin_prof', 'add_faculty', 'prof1', 'doctor', 'prof1@gitkeeper.edu')

print('Making prof1 account on gkclient')
client.create_accounts('prof1')
client.establish_ssh_keys('prof1')
client.create_gkeep_config_file('prof1')



