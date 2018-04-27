
from gkeeprobot.control.ClientControl import ClientControl
from gkeeprobot.control.ServerControl import ServerControl
from robot.api import logger

client_control = ClientControl()
server_control = ServerControl()


class ClientSetupKeywords:

    students = []

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
        ClientSetupKeywords.students.append(student)
        client_control.run_vm_python_script(faculty, 'add_to_file.py', '{}.csv'.format(class_name), line)

    def run_gkeep_add(self, faculty, class_name):
        client_control.run(faculty, 'gkeep add {} {}.csv'.format(class_name, class_name))

    def create_gkeep_config_file(self, faculty):
        client_control.run_vm_bash_script(faculty, 'make_gkeep_config.sh', faculty)

    def remove_server_user(self, username):
        server_control.run('keeper', 'sudo userdel -r {} || :'.format(username))

    def remove_client_user(self, username):
        client_control.run('keeper', 'sudo userdel -r {} || :'.format(username))

    def remove_students(self):
        for student_name in ClientSetupKeywords.students:
            self.remove_client_user(student_name)
            self.remove_server_user(student_name)

        ClientSetupKeywords.students.clear()
