
from gkeeprobot.control.ServerControl import ServerControl

control = ServerControl()


class ServerKeywords:

    def set_faculty(self, *faculty_list):
        for faculty_name in faculty_list:
            line = 'Professor,Doctor,{}@gitkeeper.edu'.format(faculty_name)
            control.run_server_script('keeper', 'add_to_file.py', 'faculty.csv', line)

    def add_file(self, username, filename, target_filename):
        control.copy(username, filename, target_filename)

    def start_gkeepd(self):
        control.run('keeper', 'screen -S gkserver -d -m gkeepd')

    def stop_gkeepd(self):
        control.run('keeper', 'screen -S gkserver -X quit')

    def server_running(self):
        result = control.run_server_script('keeper', 'server_running.py')
        assert result == 'Yes'

    def server_not_running(self):
        result = control.run_server_script('keeper', 'server_running.py')
        assert result == 'No'

    def expect_email(self, to_user, contains):
        result = control.run_server_script('keeper', 'email_check.py', to_user, contains)
        assert result == 'True'

    def user_exists(self, username):
        result = control.run_server_script('keeper', 'user_exists.py', username)
        assert result == 'Yes'

    def user_does_not_exist(self, username):
        result = control.run_server_script('keeper', 'user_exists.py', username)
        assert result == 'No'

    def remove_user(self, username):
        control.run('keeper', 'sudo userdel -r {} || :'.format(username))

    def remove_file(self, username, filename):
        control.run(username, 'rm {} || :'.format(filename))

    def clear_email(self):
        control.run('keeper', 'sudo find /email ! -name "mysmtpd.py" -type f -exec rm -f {} +')
