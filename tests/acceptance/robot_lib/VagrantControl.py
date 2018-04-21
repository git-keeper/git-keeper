import vagrant
from gkeepcore.shell_command import run_command, run_command_in_directory
from robot.api import logger

class VagrantControl:

    def __init__(self):
        self.v = vagrant.Vagrant()
        self.up_verified = False

    def make_boxes_if_missing(self):
        names = [box.name for box in self.v.box_list()]

        if 'gkserver' not in names:
            logger.console('Making gkserver.box.  This can take up to 30 minutes but only executes once per system.')
            run_command_in_directory('gkserver_base', 'bash -c ./make_box.sh')
            self.v.box_add('gkserver', 'gkserver_base/gkserver.box')

        if 'gkclient' not in names:
            logger.console('Making gkclient.box.  This can take up to 30 minutes but only executes once per system.')
            run_command_in_directory('gkclient_base', 'bash -c ./make_box.sh')
            self.v.box_add('gkclient', 'gkclient_base/gkclient.box')

    def start_vagrant(self, vagrant_start):
        if vagrant_start == 'Yes':
            if self.is_server_running():
                raise AssertionError('gkserver already running!')
            if self.is_client_running():
                raise AssertionError('gkclient already running!')
            logger.console('Starting gkserver and gkclient VMs...')
            self.v.up()
        else:
            self.check_status()
            logger.console('Using existing gkserver and gkclient VMS...')

    def start_gkeepd(self):
        self.run_on_server('keeper', 'screen -S gkserver -d -m gkeepd')

    def stop_gkeepd(self):
        self.run_on_server('keeper', 'screen -S gkserver -X quit')

    def stop_vagrant(self, vagrant_stop):
        if vagrant_stop == 'Yes':
            logger.console('Destroying gkserver and gkclient VMs...')
            self.v.destroy()
        else:
            logger.console('Leaving gkserver and gkclient VMs running...')

    def expect_email(self, to_user, contains):
        result = self.run_server_script('keeper', 'email_check.py', to_user, contains)
        assert result == 'True'

    def user_exists(self, username):
        result = self.run_server_script('keeper', 'user_exists.py', username)
        assert result == 'True'

    def remove_user(self, username):
        self.run_on_server('keeper', 'sudo userdel -r {} || :'.format(username))

    def remove_file(self, username, filename):
        self.run_on_server(username, 'rm {}'.format(filename))

    def clear_email(self):
        self.run_on_server('keeper', 'sudo find /email ! -name "mysmtpd.py" -type f -exec rm -f {} +')

    def run_on_server(self, username, cmd):
        return self.run_on(username, cmd, self.get_server_port())

    def run_on_client(self, username, cmd):
        return self.run_on(username, cmd, self.get_client_port())

    def run_server_script(self, username, script, *args):
        base = 'python3 /vagrant/server_scripts/' + script
        cmd = ' '.join([base] + list(args))
        return self.run_on_server(username, cmd).strip()

    def run_on(self, username, cmd, port):
        self.check_status()
        base = 'ssh localhost'
        port = '-p {}'.format(port)
        user_and_key = '-l {} -i ssh_keys/{}_rsa'.format(username, username)
        suppress_warnings = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR'

        full_cmd = ' '.join([base, port, user_and_key, suppress_warnings, cmd])
        return run_command(full_cmd)

    def is_server_running(self):
        result = self.v.status(vm_name='gkserver')
        return result[0].state == 'running'

    def is_client_running(self):
        result = self.v.status(vm_name='gkclient')
        return result[0].state == 'running'

    def check_status(self):
        if self.up_verified:
            return
        if not self.is_server_running():
            raise AssertionError('gkserver not running')
        if not self.is_client_running():
            raise AssertionError('gkclient not running')
        self.up_verified = True

    def get_client_port(self):
        self.check_status()
        return self.v.port(vm_name='gkclient')

    def get_server_port(self):
        self.check_status()
        return self.v.port(vm_name='gkserver')
