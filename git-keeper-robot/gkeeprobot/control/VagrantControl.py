import vagrant


class VagrantControl:

    def __init__(self):
        self.v = vagrant.Vagrant()
        self.up_verified = False

    def run_on_client(self, username, cmd):
        return self.run_on(username, cmd, self.get_client_port())

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
