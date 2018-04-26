
from gkeeprobot.control.ServerControl import ServerControl

control = ServerControl()


class ServerSetupKeywords:

    faculty = []

    def configure_faculty(self, *faculty_list):
        for faculty_name in faculty_list:
            ServerSetupKeywords.faculty.append(faculty_name)
            line = 'Professor,Doctor,{}@gitkeeper.edu'.format(faculty_name)
            control.run_vm_script('keeper', 'add_to_file.py', 'faculty.csv', line)

    def add_file(self, username, filename, target_filename):
        control.copy(username, filename, target_filename)

    def start_gkeepd(self):
        control.run('keeper', 'screen -S gkserver -d -m gkeepd')

    def stop_gkeepd(self):
        control.run('keeper', 'screen -S gkserver -X quit')

    def remove_user(self, username):
        control.run('keeper', 'sudo userdel -r {} || :'.format(username))

    def remove_faculty(self):
        for faculty_name in ServerSetupKeywords.faculty:
            self.remove_user(faculty_name)

        ServerSetupKeywords.faculty.clear()

    def remove_file(self, username, filename):
        control.run(username, 'rm {} || :'.format(filename))

    def clear_email(self):
        control.run('keeper', 'sudo find /email ! -name "mysmtpd.py" -type f -exec rm -f {} +')

    def add_faculty_account_on_server(self, faculty_name):
        control.run('keeper', 'sudo useradd -ms /bin/bash {}'.format(faculty_name))