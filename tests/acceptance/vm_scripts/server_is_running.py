
from gkeeprobot.dectorators import polling
from gkeepcore.shell_command import run_command, CommandError


@polling
def server_running():
    try:
        run_command('screen -S gkserver -Q select .')
        return True
    except CommandError:
        return False


print(server_running())