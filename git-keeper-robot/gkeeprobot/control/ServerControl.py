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

        port = self.v.get_server_port()

        base = 'ssh localhost'
        port = '-p {}'.format(port)
        user_and_key = '-l {} -i ssh_keys/{}_rsa'.format(username, username)
        suppress_warnings = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR'

        full_cmd = ' '.join([base, port, user_and_key, suppress_warnings, cmd])
        return run_command(full_cmd)
