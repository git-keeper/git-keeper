
from gkeeprobot.control.ClientControl import ClientControl
from gkeeprobot.control.ServerControl import ServerControl
from gkeepcore.shell_command import CommandError

client_control = ClientControl()
server_control = ServerControl()


class ClientSetupKeywords:

    def create_accounts(self, *names):
        for name in names:
            client_control.run_vm_bash_script('keeper', 'make_user_with_password.sh', name)

    def establish_ssh_keys(self, *names):
        temp_dir_name = client_control.vm_control.temp_dir.name
        for name in names:
            client_control.run_vm_bash_script('keeper', 'make_ssh_keys.sh', name, temp_dir_name)
            server_control.run_vm_bash_script('keeper', 'make_authorized_keys.sh', name, temp_dir_name)

    def add_to_class(self, faculty, class_name, student):
        line = 'Last,First,{}@gitkeeper.edu'.format(student)
        client_control.run_vm_python_script(faculty, 'add_to_file.py', '{}.csv'.format(class_name), line)

    def add_file_to_client(self, username, filename, target_filename):
        client_control.copy(username, filename, target_filename)

    def make_empty_file(self, username, filename):
        client_control.run(username, 'touch {}'.format(filename))

    def create_gkeep_config_file(self, faculty):
        client_control.run_vm_bash_script(faculty, 'make_gkeep_config.sh', faculty)

    def reset_client(self):
        client_control.run_vm_python_script('keeper', 'reset_client.py')