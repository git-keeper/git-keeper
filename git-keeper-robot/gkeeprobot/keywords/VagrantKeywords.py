from robot.api import logger
from gkeepcore.shell_command import run_command_in_directory
from gkeeprobot.control.VagrantControl import VagrantControl

control = VagrantControl()


class VagrantKeywords:

    server_was_running = False
    client_was_running = False

    def make_boxes_if_missing(self):
        names = [box.name for box in control.v.box_list()]

        if 'gkserver' not in names:
            logger.console('Making gkserver.box.  This can take up to 30 minutes.')
            run_command_in_directory('gkserver_base', 'bash -c ./make_box.sh')
            control.v.box_add('gkserver', 'gkserver_base/gkserver.box')

        if 'gkclient' not in names:
            logger.console('Making gkclient.box.  This can take up to 30 minutes.')
            run_command_in_directory('gkclient_base', 'bash -c ./make_box.sh')
            control.v.box_add('gkclient', 'gkclient_base/gkclient.box')

    def start_vagrant_if_not_running(self):
        if control.is_server_running():
            logger.console('Using existing gkserver VM...')
            VagrantKeywords.server_was_running = True
        else:
            logger.console('Start gkserver VM...')
            control.v.up(vm_name='gkserver')
        if control.is_client_running():
            logger.console('Using existing gkclient VM...')
            VagrantKeywords.client_was_running = True
        else:
            logger.console('Start gkclient VM...')
            control.v.up(vm_name='gkclient')

    def stop_vagrant_if_not_originally_running(self):
        if VagrantKeywords.server_was_running:
            logger.console('Leaving gkserver VM running...')
        else:
            logger.console('Destroying gkserver VM...')
            control.v.destroy(vm_name='gkserver')
        if VagrantKeywords.client_was_running:
            logger.console('Leaving gkclient VM running...')
        else:
            logger.console('Destroying gkclient VM...')
            control.v.destroy(vm_name='gkclient')

    def set_key_permissions(self):
        run_command_in_directory('ssh_keys', 'chmod 600 *')