
from gkeeprobot.dectorators import polling
from gkeepcore.shell_command import run_command, CommandError


@polling
def server_running():
    try:
        run_command('screen -S gkserver -Q select .')
        return False
    except CommandError:
        return True


print(server_running())