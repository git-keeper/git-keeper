import vagrant
from gkeepcore.shell_command import run_command


class VagrantControl:

    def __init__(self):
        self.v = vagrant.Vagrant()

    def start_vagrant(self):
        self.v.up()

    def start_gkeepd(self):
        self.run_on_server('keeper', 'screen -S gkserver -d -m gkeepd')

    def stop_gkeepd(self):
        self.run_on_server('keeper', 'screen -S gkserver -X quit')

    def stop_vagrant(self):
        self.v.destroy()

    def expect_email(self, to_user, contains):
        result = self.run_server_script('keeper', 'email_check.py', to_user, contains)
        assert result == 'True'

    def user_exists(self, username):
        result = self.run_server_script('keeper', 'user_exists.py', username)
        assert result == 'True'

    def remove_user(self, username):
        self.run_on_server('keeper', 'sudo userdel -r {}'.format(username))
        result = self.run_server_script('keeper', 'user_exists.py', username)
        assert result == 'False'

    def remove_file(self, username, filename):
        self.run_on_server(username, 'rm {}'.format(filename))

    def clear_email(self):
        self.run_on_server('keeper', 'sudo find /email ! -name "mysmtpd.py" -type f -exec rm -f {} +')

    def run_on_server(self, username, cmd):
        return self.run_on(username, cmd, self.server_port())

    def run_on_client(self, username, cmd):
        return self.run_on(username, cmd, self.client_port())

    def run_server_script(self, username, script, *args):
        base = 'python3 /vagrant/server_scripts/' + script
        cmd = ' '.join([base] + list(args))
        return self.run_on_server(username, cmd).strip()

    def run_on(self, username, cmd, port):
        base = 'ssh localhost'
        port = '-p {}'.format(port)
        user = '-l {} -i ssh_keys/{}_rsa'.format(username, username)
        other = '-o StrictHostKeyChecking=no'

        full_cmd = ' '.join([base, port, user, other, cmd])
        return run_command(full_cmd)

    def server_port(self):
        return self.v.port(vm_name='gkserver')

    def client_port(self):
        return self.v.port(vm_name='gkclient')
