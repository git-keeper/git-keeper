from robot.api import logger
from gkeepcore.shell_command import run_command_in_directory
from gkeeprobot.control.VagrantControl import VagrantControl

control = VagrantControl()


class VagrantKeywords:

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

    def start_vagrant(self, vagrant_start):
        if vagrant_start == 'Yes':
            if control.is_server_running():
                raise AssertionError('gkserver already running!')
            if control.is_client_running():
                raise AssertionError('gkclient already running!')
            logger.console('Starting gkserver and gkclient VMs...')
            control.v.up()
        else:
            control.check_status()
            logger.console('Using existing gkserver and gkclient VMS...')

    def stop_vagrant(self, vagrant_stop):
        if vagrant_stop == 'Yes':
            logger.console('Destroying gkserver and gkclient VMs...')
            control.v.destroy()
        else:
            logger.console('Leaving gkserver and gkclient VMs running...')
