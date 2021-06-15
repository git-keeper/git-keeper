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
from gkeeprobot.keywords.ClientCheckKeywords import ClientCheckKeywords

vagrant = VagrantControl()
server = ServerSetupKeywords()
client = ClientSetupKeywords()
client_check = ClientCheckKeywords()

print('Checking that gkserver is running')
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
client.create_account('admin_prof')
client.establish_ssh_keys('admin_prof')
client.create_gkeep_config_file('admin_prof')

print('Adding prof1 as faculty on gkserver')
client.run_gkeep_command('admin_prof', 'add_faculty', 'prof1', 'doctor', 'prof1@gitkeeper.edu')

print('Making prof1 account on gkclient')
client.create_account('prof1')
client.establish_ssh_keys('prof1')
client.create_gkeep_config_file('prof1')

print('Creating CS1 class with 2 students')
client.add_to_class_csv('prof1', 'cs1', 'student1')
client.add_to_class_csv('prof1', 'cs1', 'student2')
client.run_gkeep_command('prof1', '--yes add cs1 cs1.csv')
client.add_assignment_to_client('prof1', 'good_simple')

print('Making student1 and student2 accounts on gkclient')
client.create_account('student1')
client.establish_ssh_keys('student1')
client.create_git_config('student1')
client.create_account('student2')
client.establish_ssh_keys('student2')
client.create_git_config('student2')

print('Prof1 Uploads and Publishes Assignment')
client_check.gkeep_upload_succeeds('prof1', 'cs1', 'good_simple')
client_check.gkeep_publish_succeeds('prof1', 'cs1', 'good_simple')

print('Student1 Clones and Submits Assignment')
client.clone_assignment('student1', 'prof1', 'cs1', 'good_simple')
client.student_submits('student1', 'prof1', 'cs1', 'good_simple', 'correct_solution')

print('Prof1 fetches assignment')
client.fetch_assignment('prof1', 'cs1', 'good_simple', 'fetched_assignments')