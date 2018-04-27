from gkeeprobot.control.VagrantControl import VagrantControl
from gkeeprobot.control.VMControl import VMControl


class ClientControl:

    def __init__(self):
        self.v = VagrantControl()
        self.vm_control = VMControl()

    def run_vm_python_script(self, username, script, *args):
        return self.vm_control.run_vm_python_script(username, script, self.v.get_client_port(), *args)

    def run_vm_bash_script(self, username, script, *args):
        return self.vm_control.run_vm_bash_script(username, script, self.v.get_client_port(), *args)

    def run(self, username, cmd):
        return self.vm_control.run(username, self.v.get_client_port(), cmd)

    def copy(self, username, filename, target_filename):
        return self.vm_control.copy(username, self.v.get_client_port(), filename, target_filename)
