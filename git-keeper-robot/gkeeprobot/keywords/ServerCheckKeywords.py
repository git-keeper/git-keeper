from gkeeprobot.control.ServerControl import ServerControl

control = ServerControl()


class ServerCheckKeywords:
    def server_running(self):
        result = control.run_vm_python_script('keeper', 'server_is_running.py')
        assert result == 'True'

    def server_not_running(self):
        result = control.run_vm_python_script('keeper', 'server_terminated.py')
        assert result == 'True'

    def expect_email(self, to_user, contains):
        result = control.run_vm_python_script('keeper', 'email_to.py', to_user, contains)
        assert result == 'True'

    def user_exists(self, username):
        result = control.run_vm_python_script('keeper', 'user_exists.py', username)
        assert result == 'True'

    def user_does_not_exist(self, username):
        result = control.run_vm_python_script('keeper', 'user_does_not_exist.py', username)
        assert result == 'True'

    def expect_no_email(self, username):
        result = control.run_vm_python_script('keeper', 'no_email_to.py', username)
        assert result == 'True'
