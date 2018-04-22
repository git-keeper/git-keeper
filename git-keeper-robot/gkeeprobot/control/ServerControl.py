from gkeepcore.shell_command import run_command
from gkeeprobot.control.VagrantControl import VagrantControl


class ServerControl:

    def __init__(self):
        self.v = VagrantControl()

    def run_server_script(self, username, script, *args):
        base = 'python3 /vagrant/server_scripts/' + script
        cmd = ' '.join([base] + list(args))
        return self.run(username, cmd).strip()

    def run(self, username, cmd):
        base = 'ssh localhost'
        port = '-p {}'.format(self.v.get_server_port())
        user_and_key = '-l {} -i ssh_keys/{}_rsa'.format(username, username)
        suppress_warnings = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR'

        full_cmd = ' '.join([base, port, user_and_key, suppress_warnings, cmd])
        return run_command(full_cmd)

    def copy(self, username, filename, target_filename):
        base = 'scp'
        port = '-P {}'.format(self.v.get_server_port())
        key = '-i ssh_keys/{}_rsa'.format(username, username)
        suppress_warnings = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR'
        copy = '{} {}@localhost:{}'.format(filename, username, target_filename)

        full_cmd = ' '.join([base, port, key, suppress_warnings, copy])
        return run_command(full_cmd)
