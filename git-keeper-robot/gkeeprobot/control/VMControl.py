
from gkeepcore.shell_command import run_command
from tempfile import TemporaryDirectory


class VMControl:

    temp_dir = TemporaryDirectory(prefix='temp_ssh_keys', dir='.')

    def run_vm_python_script(self, username, script, port, *args):
        base = 'python3 /vagrant/vm_scripts/' + script
        cmd = ' '.join([base] + list(args))
        return self.run(username, port, cmd).strip()

    def run_vm_bash_script(self, username, script, port, *args):
        base = 'bash -c /vagrant/vm_scripts/' + script
        cmd = ' '.join([base] + list(args))
        return self.run(username, port, cmd).strip()

    def run(self, username, port, cmd):
        base = 'ssh localhost'
        port = '-p {}'.format(port)
        if username == 'keeper':
            user_and_key = '-l {} -i ssh_keys/{}_rsa'.format(username, username)
        else:
            user_and_key = '-l {} -i {}/{}_rsa'.format(username, self.temp_dir.name, username)
        suppress_warnings = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR'

        full_cmd = ' '.join([base, port, user_and_key, suppress_warnings, cmd])
        return run_command(full_cmd)

    def copy(self, username, port, filename, target_filename):
        base = 'scp'
        port = '-P {}'.format(port)
        if username == 'keeper':
            key = '-i ssh_keys/{}_rsa'.format(username)
        else:
            key = '-i ssh_keys/{}_rsa'.format(self.temp_dir.name, username)
        suppress_warnings = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR'
        copy_cmd = '{} {}@localhost:{}'.format(filename, username, target_filename)

        full_cmd = ' '.join([base, port, key, suppress_warnings, copy_cmd])
        return run_command(full_cmd)
