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

from robot.api import logger
from gkeepcore.shell_command import run_command_in_directory
from gkeeprobot.control.VagrantControl import VagrantControl
from gkeeprobot.control.ServerControl import ServerControl
from gkeeprobot.control.ClientControl import ClientControl

vagrant_control = VagrantControl()
server_control = ServerControl()
client_control = ClientControl()


class VagrantKeywords:

    server_was_running = False
    client_was_running = False

    def make_boxes_if_missing(self):
        names = [box.name for box in vagrant_control.v.box_list()]

        if 'gkserver' not in names:
            logger.console('Making gkserver.box.  '
                           'This can take up to 30 minutes.')
            run_command_in_directory('gkserver_base', 'bash -c ./make_box.sh')
            vagrant_control.v.box_add('gkserver', 'gkserver_base/gkserver.box')

        if 'gkclient' not in names:
            logger.console('Making gkclient.box.  '
                           'This can take up to 30 minutes.')
            run_command_in_directory('gkclient_base', 'bash -c ./make_box.sh')
            vagrant_control.v.box_add('gkclient', 'gkclient_base/gkclient.box')

    def start_vagrant_if_not_running(self):
        if vagrant_control.is_server_running():
            logger.console('Using existing gkserver VM...')
            VagrantKeywords.server_was_running = True
        else:
            logger.console('Start gkserver VM...')
            vagrant_control.v.up(vm_name='gkserver')
        if vagrant_control.is_client_running():
            logger.console('Using existing gkclient VM...')
            VagrantKeywords.client_was_running = True
        else:
            logger.console('Start gkclient VM...')
            vagrant_control.v.up(vm_name='gkclient')

    def stop_vagrant_if_not_originally_running(self):
        if VagrantKeywords.server_was_running:
            logger.console('Leaving gkserver VM running...')
        else:
            logger.console('Destroying gkserver VM...')
            vagrant_control.v.destroy(vm_name='gkserver')
        if VagrantKeywords.client_was_running:
            logger.console('Leaving gkclient VM running...')
        else:
            logger.console('Destroying gkclient VM...')
            vagrant_control.v.destroy(vm_name='gkclient')

    def set_key_permissions(self):
        run_command_in_directory('ssh_keys', 'chmod 600 *')
