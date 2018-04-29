
from gkeeprobot.control.ServerControl import ServerControl

control = ServerControl()


class ServerSetupKeywords:

    def configure_faculty(self, *faculty_list):
        for faculty_name in faculty_list:
            line = 'Professor,Doctor,{}@gitkeeper.edu'.format(faculty_name)
            control.run_vm_python_script('keeper', 'add_to_file.py', 'faculty.csv', line)

    def add_file_to_server(self, username, filename, target_filename):
        control.copy(username, filename, target_filename)

    def start_gkeepd(self):
        control.run('keeper', 'screen -S gkserver -d -m gkeepd')

    def add_account_on_server(self, faculty_name):
        control.run('keeper', 'sudo useradd -ms /bin/bash {}'.format(faculty_name))

    def reset_server(self):
        control.run_vm_python_script('keeper', 'reset_server.py')