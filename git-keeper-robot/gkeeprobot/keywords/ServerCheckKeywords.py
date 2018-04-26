from gkeeprobot.control.ServerControl import ServerControl

control = ServerControl()

class ServerCheckKeywords:
    def server_running(self):
        result = control.run_vm_script('keeper', 'server_running.py')
        assert result == 'Yes'

    def server_not_running(self):
        result = control.run_vm_script('keeper', 'server_running.py')
        assert result == 'No'

    def expect_email(self, to_user, contains):
        result = control.run_vm_script('keeper', 'email_check.py', to_user, contains)
        assert result == 'True'

    def user_exists(self, username):
        result = control.run_vm_script('keeper', 'user_exists.py', username)
        assert result == 'Yes'

    def user_does_not_exist(self, username):
        result = control.run_vm_script('keeper', 'user_exists.py', username)
        assert result == 'No'

    def no_email_to(self, username):
        result = control.run_vm_script('keeper', 'no_email_to.py', username)
        assert result == 'True'
